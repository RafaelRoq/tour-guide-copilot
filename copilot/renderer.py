"""Renderer. Converts structured JSON into static HTML, markdown, or JSON files."""

import html
import json
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .schemas import sanitize_slug
from . import __version__


def render(
    itinerary: dict,
    plans: dict,
    config: Config,
    output_dir: str,
) -> list[str]:
    """Render itinerary and plans into output files.

    Args:
        itinerary: The itinerary dict from itinerary.py.
        plans: The plans dict from plans.py.
        config: Application configuration.
        output_dir: Directory to write output files to.

    Returns:
        List of paths to created files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Build the combined data structure
    data = _build_combined(itinerary, plans, config)

    created = []
    fmt = config.output_format.lower()

    if fmt in ("json", "all"):
        path = output_path / "guide.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        created.append(str(path))

    if fmt in ("markdown", "all"):
        path = output_path / "guide.md"
        path.write_text(_render_markdown(data), encoding="utf-8")
        created.append(str(path))

    if fmt in ("html", "all"):
        path = output_path / "index.html"
        html = _render_html(data, config)
        path.write_text(html, encoding="utf-8")
        created.append(str(path))

    return created


def _build_combined(itinerary: dict, plans: dict, config: Config) -> dict:
    """Build the full JSON structure from itinerary and plans."""
    return {
        "guide": {
            "name": config.guide_name,
            "city": config.guide_city,
            "language": config.guide_language,
            "tagline": itinerary.get("tagline"),
            "years": config.guide_years,
            "tip_url": config.guide_tip_url,
        },
        "itinerary": itinerary,
        "plans": plans.get("plans", []),
        "warnings": plans.get("warnings", []),
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": __version__,
            "model": config.model,
        },
    }


def _render_markdown(data: dict) -> str:
    """Render the combined data as a markdown document."""
    lines = []
    guide = data["guide"]
    itin = data["itinerary"]

    # Header
    lines.append(f"# {guide['name']} — {guide['city']}")
    if guide.get("tagline"):
        lines.append(f"\n*{guide['tagline']}*")
    lines.append("")

    # Itinerary
    title = itin.get("title", "Tour")
    duration = itin.get("duration_minutes")
    dur_str = f" ({duration} min)" if duration else ""
    lines.append(f"## {title}{dur_str}")
    lines.append("")

    for stop in itin.get("stops", []):
        lines.append(f"### {stop['order']}. {stop['name']}")
        lines.append("")
        lines.append(stop["description"])
        if stop.get("tip"):
            lines.append(f"\n> **Tip:** {stop['tip']}")
        lines.append("")

    # Plans
    lines.append("## After the tour")
    lines.append("")

    for plan in data.get("plans", []):
        lines.append(f"### {plan['situation']}")
        lines.append("")
        recs = plan.get("recommendations", [])
        if not recs:
            lines.append("*No recommendation available yet.*")
            lines.append("")
            continue
        for rec in recs:
            lines.append(f"**{rec['name']}**")
            if rec.get("description"):
                lines.append(rec["description"])
            parts = []
            if rec.get("what_to_order"):
                parts.append(f"Order: {rec['what_to_order']}")
            if rec.get("what_to_avoid"):
                parts.append(f"Avoid: {rec['what_to_avoid']}")
            if rec.get("vibe"):
                parts.append(f"Vibe: {rec['vibe']}")
            if rec.get("price_range"):
                parts.append(f"Price: {rec['price_range']}")
            if parts:
                lines.append(". ".join(parts) + ".")
            lines.append("")

    # Warnings
    warnings = data.get("warnings", [])
    if warnings:
        lines.append("## Good to know")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def _render_html(data: dict, config: Config) -> str:
    """Render the combined data as a static HTML page using Jinja2."""
    templates_dir = config.templates_dir
    if not templates_dir.exists():
        # Fallback: generate minimal HTML without template
        return _render_html_minimal(data)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )

    try:
        template = env.get_template("index.html")
    except Exception:
        return _render_html_minimal(data)

    return template.render(data=data)


def _render_html_minimal(data: dict) -> str:
    """Fallback HTML renderer when no template is available.

    All user-supplied content is escaped with html.escape() to prevent XSS.
    """
    e = html.escape  # shorthand
    guide = data["guide"]
    itin = data["itinerary"]

    stops_html = ""
    for stop in itin.get("stops", []):
        tip = f'<p class="tip">💡 {e(stop["tip"])}</p>' if stop.get("tip") else ""
        stops_html += f"""
        <div class="stop">
            <div class="stop-number">{int(stop['order'])}</div>
            <div class="stop-content">
                <h3>{e(stop['name'])}</h3>
                <p>{e(stop['description'])}</p>
                {tip}
            </div>
        </div>"""

    plans_html = ""
    for plan in data.get("plans", []):
        slug = e(plan.get("slug", sanitize_slug(plan.get("situation", "plan"))))
        recs = plan.get("recommendations", [])
        if not recs:
            recs_html = '<p class="empty">No recommendation available yet.</p>'
        else:
            recs_html = ""
            for rec in recs:
                desc = f'<p class="rec-description">{e(rec["description"])}</p>' if rec.get("description") else ""
                details = []
                if rec.get("what_to_order"):
                    details.append(f"<strong>Order:</strong> {e(rec['what_to_order'])}")
                if rec.get("what_to_avoid"):
                    details.append(f"<strong>Avoid:</strong> {e(rec['what_to_avoid'])}")
                if rec.get("vibe"):
                    details.append(f"<strong>Vibe:</strong> {e(rec['vibe'])}")
                if rec.get("price_range"):
                    details.append(f"<strong>Price:</strong> {e(rec['price_range'])}")
                details_html = "<br>".join(details)
                recs_html += f"""
                <div class="recommendation">
                    <h4>{e(rec['name'])}</h4>
                    {desc}
                    <p>{details_html}</p>
                </div>"""
        plans_html += f"""
        <div class="plan" id="{slug}">
            <div class="plan-header" onclick="togglePlan(this)">
                <h3>{e(plan['situation'])}</h3>
                <span class="plan-arrow">▶</span>
            </div>
            <div class="plan-body"><div class="plan-body-inner">
                {recs_html}
            </div></div>
        </div>"""

    warnings_html = ""
    for w in data.get("warnings", []):
        warnings_html += f"<li>{e(w)}</li>"
    if warnings_html:
        warnings_html = f"""
        <div class="warnings">
            <h3>⚠️ Good to know</h3>
            <ul>{warnings_html}</ul>
        </div>"""

    title = e(itin.get("title", f"{guide['name']} — {guide['city']}"))
    guide_name = e(guide['name'])
    guide_city = e(guide.get('city', ''))
    meta = f'<p class="guide-meta">{e(guide["years"])}</p>' if guide.get("years") else ""
    tagline = f'<p class="tagline">{e(guide["tagline"])}</p>' if guide.get("tagline") else ""

    tip_url = guide.get("tip_url", "")
    if tip_url:
        thank_btn = f'<a class="thank-btn" href="{e(tip_url)}" target="_blank" rel="noopener noreferrer">❤️ Thank {guide_name}</a>'
    else:
        thank_btn = f'<span class="thank-btn" style="opacity:0.5;cursor:default;">❤️ Thank {guide_name}</span>'

    lang = e(guide.get('language', 'en'))

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, system-ui, sans-serif; color: #1a1a1a;
               max-width: 480px; margin: 0 auto; padding: 16px; background: #fafafa; }}
        .header {{ text-align: center; padding: 20px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px; }}
        .header h1 {{ font-size: 1.5rem; }}
        .guide-meta {{ color: #888; font-size: 0.8rem; margin-top: 4px; }}
        .tagline {{ color: #666; font-style: italic; margin-top: 6px; font-size: 0.9rem; }}
        .tabs {{ display: flex; border-bottom: 2px solid #e0e0e0; margin-bottom: 16px; }}
        .tab {{ flex: 1; text-align: center; padding: 10px; cursor: pointer; font-weight: 600;
                color: #888; border-bottom: 2px solid transparent; margin-bottom: -2px; }}
        .tab.active {{ color: #1a1a1a; border-bottom-color: #1a1a1a; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .section-title {{ font-size: 1.1rem; color: #333; margin-bottom: 16px; }}
        .stop {{ display: flex; gap: 12px; margin-bottom: 16px; }}
        .stop-number {{ width: 28px; height: 28px; background: #1a1a1a; color: white;
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;
                        font-size: 0.85rem; font-weight: 600; flex-shrink: 0; margin-top: 2px; }}
        .stop-content h3 {{ font-size: 1rem; }}
        .stop-content p {{ color: #444; font-size: 0.9rem; line-height: 1.5; margin-top: 4px; }}
        .tip {{ color: #666; font-size: 0.85rem; font-style: italic; margin-top: 6px; }}
        .plan {{ margin-bottom: 8px; background: white; border-radius: 8px; overflow: hidden; }}
        .plan-header {{ display: flex; justify-content: space-between; align-items: center;
                        padding: 12px; cursor: pointer; }}
        .plan-header h3 {{ font-size: 1rem; margin: 0; }}
        .plan-arrow {{ font-size: 0.8rem; color: #888; transition: transform 0.2s; }}
        .plan.open .plan-arrow {{ transform: rotate(90deg); }}
        .plan-body {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }}
        .plan.open .plan-body {{ max-height: 800px; }}
        .plan-body-inner {{ padding: 0 12px 12px; }}
        .recommendation {{ margin: 10px 0; padding-top: 8px; border-top: 1px solid #f0f0f0; }}
        .recommendation:first-child {{ border-top: none; padding-top: 0; }}
        .recommendation h4 {{ font-size: 0.95rem; margin-bottom: 4px; }}
        .rec-description {{ font-size: 0.9rem; color: #333; line-height: 1.5; margin-bottom: 6px; font-style: italic; }}
        .recommendation p {{ font-size: 0.9rem; color: #444; line-height: 1.5; }}
        .empty {{ color: #999; font-style: italic; }}
        .warnings {{ margin-top: 12px; padding: 12px; background: #fff8e1; border-radius: 8px; }}
        .warnings h3 {{ font-size: 1rem; margin-bottom: 8px; }}
        .warnings ul {{ padding-left: 20px; }}
        .warnings li {{ font-size: 0.9rem; color: #555; margin-bottom: 6px; }}
        .thank-container {{ text-align: center; margin: 28px 0 8px; }}
        .thank-btn {{ display: inline-block; padding: 12px 28px; background: #1a1a1a; color: white;
                      border: none; border-radius: 24px; font-size: 0.95rem; font-weight: 600;
                      cursor: pointer; text-decoration: none; }}
        .thank-btn:hover {{ background: #333; }}
        .thank-note {{ font-size: 0.75rem; color: #999; margin-top: 6px; }}
        .footer {{ text-align: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0;
                   font-size: 0.8rem; color: #aaa; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{guide_name} · {guide_city}</h1>
        {meta}
        {tagline}
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('itinerary')">Your tour</div>
        <div class="tab" onclick="switchTab('plans')">{guide_name}'s plans</div>
    </div>

    <div id="itinerary" class="tab-content active">
        <h2 class="section-title">{title}</h2>
        {stops_html}
    </div>

    <div id="plans" class="tab-content">
        <h2 class="section-title">What do you need?</h2>
        {plans_html}
        {warnings_html}
    </div>

    <div class="thank-container">
        {thank_btn}
        <p class="thank-note">If {guide_name}'s tips helped you, let them know.</p>
    </div>

    <div class="footer">
        Powered by Tour Guide Copilot · {guide_name}'s knowledge, structured by AI
    </div>

    <script>
        function switchTab(tab) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            document.querySelector('[onclick*="' + tab + '"]').classList.add('active');
        }}
        function togglePlan(header) {{
            header.parentElement.classList.toggle('open');
        }}
    </script>
</body>
</html>"""
