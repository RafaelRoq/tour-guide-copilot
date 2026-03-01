# Contributing to Tour Guide Copilot

Thanks for your interest in contributing. This document explains how
to make useful contributions while keeping the project simple.

## What's most valuable

In order of impact:

1. **New guide examples.** Write a guide document for your city in
   `examples/input/`. This is the single most useful contribution —
   it tests the prompts in new contexts and makes the project more
   useful to more people.

2. **Prompt improvements.** If you find a way to make the prompts
   produce better output, open a PR with a before/after comparison
   showing the change.

3. **Bug fixes and quality improvements.** Cleaner code, better error
   messages, edge case handling.

4. **Translations.** Verify that the prompts produce good output in
   a new language and add examples.

## Guidelines

### Keep it simple

This project is deliberately minimal. Before adding a dependency or
a feature, ask: does the core pipeline (document → AI → output) need
this to work? If not, it belongs in `extensions/`, not in `copilot/`.

### No orchestration frameworks

We use the OpenAI API directly. Please don't introduce orchestration
frameworks. The goal is that anyone can read the code and understand
it in 10 minutes.

### Prompts are files

Prompts live in `prompts/` as markdown files. They should never be
hardcoded in Python. This makes them easy to read, version, and
improve independently of the code.

### Extensions

Optional features like RAG, conversational chat, TTS, or payment
integration go in an `extensions/` directory with their own README.
They should never modify or depend on changes to the core modules.

## Local setup

```bash
git clone https://github.com/RafaelRoq/tour-guide-copilot.git
cd tour-guide-copilot
pip install -r requirements.txt
cp .env.example .env
```

You can run the pipeline with **OpenAI** (set `OPENAI_API_KEY` in `.env`)
or with a **local model via Ollama** (no API key needed — useful for
iterating on prompts without cost):

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.1:8b
# In .env: set OPENAI_BASE_URL=http://localhost:11434/v1 and OPENAI_MODEL=llama3.1:8b
```

Run the tests:

```bash
python -m pytest tests/ -v
```

## How to submit

1. Fork the repo.
2. Create a branch with a descriptive name.
3. Make your changes.
4. If you changed prompts, include sample input and output.
5. Open a PR with a clear description of what and why.

## License

By contributing, you agree that:

- **Code contributions** (in `copilot/`, `templates/`, `tests/`) are
  licensed under MIT.
- **Content contributions** (in `prompts/`, `docs/`, `examples/`)
  are licensed under CC BY-SA 4.0.
