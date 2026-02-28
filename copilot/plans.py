"""Plans generator. Turns guide knowledge into post-tour plans by situation."""

from .config import Config
from .llm import load_prompt, call_llm, prepare_prompt
from .schemas import validate_plans


def generate_plans(document: str, config: Config) -> tuple[dict, str]:
    """Generate post-tour plans from the guide's document.

    Args:
        document: The guide's knowledge as plain text.
        config: Application configuration.

    Returns:
        A tuple of (validated_plans_dict, raw_response).
        The raw response is returned for debugging/logging.

    Raises:
        PromptError: If prompt files are missing.
        SchemaError: If the model output doesn't match the expected structure.
    """
    system_prompt = load_prompt(config.prompts_dir / "00_system.md")
    user_template = load_prompt(config.prompts_dir / "02_generate_plans.md")
    user_prompt = prepare_prompt(user_template, guide_document=document, config=config)

    # Use temperature 0.2 for plans — slightly higher than itinerary
    # because the model needs to reorganize unstructured recommendations
    # into situation categories, which benefits from some flexibility.
    parsed, raw = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        config=config,
        temperature=0.2,
        label="plans",
    )

    validated = validate_plans(parsed, raw_response=raw)
    return validated, raw
