"""
800CarGuru — AI Programmatic SEO Page Generator
================================================
Generates structured SEO landing pages from a service-location-intent dataset.
Each page is output as JSON + a rendered HTML preview.

Usage:
    python generate.py                          # generates all pages in dataset
    python generate.py --service "Battery Replacement" --location "Dubai Marina"
    python generate.py --limit 3               # generate first 3 rows only

Requirements:
    pip install -r requirements.txt
    Add OPENAI_API_KEY=sk-... to a .env file in the project root
"""

import os
import json
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from seed import DATASET

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
OUTPUT_DIR = Path("sample_output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# JSON HELPER — strips markdown fences
# ─────────────────────────────────────────────

def clean_json(text: str) -> dict:
    """Strip markdown fences GPT sometimes wraps around JSON, then parse."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]   # remove opening ```json line
        text = text.rsplit("```", 1)[0]  # remove closing ```
    return json.loads(text.strip())


# ─────────────────────────────────────────────
# PROMPT FUNCTIONS — one per content block
# ─────────────────────────────────────────────

def prompt_meta(row):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.4,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an SEO specialist for 800CarGuru, a UAE automotive service company. "
                    "Write concise, high-CTR meta tags. Never use exclamation marks. "
                    "Respond ONLY with valid JSON — no markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write a meta title (max 60 chars) and meta description (max 155 chars) for:\n"
                    f"Service: {row['service']}\n"
                    f"Location: {row['location']}\n"
                    f"Intent: {row['intent']}\n"
                    f"Price from: {row['price_from']}\n"
                    f"ETA: {row['eta']}\n\n"
                    f'Respond with: {{"title": "...", "description": "..."}}'
                ),
            },
        ],
    )
    return clean_json(resp.choices[0].message.content)


def prompt_hero(row):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.6,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a conversion copywriter for 800CarGuru UAE. "
                    "Write punchy, high-intent hero copy for local service pages. "
                    "Be direct. No fluff. No exclamation marks. "
                    "Respond ONLY with valid JSON — no markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write hero copy for a {row['intent']} {row['service']} page in {row['location']}.\n"
                    f"ETA: {row['eta']} | Price from: {row['price_from']} | Warranty: {row['warranty']}\n\n"
                    f'Respond with: {{"headline": "...", "subheadline": "...", "urgency_line": "..."}}'
                ),
            },
        ],
    )
    return clean_json(resp.choices[0].message.content)


def prompt_trust(row):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.4,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write trust-building copy for 800CarGuru UAE automotive services. "
                    "Each trust point should be specific, short, and reassuring. "
                    "Respond ONLY with valid JSON — no markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write 3 trust signals for {row['service']} in {row['location']}.\n"
                    f"Warranty: {row['warranty']} | ETA: {row['eta']}\n\n"
                    f'Respond with: {{"trust_points": ["...", "...", "..."]}}'
                ),
            },
        ],
    )
    return clean_json(resp.choices[0].message.content)


def prompt_faq(row):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write FAQ content for 800CarGuru UAE local service pages. "
                    "FAQs should address real customer concerns: price, timing, coverage, process. "
                    "Keep answers under 50 words each. "
                    "Respond ONLY with valid JSON — no markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write 3 FAQs for {row['intent']} {row['service']} in {row['location']}.\n"
                    f"Price from: {row['price_from']} | ETA: {row['eta']}\n\n"
                    f'Respond with: {{"faqs": [{{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}]}}'
                ),
            },
        ],
    )
    return clean_json(resp.choices[0].message.content)


def prompt_local_angle(row):
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.6,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write localised content for 800CarGuru UAE. "
                    "Make the copy feel native to the area — mention local context where natural. "
                    "Keep it to 2-3 sentences. "
                    "Respond ONLY with valid JSON — no markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write a local relevance paragraph for {row['service']} in {row['location']}, UAE.\n"
                    f"Intent: {row['intent']} | ETA: {row['eta']}\n\n"
                    f'Respond with: {{"local_paragraph": "..."}}'
                ),
            },
        ],
    )
    return clean_json(resp.choices[0].message.content)


# ─────────────────────────────────────────────
# PAGE ASSEMBLER
# ─────────────────────────────────────────────

def generate_page(row):
    print(f"\n  Generating: {row['service']} — {row['location']} ({row['intent']})")

    print("    [1/5] meta...")
    meta = prompt_meta(row)

    print("    [2/5] hero...")
    hero = prompt_hero(row)

    print("    [3/5] trust...")
    trust = prompt_trust(row)

    print("    [4/5] faq...")
    faq = prompt_faq(row)

    print("    [5/5] local angle...")
    local = prompt_local_angle(row)

    return {
        "slug": f"{row['service_slug']}-{row['location_slug']}",
        "service": row["service"],
        "location": row["location"],
        "intent": row["intent"],
        "meta": meta,
        "hero": hero,
        "trust": trust,
        "faq": faq,
        "local": local,
        "cta": {
            "phone": row["cta_phone"],
            "whatsapp": row["cta_whatsapp"],
            "price_from": row["price_from"],
            "eta": row["eta"],
        },
    }


# ─────────────────────────────────────────────
# HTML RENDERER
# ─────────────────────────────────────────────

def render_html(page):
    trust_html = "\n".join(
        f'<div class="trust-item"><div class="trust-icon">&#10003;</div><p>{pt}</p></div>'
        for pt in page["trust"]["trust_points"]
    )
    faq_html = "\n".join(
        f'<div class="faq-item"><h4>{item["q"]}</h4><p>{item["a"]}</p></div>'
        for item in page["faq"]["faqs"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{page['meta']['title']}</title>
  <meta name="description" content="{page['meta']['description']}"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #1a1a1a; background: #fff; line-height: 1.6; }}
    a {{ color: inherit; text-decoration: none; }}
    nav {{ background: #0a0a0a; padding: 14px 24px; display: flex;
           justify-content: space-between; align-items: center; }}
    .logo {{ color: #fff; font-size: 18px; font-weight: 700; }}
    .logo span {{ color: #22c55e; }}
    .nav-phone {{ color: #fff; font-size: 14px; font-weight: 500; }}
    .hero {{ background: #0f0f1a; color: #fff; padding: 64px 24px 56px; text-align: center; }}
    .hero-badge {{ display: inline-block; background: #22c55e; color: #000;
                   font-size: 12px; font-weight: 700; padding: 4px 14px;
                   border-radius: 20px; text-transform: uppercase;
                   letter-spacing: 0.5px; margin-bottom: 20px; }}
    .hero h1 {{ font-size: clamp(26px, 5vw, 42px); font-weight: 800;
                line-height: 1.2; max-width: 680px; margin: 0 auto 16px; }}
    .hero .sub {{ font-size: 18px; color: #a0a0a0; max-width: 500px; margin: 0 auto 12px; }}
    .urgency {{ font-size: 14px; color: #22c55e; margin-bottom: 32px; }}
    .ctas {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
    .btn-call {{ background: #22c55e; color: #000; font-weight: 700;
                 padding: 14px 28px; border-radius: 8px; font-size: 15px; }}
    .btn-wa {{ background: #25d366; color: #fff; font-weight: 700;
               padding: 14px 28px; border-radius: 8px; font-size: 15px; }}
    .price-note {{ margin-top: 20px; font-size: 13px; color: #666; }}
    .meta-tag {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px;
                 padding: 12px 16px; margin: 12px 24px 0; font-size: 12px;
                 color: #166534; font-family: monospace; }}
    .trust {{ background: #f9f9f9; padding: 48px 24px; text-align: center; }}
    .trust h2 {{ font-size: 22px; font-weight: 700; margin-bottom: 28px; }}
    .trust-grid {{ display: flex; gap: 16px; justify-content: center;
                   flex-wrap: wrap; max-width: 800px; margin: 0 auto; }}
    .trust-item {{ background: #fff; border: 1px solid #e5e5e5; border-radius: 10px;
                   padding: 20px 24px; flex: 1; min-width: 200px; max-width: 260px; text-align: left; }}
    .trust-icon {{ color: #22c55e; font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
    .trust-item p {{ font-size: 14px; color: #444; line-height: 1.5; }}
    .local {{ padding: 48px 24px; max-width: 720px; margin: 0 auto; }}
    .local h2 {{ font-size: 20px; font-weight: 700; margin-bottom: 16px; }}
    .local p {{ font-size: 15px; color: #444; line-height: 1.7; }}
    .faq {{ background: #f9f9f9; padding: 48px 24px; }}
    .faq-inner {{ max-width: 720px; margin: 0 auto; }}
    .faq h2 {{ font-size: 22px; font-weight: 700; margin-bottom: 24px; }}
    .faq-item {{ background: #fff; border: 1px solid #e5e5e5; border-radius: 8px;
                 padding: 18px 20px; margin-bottom: 12px; }}
    .faq-item h4 {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; color: #111; }}
    .faq-item p {{ font-size: 14px; color: #555; line-height: 1.6; }}
    .bottom-cta {{ background: #0a0a0a; color: #fff; padding: 48px 24px; text-align: center; }}
    .bottom-cta h2 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
    .bottom-cta p {{ color: #888; margin-bottom: 28px; font-size: 15px; }}
    footer {{ text-align: center; padding: 20px; font-size: 12px; color: #aaa; }}
  </style>
</head>
<body>

<nav>
  <div class="logo">800<span>Car</span>Guru</div>
  <div class="nav-phone">{page['cta']['phone']}</div>
</nav>

<div class="meta-tag">
  SEO Meta &mdash; Title: "{page['meta']['title']}" &nbsp;|&nbsp; Desc: "{page['meta']['description']}"
</div>

<section class="hero">
  <div class="hero-badge">{page['intent']} &middot; {page['location']}</div>
  <h1>{page['hero']['headline']}</h1>
  <p class="sub">{page['hero']['subheadline']}</p>
  <p class="urgency">{page['hero']['urgency_line']}</p>
  <div class="ctas">
    <a href="tel:{page['cta']['phone']}" class="btn-call">Call Now &mdash; {page['cta']['phone']}</a>
    <a href="{page['cta']['whatsapp']}" class="btn-wa">WhatsApp Us</a>
  </div>
  <p class="price-note">From {page['cta']['price_from']} &middot; {page['cta']['eta']} response &middot; {page['trust']['trust_points'][0]}</p>
</section>

<section class="trust">
  <h2>Why {page['location']} drivers choose 800CarGuru</h2>
  <div class="trust-grid">{trust_html}</div>
</section>

<section class="local">
  <h2>{page['service']} in {page['location']}</h2>
  <p>{page['local']['local_paragraph']}</p>
</section>

<section class="faq">
  <div class="faq-inner">
    <h2>Frequently asked questions</h2>
    {faq_html}
  </div>
</section>

<section class="bottom-cta">
  <h2>Need {page['service']} in {page['location']} now?</h2>
  <p>Our team reaches you in {page['cta']['eta']}. Available {page['intent']}.</p>
  <div class="ctas">
    <a href="tel:{page['cta']['phone']}" class="btn-call">Call {page['cta']['phone']}</a>
    <a href="{page['cta']['whatsapp']}" class="btn-wa">WhatsApp Us</a>
  </div>
</section>

<footer>
  &copy; 2025 800CarGuru &middot; {page['location']} &middot; {page['service']}
  &middot; Slug: /{page['slug']}
  &middot; Generated by AI Programmatic SEO Engine v1
</footer>

</body>
</html>"""


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="800CarGuru SEO Page Generator")
    parser.add_argument("--service", help="Filter by service name")
    parser.add_argument("--location", help="Filter by location name")
    parser.add_argument("--limit", type=int, help="Max pages to generate")
    args = parser.parse_args()

    rows = DATASET
    if args.service:
        rows = [r for r in rows if args.service.lower() in r["service"].lower()]
    if args.location:
        rows = [r for r in rows if args.location.lower() in r["location"].lower()]
    if args.limit:
        rows = rows[: args.limit]

    if not rows:
        print("No matching rows found in dataset.")
        return

    print(f"\n800CarGuru SEO Generator")
    print(f"{'─' * 40}")
    print(f"Generating {len(rows)} page(s)...")

    results = []
    for row in rows:
        try:
            page = generate_page(row)
            results.append(page)
            slug = page["slug"]

            json_path = OUTPUT_DIR / f"{slug}.json"
            with open(json_path, "w") as f:
                json.dump(page, f, indent=2)

            html_path = OUTPUT_DIR / f"{slug}.html"
            with open(html_path, "w") as f:
                f.write(render_html(page))

            print(f"    Saved: {html_path}")

        except Exception as e:
            print(f"    ERROR on {row['service']} / {row['location']}: {e}")

    print(f"\n{'─' * 40}")
    print(f"Done. {len(results)} page(s) in /sample_output/")
    print(f"\nOpen in browser:")
    for page in results:
        print(f"  open sample_output/{page['slug']}.html")


if __name__ == "__main__":
    main()