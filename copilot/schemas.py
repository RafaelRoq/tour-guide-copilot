"""Schema validation for model outputs and slug generation.

Validates that the JSON returned by the model matches the expected
structure. No external dependencies — just plain Python checks.
"""

import re
import unicodedata

from .exceptions import SchemaError


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def sanitize_slug(text: str) -> str:
    """Convert arbitrary text into a safe HTML id: [a-z0-9-], no leading/trailing dashes.

    Examples:
        "¿Dónde como?" → "donde-como"
        "A bar tonight?" → "a-bar-tonight"
        "2 free hours"  → "2-free-hours"
    """
    # Normalize unicode (é → e, ñ → n, etc.)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace non-alnum with dashes, collapse, strip
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "plan"


def ensure_unique_slugs(plans: list[dict]) -> list[dict]:
    """Generate safe, unique slugs from each plan's situation. Mutates in place and returns.

    Always derives from the situation text, ignoring any slug the model may
    have generated, to ensure consistent and readable HTML ids.
    """
    seen: dict[str, int] = {}
    for plan in plans:
        base = sanitize_slug(plan.get("situation", "plan"))
        if base in seen:
            seen[base] += 1
            plan["slug"] = f"{base}-{seen[base]}"
        else:
            seen[base] = 1
            plan["slug"] = base
    return plans


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _check_type(value, expected_type, field_name: str, raw: str = ""):
    """Assert a value has the expected type."""
    if not isinstance(value, expected_type):
        raise SchemaError(
            f"Field '{field_name}' expected {expected_type.__name__}, "
            f"got {type(value).__name__}.",
            raw_response=raw,
        )


def _check_required(data: dict, fields: list[str], context: str, raw: str = ""):
    """Assert that all required fields are present in a dict."""
    missing = [f for f in fields if f not in data]
    if missing:
        raise SchemaError(
            f"{context}: missing required fields: {', '.join(missing)}.",
            raw_response=raw,
        )


# ---------------------------------------------------------------------------
# Itinerary validation
# ---------------------------------------------------------------------------

def _normalize_coordinates(val) -> "dict | None":
    """Return a valid {lat, lng} dict, or None if invalid/absent."""
    if val is None:
        return None
    if isinstance(val, dict) and "lat" in val and "lng" in val:
        return val
    return None


def validate_itinerary(data: dict, raw_response: str = "") -> dict:
    """Validate and normalize the itinerary JSON from the model.

    Required structure:
        {
            "title": str,
            "duration_minutes": int | None,
            "stops": [
                {"order": int, "name": str, "description": str,
                 "tip": str|None, "coordinates": {"lat": float, "lng": float}|None}, ...
            ]
        }

    Returns the validated (and slightly normalized) dict.
    """
    raw = raw_response
    _check_type(data, dict, "itinerary (root)", raw)

    # Title — default if missing
    data.setdefault("title", "Tour")
    _check_type(data["title"], str, "itinerary.title", raw)

    # Duration — optional, coerce to int or None
    dur = data.get("duration_minutes")
    if dur is not None:
        try:
            data["duration_minutes"] = int(dur)
        except (ValueError, TypeError):
            data["duration_minutes"] = None
    else:
        data["duration_minutes"] = None

    # Stops — required, must be a non-empty list
    if "stops" not in data:
        raise SchemaError("Itinerary has no 'stops' field.", raw)
    _check_type(data["stops"], list, "itinerary.stops", raw)
    if not data["stops"]:
        raise SchemaError("Itinerary 'stops' is empty — model returned no stops.", raw)

    for i, stop in enumerate(data["stops"]):
        prefix = f"itinerary.stops[{i}]"
        _check_type(stop, dict, prefix, raw)
        _check_required(stop, ["name", "description"], prefix, raw)

        # Order — default to position if missing
        if "order" not in stop:
            stop["order"] = i + 1
        try:
            stop["order"] = int(stop["order"])
        except (ValueError, TypeError):
            stop["order"] = i + 1

        _check_type(stop["name"], str, f"{prefix}.name", raw)
        _check_type(stop["description"], str, f"{prefix}.description", raw)

        # tip — optional string
        val = stop.get("tip")
        if val is not None and not isinstance(val, str):
            stop["tip"] = str(val)
        stop.setdefault("tip", None)

        # coordinates — optional {lat, lng} object
        stop["coordinates"] = _normalize_coordinates(stop.get("coordinates"))

    # Tagline — optional, keep if present
    if "tagline" in data and not isinstance(data["tagline"], str):
        data["tagline"] = str(data["tagline"]) if data["tagline"] else None

    return data


# ---------------------------------------------------------------------------
# Plans validation
# ---------------------------------------------------------------------------

def validate_plans(data: dict, raw_response: str = "") -> dict:
    """Validate and normalize the plans JSON from the model.

    Required structure:
        {
            "plans": [
                {
                    "situation": str,
                    "slug": str,  (will be sanitized)
                    "recommendations": [
                        {"name": str, "description": str,
                         "what_to_order": str|None, "what_to_avoid": str|None,
                         "vibe": str|None, "price_range": str|None,
                         "coordinates": {"lat": float, "lng": float}|None}, ...
                    ]
                }, ...
            ],
            "warnings": [str, ...]
        }

    Returns the validated (and normalized) dict.
    """
    raw = raw_response
    _check_type(data, dict, "plans (root)", raw)

    # Plans list
    if "plans" not in data:
        raise SchemaError("Plans output has no 'plans' field.", raw)
    _check_type(data["plans"], list, "plans.plans", raw)

    for i, plan in enumerate(data["plans"]):
        prefix = f"plans[{i}]"
        _check_type(plan, dict, prefix, raw)
        _check_required(plan, ["situation"], prefix, raw)
        _check_type(plan["situation"], str, f"{prefix}.situation", raw)

        # Recommendations — default to empty list
        plan.setdefault("recommendations", [])
        _check_type(plan["recommendations"], list, f"{prefix}.recommendations", raw)

        for j, rec in enumerate(plan["recommendations"]):
            rprefix = f"{prefix}.recommendations[{j}]"
            _check_type(rec, dict, rprefix, raw)
            _check_required(rec, ["name", "description"], rprefix, raw)
            _check_type(rec["name"], str, f"{rprefix}.name", raw)
            _check_type(rec["description"], str, f"{rprefix}.description", raw)

            # Optional string fields — normalize
            for opt_field in ("what_to_order", "what_to_avoid", "vibe", "price_range"):
                val = rec.get(opt_field)
                if val is not None and not isinstance(val, str):
                    rec[opt_field] = str(val)
                rec.setdefault(opt_field, None)

            # coordinates — optional {lat, lng} object
            rec["coordinates"] = _normalize_coordinates(rec.get("coordinates"))

    # Sanitize slugs (generates safe ones, ensures uniqueness)
    ensure_unique_slugs(data["plans"])

    # Warnings — default to empty list, ensure all are strings
    data.setdefault("warnings", [])
    _check_type(data["warnings"], list, "plans.warnings", raw)
    data["warnings"] = [str(w) for w in data["warnings"]]

    return data
