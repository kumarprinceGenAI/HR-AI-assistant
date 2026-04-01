import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_into_sections(text: str):
    """
    Step 1: Split document into logical sections
    """

    splits = re.split(r"\n(?=\d+\.\s)", text)

    sections = []

    for chunk in splits:
        chunk = chunk.strip()

        if len(chunk) < 50:
            continue

        sections.append(chunk)

    return sections


def chunk_sections(sections):
    """
    Step 2: Apply RecursiveCharacterTextSplitter inside sections
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,      # smaller because HR policies are short
        chunk_overlap=50,    # slight overlap for safety
        separators=["\n\n", "\n", ".", " "]  # smart splitting priority
    )

    final_chunks = []

    for section in sections:

        # 🔥 If section is small → keep as is
        if len(section) < 300:
            final_chunks.append(section)
        else:
            # 🔥 If large → split further
            chunks = splitter.split_text(section)
            final_chunks.extend(chunks)

    return final_chunks