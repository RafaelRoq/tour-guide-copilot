"""Document parser. Reads the guide's knowledge from various file formats."""

from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def parse_document(file_path: str) -> str:
    """Read a guide's document and return clean text.

    Supports .md, .txt, and .pdf files. No semantic transformation —
    just reading and basic cleanup.

    Args:
        file_path: Path to the guide's document.

    Returns:
        The document content as a clean string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not supported.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format: {path.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    else:
        return _read_text(path)


def _read_text(path: Path) -> str:
    """Read a plain text or markdown file."""
    text = path.read_text(encoding="utf-8")
    return _clean(text)


def _read_pdf(path: Path) -> str:
    """Read a PDF file and extract text.

    Requires pypdf to be installed. If not available, raises an
    ImportError with install instructions.

    Warns if the extracted text looks suspiciously short or noisy,
    which often indicates a scanned PDF without OCR.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "PDF support requires pypdf. Install it with: "
            "pip install pypdf"
        )

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages)
    cleaned = _clean(text)

    # Warn about low-quality extraction
    if len(reader.pages) > 0:
        chars_per_page = len(cleaned) / len(reader.pages)
        if chars_per_page < 50:
            import warnings
            warnings.warn(
                f"PDF extraction yielded very little text (~{chars_per_page:.0f} chars/page). "
                f"The file may be a scanned image without OCR. "
                f"For best results, convert to .md or .txt first.",
                stacklevel=2,
            )

    return cleaned


def _clean(text: str) -> str:
    """Basic text cleanup: normalize whitespace, strip edges."""
    lines = text.splitlines()
    # Remove completely blank lines at start and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # Collapse multiple blank lines into one
    cleaned = []
    prev_blank = False
    for line in lines:
        if not line.strip():
            if not prev_blank:
                cleaned.append("")
            prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False
    return "\n".join(cleaned).strip()
