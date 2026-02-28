# Changelog

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
