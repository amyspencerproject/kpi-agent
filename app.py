import os
import json
import uuid
from datetime import datetime, timezone, date
from dotenv import load_dotenv
import anthropic
from supabase import create_client
import streamlit as st

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

APP_PASSWORD = os.getenv("APP_PASSWORD")
DAILY_LIMIT = 10

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

VERIFY_PROMPT = """You are a KPI verification assistant. You have been given a list of KPIs for a specific industry.

Your job is to verify each KPI by searching for evidence that it is a real, commonly tracked metric in that industry.

For each KPI, search the web and assign a verified confidence score:
- high: strong evidence found — appears in industry benchmarks, analyst reports, or widely cited sources
- medium: some evidence found — mentioned in industry content but not universally standardized
- low: little or no evidence found — rarely mentioned, emerging, or poorly defined

Respond ONLY with a valid JSON array of objects in this exact structure, one per KPI:
[
  {
    "name": "<exact KPI name as provided>",
    "confidence": "<high | medium | low>"
  }
]

No explanation, no markdown, just the raw JSON array.
"""


# --- Session ID ---
def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]


# --- Rate limiting ---
def get_query_count(session_id: str) -> int:
    today = date.today().isoformat()
    result = supabase.table("rate_limits").select("query_count").eq("session_id", session_id).eq("query_date", today).execute()
    if result.data:
        return result.data[0]["query_count"]
    return 0


def increment_query_count(session_id: str):
    today = date.today().isoformat()
    existing = supabase.table("rate_limits").select("query_count").eq("session_id", session_id).eq("query_date", today).execute()
    if existing.data:
        new_count = existing.data[0]["query_count"] + 1
        supabase.table("rate_limits").update({"query_count": new_count}).eq("session_id", session_id).eq("query_date", today).execute()
    else:
        supabase.table("rate_limits").insert({"session_id": session_id, "query_date": today, "query_count": 1}).execute()


# --- Verification layer ---
def verify_kpis(industry: str, kpis: list) -> list:
    """
    Makes a second Claude API call with web search enabled.
    Returns the same KPI list with confidence scores updated based on web evidence.
    Swappable: replace this function body with a Perplexity call in the future.
    """
    kpi_names = [kpi["name"] for kpi in kpis]
    user_message = f"Industry: {industry}\n\nKPIs to verify:\n" + "\n".join(f"- {name}" for name in kpi_names)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=VERIFY_PROMPT,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract the text block from the response (web search may add tool_use blocks)
        verified_text = None
        for block in response.content:
            if block.type == "text":
                verified_text = block.text
                break

        if not verified_text:
            return kpis  # Fall back to original if no text returned

        verified_list = json.loads(verified_text)

        # Build a lookup map from the verified results
        verified_map = {item["name"]: item["confidence"] for item in verified_list}

        # Update confidence scores in the original KPI list
        for kpi in kpis:
            if kpi["name"] in verified_map:
                kpi["confidence"] = verified_map[kpi["name"]]

        return kpis

    except Exception:
        return kpis  # Always fall back gracefully — never break the main flow


# --- KPI fetch ---
def get_kpis(industry: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": industry}]
    )
    data = json.loads(response.content[0].text)

    # Verify confidence scores against live web sources
    data["kpis"] = verify_kpis(data["industry"], data["kpis"])

    data["queried_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return data


# --- Supabase storage ---
def save_to_supabase(data: dict, session_id: str):
    supabase.table("queries").insert({
        "industry": data["industry"],
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "kpis": data["kpis"],
        "session_id": session_id
    }).execute()


def save_custom_kpi_to_supabase(industry: str, kpi: dict, session_id: str):
    result = supabase.table("queries").select("id, kpis").eq("industry", industry).eq("session_id", session_id).order("queried_at", desc=True).limit(1).execute()
    if result.data:
        row = result.data[0]
        updated_kpis = row["kpis"] + [kpi]
        supabase.table("queries").update({"kpis": updated_kpis}).eq("id", row["id"]).execute()


# --- Password gate ---
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.title("📊 KPI First")
    st.markdown("Enter the access password to continue.")
    password = st.text_input("Password", type="password")
    if st.button("Enter"):
        if password == APP_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# --- Page config ---
st.set_page_config(page_title="KPI First", page_icon="📊", layout="centered")

if not check_password():
    st.stop()

session_id = get_session_id()
query_count = get_query_count(session_id)
queries_remaining = DAILY_LIMIT - query_count

st.title("📊 KPI First")
st.markdown("Enter an industry to see its key performance indicators and the data required to track them.")
st.caption(f"Queries remaining today: {queries_remaining} / {DAILY_LIMIT}")

# --- Input ---
industry = st.text_input("Industry", placeholder="e.g. E-commerce, Healthcare, SaaS")
analyze = st.button("Analyze KPIs", type="primary", disabled=(queries_remaining <= 0))

if queries_remaining <= 0:
    st.warning("You've reached your daily limit of 10 queries. Come back tomorrow!")

# --- Fetch and store results ---
if analyze and industry.strip():
    with st.spinner(f"Analyzing KPIs for **{industry}**..."):
        try:
            data = get_kpis(industry.strip())
            save_to_supabase(data, session_id)
            increment_query_count(session_id)
            st.session_state["kpi_data"] = data
            st.rerun()
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
        custom_confidence = st.selectbox("Confidence", options=["Medium", "High", "Low"], index=0)
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
            save_custom_kpi_to_supabase(data["industry"], new_kpi, session_id)
            st.session_state["kpi_data"]["kpis"].append(new_kpi)
            st.success(f"'{custom_name.strip()}' added successfully.")
            st.rerun()
