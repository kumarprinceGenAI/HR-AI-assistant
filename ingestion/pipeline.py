from langchain_core.documents import Document

from ingestion.loader import load_pdf
from ingestion.cleaner import clean_text
from ingestion.chunker import split_into_sections, chunk_sections
from ingestion.metadata import extract_metadata


def remove_duplicate_blocks(text: str) -> str:
    """
    Remove repeated lines
    """
    seen = set()
    result = []

    for line in text.split("\n"):
        if line not in seen:
            seen.add(line)
            result.append(line)

    return "\n".join(result)


def process_pdf(file_path: str):
    """
    Full pipeline:
    PDF → Clean → Deduplicate → Chunk → Metadata → Documents
    """

    docs = load_pdf(file_path)

    processed_text = ""

    # 🔹 Step 1: Page processing
    for i, doc in enumerate(docs):
        text = doc.page_content

        # Remove TOC only from first page
        if i == 0 and "Table of Contents" in text:
            parts = text.split("Table of Contents")
            if len(parts) > 1:
                text = parts[0]

        cleaned = clean_text(text)
        processed_text += cleaned + "\n"

    # 🔹 Step 2: Deduplicate
    processed_text = remove_duplicate_blocks(processed_text)

    # 🔹 Step 3: Chunking
    sections = split_into_sections(processed_text)
    chunks = chunk_sections(sections)

    # 🔹 Step 4: Convert to Documents
    documents = []

    for chunk in chunks:
        metadata = extract_metadata(chunk, file_path)

        doc = Document(
            page_content=chunk,
            metadata=metadata
        )

        documents.append(doc)

    return documents