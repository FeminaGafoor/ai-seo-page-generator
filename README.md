# 800CarGuru — AI Programmatic SEO Engine

A proof-of-concept that generates structured, conversion-optimised SEO landing pages from a **service x location x intent** dataset using GPT-4o.

---

## What it does

Takes a single data row:

```python
{
    "service": "Battery Replacement",
    "location": "Dubai Marina",
    "intent": "emergency",
    "eta": "30 minutes",
    "price_from": "AED 199"
}
```

And generates a complete SEO page with:
- Meta title + description (SEO-optimised)
- Hero block — headline, subheadline, urgency line
- Trust signals — 3 location-specific trust points
- Local relevance paragraph
- FAQ block — 3 questions covering price, timing, coverage
- CTAs — click-to-call + WhatsApp
- HTML preview — opens directly in browser

---

## Architecture

```
Master Database
  services x locations x intent types
        |
Keyword Clustering (one page per combo)
        |
Modular Prompt Library (GPT-4o)
  prompt_meta()   -> meta title + description
  prompt_hero()   -> headline, subheadline, urgency
  prompt_trust()  -> 3 trust signals
  prompt_faq()    -> 3 FAQs
  prompt_local()  -> local relevance paragraph
        |
Page Assembler -> structured JSON
        |
HTML Renderer -> browser-ready preview
        |
[Next: CMS API push + Search Console + lead tracking]
```

---

## Quick start

```bash
# Install
pip install openai

# Set API key
export OPENAI_API_KEY=your_key_here

# Run
python generate.py --limit 3

# Open a page
open sample_output/battery-replacement-dubai-marina.html
```

---

## Usage

```bash
python generate.py                                    # all pages
python generate.py --service "Battery Replacement"   # filter by service
python generate.py --location "Dubai Marina"         # filter by location
python generate.py --limit 3                         # limit output
```

---

## Scaling to 500+ pages

This PoC generates 5 pages. The same engine scales to 5,000 by:

1. Expanding seed data to full PostgreSQL (10 services x 50 locations x 5 intents = 2,500 combos)
2. Running via n8n workflow automation on a schedule
3. Pushing JSON to WordPress REST API or headless CMS
4. Adding uniqueness checks before publish
5. Connecting CTAs to CRM lead attribution
6. Monitoring via GA4 + Search Console, auto-flagging weak pages

---

## Tech stack

| Layer | Tool |
|---|---|
| LLM | GPT-4o (OpenAI API) |
| Language | Python 3.11+ |
| Data | CSV / PostgreSQL (production) |
| Automation | n8n (production pipeline) |
| CMS | WordPress REST API / headless |
| Analytics | GA4 + Search Console |

---

Built by Femina Azeez — AI Engineer