# KPI Agent — Product Requirements Document

| Field   | Value      |
| ------- | ---------- |
| Version | 1.0        |
| Status  | Draft      |
| Author  | Spencer    |
| Date    | March 2026 |
| Product | KPI Agent  |

---

## 1. Overview

KPI Agent is an AI-powered research tool that helps Product Managers and Go-to-Market teams understand how any given industry measures success. Given an industry as input, the agent identifies the key performance indicators (KPIs) that industry uses, maps those KPIs to the underlying operational data required to calculate them, and identifies the software systems typically used to capture that data.

This tool was conceived from a real problem: at a Series A SaaS company, determining the Ideal Customer Profile (ICP) and expanding vertically into new industries required significant manual research. The company's product — an ETL data platform powered by a proprietary LLM capable of auto-generating schemas, primary keys, rate limiting, and authentication for any web-based API — needed a fast way to understand each prospect industry's data landscape. KPI Agent solves that problem.

---

## 2. Problem Statement

PM and GTM teams entering new industries face a recurring challenge: they do not know how that industry measures success, what data those measurements require, or what software systems produce that data. This leads to:

- Slow sales cycles due to manual research before customer conversations
- Inconsistent ICP definitions across team members
- Missed vertical expansion opportunities due to lack of industry data fluency
- Inability to quickly validate whether a new industry is a good fit for the product

---

## 3. Goals

### Primary Goals

- Allow any user to input an industry and receive a structured, accurate list of KPIs
- Map each KPI to the operational data entities required to calculate it
- Identify the software systems that typically generate or store that data
- Store query results with timestamps to allow accuracy tracking over time

### Secondary Goals

- Allow users to add custom KPIs based on insider or proprietary knowledge
- Enable team-level data sharing via a shared customer ID
- Provide a quality/confidence signal on returned KPI data

---

## 4. Target Users

| User Type          | Use Case                                                                        |
| ------------------ | ------------------------------------------------------------------------------- |
| Product Manager    | Understand a new vertical before roadmap planning or customer discovery         |
| GTM / Sales        | Prep for prospect conversations; understand the data stack of a target industry |
| Founder / Exec     | Evaluate new ICP segments and vertical expansion opportunities                  |
| Solutions Engineer | Map customer data infrastructure during pre-sales technical discovery           |

---

## 5. Features — v1

### 5.1 Industry KPI Lookup

The core feature. The user inputs an industry name and the agent returns a structured JSON response containing:

- Industry name
- List of KPIs, each containing:
  - KPI name
  - Description of what it measures
  - Required data entities needed to calculate it
  - Software systems that typically produce or store the required data
- Timestamp of when the query was run

### 5.2 KPI Data Storage

All query results are stored persistently so that:

- Users can review past queries
- KPI accuracy can be tracked and compared over time
- Data does not need to be re-queried on repeat lookups

### 5.3 Custom KPI Entry

Users can manually add KPIs to any industry record. This is designed for insider knowledge — for example, a salesperson who learns from a customer that their team tracks an unusual or proprietary metric. Custom KPIs are flagged as user-submitted and stored alongside AI-generated KPIs.

**Implementation decisions (shipped):**
- Form appears below AI-generated KPI cards after an industry has been analyzed
- Required field: KPI Name
- Optional fields: Description
- Confidence is user-selected via dropdown (High / Medium / Low); defaults to Medium if not changed
- Custom KPIs are appended to the most recent matching industry entry in `history.json`
- `source` is automatically set to `user_submitted`
- `added_at` timestamp is recorded at time of submission
- No validation beyond requiring a name; description, required_data, and systems are not required for user-submitted KPIs

### 5.4 Team Data Sharing

Users with the same Customer ID can access the same pool of stored KPI data. This allows GTM teams to share research without duplicating queries, and ensures that custom KPIs added by one team member are visible to others on the same account.

### 5.5 Data Quality Signal

Each AI-generated KPI includes a confidence or quality signal to help users assess the reliability of the data. Confidence scores are verified against live web sources via a second API call using Claude with web search enabled. For each KPI, the verifier searches for real-world evidence and assigns:

- **high** — strong evidence found in industry benchmarks, analyst reports, or widely cited sources
- **medium** — some evidence found, but not universally standardized
- **low** — little or no evidence found; emerging or poorly defined metric

This replaces the prior approach of AI self-evaluation. User-submitted KPIs retain user-selected confidence (High / Medium / Low dropdown, defaults to Medium).

---

## 6. Output Format

The agent returns results as structured JSON to support frontend rendering:

```json
{
  "industry": "string",
  "queried_at": "ISO 8601 timestamp",
  "kpis": [
    {
      "name": "string",
      "description": "string",
      "confidence": "high | medium | low",
      "required_data": ["string"],
      "systems": ["string"],
      "source": "ai_generated | user_submitted"
    }
  ]
}
```

---

## 7. Out of Scope — v1

The following features are explicitly excluded from v1 to keep scope manageable:

- User authentication and account management
- Billing or usage metering
- Real-time data from live industry sources
- Integrations with CRM or sales tools
- Multi-language support

> **Note:** A Streamlit-based frontend was originally listed as out of scope but has been built and shipped as part of v1.

---

## 8. Future Considerations

- Industry comparison view (e.g., e-commerce vs. fintech KPI overlap)
- CRM integration to attach KPI profiles to prospect accounts
- Feedback mechanism to upvote/downvote individual KPIs
- Exportable reports (PDF, CSV) for use in sales decks
- API endpoint for programmatic access by other tools

---

## 9. Success Metrics

| Metric                       | Target                                      |
| ---------------------------- | ------------------------------------------- |
| KPI accuracy (manual review) | > 85% rated accurate                        |
| Query response time          | < 10 seconds per industry                   |
| Custom KPI adoption          | At least 1 custom KPI added per active team |
| Data freshness               | Timestamps enable monthly accuracy audits   |

---

## 10. Open Questions

- What database will be used to store KPI data? (SQLite for v1 / Postgres later?)
- How is Customer ID assigned and managed in v1 without a full auth system?

**Resolved:**
- ~~What is the confidence scoring methodology?~~ → Web-search verified for `ai_generated` KPIs (a second Claude API call with web search enabled checks each KPI against live sources); user-selected for `user_submitted` KPIs (High / Medium / Low dropdown, defaults to Medium)
- ~~Should user-submitted KPIs require any validation before being stored?~~ → KPI Name is required; all other fields are optional. No additional validation in v1.
