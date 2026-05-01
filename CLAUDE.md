# Project: KPI Agent

## What this project does

This project builds an AI agent that helps PM and GTM teams understand how a given industry measures success — and what operational data is required to support those metrics.

This AI agent should:

- Take an industry as input
- Identify how that industry measures success (KPIs)
- Map those KPIs to required operational data entities and systems required to calculate and track an industry's core KPIs

## Example

Input: "E-commerce"
Output:

```json
{
  "industry": "E-commerce",
  "kpis": [
    {
      "name": "Customer Acquisition Cost (CAC)",
      "description": "Total cost to acquire a new customer",
      "required_data": ["marketing spend", "new customers acquired"],
      "systems": ["CRM", "ad platforms", "billing system"]
    }
  ]
}
```

## Goals

The AI agent helps product teams quickly understand how an industry measures success and what data infrastructure supports those metrics.

## Output Format

Return results as JSON with the following structure:

- industry (string)
- queried_at (UTC timestamp string)
- kpis (array of objects containing: name, description, confidence, required_data, systems, source)
  - confidence: "high" | "medium" | "low" — AI-evaluated for ai_generated KPIs, user-selected for user_submitted
  - source: "ai_generated" | "user_submitted"

## Tech Stack

- Python
- Anthropic Claude API (claude-sonnet-4-6)
- Streamlit (browser-based UI)
- python-dotenv for environment variables

## Project Structure

- `app.py` — Streamlit frontend (primary interface)
- `.env` — API key (not committed to GitHub)
- `venv/` — Python virtual environment

## Current Status

**Shipped:**
- Industry KPI lookup returning structured JSON (5–8 KPIs per industry)
- Confidence signal per KPI, web-verified via second Claude API call with web search
- `web_verified` boolean on each KPI stored in Supabase
- Source tagging (ai_generated / user_submitted)
- Timestamp on all queries
- Supabase (Postgres) for data persistence, with separate production and development databases
- Streamlit UI with collapsible KPI cards and raw JSON viewer
- Custom KPI entry form with user-selected confidence
- Team data sharing via optional team code at login (validated against teams table in Supabase)
- Rate limiting (10 queries/session/day) tracked in Supabase
- Password protection on the app

**All v1.1 features shipped. No outstanding PRD items.**

## Preferences

- I am a beginner in Python
- Explain changes clearly before making them
- Warn me before using too many resources such as tokens

## Standing Rules

- **Explain before editing:** Always describe what a code change does in plain language before making it. Flag any trade-offs.
- **Update CLAUDE.md when features ship:** Keep the Current Status section accurate after every significant change.
- **Update PRD.md when features ship:** Move items from "Not yet built" to "Shipped" and update version/date as needed.
- **Update memory files proactively:** After shipping features, deleting files, or making key decisions, update the memory files in `.claude/` without waiting to be asked.
- **Present options for design decisions:** When a meaningful design choice comes up (data model, UX flow, auth approach), present 2-3 options with tradeoffs and wait for approval before building.
