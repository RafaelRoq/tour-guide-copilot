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

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "sk-...":
        raise ConfigError(
            "OPENAI_API_KEY is not set.\n"
            "Copy .env.example to .env and add your API key."
        )

    return Config(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
        guide_language=os.getenv("GUIDE_LANGUAGE", "en"),
        guide_name=os.getenv("GUIDE_NAME", "Guide"),
        guide_city=os.getenv("GUIDE_CITY", ""),
        guide_years=os.getenv("GUIDE_YEARS", ""),
        guide_tip_url=os.getenv("GUIDE_TIP_URL", ""),
        output_format=os.getenv("OUTPUT_FORMAT", "html"),
        max_document_chars=int(os.getenv("MAX_DOCUMENT_CHARS", str(DEFAULT_MAX_DOCUMENT_CHARS))),
    )
