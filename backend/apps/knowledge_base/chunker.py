import re


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]

        last_period = chunk.rfind(".")
        last_newline = chunk.rfind("\n")

        split_at = max(last_period, last_newline)

        if split_at > chunk_size * 0.5 and end < text_length:
            end = start + split_at + 1
            chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, start + 1)

    return chunks