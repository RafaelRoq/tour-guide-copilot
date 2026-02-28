"""Tests for the schemas module: slug generation and JSON validation."""

import pytest

from copilot.schemas import (
    sanitize_slug,
    ensure_unique_slugs,
    validate_itinerary,
    validate_plans,
)
from copilot.exceptions import SchemaError


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

class TestSanitizeSlug:
    def test_basic(self):
        assert sanitize_slug("A bar tonight?") == "a-bar-tonight"

    def test_accents(self):
        assert sanitize_slug("¿Dónde como?") == "donde-como"

    def test_numbers(self):
        assert sanitize_slug("2 free hours") == "2-free-hours"

    def test_empty_fallback(self):
        assert sanitize_slug("   ") == "plan"
        assert sanitize_slug("???") == "plan"

    def test_no_leading_trailing_dashes(self):
        assert sanitize_slug("--hello--") == "hello"


class TestEnsureUniqueSlugs:
    def test_unique_situations(self):
        plans = [
            {"situation": "Where to eat"},
            {"situation": "Where to drink"},
        ]
        ensure_unique_slugs(plans)
        assert plans[0]["slug"] == "where-to-eat"
        assert plans[1]["slug"] == "where-to-drink"

    def test_duplicate_situations(self):
        plans = [
            {"situation": "Where to eat"},
            {"situation": "Where to eat"},
            {"situation": "Where to eat"},
        ]
        ensure_unique_slugs(plans)
        assert plans[0]["slug"] == "where-to-eat"
        assert plans[1]["slug"] == "where-to-eat-2"
        assert plans[2]["slug"] == "where-to-eat-3"

    def test_ignores_model_slug(self):
        """Slugs are always derived from situation, not from model output."""
        plans = [{"situation": "Dinner spots", "slug": "something-the-model-made-up"}]
        ensure_unique_slugs(plans)
        assert plans[0]["slug"] == "dinner-spots"


# ---------------------------------------------------------------------------
# Itinerary validation
# ---------------------------------------------------------------------------

class TestValidateItinerary:
    def test_valid_minimal(self):
        data = {
            "stops": [
                {"order": 1, "name": "Plaza Mayor", "description": "The main square."}
            ]
        }
        result = validate_itinerary(data)
        assert result["title"] == "Tour"  # default
        assert result["duration_minutes"] is None
        assert result["stops"][0]["tip"] is None

    def test_coerces_duration(self):
        data = {
            "duration_minutes": "120",
            "stops": [{"order": 1, "name": "A", "description": "B"}],
        }
        result = validate_itinerary(data)
        assert result["duration_minutes"] == 120

    def test_auto_numbers_stops(self):
        data = {
            "stops": [
                {"name": "First", "description": "A"},
                {"name": "Second", "description": "B"},
            ]
        }
        result = validate_itinerary(data)
        assert result["stops"][0]["order"] == 1
        assert result["stops"][1]["order"] == 2

    def test_missing_stops_raises(self):
        with pytest.raises(SchemaError, match="stops"):
            validate_itinerary({"title": "test"})

    def test_empty_stops_raises(self):
        with pytest.raises(SchemaError, match="empty"):
            validate_itinerary({"stops": []})

    def test_missing_stop_name_raises(self):
        with pytest.raises(SchemaError, match="name"):
            validate_itinerary({"stops": [{"description": "no name here"}]})

    def test_preserves_raw_response(self):
        try:
            validate_itinerary({"stops": []}, raw_response='{"stops":[]}')
        except SchemaError as e:
            assert e.raw_response == '{"stops":[]}'


# ---------------------------------------------------------------------------
# Plans validation
# ---------------------------------------------------------------------------

class TestValidatePlans:
    def test_valid_minimal(self):
        data = {
            "plans": [
                {
                    "situation": "Where to eat",
                    "recommendations": [{"name": "La Taberna"}],
                }
            ],
            "warnings": ["Watch your pockets"],
        }
        result = validate_plans(data)
        assert result["plans"][0]["slug"] == "where-to-eat"
        assert result["plans"][0]["recommendations"][0]["what_to_order"] is None

    def test_missing_plans_raises(self):
        with pytest.raises(SchemaError, match="plans"):
            validate_plans({})

    def test_missing_situation_raises(self):
        with pytest.raises(SchemaError, match="situation"):
            validate_plans({"plans": [{"recommendations": []}]})

    def test_coerces_warnings_to_strings(self):
        data = {
            "plans": [{"situation": "Test", "recommendations": []}],
            "warnings": [42, True],
        }
        result = validate_plans(data)
        assert result["warnings"] == ["42", "True"]

    def test_defaults_empty_warnings(self):
        data = {
            "plans": [{"situation": "Test", "recommendations": []}],
        }
        result = validate_plans(data)
        assert result["warnings"] == []

    def test_optional_recommendation_fields(self):
        data = {
            "plans": [
                {
                    "situation": "Dinner",
                    "recommendations": [
                        {
                            "name": "Place",
                            "what_to_order": "The rice",
                            "vibe": "Cozy",
                            # no description, what_to_avoid, price_range
                        }
                    ],
                }
            ],
        }
        result = validate_plans(data)
        rec = result["plans"][0]["recommendations"][0]
        assert rec["what_to_order"] == "The rice"
        assert rec["description"] is None
        assert rec["what_to_avoid"] is None
        assert rec["price_range"] is None
