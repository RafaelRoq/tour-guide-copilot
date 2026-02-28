"""Itinerary generator. Turns guide knowledge into a structured tour itinerary."""

from .config import Config
from .llm import load_prompt, call_llm, prepare_prompt
from .schemas import validate_itinerary


def generate_itinerary(document: str, config: Config) -> tuple[dict, str]:
    """Generate a structured itinerary from the guide's document.

    Args:
        document: The guide's knowledge as plain text.
        config: Application configuration.

    Returns:
        A tuple of (validated_itinerary_dict, raw_response).
        The raw response is returned for debugging/logging.

    Raises:
        PromptError: If prompt files are missing.
        SchemaError: If the model output doesn't match the expected structure.
    """
    system_prompt = load_prompt(config.prompts_dir / "00_system.md")
    user_template = load_prompt(config.prompts_dir / "01_extract_itinerary.md")
    user_prompt = prepare_prompt(user_template, guide_document=document, config=config)

    # Use temperature 0.0 for itinerary extraction — we want faithful
    # extraction of the guide's stops, not creative interpretation.
    parsed, raw = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        config=config,
        temperature=0.0,
        label="itinerary",
    )

    validated = validate_itinerary(parsed, raw_response=raw)
    return validated, raw
