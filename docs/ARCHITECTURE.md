# Architecture

## Overview

Tour Guide Copilot is a command-line tool with a simple pipeline:

```
Input document → Parser → AI generation → Renderer → Output files
```

There is no server, no database, no authentication. The tool reads a
file, calls the OpenAI API, and writes output files. That's it.

## Data flow

```
┌──────────────────┐
│  Guide's          │
│  document         │   parser.py reads and cleans the text
│  (.md / .txt)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Clean text      │   Sent to both generation modules
└────────┬─────────┘
         │
         ├──────────────────────────────┐
         ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│  itinerary.py     │        │  plans.py         │
│                   │        │                   │
│  System prompt    │        │  System prompt    │
│  + prompt 01      │        │  + prompt 02      │
│  + document       │        │  + document       │
│       ↓           │        │       ↓           │
│  OpenAI API call  │        │  OpenAI API call  │
│       ↓           │        │       ↓           │
│  Structured JSON  │        │  Structured JSON  │
└────────┬─────────┘        └────────┬─────────┘
         │                            │
         ▼                            ▼
┌──────────────────────────────────────────────┐
│  renderer.py                                  │
│                                               │
│  Combines both JSONs + config into:           │
│  · HTML (mobile-first, with tabs)             │
│  · Markdown (flat document)                   │
│  · JSON (combined structure)                  │
└──────────────────────────────────────────────┘
```

## Key design decisions

### No RAG

A guide's document typically ranges from 1,000 to 10,000 words. This
fits entirely within GPT-4o's context window (~128k tokens). RAG would
add embeddings, a vector store, chunking logic, and retrieval ranking
— all unnecessary for this input size.

If a contributor needs RAG for guides with very large corpora (e.g.,
an entire book), it can be added as an extension.

### No orchestration framework

We call the OpenAI API directly using the `openai` Python package.
Orchestration frameworks add abstraction layers that make the code
harder to read and debug for contributors who aren't familiar with
them. For two API calls, the overhead isn't justified.

### Prompts as files

Prompts are stored as markdown files in `prompts/`. This has three
benefits:

1. **Readable.** Anyone can open the file and understand what the AI
   is being asked to do.
2. **Versionable.** Changes to prompts show up clearly in git diffs.
3. **Contributable.** Someone who doesn't write Python can still
   improve the prompts.

### JSON as intermediate format

The AI generation step produces structured JSON. The rendering step
consumes that JSON. This separation means:

- You can generate once and render to many formats without re-calling
  the API.
- New renderers (PDF, Telegram, email) can be added without touching
  the generation logic.
- The JSON serves as a contract between the two halves of the system.

See `docs/SCHEMA.md` for the full schema specification.

### Static HTML output

The default output is a single HTML file with inline CSS and minimal
JavaScript. No build step, no dependencies, no server needed. The
file works offline and on low-bandwidth connections.

This matters because the end use case is a tourist in a foreign city
with possibly limited data. The output must be ultralight.

## Module responsibilities

| Module | Does | Doesn't |
|--------|------|---------|
| `config.py` | Load .env, validate settings | Make API calls |
| `parser.py` | Read files, clean text | Transform content semantically |
| `itinerary.py` | Call API with prompt 01, return JSON | Render output |
| `plans.py` | Call API with prompt 02, return JSON | Render output |
| `renderer.py` | Convert JSON to HTML/MD/JSON files | Call the API |
| `generator.py` | Orchestrate the full pipeline | Do anything directly |
| `cli.py` | Parse CLI arguments, call generator | Contain business logic |

## Extending the project

Extensions should go in an `extensions/` directory and never modify
core modules. An extension can:

- Add a new renderer (e.g., PDF, Telegram message).
- Add a new input parser (e.g., audio transcription).
- Add RAG for large corpora.
- Add a web interface.

Each extension should have its own README explaining what it does
and how to use it.
