"""Tests for the renderer module."""

import json
import tempfile
from pathlib import Path

from copilot.renderer import render, _render_markdown, _build_combined
from copilot.config import Config


SAMPLE_ITINERARY = {
    "title": "Test Tour",
    "tagline": "10 years of walking so you don't have to trust Google.",
    "duration_minutes": 90,
    "stops": [
        {
            "order": 1,
            "name": "Main Square",
            "description": "The heart of the city.",
            "tip": "Visit in the morning.",
            "coordinates": None,
        }
    ],
}

SAMPLE_PLANS = {
    "plans": [
        {
            "situation": "Where do I eat?",
            "slug": "eat-after-tour",
            "recommendations": [
                {
                    "name": "The corner taberna with the blue awning",
                    "description": "Been going here for years. The owner knows every regular by name.",
                    "what_to_order": "The house special",
                    "what_to_avoid": "The tourist menu",
                    "price_range": "€€",
                    "vibe": "Cozy and local",
                    "coordinates": None,
                }
            ],
        }
    ],
    "warnings": ["Watch your pockets in crowded areas."],
}


def _make_config(**overrides) -> Config:
    defaults = dict(
        api_key="test",
        guide_name="TestGuide",
        guide_city="TestCity",
        guide_language="en",
        output_format="all",
    )
    defaults.update(overrides)
    return Config(**defaults)


def test_build_combined():
    """Combined structure has all expected keys."""
    config = _make_config()
    data = _build_combined(SAMPLE_ITINERARY, SAMPLE_PLANS, config)

    assert data["guide"]["name"] == "TestGuide"
    assert data["guide"]["city"] == "TestCity"
    assert len(data["itinerary"]["stops"]) == 1
    assert len(data["plans"]) == 1
    assert len(data["warnings"]) == 1
    assert "generated_at" in data["metadata"]


def test_render_markdown():
    """Markdown renderer produces readable output."""
    config = _make_config()
    data = _build_combined(SAMPLE_ITINERARY, SAMPLE_PLANS, config)
    md = _render_markdown(data)

    assert "# TestGuide — TestCity" in md
    assert "Main Square" in md
    assert "Where do I eat?" in md
    assert "The house special" in md
    assert "Watch your pockets" in md


def test_render_creates_files():
    """Render creates output files in the specified directory."""
    config = _make_config(output_format="all")
    with tempfile.TemporaryDirectory() as tmpdir:
        created = render(SAMPLE_ITINERARY, SAMPLE_PLANS, config, tmpdir)

        assert len(created) == 3
        extensions = {Path(f).suffix for f in created}
        assert extensions == {".json", ".md", ".html"}

        # Verify JSON is valid
        json_file = [f for f in created if f.endswith(".json")][0]
        data = json.loads(Path(json_file).read_text())
        assert data["guide"]["name"] == "TestGuide"


def test_render_html_only():
    """Render creates only HTML when format is html."""
    config = _make_config(output_format="html")
    with tempfile.TemporaryDirectory() as tmpdir:
        created = render(SAMPLE_ITINERARY, SAMPLE_PLANS, config, tmpdir)

        assert len(created) == 1
        assert created[0].endswith(".html")


def test_render_html_escapes_xss():
    """HTML renderer escapes potentially dangerous content."""
    xss_itinerary = {
        "title": '<script>alert(1)</script>',
        "duration_minutes": 90,
        "stops": [
            {
                "order": 1,
                "name": '<img onerror="alert(1)" src=x>',
                "description": "Normal description",
                "tip": None,
                "coordinates": None,
            }
        ],
    }
    config = _make_config(output_format="html")
    with tempfile.TemporaryDirectory() as tmpdir:
        created = render(xss_itinerary, SAMPLE_PLANS, config, tmpdir)
        html_content = Path(created[0]).read_text()

        # Malicious content must be escaped, not rendered as HTML
        assert "<script>alert" not in html_content
        assert '<img onerror' not in html_content
        assert "&lt;script&gt;" in html_content
