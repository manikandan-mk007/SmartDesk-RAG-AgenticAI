import re

from django.conf import settings


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def split_words_with_overlap(
    text: str,
    max_words: int,
    overlap_words: int,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    if len(words) <= max_words:
        return [text.strip()]

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = max(0, end - overlap_words)

    return chunks


def split_by_issue_blocks(text: str) -> list[str]:
    """
    Best for your 500+ issue/fix KB files.
    It keeps each issue as a focused chunk instead of mixing many issues together.
    """
    text = text.strip()

    if not text:
        return []

    parts = re.split(
        r"(?=\n?User issue:)",
        text,
        flags=re.IGNORECASE,
    )

    blocks = []

    for part in parts:
        block = part.strip()

        if not block:
            continue

        blocks.append(block)

    return blocks


def split_by_paragraphs(
    text: str,
    max_words: int,
    overlap_words: int,
) -> list[str]:
    paragraphs = [
        item.strip()
        for item in re.split(r"\n\s*\n", text)
        if item.strip()
    ]

    if not paragraphs:
        return split_words_with_overlap(text, max_words, overlap_words)

    chunks = []
    current_parts = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_words = count_words(paragraph)

        if paragraph_words > max_words:
            if current_parts:
                chunks.append("\n\n".join(current_parts).strip())
                current_parts = []
                current_word_count = 0

            chunks.extend(
                split_words_with_overlap(
                    paragraph,
                    max_words=max_words,
                    overlap_words=overlap_words,
                )
            )
            continue

        if current_word_count + paragraph_words > max_words and current_parts:
            chunks.append("\n\n".join(current_parts).strip())
            current_parts = [paragraph]
            current_word_count = paragraph_words
        else:
            current_parts.append(paragraph)
            current_word_count += paragraph_words

    if current_parts:
        chunks.append("\n\n".join(current_parts).strip())

    return chunks


def split_clean_text_into_chunks(text: str) -> list[str]:
    max_words = getattr(settings, "KB_CHUNK_MAX_WORDS", 220)
    overlap_words = getattr(settings, "KB_CHUNK_OVERLAP_WORDS", 35)
    split_by_issue = getattr(settings, "KB_SPLIT_BY_ISSUE", True)

    text = (text or "").strip()

    if not text:
        return []

    final_chunks = []

    if split_by_issue:
        issue_blocks = split_by_issue_blocks(text)

        # If issue blocks are detected, keep issue-wise chunks.
        if len(issue_blocks) > 1:
            for block in issue_blocks:
                if count_words(block) > max_words:
                    final_chunks.extend(
                        split_words_with_overlap(
                            block,
                            max_words=max_words,
                            overlap_words=overlap_words,
                        )
                    )
                else:
                    final_chunks.append(block)

            return [
                chunk.strip()
                for chunk in final_chunks
                if count_words(chunk) >= 15
            ]

    final_chunks = split_by_paragraphs(
        text,
        max_words=max_words,
        overlap_words=overlap_words,
    )

    return [
        chunk.strip()
        for chunk in final_chunks
        if count_words(chunk) >= 15
    ]