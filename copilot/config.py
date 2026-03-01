"""Configuration loader. Reads .env and validates required settings."""

import os
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv

from .exceptions import ConfigError

# Default limit: ~400k chars ≈ ~100k tokens. GPT-4o supports 128k context,
# but we leave room for prompts and system messages.
DEFAULT_MAX_DOCUMENT_CHARS = 400_000


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    api_key: str = ""
    model: str = "gpt-4o"
    temperature: float = 0.3
    base_url: str = ""
    guide_language: str = "en"
    guide_name: str = "Guide"
    guide_city: str = ""
    guide_years: str = ""
    guide_tip_url: str = ""
    output_format: str = "html"
    max_document_chars: int = DEFAULT_MAX_DOCUMENT_CHARS

    # Internal paths (resolved at load time)
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def prompts_dir(self) -> Path:
        return self.project_root / "prompts"

    @property
    def templates_dir(self) -> Path:
        return self.project_root / "templates" / "site"


def load_config(env_path: str | None = None) -> Config:
    """Load configuration from .env file and environment variables.

    Args:
        env_path: Optional path to .env file. If None, looks in the
                  project root directory.

    Returns:
        A validated Config instance.

    Raises:
        ConfigError: If required configuration (e.g. OPENAI_API_KEY) is missing.
    """
    if env_path:
        load_dotenv(env_path)
    else:
        # Look for .env in the project root
        root = Path(__file__).parent.parent
        load_dotenv(root / ".env")

    base_url = os.getenv("OPENAI_BASE_URL", "")
    api_key = os.getenv("OPENAI_API_KEY", "")

    is_local = bool(base_url) and (
        "localhost" in base_url or "127.0.0.1" in base_url
    )

    if not is_local and (not api_key or api_key == "sk-..."):
        raise ConfigError(
            "OPENAI_API_KEY is not set.\n"
            "Copy .env.example to .env and add your API key.\n"
            "To use a local model via Ollama, set OPENAI_BASE_URL=http://localhost:11434/v1 instead."
        )

    # Warn if both are set — local URL takes precedence
    if is_local and api_key and api_key != "sk-...":
        import warnings
        warnings.warn(
            "Both OPENAI_BASE_URL (local) and OPENAI_API_KEY are set. "
            "Using the local endpoint — OPENAI_API_KEY will be ignored.",
            stacklevel=2,
        )

    # Ollama requires a non-empty api_key value; any string works
    if is_local and not api_key:
        api_key = "ollama"

    return Config(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
        base_url=base_url,
        guide_language=os.getenv("GUIDE_LANGUAGE", "en"),
        guide_name=os.getenv("GUIDE_NAME", "Guide"),
        guide_city=os.getenv("GUIDE_CITY", ""),
        guide_years=os.getenv("GUIDE_YEARS", ""),
        guide_tip_url=os.getenv("GUIDE_TIP_URL", ""),
        output_format=os.getenv("OUTPUT_FORMAT", "html"),
        max_document_chars=int(os.getenv("MAX_DOCUMENT_CHARS", str(DEFAULT_MAX_DOCUMENT_CHARS))),
    )
