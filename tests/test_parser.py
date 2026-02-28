"""Tests for the document parser."""

import tempfile
from pathlib import Path

from copilot.parser import parse_document, _clean


def test_read_markdown():
    """Parser reads a markdown file and returns clean text."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# My Tour\n\nStop 1: Plaza Mayor\n\nGreat place.\n")
        f.flush()
        result = parse_document(f.name)

    assert "# My Tour" in result
    assert "Plaza Mayor" in result


def test_read_txt():
    """Parser reads a plain text file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is my tour guide knowledge.\n")
        f.flush()
        result = parse_document(f.name)

    assert "tour guide knowledge" in result


def test_unsupported_format():
    """Parser raises ValueError for unsupported formats."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".docx", delete=False) as f:
        f.write("content")
        f.flush()
        try:
            parse_document(f.name)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported format" in str(e)


def test_file_not_found():
    """Parser raises FileNotFoundError for missing files."""
    try:
        parse_document("/nonexistent/file.md")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def test_clean_collapses_blank_lines():
    """Clean function collapses multiple blank lines."""
    text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
    result = _clean(text)
    assert result == "Line 1\n\nLine 2\n\nLine 3"


def test_clean_strips_edges():
    """Clean function strips blank lines from start and end."""
    text = "\n\n\nContent here\n\n\n"
    result = _clean(text)
    assert result == "Content here"
