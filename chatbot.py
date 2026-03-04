import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

conversation_history = []

SYSTEM_PROMPT = """You are a KPI and business intelligence expert. When the user provides an industry name, respond with a JSON object that identifies how that industry measures success.

Your response must be valid JSON with this exact structure:
{
  "industry": "<industry name>",
  "kpis": [
    {
      "name": "<KPI name>",
      "description": "<what this KPI measures and why it matters>",
      "confidence": "<high | medium | low>",
      "required_data": ["<data point 1>", "<data point 2>", "..."],
      "systems": ["<system 1>", "<system 2>", "..."],
      "source": "ai_generated"
    }
  ]
}

Rules:
- Return 5 to 8 of the most important KPIs for the industry
- required_data: list the specific data fields or metrics needed to calculate the KPI
- systems: list the software systems or data sources that typically store this data (e.g. CRM, ERP, billing system)
- confidence: rate how universally recognized this KPI is in the industry
  - high: universally tracked, appears in public benchmarks and analyst reports
  - medium: commonly tracked but varies by company size or sub-sector
  - low: emerging, niche, or inconsistently defined across the industry
- source: always set to "ai_generated"
- Respond ONLY with the JSON object — no explanation, no markdown code fences, just raw JSON
"""


def chat(user_message):
    conversation_history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    assistant_message = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_message})
    return assistant_message


def save_to_history(data: dict):
    history_file = "history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.append(data)
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


def display_response(raw_response):
    """Try to parse and pretty-print JSON. Fall back to plain text if it fails."""
    try:
        parsed = json.loads(raw_response)
        parsed["queried_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        save_to_history(parsed)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        # If Claude returned something that isn't valid JSON, print it as-is
        print(raw_response)


print("KPI Agent ready!")
print("Enter an industry name to get its key KPIs and required data.")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Industry: ")
    if user_input.lower() == "quit":
        break
    print("\nAnalyzing KPIs...\n")
    response = chat(user_input)
    display_response(response)
    print()
