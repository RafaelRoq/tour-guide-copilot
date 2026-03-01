# Changelog

## 0.3.0 — Ollama support, CI, and quality improvements

### Added
- Ollama support via `OPENAI_BASE_URL`: run the pipeline locally with
  no API key required. Tested with `llama3.1:8b`. Configured as Option B
  in `.env.example`.
- CI: GitHub Actions workflow runs the full test suite on push and PR
  to main (`pytest`, Python 3.12).
- Live demo page via GitHub Pages (`docs/index.html` — Manolo/Madrid
  example).

### Changed
- README: reframed "no fabrication guarantee" as "guarding against
  fabrication" — honest about what schema validation can and cannot catch.
- README: added "What's next" section (conversational onboarding, async
  tours, i18n) and live demo link at the top of the file.
- README: added "Using Ollama" section under Configuration.
- `cli.py`: reconfigure stdout/stderr to UTF-8 at startup — fixes emoji
  crash on Windows with cp1252 default encoding.
- `tests/test_renderer.py`: explicit `encoding="utf-8"` when reading
  generated HTML — fixes test failure on Windows.
- `pyproject.toml`: added `[tool.pytest.ini_options]` with `pythonpath`
  so pytest can import the `copilot` package without installing it.

### Security
- Added `rel="noopener noreferrer"` to all `target="_blank"` links in
  `templates/site/index.html` and `renderer.py` fallback.

## 0.2.0 — Reliability and structure

### Added
- `exceptions.py` — Custom exception hierarchy (`CopilotError`, `ConfigError`,
  `PromptError`, `SchemaError`, `DocumentTooLargeError`)
- `schemas.py` — JSON schema validation for itinerary and plans output,
  safe slug generation (`sanitize_slug`), slug uniqueness enforcement
- `llm.py` — Unified LLM helper (prompt loading, variable replacement,
  API call, JSON parsing, error handling) shared by itinerary and plans
- Document size guard (`MAX_DOCUMENT_CHARS`) — aborts before calling the
  API if the document exceeds the configured limit
- Raw model responses saved to `.raw_itinerary.json` / `.raw_plans.json`
  for debugging
- PDF quality warning when extraction yields very little text
- XSS protection: `html.escape` on all user content in fallback renderer,
  `autoescape=True` in Jinja2 renderer
- Test suite for schemas, config, and renderer XSS

### Changed
- `config.py` — Raises `ConfigError` instead of calling `sys.exit(1)`
- `itinerary.py` — Uses `llm.py` helper, temperature fixed at 0.0 for
  faithful extraction, validates output against schema
- `plans.py` — Uses `llm.py` helper, temperature 0.2 for flexible
  reorganization, validates output against schema
- `generator.py` — Checks document size, saves debug files, propagates
  validated outputs
- `cli.py` — Catches `CopilotError` with clean error messages instead
  of showing raw stack traces
- `renderer.py` — All content escaped in minimal renderer, safe slugs
  for plan `id` attributes

### Removed
- Duplicate prompt-loading and API-calling code from `itinerary.py` and
  `plans.py` (replaced by `llm.py`)

## 0.1.0 — Initial release

- Core pipeline: document → AI → itinerary + plans → output
- Supported input formats: `.md`, `.txt`, `.pdf`
- Supported output formats: HTML, Markdown, JSON
- Three base prompts: system, itinerary extraction, plans generation
- Mobile-first HTML template with two-tab layout
- CLI with `generate` and `preview` commands
- Example guide document: Madrid (Manolo)
- Dual license: MIT (code) + CC BY-SA 4.0 (content)
