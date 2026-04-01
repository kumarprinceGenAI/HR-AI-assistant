import re
from collections import Counter


def clean_text(text: str) -> str:
    """
    Clean raw PDF text safely (robust + generic)
    """

    # 1. Normalize newlines
    text = re.sub(r"\n+", "\n", text)

    # 2. Remove page numbers
    text = re.sub(r"Page \d+", "", text)

    # 3. Remove company header
    text = re.sub(r"\n?Traveling Prince Pvt\. Ltd\.\n?", "\n", text)

    # 4. Split into lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # 5. Count repeated lines
    line_counts = Counter(lines)

    cleaned_lines = []

    for line in lines:

        # 🔥 Remove repeated short lines (headers)
        if line_counts[line] >= 2 and len(line) < 40:
            continue

        # 🔥 Remove generic title-like patterns
        if re.match(r".*Handbook.*", line):
            continue

        # 🔥 Remove standalone version lines
        if re.match(r".*v\d+\.\d+.*", line):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 6. Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()