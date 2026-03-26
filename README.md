# KPI First

An AI-powered research tool that helps Product Managers and Go-to-Market teams understand how any industry measures success — built to solve a problem I ran into firsthand.

---

## The Problem

At a Series A SaaS company, our GTM and PM teams were spending hours on manual research before every new vertical conversation. We needed to know how each industry measured success, what data those measurements required, and what software systems produced that data — before we could have a meaningful sales conversation or define our ICP.

There was no fast way to get that answer. So I built one.

---

## What It Does

Input any industry, and KPI Agent returns:

- The **KPIs** that industry uses to measure success
- The **operational data** required to calculate each KPI
- The **software systems** that typically produce or store that data
- A **confidence signal** on each KPI (high / medium / low)

Results are stored in a database with a timestamp, and users can add custom KPIs from their own insider knowledge.

---

## Why It's Built This Way

A few product decisions worth noting:

- **Structured JSON output** — results are returned as typed JSON so they can be rendered, stored, and eventually consumed by other tools (CRM enrichment, API access)
- **Confidence signal per KPI** — not all KPIs are equally universal; the signal helps users know whether a metric is industry-standard or niche
- **Custom KPI entry** — salespeople often learn proprietary metrics directly from customers; the tool captures that knowledge alongside AI-generated results
- **Persistent storage** — results are timestamped and stored so accuracy can be tracked over time and teams don't duplicate queries
- **Rate limiting** — public deployment is protected against abuse without requiring user accounts

---

## Try It

[Live app →](https://kpi-agent-ejvkkzxorahkqbjb5ez8xv.streamlit.app/)

Password available on request.

---

## Tech Stack

- **Python** — core application
- **Anthropic Claude API** — AI agent (claude-sonnet-4-6)
- **Streamlit** — browser-based UI
- **Supabase** — Postgres database for query storage and rate limiting
- **Streamlit Community Cloud** — public deployment

---

## Project Structure

```
kpi-agent/
├── app.py           # Streamlit frontend (primary interface)
├── chatbot.py       # Terminal-based interface
├── requirements.txt # Python dependencies
├── CLAUDE.md        # Project context for Claude Code
├── PRD.md           # Product Requirements Document
├── RESEARCH.md      # User research log
└── .env             # API key (not committed to GitHub)
```

---

## Documentation

- [PRD.md](./PRD.md) — Full product requirements, feature decisions, and roadmap
- [RESEARCH.md](./RESEARCH.md) — User research log from live testing

---

## Roadmap

- [x] Industry KPI lookup with structured JSON output
- [x] Confidence signal per KPI (AI-evaluated)
- [x] Source tagging (ai_generated / user_submitted)
- [x] Persistent storage with timestamps (Supabase)
- [x] Custom KPI entry with user-selected confidence
- [x] Streamlit browser-based UI
- [x] Public deployment with password protection and rate limiting
- [ ] Team data sharing via Customer ID
- [ ] Exportable reports (PDF, CSV)
- [ ] API endpoint for programmatic access

---

## License

MIT
