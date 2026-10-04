from dataclasses import dataclass
from io import BytesIO
from collections import Counter
import fitz  # PyMuPDF


@dataclass
class ResumeDocument:
    text: str
    page_count: int
    fonts: list[tuple[str, int]]
    font_sizes: list[tuple[float, int]]


def extract_pdf(file_bytes: bytes) -> ResumeDocument:
    doc = fitz.open(stream=BytesIO(file_bytes), filetype="pdf")
    texts: list[str] = []
    font_counter: Counter[str] = Counter()
    size_counter: Counter[float] = Counter()

    for page in doc:
        texts.append(page.get_text("text"))
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font = str(span.get("font", "Unknown"))
                    size = round(float(span.get("size", 0)), 1)
                    font_counter[font] += len(span.get("text", "")) or 1
                    if size:
                        size_counter[size] += len(span.get("text", "")) or 1

    return ResumeDocument(
        text="\n".join(texts).strip(),
        page_count=len(doc),
        fonts=font_counter.most_common(8),
        font_sizes=size_counter.most_common(8),
    )
