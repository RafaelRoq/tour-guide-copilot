"""Unified LLM helper. Single place for prompt loading, variable replacement,
API calls, JSON parsing, and error handling.

Both itinerary.py and plans.py delegate to this module instead of
duplicating the same logic.
"""

import json
import logging
from pathlib import Path

from openai import OpenAI

from .config import Config
from .exceptions import PromptError, SchemaError

logger = logging.getLogger(__name__)


def load_prompt(path: Path) -> str:
    """Load a prompt file as text.

    Raises:
        PromptError: If the file is missing or unreadable, with a clear message.
    """
    if not path.exists():
        raise PromptError(
            f"Prompt file not found: {path}\n"
            f"Make sure the prompts/ directory exists and contains {path.name}."
        )
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PromptError(f"Cannot read prompt file {path}: {exc}") from exc


def call_llm(
    *,
    system_prompt: str,
    user_prompt: str,
    config: Config,
    temperature: float | None = None,
    label: str = "LLM call",
) -> tuple[dict, str]:
    """Call the OpenAI API with JSON mode and return parsed output + raw response.

    Args:
        system_prompt: The system message.
        user_prompt: The user message (with variables already replaced).
        config: Application configuration (api_key, model).
        temperature: Override for this specific call. If None, uses config.temperature.
        label: Human-readable label for log messages (e.g. "itinerary", "plans").

    Returns:
        A tuple of (parsed_dict, raw_response_string).
        The raw response is always returned so callers can save it for debugging.

    Raises:
        SchemaError: If the response is not valid JSON.
    """
    temp = temperature if temperature is not None else config.temperature

    logger.debug("Calling %s (model=%s, temperature=%.1f)", label, config.model, temp)

    client = OpenAI(api_key=config.api_key)

    response = client.chat.completions.create(
        model=config.model,
        temperature=temp,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or ""

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SchemaError(
            f"{label}: model returned invalid JSON — {exc}",
            raw_response=raw,
        ) from exc

    return parsed, raw


def prepare_prompt(
    template: str,
    *,
    guide_document: str,
    config: Config,
) -> str:
    """Replace standard variables in a prompt template.

    Variables: {guide_document}, {guide_name}, {guide_city}, {language}.
    """
    return (
        template
        .replace("{guide_document}", guide_document)
        .replace("{guide_name}", config.guide_name)
        .replace("{guide_city}", config.guide_city)
        .replace("{language}", config.guide_language)
    )
