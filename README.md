# KPI Agent

An AI-powered research tool that helps Product Managers and Go-to-Market teams understand how any industry measures success — and what data infrastructure supports those metrics.

---

## What It Does

Input any industry, and KPI Agent returns:

- The **KPIs** that industry uses to measure success
- The **operational data** required to calculate each KPI
- The **software systems** that typically produce or store that data
- A **confidence signal** on each KPI (high / medium / low)

Results are displayed in a browser-based UI, stored locally with a timestamp, and can be supplemented with custom KPIs from your own knowledge.

---

## Roadmap

- [x] Industry KPI lookup with structured JSON output
- [x] Confidence signal per KPI (AI-evaluated)
- [x] Source tagging (ai_generated / user_submitted)
- [x] Persistent KPI data storage with timestamps
- [x] Custom KPI entry with user-selected confidence
- [x] Streamlit browser-based UI
- [ ] Team data sharing via Customer ID
- [ ] Database storage (SQLite / Postgres)

---

## Documentation

- [PRD.md](./PRD.md) — Full product requirements document


---

## Why I Built This

At a Series A SaaS company, our team struggled to quickly understand the data landscape of new industries we were targeting. We needed to know how each industry measured success before we could have meaningful sales conversations or define our ICP.

This agent solves that problem — turning hours of manual research into a single query.

---

## Tech Stack

- **Python** — core application
- **Anthropic Claude API** — AI agent (claude-sonnet-4-6)
- **Streamlit** — browser-based UI
- **python-dotenv** — environment variable management

---

## Project Structure

```
kpi-agent/
├── app.py           # Streamlit frontend (primary interface)
├── chatbot.py       # Terminal-based interface
├── history.json     # Local query storage (gitignored)
├── CLAUDE.md        # Project context for Claude Code
├── PRD.md           # Product Requirements Document
├── .env             # API key (not committed to GitHub)
├── .gitignore       # Ignores .env, venv, history.json, __pycache__
└── venv/            # Python virtual environment
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com)

### Installation

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/kpi-agent.git
cd kpi-agent
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install anthropic streamlit python-dotenv
```

4. Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

5. Run the Streamlit app:
```bash
streamlit run app.py
```

Or use the terminal interface:
```bash
python chatbot.py
```

---

## Example Output

**Input:** `E-commerce`

```json
{
  "industry": "E-commerce",
  "queried_at": "2026-03-07 10:00:00 UTC",
  "kpis": [
    {
      "name": "Customer Acquisition Cost (CAC)",
      "description": "Total cost to acquire a new customer",
      "confidence": "high",
      "required_data": ["marketing spend", "new customers acquired"],
      "systems": ["CRM", "ad platforms", "billing system"],
      "source": "ai_generated"
    }
  ]
}
```

---

## License

MIT
