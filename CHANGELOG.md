# Changelog

All notable changes to KPI Agent are documented here.

---

## [v0.3] — 2026-03-17
### Public Deployment

First public release. Deployed to Streamlit Community Cloud with access control, persistent storage, and rate limiting.

**Added**
- Password protection — shared password gates access to the app
- Supabase integration — all query results and custom KPIs stored in Postgres
- Rate limiting — 10 queries per session per day, tracked in Supabase
- Query counter displayed in UI so users know their remaining daily queries
- Session ID generated per visitor for anonymous usage tracking
- `requirements.txt` for Streamlit Cloud deployment

**QA — 2026-03-17**
- [x] App password functioning
- [x] Daily limit message displayed in UI
- [x] Daily limit enforced correctly
- [x] Query data saved to Supabase
- [x] Timestamp correct (UTC)
- [x] Custom KPI add working — confirmed in JSON and Supabase

---

## [v0.2] — 2026-03-04
### Core Features Complete

**Added**
- Confidence signal per KPI (`high` / `medium` / `low`) — AI-evaluated for generated KPIs
- Source tagging (`ai_generated` / `user_submitted`)
- Custom KPI entry form — users can add insider knowledge with optional description and confidence level
- Custom KPIs appended to most recent matching industry entry in storage
- Streamlit UI with collapsible KPI cards and raw JSON viewer
- Local persistence to `history.json` with timestamps

---

## [v0.1] — 2026-03-01
### Initial Build

**Added**
- Industry KPI lookup via Anthropic Claude API
- Structured JSON output: industry, KPIs, required data, systems
- Terminal-based interface (`chatbot.py`)
- Basic Streamlit frontend (`app.py`)
- Local query storage to `history.json`
