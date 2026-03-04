import os
import json
from datetime import datetime, timezone
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


def get_kpis(industry: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": industry}]
    )
    data = json.loads(response.content[0].text)
    data["queried_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return data


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


def save_custom_kpi(industry: str, kpi: dict):
    history_file = "history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []
    for entry in reversed(history):
        if entry.get("industry", "").lower() == industry.lower():
            entry["kpis"].append(kpi)
            break
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


# --- Page config ---
st.set_page_config(page_title="KPI Agent", page_icon="📊", layout="centered")

st.title("📊 KPI Agent")
st.markdown("Enter an industry to see its key performance indicators and the data required to track them.")

# --- Input ---
industry = st.text_input("Industry", placeholder="e.g. E-commerce, Healthcare, SaaS")
analyze = st.button("Analyze KPIs", type="primary")

# --- Fetch and store results in session state ---
if analyze and industry.strip():
    with st.spinner(f"Analyzing KPIs for **{industry}**..."):
        try:
            data = get_kpis(industry.strip())
            save_to_history(data)
            st.session_state["kpi_data"] = data
        except json.JSONDecodeError:
            st.error("The response wasn't valid JSON. Try again.")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

elif analyze and not industry.strip():
    st.warning("Please enter an industry name first.")

# --- Display results ---
if "kpi_data" in st.session_state:
    data = st.session_state["kpi_data"]
    confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}

    st.subheader(f"KPIs for {data.get('industry', '')}")
    st.caption(f"Queried: {data['queried_at']}")

    for kpi in data.get("kpis", []):
        confidence = kpi.get("confidence", "medium").lower()
        icon = confidence_colors.get(confidence, "⚪")
        with st.expander(f"{icon} {kpi['name']}"):
            col1, col2 = st.columns(2)
            col1.markdown(f"**Confidence:** {icon} {confidence.capitalize()}")
            col2.markdown(f"**Source:** {kpi.get('source', 'ai_generated').replace('_', ' ').title()}")

            st.markdown(f"**Description**  \n{kpi.get('description', '')}")

            required_data = kpi.get("required_data", [])
            if required_data:
                st.markdown("**Required Data**")
                for item in required_data:
                    st.markdown(f"- {item}")

            systems = kpi.get("systems", [])
            if systems:
                st.markdown(f"**Systems:** {', '.join(systems)}")

    with st.expander("Show raw JSON"):
        st.json(data)

    # --- Custom KPI form ---
    st.divider()
    st.subheader("Add a Custom KPI")
    st.markdown("Add insider knowledge — a KPI your team or a customer tracks that isn't listed above.")

    with st.form("custom_kpi_form", clear_on_submit=True):
        custom_name = st.text_input("KPI Name *")
        custom_description = st.text_area("Description (optional)")
        custom_confidence = st.selectbox(
            "Confidence",
            options=["Medium", "High", "Low"],
            index=0
        )
        submitted = st.form_submit_button("Add KPI")

    if submitted:
        if not custom_name.strip():
            st.warning("KPI Name is required.")
        else:
            new_kpi = {
                "name": custom_name.strip(),
                "description": custom_description.strip(),
                "confidence": custom_confidence.lower(),
                "required_data": [],
                "systems": [],
                "source": "user_submitted",
                "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            save_custom_kpi(data["industry"], new_kpi)
            st.session_state["kpi_data"]["kpis"].append(new_kpi)
            st.success(f"'{custom_name.strip()}' added successfully.")
            st.rerun()
