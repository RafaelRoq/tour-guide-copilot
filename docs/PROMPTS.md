# Prompts documentation

This document explains the design and purpose of each prompt in the
`prompts/` directory.

## Overview

There are three prompt files:

| File | Purpose |
|------|---------|
| `00_system.md` | Base system prompt — personality and rules |
| `01_extract_itinerary.md` | Extracts a structured tour itinerary |
| `02_generate_plans.md` | Generates post-tour plans by situation |

## How prompts are used

1. `00_system.md` is sent as the **system message** in every API call.
   It defines the AI's behavior: never invent, preserve the guide's
   voice, output valid JSON.

2. `01_extract_itinerary.md` and `02_generate_plans.md` are sent as
   the **user message**, with three placeholders replaced at runtime:
   - `{guide_document}` → the full text from the guide's file
   - `{guide_name}` → from config
   - `{guide_city}` → from config
   - `{language}` → from config

## Design principles

### Explicit JSON structure in the prompt

Each prompt includes the exact JSON structure expected in the response.
This is more reliable than asking for "structured output" in the
abstract. The model follows a concrete example better than a verbal
description.

### Rules as a numbered list

Each prompt has a "Rules" section with specific constraints. These are
ordered from most important to least. The first rule is always
**"Never invent"** because fabricated content is the worst failure mode.

### Guide info at the end

The guide's document and metadata go at the bottom of the prompt, after
the instructions. This ensures the model reads the rules before
processing the content.

## Contributing to prompts

If you want to improve a prompt:

1. Test your change against at least one example document.
2. Include before/after output in your PR.
3. Explain what improved and why.
4. Don't change the JSON structure without also updating
   `docs/SCHEMA.md` and the renderer.
