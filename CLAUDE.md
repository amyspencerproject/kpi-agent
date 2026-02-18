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
- kpis (array of objects containing: name, description, required_data, systems)

## Tech Stack

- Python
- Anthropic Claude API (claude-sonnet-4-6)
- python-dotenv for environment variables

## Project Structure

- `chatbot.py` — main chatbot script
- `.env` — API key (not committed to GitHub)
- `venv/` — Python virtual environment

## Current Status

- Basic chatbot is working
- Next steps: Test the agent's responses and validate that returned KPIs and data mappings are accurate

## Preferences

- I am a beginner in Python
- Explain changes clearly before making them
- Warn me before using too many resources such as tokens
