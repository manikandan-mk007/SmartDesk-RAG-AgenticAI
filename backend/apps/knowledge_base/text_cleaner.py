import re


RAW_MARKDOWN_LABELS = [
    "tags:",
    "**tags:**",
    "support note:",
    "**support note:**",
]


def normalize_spaces(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("\ufeff", "")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def clean_line(line: str) -> str:
    line = line.strip()

    if not line:
        return ""

    # Remove horizontal separators
    if re.fullmatch(r"[-_*]{3,}", line):
        return ""

    # Remove issue number headings like "## Issue 201"
    if re.match(r"^#{1,6}\s*Issue\s+\d+\s*$", line, flags=re.IGNORECASE):
        return ""

    # Remove pure markdown heading marks but keep text
    line = re.sub(r"^#{1,6}\s*", "", line)

    # Convert raw KB labels into cleaner semantic labels
    line = re.sub(
        r"^\*\*Category:\*\*\s*",
        "Topic: ",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(
        r"^\*\*Question:\*\*\s*",
        "User issue: ",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(
        r"^\*\*Answer:\*\*\s*",
        "Recommended fix: ",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"^Category:\s*",
        "Topic: ",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(
        r"^Question:\s*",
        "User issue: ",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(
        r"^Answer:\s*",
        "Recommended fix: ",
        line,
        flags=re.IGNORECASE,
    )

    # Remove raw tags and internal support notes from user-facing RAG source
    lower_line = line.lower()
    if any(lower_line.startswith(label) for label in RAW_MARKDOWN_LABELS):
        return ""

    # Normalize common sections
    line = re.sub(
        r"^Fix steps:\s*",
        "Recommended steps:",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(
        r"^Likely cause:\s*",
        "Likely cause: ",
        line,
        flags=re.IGNORECASE,
    )

    # Remove remaining markdown bold markers
    line = line.replace("**", "")

    # Normalize numbered list spacing
    line = re.sub(r"^(\d+)\.\s*", r"\1. ", line)

    return line.strip()


def remove_duplicate_lines(lines: list[str]) -> list[str]:
    cleaned = []
    seen = set()

    for line in lines:
        key = line.lower().strip()

        if not key:
            cleaned.append("")
            continue

        # Avoid removing numbered troubleshooting steps that may share similar text
        if key in seen and not re.match(r"^\d+\.", key):
            continue

        seen.add(key)
        cleaned.append(line)

    return cleaned


def clean_uploaded_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = normalize_spaces(raw_text)
    raw_lines = text.split("\n")

    cleaned_lines = []

    for line in raw_lines:
        cleaned = clean_line(line)

        if cleaned:
            cleaned_lines.append(cleaned)
        else:
            cleaned_lines.append("")

    cleaned_lines = remove_duplicate_lines(cleaned_lines)

    cleaned_text = "\n".join(cleaned_lines)

    # Collapse too many blank lines
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    # Keep one clean space around labels
    cleaned_text = re.sub(r"[ \t]+\n", "\n", cleaned_text)

    return cleaned_text.strip()