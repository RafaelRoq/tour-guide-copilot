# 🧭 Tour Guide Copilot

**[→ Live demo](https://rafaelroq.github.io/tour-guide-copilot/)** · Open it on your phone.

**Every AI app wants to replace the tour guide. This one works for them.**

An open source tool that turns a tour guide's knowledge into a mobile-first
page with the tour itinerary, post-tour plans, and a way for tourists to
say thanks — powered by AI, controlled by the guide.

---

## The problem

The tour ends. The group disperses. And the guide's knowledge — every
hidden bar, every local dish, every "skip this, go here instead" —
disappears with them.

An hour later, a tourist from the group is hungry. They open a map app
and end up at a tourist trap three blocks from the place the guide would
have recommended. The guide would know exactly where to send them, but
they're already leading their next tour.

**The guide's knowledge dies the moment the tour ends.** The tourist loses
access to the one person who actually knows the city. The guide loses
the chance to keep helping — and to be recognized for it.

This happens thousands of times a day, in every city with walking tours.

## The landscape

The tools in this space fall into a few categories, and none of them
solve this problem.

- **Booking marketplaces** connect tourists with tours, but the
  relationship ends at the reservation. The guide's knowledge isn't
  part of the product.
- **Self-guided tour apps** use AI or prewritten scripts to replace
  the human guide entirely.
- **General-purpose AI** can suggest restaurants in any city, but the
  recommendations are generic — based on ratings, not on years of
  walking those streets.
- **Digital tip jars** solve the cashless problem, but only the payment
  part. The knowledge still disappears when the tour ends.
- **DIY solutions** (link aggregators, personal QR codes) exist, but
  they're unstructured and require the guide to do all the organizing.

**The gap**: no tool takes what the guide actually knows and turns it
into something the tourist can use after the tour is over — while giving
the guide credit for it.

## What this project does

Tour Guide Copilot takes a document where a guide has written down their
knowledge and uses AI to generate a complete, shareable page with three
components:

1. **A tour itinerary** — stops in order, with brief context the tourist
   can follow along during the walk.
2. **Post-tour plans by situation** — "Where do I eat?", "What do I do
   with 2 free hours?", "A good bar tonight?", "Where should I go
   tomorrow morning?" Each plan contains the guide's specific, opinionated
   recommendations.
3. **A thank-you link** — a simple, non-intrusive way for the tourist to
   recognize the guide after the plans have been useful. The guide
   configures their own link (PayPal, Bizum, or any URL); the project
   just displays it. In this version the button is an external link — no
   payment processing happens inside the tool. A native tip or review
   mechanism is the natural next step for this feature.

The output is a static, mobile-first webpage that the guide shares via
QR code or link. No app, no login, no backend.

```
Guide's              AI structures         Static page:
knowledge doc    →   itinerary, plans,  →  itinerary + plans
(.md / .txt)         guide profile         + thank-you link
```

### The full cycle

This is the cycle that makes the copilot useful — not just for the
tourist, but for the guide:

```
Guide writes knowledge → AI structures it → Tourist scans QR during tour
    ↑                                              ↓
    ↑                                     Tourist returns later,
    ↑                                     uses plans (dinner, bar, ...)
    ↑                                              ↓
    └──── Guide gets recognition ←──── Plans were helpful, tourist
           (thank-you link)              says thanks
```

Without the thank-you step, the guide puts in the work and gets nothing
back. Without the plans, the thank-you button has no context — it's just
another tip jar. The three pieces work together.

### What makes this different from general-purpose AI

Any chatbot can recommend restaurants in a city. But it doesn't know that
at a certain *taberna* off the main street you should order the *arroz a
banda*, not the paella — because that's what locals order and it costs
half the price. It doesn't know which bars don't accept cards or photos,
or that the *bravas* around the corner are only worth it before 2 PM.

**A guide does.** This tool captures that specificity — the opinions, the
insider criteria, the "order this, skip that, sit here" — and makes it
available to the tourist long after the tour is over.

### Guarding against fabrication

The prompts explicitly instruct the model to only use information present
in the guide's document. If the guide hasn't mentioned breakfast spots,
the output should say so rather than invent recommendations.

That said, this is a behavioural constraint on the model — not something
the code can verify. A model can still hallucinate content that passes
schema validation. Two layers reduce the risk:

- **Prompts**: the model is told to omit rather than invent. The raw
  responses are always saved to `.raw_itinerary.json` and `.raw_plans.json`
  so you can inspect what the model actually produced.
- **Schema validation**: all model output is validated against a strict
  structure. If the JSON is malformed or missing required fields, the
  pipeline fails with a clear error instead of silently producing garbage.
  This catches structural problems — not semantic ones.

> **Note**: The example guides (Manolo in Madrid, Lucía in Barcelona)
> are fictional. All place names and recommendations in the examples
> are illustrative.

## Quickstart

```bash
git clone https://github.com/RafaelRoq/tour-guide-copilot.git
cd tour-guide-copilot
cp .env.example .env
# Add your OPENAI_API_KEY to .env (or configure Ollama — see Configuration below)
pip install -r requirements.txt
./run.sh examples/input/madrid_manolo.md
```

`run.sh` checks that `.env` exists and dependencies are installed before
running. If anything is missing it prints a clear message explaining what
to do next.

Output goes to `./output/` by default. You'll find `index.html` there —
open it in any browser. You can pass any CLI option after the input file:

```bash
./run.sh examples/input/madrid_manolo.md --format all
# Creates: output/index.html, output/guide.json, output/guide.md
```

**Alternative (works on Windows without Git Bash):**

```bash
python -m copilot generate --input examples/input/madrid_manolo.md
python -m copilot preview --input examples/input/madrid_manolo.md  # opens in browser
```

### Configuration

Copy `.env.example` and set your values:

```env
# Required
OPENAI_API_KEY=sk-...

# Model (optional — sensible defaults)
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.3

# Guide info
GUIDE_LANGUAGE=en              # Output language (en, es, fr, de, it, pt)
GUIDE_NAME=Manolo
GUIDE_CITY=Madrid
GUIDE_YEARS=12 years as a guide   # Optional — shown in the page header
GUIDE_TIP_URL=https://paypal.me/example  # Optional — enables the thank-you button

# Output
OUTPUT_FORMAT=html             # html, markdown, json, all

# Limits
# MAX_DOCUMENT_CHARS=400000   # ~100k tokens; raise for very long documents
```

`GUIDE_YEARS` and `GUIDE_TIP_URL` are optional. If omitted, the page
still works — it just won't show those elements.

### Using Ollama instead of OpenAI

To run the pipeline with a local model (no API key, no cost):

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3.1:8b
   ```
2. In your `.env`, replace the OpenAI settings with:
   ```env
   OPENAI_BASE_URL=http://localhost:11434/v1
   OPENAI_MODEL=llama3.1:8b
   # OPENAI_API_KEY is not needed
   ```
3. Run as usual:
   ```bash
   python -m copilot generate --input examples/input/madrid_manolo.md
   ```

**Model requirements**: the model must support JSON mode
(`response_format: json_object`). `llama3.1:8b` and `qwen2.5:7b` work
reliably. Smaller models (3B and below) may produce schema errors on
complex guide documents.

This mode is recommended for contributors iterating on prompts. For
production use, GPT-4o produces noticeably better results.

### Writing a guide document

The input is a plain text or markdown file where the guide writes what
they know. No special format required — just write naturally, as if
telling a friend who's visiting the city for the first time.

Here's a suggested structure (not mandatory, but helps the AI produce
better results):

```markdown
# [Your name] — [City]

## My tour

[Describe the route: where you start, what stops you make, what you
tell tourists at each stop, in what order. Include any stories or
context that makes each stop interesting.]

## Where to eat

[Specific places. For each: name, what to order, what to avoid, price
range, any tips like "go before 2 PM" or "cash only".]

## Where to drink

[Bars for different vibes: casual, fancy, local, late night. Same
level of detail as food.]

## What to do with free time

[Ideas for 1-2 hours, half a day, a rainy afternoon. Be specific
about what's worth it and what's overrated.]

## Watch out for

[Tourist traps, overpriced spots, common scams, streets to avoid at
certain hours. Practical stuff: tipping norms, metro tips, opening
hours to be aware of.]
```

**About PDFs**: the tool accepts `.pdf` files, but text extraction from
PDFs is best-effort. Scanned documents without OCR will produce poor
results. For best quality, use `.md` or `.txt`.

See `examples/input/madrid_manolo.md` for a complete example.

## How it works

```
┌──────────────────┐
│  Guide's          │
│  document         │
│  (.md / .txt)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   parser.py       │   Reads and cleans the document
└────────┬─────────┘
         │
         ├──────────────────────────────┐
         ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│  itinerary.py     │        │  plans.py         │
│                   │        │                   │
│  Extracts stops,  │        │  Generates plans  │
│  order, context   │        │  by situation     │
└────────┬─────────┘        └────────┬─────────┘
         │                            │
         ▼                            ▼
┌──────────────────────────────────────────────┐
│  renderer.py                                  │
│                                               │
│  Combines into a static page:                │
│  · Guide profile (name, years, tagline)      │
│  · Tour itinerary (tab 1)                    │
│  · Post-tour plans as accordion (tab 2)      │
│  · Thank-you link                            │
└──────────────────────────────────────────────┘
```

No RAG, no vector database, no embeddings. A guide's document fits in
GPT-4o's context window. The prompts do the heavy lifting.

**Why no RAG?** A typical guide document is a few thousand words — well
within the model's context limit. RAG adds complexity (embeddings,
vector store, chunking) with no benefit for this use case. If a future
contributor needs RAG for guides with very large corpora, it can be
built as an optional extension in `extensions/` without touching the core.

### Repository structure

```
tour-guide-copilot/
├── copilot/                   # Source code (Python package)
│   ├── cli.py                 #   Command-line interface
│   ├── config.py              #   Loads .env, validates settings
│   ├── exceptions.py          #   Custom error types
│   ├── generator.py           #   Orchestrates the full pipeline
│   ├── itinerary.py           #   Itinerary generation (calls LLM)
│   ├── llm.py                 #   Unified LLM helper (shared by itinerary + plans)
│   ├── parser.py              #   Reads guide documents (.md, .txt, .pdf)
│   ├── plans.py               #   Post-tour plans generation (calls LLM)
│   ├── renderer.py            #   Outputs HTML / markdown / JSON
│   └── schemas.py             #   JSON validation + slug generation
│
├── prompts/                   # Prompt templates (the soul of the project)
│   ├── 00_system.md           #   Base system prompt (personality, rules)
│   ├── 01_extract_itinerary.md#   Knowledge → structured itinerary
│   └── 02_generate_plans.md   #   Knowledge → post-tour plans
│
├── templates/site/            # HTML template (Jinja2, mobile-first)
│   └── index.html
│
├── examples/                  # Ready-to-run examples
│   ├── input/                 #   Guide documents (fictional)
│   └── output/                #   Pre-generated outputs
│
├── tests/                     # Test suite
├── docs/                      # Extended documentation
│   ├── PHILOSOPHY.md          #   The thesis: why augment, not replace
│   ├── ARCHITECTURE.md        #   Technical decisions and data flow
│   └── PROMPTS.md             #   Detailed prompt documentation
│
├── run.sh                     # Run the pipeline with prerequisite checks
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT (code)
└── LICENSE-CONTENT            # CC BY-SA 4.0 (prompts, docs, examples)
```

**Where to touch what:**

- **Prompts** → `prompts/*.md` — this is where the real intelligence lives.
  Changing a prompt changes the output quality.
- **HTML/CSS** → `templates/site/index.html` — the tourist-facing page.
- **New output formats** → `copilot/renderer.py` — add a new renderer
  function alongside the existing HTML/markdown/JSON ones.
- **New guide examples** → `examples/input/` — add a `.md` file and
  optionally pre-generate the output.
- **Schema changes** → `copilot/schemas.py` — if the model output
  structure changes, update validation here.

### Modules

| Module | Responsibility |
|--------|---------------|
| `config.py` | Loads `.env`, validates settings, sensible defaults |
| `exceptions.py` | `ConfigError`, `PromptError`, `SchemaError`, `DocumentTooLargeError` |
| `parser.py` | Reads `.md`, `.txt`, `.pdf` → clean text (warns on poor PDF quality) |
| `llm.py` | Loads prompts, replaces variables, calls API, parses JSON, handles errors |
| `itinerary.py` | Guide's text → structured itinerary (temperature 0.0 for faithful extraction) |
| `plans.py` | Guide's text → plans by situation (temperature 0.2 for flexible reorganization) |
| `schemas.py` | Validates JSON structure, generates safe HTML slugs, ensures uniqueness |
| `generator.py` | Orchestrates pipeline, checks document size, saves debug files |
| `renderer.py` | JSON → static HTML (Jinja2 with autoescape), markdown, or JSON |
| `cli.py` | Catches all `CopilotError` subtypes and prints clean messages |

### Design decisions

| Decision | Chosen | Why |
|----------|--------|-----|
| No RAG | Full context window | Document fits; RAG adds complexity with no benefit |
| OpenAI directly | `openai` package | No orchestration framework — fewer deps, less abstraction |
| Static HTML | Jinja2 templates | Zero infra, works offline, ultralight |
| CLI first | argparse | Easiest to test, contribute, and automate |
| Prompts as files | Separate `.md` files | Versionable, editable by non-coders, easy to contribute |
| JSON intermediate | Typed structure | Generate once, render to many formats |
| Schema validation | Custom validators | Catches malformed output before it reaches the renderer |
| External thank-you link | Simple `<a>` to guide's URL | No payment processing, no accounts — guide owns the link |
| HTML escaping | `html.escape` + Jinja2 autoescape | Prevents XSS from model-generated content |

## The philosophy

Many AI tools in tourism follow a similar logic: feed the model enough
data and it can replace the human guide.

This project goes the opposite way.

**A guide's value isn't information — it's curation.** It's knowing that
this bar is better than that one, not because of its rating, but because
they've been going there for years. It's the story about the building on
the corner that isn't on Wikipedia. It's the opinion — "skip this, go
here instead" — that only comes from experience.

AI is good at structuring knowledge. It's not good at generating the
kind of specific, opinionated, local knowledge that makes a guide worth
following. So instead of replacing that knowledge, we structure it and
make it accessible.

The copilot's job is to make the guide's expertise available beyond the
tour — and to make sure the guide gets something back when it helps.

**Copilot, not replacement.**

For the full thesis, see [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md).

## Scope

The copilot covers the complete cycle from knowledge to recognition:

- ✅ Extracting a structured itinerary from the guide's document
- ✅ Generating post-tour plans organized by situation
- ✅ Building a mobile-first static page with guide profile and tagline
- ✅ Displaying a thank-you link so tourists can recognize the guide
- ✅ Practical warnings and tips extracted from the guide's knowledge
- ✅ Schema validation of all model output (no silent failures)
- ✅ Raw response logging for debugging

What's deliberately outside the scope of this project:

- ❌ No backend, authentication, or database
- ❌ No marketplace or guide discovery
- ❌ No payment processing (the thank-you link points to the guide's own
  URL — PayPal, Bizum, or whatever they choose)
- ❌ No chatbot or real-time interaction with tourists
- ❌ No scraping or third-party data
- ❌ No RAG in the core (available as a future extension for very large
  guide corpora)

Everything outside the scope can be built as an extension in the
`extensions/` folder. The core stays minimal: **document in → AI →
itinerary + plans + thank-you → static page.**

## Contributing

Contributions are welcome — especially these:

- **New guide examples** in different cities and languages. This is the
  single most useful contribution. Add a `.md` file to `examples/input/`
  and optionally include the generated output.
- **Prompt improvements** with before/after examples showing the change.
  Every prompt PR must include a sample input and the resulting output.
- **Translations** of the output templates and UI strings.
- **Optional extensions** (RAG, chat, TTS, i18n) in the `extensions/`
  folder — never in the core.

### Before opening a PR

1. Make sure the schema isn't broken: run the existing examples and verify
   the output is valid JSON that passes `schemas.validate_itinerary` and
   `schemas.validate_plans`.
2. Don't add content the guide didn't write. The "no fabrication" rule
   applies to examples too — if a recommendation isn't in the input
   document, it shouldn't appear in the output.
3. Keep dependencies minimal. If you need a new package, justify it.
4. Run `python -m py_compile copilot/*.py` to check for syntax errors.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the full guidelines.

## FAQ

**Does it need internet?**
To *generate* the page, yes — it calls the OpenAI API. Once generated,
the HTML page is fully static and works offline. No requests are made
when the tourist opens it.

**What data is sent to the model?**
The full text of the guide's document, plus the prompt templates. No
personal data from tourists is ever sent. The guide controls what goes
into the document.

**How do I change the language of the output?**
Set `GUIDE_LANGUAGE` in `.env` (e.g. `es`, `fr`, `de`). The model will
generate itinerary and plan content in that language. Note: UI strings
in the HTML template ("Your tour", "What do you need?") are currently
in English. Internationalization of UI strings is planned as an extension.

**What if the model hallucinates recommendations?**
The prompts explicitly instruct the model to only use information from
the guide's document. The schema validates the output structure. If
something looks wrong, check the raw response files in the output
directory (`.raw_itinerary.json`, `.raw_plans.json`) for debugging.

**Can I use a different model?**
Set `OPENAI_MODEL` in `.env` to any model that supports
`response_format: json_object`. The tool has been tested with `gpt-4o`.

## What's next

Directions being considered for future versions — contributions welcome:

- **Voice onboarding**: guides already explain their tours out loud — that's
  their natural format. A voice-first interface (speech-to-text → existing
  pipeline) would let a guide record themselves talking about their tour and
  produce the same output without writing a single word. The pipeline doesn't
  change; only the input format does.
- **Conversational onboarding**: an alternative to voice — the guide answers
  structured questions in a chat interface. The AI conducts the interview and
  produces the same structured output the pipeline already knows how to render.
  Useful for guides who prefer to respond to prompts rather than speak freely.
- **Managed hosting + QR code**: currently the pipeline outputs a local HTML
  file that the guide must host somewhere. The missing step is publishing the
  page automatically to a public URL and handing the guide a ready-to-print QR
  code — the piece that closes the loop between generation and the tourist
  scanning it during the tour.
- **Async tours**: the guide's captured knowledge powers a self-guided tour
  experience — tourists follow the itinerary and query the guide's AI without
  the guide being present. Requires RAG over the guide's corpus and builds
  directly on the knowledge base created during onboarding.
- **UI string translations**: the HTML template has hardcoded English labels
  ("Your tour", "What do you need?"). Making these translatable would make
  the tourist-facing page fully multilingual end to end.

A live demo is available at
[rafaelroq.github.io/tour-guide-copilot](https://rafaelroq.github.io/tour-guide-copilot/)
— a pre-generated example (fictional guide Manolo, Madrid) so you can see
the output without running the tool.

If you're working on one of the above directions, open an issue first to
coordinate.

## License

- **Code** (`copilot/`, `templates/`, `tests/`): [MIT](LICENSE)
- **Content** (`prompts/`, `docs/`, `examples/`):
  [CC BY-SA 4.0](LICENSE-CONTENT)

You can use the code in a commercial product. If you use the prompts or
the "plans by situation" framework, you must give attribution and share
your changes to the content under the same license.

---

*Built by a Senior Data Scientist who believes AI should make experts
more powerful, not more replaceable.*
