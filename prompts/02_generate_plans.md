Generate post-tour plans from the guide's document below. Plans are
organized by **situations** — questions a tourist might ask after the
tour ends.

Return a JSON object with this exact structure. Here is an example
with realistic values — your output should follow this format:

```json
{
  "plans": [
    {
      "situation": "Where do I eat after the tour?",
      "slug": "eat-after-tour",
      "recommendations": [
        {
          "name": "The tapas counter with the blue tiles",
          "description": "I've been eating here for 8 years. The owner still makes everything himself. It's the kind of place where locals argue about football at the bar.",
          "what_to_order": "Croquetas and the house vermouth",
          "what_to_avoid": "The fish on Mondays — they don't get fresh delivery",
          "price_range": "€",
          "vibe": "Standing-room, loud, no-frills",
          "coordinates": { "lat": 40.4172, "lng": -3.7025 }
        }
      ]
    },
    {
      "situation": "A good bar tonight?",
      "slug": "bar-tonight",
      "recommendations": [
        {
          "name": "The sherry bar with sawdust on the floor",
          "description": "Like stepping into 1920s Madrid. Sherry poured from old barrels, no music, no photos allowed. If you only visit one bar, make it this one.",
          "what_to_order": "Fino sherry",
          "what_to_avoid": null,
          "price_range": "€",
          "vibe": "Old-school, atmospheric, cash only",
          "coordinates": null
        }
      ]
    }
  ],
  "warnings": [
    "Avoid any restaurant with photos on the door or a person outside trying to get you in."
  ]
}
```

**Every recommendation MUST have a `description` field.** This is
the guide's personal take — why this place, what's the story, what
makes it special. 1-2 sentences in the guide's voice. This field is
never null.

## Standard situations to look for

Try to populate these situations from the guide's knowledge. If the
guide has no relevant information for a situation, include it with
an empty `recommendations` array.

| Slug | Situation |
|------|-----------|
| `eat-after-tour` | Where do I eat after the tour? |
| `2-free-hours` | What do I do with 2 free hours? |
| `half-day` | What do I do with half a day? |
| `bar-tonight` | A good bar tonight? |
| `breakfast-tomorrow` | Where should I have breakfast tomorrow? |
| `rainy-day` | What if it rains? |
| `local-shopping` | Where do locals actually shop? |

## Rules

- **Every recommendation MUST include `description`.** This is the most
  important field — the guide's personal take in 1-2 sentences. Why this
  place, what's the story, what makes it worth going. Never null, never
  omitted. If the guide said something about it, put it here.
- **Never invent.** If the guide doesn't mention breakfast spots, the
  `breakfast-tomorrow` plan has `"recommendations": []`. Do not fill
  it with generic suggestions.
- If the guide mentions topics that don't fit any standard situation,
  create a new plan entry with an appropriate situation and slug.
- `name` should be evocative, not generic. "The sherry bar with
  sawdust on the floor" is better than "Bar on Cava Baja". Use the
  guide's own words and details to create a name that paints a picture.
  If the guide gives a real name, use it.
- `description` is where the guide's personality lives. Include their
  reasoning, their story, their insider detail. "Like stepping into
  1920s Madrid — sherry from old barrels, no music, no photos allowed"
  tells the tourist something useful. Keep it to 1-2 sentences.
- `what_to_order` and `what_to_avoid` capture the guide's specific,
  opinionated picks. These are what make the plans valuable. Extract
  them whenever present.
- `price_range` uses: `"Free"`, `"€"`, `"€€"`, `"€€€"`. Only set it
  if the guide gives enough info to estimate. Null otherwise.
- `vibe` is a short (3-8 words) description of the atmosphere.
- `warnings` are general tips that apply across situations: scams,
  transport, cultural norms, tipping, opening hours, safety, free
  services. **Extract EVERY practical tip from the guide's document.**
  If the guide mentions metro hours, tipping norms, tap water, siesta
  times, or any other useful fact, it must appear here. Do not
  summarize or merge — one warning per distinct tip.
- Only include `coordinates` when confidently identifiable.
- Preserve the guide's voice in all text fields.

## Guide's document

{guide_document}

## Guide info

- Name: {guide_name}
- City: {guide_city}
- Language for output: {language}
