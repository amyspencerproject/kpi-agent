import os
import json
from dotenv import load_dotenv
import anthropic
import streamlit as st

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a KPI and business intelligence expert. When the user provides an industry name, respond with a JSON object that identifies how that industry measures success.

Your response must be valid JSON with this exact structure:
{
  "industry": "<industry name>",
  "kpis": [
    {
      "name": "<KPI name>",
      "description": "<what this KPI measures and why it matters>",
      "required_data": ["<data point 1>", "<data point 2>", "..."],
      "systems": ["<system 1>", "<system 2>", "..."]
    }
  ]
}

Rules:
- Return 5 to 8 of the most important KPIs for the industry
- required_data: list the specific data fields or metrics needed to calculate the KPI
- systems: list the software systems or data sources that typically store this data (e.g. CRM, ERP, billing system)
- Respond ONLY with the JSON object — no explanation, no markdown code fences, just raw JSON
"""


def get_kpis(industry: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": industry}]
    )
    return json.loads(response.content[0].text)


# --- Page config ---
st.set_page_config(page_title="KPI Agent", page_icon="📊", layout="centered")

st.title("📊 KPI Agent")
st.markdown("Enter an industry to see its key performance indicators and the data required to track them.")

# --- Input ---
industry = st.text_input("Industry", placeholder="e.g. E-commerce, Healthcare, SaaS")
analyze = st.button("Analyze KPIs", type="primary")

# --- Results ---
if analyze and industry.strip():
    with st.spinner(f"Analyzing KPIs for **{industry}**..."):
        try:
            data = get_kpis(industry.strip())
        except json.JSONDecodeError:
            st.error("The response wasn't valid JSON. Try again.")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    st.subheader(f"KPIs for {data.get('industry', industry)}")

    for kpi in data.get("kpis", []):
        with st.expander(kpi["name"]):
            st.markdown(f"**Description**  \n{kpi['description']}")

            st.markdown("**Required Data**")
            for item in kpi.get("required_data", []):
                st.markdown(f"- {item}")

            systems = kpi.get("systems", [])
            if systems:
                st.markdown(f"**Systems:** {', '.join(systems)}")

    with st.expander("Show raw JSON"):
        st.json(data)

elif analyze and not industry.strip():
    st.warning("Please enter an industry name first.")
