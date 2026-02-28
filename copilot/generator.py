"""Generator. Orchestrates the full pipeline: parse → generate → render."""

import json
import logging
from pathlib import Path

from .config import Config
from .exceptions import DocumentTooLargeError
from .parser import parse_document
from .itinerary import generate_itinerary
from .plans import generate_plans
from .renderer import render

logger = logging.getLogger(__name__)


def generate(input_path: str, output_dir: str, config: Config) -> list[str]:
    """Run the full generation pipeline.

    1. Parse the guide's document.
    2. Check document size against configured limit.
    3. Generate itinerary via AI.
    4. Generate post-tour plans via AI.
    5. Save raw model responses for debugging.
    6. Render outputs to the specified format(s).

    Args:
        input_path: Path to the guide's document.
        output_dir: Directory to write output files to.
        config: Application configuration.

    Returns:
        List of paths to created files.

    Raises:
        DocumentTooLargeError: If the document exceeds the configured limit.
        PromptError: If prompt files are missing.
        SchemaError: If the model output doesn't match the expected structure.
    """
    print(f"📄 Reading {input_path}...")
    document = parse_document(input_path)
    print(f"   {len(document):,} characters loaded.")

    # P0: Guard against documents that would exceed the model's context window
    if len(document) > config.max_document_chars:
        raise DocumentTooLargeError(len(document), config.max_document_chars)

    print(f"🗺️  Generating itinerary with {config.model}...")
    itinerary, raw_itinerary = generate_itinerary(document, config)
    stops_count = len(itinerary.get("stops", []))
    print(f"   {stops_count} stops extracted.")

    print(f"📋 Generating post-tour plans with {config.model}...")
    plans, raw_plans = generate_plans(document, config)
    plans_count = len(plans.get("plans", []))
    print(f"   {plans_count} situations covered.")

    # Save raw model responses for debugging (always, regardless of output format)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _save_debug(out / ".raw_itinerary.json", raw_itinerary)
    _save_debug(out / ".raw_plans.json", raw_plans)

    print(f"🎨 Rendering to {config.output_format}...")
    created = render(itinerary, plans, config, output_dir)
    for path in created:
        print(f"   ✅ {path}")

    return created


def _save_debug(path: Path, raw_response: str) -> None:
    """Save a raw model response to a dotfile for debugging."""
    try:
        path.write_text(raw_response, encoding="utf-8")
        logger.debug("Raw response saved to %s", path)
    except OSError as exc:
        logger.warning("Could not save debug file %s: %s", path, exc)
