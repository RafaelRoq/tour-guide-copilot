"""Tests for the config module."""

import pytest

from copilot.config import Config, load_config
from copilot.exceptions import ConfigError


def test_config_defaults():
    """Config has sensible defaults."""
    config = Config(api_key="test-key")
    assert config.model == "gpt-4o"
    assert config.temperature == 0.3
    assert config.guide_language == "en"
    assert config.output_format == "html"
    assert config.max_document_chars == 400_000


def test_config_prompts_dir_exists():
    """Config resolves prompts directory correctly."""
    config = Config(api_key="test-key")
    assert config.prompts_dir.name == "prompts"
    assert config.prompts_dir.exists()


def test_missing_api_key_raises_config_error():
    """load_config raises ConfigError (not sys.exit) when key is missing."""
    with pytest.raises(ConfigError, match="API_KEY"):
        load_config("/nonexistent/.env")


def test_placeholder_api_key_raises_config_error(tmp_path):
    """load_config rejects the placeholder sk-... value."""
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=sk-...\n")
    with pytest.raises(ConfigError, match="API_KEY"):
        load_config(str(env))
