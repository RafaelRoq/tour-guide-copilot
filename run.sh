#!/usr/bin/env bash
# run.sh — Run Tour Guide Copilot with prerequisite checks.
# Usage: ./run.sh <path-to-guide-document> [--output ./output] [--format html]

set -euo pipefail

# ── 1. Check for .env ────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "❌  Missing .env file."
    echo ""
    echo "    Copy the example and configure it:"
    echo "      cp .env.example .env"
    echo ""
    echo "    Then set either:"
    echo "      OPENAI_API_KEY=sk-...          (OpenAI)"
    echo "      OPENAI_BASE_URL=http://localhost:11434/v1  (Ollama)"
    echo ""
    exit 1
fi

# ── 2. Check Python ───────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo ""
    echo "❌  Python not found."
    echo ""
    echo "    Install Python 3.10+ from https://python.org"
    echo ""
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)

# ── 3. Check dependencies ─────────────────────────────────────────────────────
if ! "$PYTHON" -c "import openai, dotenv, jinja2, pypdf" &>/dev/null; then
    echo ""
    echo "❌  Missing Python dependencies."
    echo ""
    echo "    Install them with:"
    echo "      pip install -r requirements.txt"
    echo ""
    exit 1
fi

# ── 4. Run ────────────────────────────────────────────────────────────────────
if [ $# -eq 0 ]; then
    echo ""
    echo "Usage: ./run.sh <path-to-guide-document> [options]"
    echo ""
    echo "Examples:"
    echo "  ./run.sh examples/input/madrid_manolo.md"
    echo "  ./run.sh my_guide.pdf --output ./output --format html"
    echo ""
    echo "Options:"
    echo "  --output, -o   Output directory (default: ./output)"
    echo "  --format, -f   Output format: html | markdown | json | all (default: html)"
    echo ""
    exit 1
fi

"$PYTHON" -m copilot generate --input "$@"
