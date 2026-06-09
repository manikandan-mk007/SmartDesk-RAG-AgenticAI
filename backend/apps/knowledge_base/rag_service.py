import re

from django.conf import settings

from apps.ai_engine.llm_provider import LLMProvider, LLMProviderError, extract_json_from_text
from apps.ai_engine.prompt_templates import (
    RAG_ANSWER_SYSTEM_PROMPT,
    build_rag_answer_prompt,
)

from .embeddings import generate_embedding
from .vector_store import VectorStoreService


RAW_KB_MARKERS = [
    "## Issue",
    "**Category:**",
    "**Question:**",
    "**Answer:**",
    "**Tags:**",
    "Tags:",
    "Support note:",
    "---",
]

DEVICE_TYPO_MAP = {
    "loptop": "laptop",
    "lapotp": "laptop",
    "labtop": "laptop",
    "notbook": "notebook",
}

def normalize_question_for_retrieval(question: str) -> str:
    text = question or ""
    normalized = text.lower()

    for wrong, correct in DEVICE_TYPO_MAP.items():
        normalized = re.sub(rf"\b{wrong}\b", correct, normalized, flags=re.IGNORECASE)

    return normalized


def detect_preferred_sources(question: str) -> list[str]:
    q = normalize_question_for_retrieval(question)

    has_windows = any(word in q for word in ["windows", "win 10", "win 11"])
    has_mac = any(word in q for word in ["mac", "macbook", "imac", "macos"])
    has_linux = any(word in q for word in ["linux", "ubuntu", "fedora", "debian"])
    has_laptop = any(word in q for word in ["laptop", "notebook", "macbook"])
    has_pc = any(word in q for word in ["pc", "desktop", "workstation", "computer"])

    if has_windows and has_laptop:
        return ["windows_laptop", "window_laptop"]

    if has_mac and has_laptop:
        return ["mac_laptop", "macbook"]

    if has_linux and has_laptop:
        return ["linux_laptop", "linuxs_laptop"]

    if has_windows and has_pc:
        return ["windows_pc", "window_pc"]

    if has_mac and has_pc:
        return ["mac_pc", "imac"]

    if has_linux and has_pc:
        return ["linux_pc", "linuxs_pc"]

    if has_laptop:
        return ["windows_laptop", "mac_laptop", "linux_laptop", "linuxs_laptop", "laptop"]

    if has_pc:
        return ["windows_pc", "mac_pc", "linux_pc", "linuxs_pc", "pc", "desktop"]

    return []


def result_source_text(item: dict) -> str:
    metadata = item.get("metadata", {}) or {}

    value = " ".join(
        [
            str(metadata.get("document_title", "")),
            str(metadata.get("file_name", "")),
            str(metadata.get("source", "")),
        ]
    )

    return value.lower().replace("-", "_").replace(" ", "_")


def source_matches_preference(item: dict, preferred_sources: list[str]) -> bool:
    source_text = result_source_text(item)

    return any(source in source_text for source in preferred_sources)


def apply_device_source_preference(question: str, results: list[dict]) -> list[dict]:
    preferred_sources = detect_preferred_sources(question)

    if not preferred_sources:
        return results

    preferred_results = [
        item for item in results if source_matches_preference(item, preferred_sources)
    ]

    # If matching laptop/PC documents exist, use them first.
    # If not, safely fallback to normal vector results.
    if preferred_results:
        return preferred_results

    return results

def parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in ["true", "yes", "1"]

    return bool(value)


def has_raw_kb_markers(text: str) -> bool:
    if not text:
        return False

    lowered = text.lower()

    markers = [
        "## issue",
        "**category:**",
        "**question:**",
        "**answer:**",
        "**tags:**",
        "\ntags:",
        "\nsupport note:",
    ]

    return any(marker in lowered for marker in markers)


def sanitize_context_text(text: str) -> str:
    text = text or ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("**", "")

    lines = []

    for line in text.split("\n"):
        clean = line.strip()

        if not clean:
            lines.append("")
            continue

        if re.match(r"^#{1,6}\s*Issue\s+\d+\s*$", clean, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"[-_*]{3,}", clean):
            continue

        if clean.lower().startswith("tags:"):
            continue

        if clean.lower().startswith("support note:"):
            continue

        clean = re.sub(r"^Category:\s*", "Topic: ", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^Question:\s*", "User issue: ", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^Answer:\s*", "Recommended fix: ", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^Fix steps:\s*", "Recommended steps:", clean, flags=re.IGNORECASE)

        lines.append(clean)

    clean_text = "\n".join(lines)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

    return clean_text.strip()


def sanitize_final_answer(answer: str) -> str:
    answer = (answer or "").strip()

    answer = answer.replace("**", "")
    answer = re.sub(r"^#{1,6}\s*", "", answer, flags=re.MULTILINE)
    answer = re.sub(r"\n?---+\n?", "\n", answer)

    forbidden_label_patterns = [
        r"^\s*Issue\s+\d+\s*$",
        r"^\s*Category:\s*.*$",
        r"^\s*Question:\s*.*$",
        r"^\s*Answer:\s*",
        r"^\s*Tags:\s*.*$",
        r"^\s*Support note:\s*.*$",
    ]

    cleaned_lines = []

    for line in answer.splitlines():
        skip = False

        for pattern in forbidden_label_patterns:
            if re.match(pattern, line, flags=re.IGNORECASE):
                skip = True
                break

        if not skip:
            cleaned_lines.append(line)

    answer = "\n".join(cleaned_lines).strip()
    answer = re.sub(r"\n{3,}", "\n\n", answer)

    return answer


def extract_numbered_steps(text: str) -> list[str]:
    steps = []

    for line in text.splitlines():
        line = line.strip()

        match = re.match(r"^\d+\.\s*(.+)$", line)

        if match:
            step = match.group(1).strip()

            if step:
                steps.append(step)

    return steps


def extract_likely_cause(text: str) -> str:
    match = re.search(
        r"Likely cause:\s*(.+)",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    return match.group(1).strip()


def get_unresolved_attempt_count(question: str) -> int:
    match = re.search(
        r"Unresolved attempt count:\s*(\d+)",
        question or "",
        flags=re.IGNORECASE,
    )

    if not match:
        return 0

    try:
        return int(match.group(1))
    except ValueError:
        return 0


def build_clean_fallback_from_context(question: str, top_text: str, top_score: float) -> dict:
    clean_text = sanitize_context_text(top_text)
    steps = extract_numbered_steps(clean_text)
    likely_cause = extract_likely_cause(clean_text)
    unresolved_count = get_unresolved_attempt_count(question)

    answer_lines = []

    if likely_cause:
        answer_lines.append(f"The issue may be related to {likely_cause.lower()}.")

    if steps:
        for index, step in enumerate(steps[:4], start=1):
            answer_lines.append(f"Step {index}: {step}")
    else:
        # Last safe fallback: summarize cleaned text, but never raw markdown.
        compact = re.sub(r"\s+", " ", clean_text).strip()

        if compact:
            answer_lines.append(compact[:700].rstrip() + ("..." if len(compact) > 700 else ""))

    needs_ticket = unresolved_count >= 3

    if needs_ticket:
        answer_lines.append(
            "Since the issue is still not resolved after multiple attempts, please create a support ticket or contact our agent. They can check the device, logs, screenshots, hardware condition, account status, or configuration directly."
        )

    answer = "\n\n".join(answer_lines).strip()

    if not answer:
        answer = (
            "The available knowledge base does not contain enough information "
            "for a confirmed fix. Please create a support ticket so an agent can help."
        )
        needs_ticket = True

    return {
        "answer": answer,
        "confidence_score": round(top_score, 4),
        "needs_ticket": needs_ticket,
        "suggested_ticket_subject": question[:120] if needs_ticket else "",
        "suggested_ticket_description": (
            "User issue:\n"
            f"{question}\n\n"
            "The user needs agent support because the issue was not resolved from the knowledge base guidance."
            if needs_ticket
            else ""
        ),
        "model_used": "rag-clean-fallback",
    }


def build_context(results: list[dict]) -> str:
    context_parts = []

    for index, item in enumerate(results, start=1):
        metadata = item.get("metadata", {})
        source = metadata.get("document_title", "Knowledge Base")
        clean_text = sanitize_context_text(item.get("text", ""))

        context_parts.append(
            f"Source {index}: {source}\n"
            f"Content:\n{clean_text}"
        )

    return "\n\n====\n\n".join(context_parts)


def build_sources(results: list[dict]) -> list[dict]:
    sources = []

    for item in results:
        metadata = item.get("metadata", {})

        sources.append(
            {
                "document_id": metadata.get("document_id"),
                "document_title": metadata.get("document_title"),
                "file_name": metadata.get("file_name"),
                "chunk_index": metadata.get("chunk_index"),
                "similarity_score": round(item.get("similarity_score", 0.0), 4),
            }
        )

    return sources


def fallback_rag_answer(question: str, results: list[dict]) -> dict:
    if not results:
        return {
            "answer": (
                "The available knowledge base does not contain enough information "
                "for this question. Please create a support ticket so an agent can help."
            ),
            "confidence_score": 0.0,
            "needs_ticket": True,
            "suggested_ticket_subject": question[:120],
            "suggested_ticket_description": question,
            "model_used": "rag-fallback",
        }

    top_text = results[0].get("text", "")
    top_score = results[0].get("similarity_score", 0.0)

    if top_score < settings.RAG_MIN_SCORE:
        return {
            "answer": (
                "The available knowledge base does not contain a confident answer "
                "for this question. Please create a support ticket so an agent can check it."
            ),
            "confidence_score": round(top_score, 4),
            "needs_ticket": True,
            "suggested_ticket_subject": question[:120],
            "suggested_ticket_description": question,
            "model_used": "rag-fallback-low-confidence",
        }

    return build_clean_fallback_from_context(
        question=question,
        top_text=top_text,
        top_score=top_score,
    )


def ask_rag(question: str) -> dict:
    retrieval_question = normalize_question_for_retrieval(question)

    query_embedding = generate_embedding(retrieval_question)

    vector_store = VectorStoreService()
    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=max(settings.RAG_TOP_K * 4, 12),
    )

    filtered_results = [
        item
        for item in results
        if item.get("similarity_score", 0.0) >= settings.RAG_MIN_SCORE
    ]

    filtered_results = apply_device_source_preference(
        question=retrieval_question,
        results=filtered_results,
    )

    filtered_results = filtered_results[: settings.RAG_TOP_K]

    if not filtered_results:
        fallback = fallback_rag_answer(question, results=[])
        return {
            **fallback,
            "sources": [],
            "has_context": False,
        }

    context = build_context(filtered_results)
    sources = build_sources(filtered_results)

    provider = LLMProvider()

    try:
        response_text, model_used = provider.generate_text(
            system_prompt=RAG_ANSWER_SYSTEM_PROMPT,
            user_prompt=build_rag_answer_prompt(
                question=question,
                context=context,
            ),
        )

        data = extract_json_from_text(response_text)

        answer = str(data.get("answer", "")).strip()

        if not answer:
            raise ValueError("Empty answer from LLM.")

        if has_raw_kb_markers(answer):
            raise ValueError("Raw KB formatted answer detected.")

        answer = sanitize_final_answer(answer)

        if not answer:
            raise ValueError("Answer became empty after sanitization.")

        confidence_score = float(
            data.get(
                "confidence_score",
                filtered_results[0].get("similarity_score", 0.0),
            )
        )

        needs_ticket = parse_bool(data.get("needs_ticket", False))

        unresolved_count = get_unresolved_attempt_count(question)

        if unresolved_count >= 3:
            needs_ticket = True

        return {
            "answer": answer,
            "confidence_score": round(confidence_score, 4),
            "needs_ticket": needs_ticket,
            "suggested_ticket_subject": str(
                data.get("suggested_ticket_subject", "")
            ).strip(),
            "suggested_ticket_description": str(
                data.get("suggested_ticket_description", "")
            ).strip(),
            "model_used": model_used,
            "sources": sources,
            "has_context": True,
        }

    except (LLMProviderError, ValueError, KeyError, TypeError):
        fallback = fallback_rag_answer(question, filtered_results)

        return {
            **fallback,
            "sources": sources,
            "has_context": True,
        }