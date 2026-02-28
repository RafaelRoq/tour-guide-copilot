Extract a structured tour itinerary from the guide's document below.

Return a JSON object with this exact structure:

```json
{
  "title": "Name of the tour",
  "tagline": "One sentence that captures the guide's personality and style. Written as if the guide said it.",
  "duration_minutes": 120,
  "stops": [
    {
      "order": 1,
      "name": "Stop name",
      "description": "1-3 sentences about what makes this stop interesting. Use the guide's voice and tone.",
      "tip": "A practical tip for this stop, or null if the guide didn't mention one.",
      "coordinates": { "lat": 40.4154, "lng": -3.7074 }
    }
  ]
}
```

## Rules

- Extract stops in the order the guide presents them.
- Keep descriptions to 1-3 sentences. Capture what's interesting, not
  encyclopedic facts.
- The `tip` field is for practical advice specific to the stop: best
  time to visit, where to stand for photos, what to notice. Null if
  the guide didn't provide one.
- Only include `coordinates` if the stop is a well-known landmark or
  the guide provides a clear address. Set to null if uncertain.
- `duration_minutes` should only be set if the guide mentions how long
  the tour takes. Null otherwise.
- `tagline` should feel like something the guide would actually say.
  Derive it from their tone and personality in the document. It should
  be warm and personal, never reference other companies, apps, or
  services. Example: "12 years walking these streets — ask me anything."
  If the document has no personality cues, set to null.
- If the guide's document doesn't contain a clear tour route, do your
  best to infer the order from context. If impossible, set all `order`
  values to 0 and note the ambiguity in the title.

## Guide's document

{guide_document}

## Guide info

- Name: {guide_name}
- City: {guide_city}
- Language for output: {language}
