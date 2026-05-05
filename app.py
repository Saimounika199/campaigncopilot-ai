# ==========================================================
# Features:
# 1. Brief Score Dashboard
# 2. Clarifying Questions
# 3. Execution Plan
# 4. QA Risk Check
# ==========================================================

import os
import psycopg2
import re
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
def save_to_db(campaign_name, brief, score, plan):
    conn = psycopg2.connect(
        dbname="campaigncopilot",
        user="saimounika",
        port=5433
    )

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaign_runs (
            id SERIAL PRIMARY KEY,
            campaign_name TEXT,
            brief TEXT,
            score TEXT,
            plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        INSERT INTO campaign_runs
        (campaign_name, brief, score, plan)
        VALUES (%s, %s, %s, %s)
    """, (campaign_name, brief, score, plan))

    conn.commit()
    cur.close()
    conn.close()

# ==========================================================
# ENV
# ==========================================================
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY_LLM"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_LLM"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION_LLM")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_LLM")

# ==========================================================
# PAGE
# ==========================================================
st.set_page_config(
    page_title="CampaignCopilot AI",
    page_icon="🚀",
    layout="wide"
)

# ==========================================================
# CSS
# ==========================================================
st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#0f172a,#111827,#1e293b,#312e81);
color:white;
}

html,body,p,div,span,label,h1,h2,h3{
color:white !important;
}

section[data-testid="stSidebar"]{
background:rgba(17,24,39,.98);
}

section[data-testid="stSidebar"] *{
color:white !important;
}

textarea{
background:#1e293b !important;
color:white !important;
border-radius:14px !important;
}

.stButton > button{
width:100%;
height:50px;
border:none;
border-radius:14px;
font-weight:700;
color:white;
background:linear-gradient(90deg,#2563eb,#7c3aed);
}

.metric-box{
padding:18px;
border-radius:16px;
background:rgba(255,255,255,.08);
text-align:center;
}

.metric-title{
font-size:14px;
color:#cbd5e1 !important;
}

.metric-value{
font-size:28px;
font-weight:800;
}

div[data-testid="stExpander"]{
background:rgba(255,255,255,.04) !important;
border-radius:16px !important;
}

details summary{
background:#1e293b !important;
padding:14px !important;
font-weight:700 !important;
}

details summary *{
color:white !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HELPER
# ==========================================================
def ask_ai(prompt):
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": """
You are a senior marketing operations strategist.

Keep responses:
- concise
- practical
- business-ready
- short bullet points
- no long essays
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=1800
    )
    return response.choices[0].message.content


def get_score(text):
    m = re.search(r"(\\d{2,3})", text)
    if m:
        return int(m.group(1))
    return 75


# ==========================================================
# HEADER
# ==========================================================
st.title("🚀 CampaignCopilot AI")
st.caption("Turn vague campaign briefs into launch-ready plans")

# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.header("📌 Core Features")
st.sidebar.write("""
✅ Brief Health Score  
✅ Missing Questions  
✅ Execution Plan  
✅ Risk QA Check  
""")

# ==========================================================
# SAMPLE BRIEF
# ==========================================================
sample_brief = """
Campaign Name: Q3 Enterprise Trial-to-Paid Push

Business Objective:
Convert 200 enterprise trials to paid contracts before Q3 end.

Target Audience:
Enterprise trial users, decision makers in tech and finance.

Key Message:
Reduce manual reporting delays and act faster.

Channels:
Email, LinkedIn, social, sales outreach

Budget:
Not specified

Timeline:
Launch July 1. Assets ready June 20.

Success Metrics:
Conversion rate from 14% to 22%.

Constraints:
No competitor mentions.
Tone confident not aggressive.
"""

# ==========================================================
# INPUT
# ==========================================================
brief = st.text_area(
    "📝 Paste Campaign Brief",
    value=sample_brief,
    height=360
)

# ==========================================================
# BUTTONS
# ==========================================================
c1, c2, c3 = st.columns(3)

with c1:
    score_btn = st.button("📊 Analyze Brief")

with c2:
    plan_btn = st.button("🚀 Generate Plan")

with c3:
    qa_btn = st.button("✅ QA Check")

# ==========================================================
# ANALYZE
# ==========================================================
if score_btn:

    with st.spinner("Reviewing brief..."):

        prompt = f"""
Review this campaign brief.

{brief}

Return exactly:

Overall Brief Score: X/100

1. What's Good (3 bullets)
2. Missing Items (3 bullets)
3. Clarifying Questions (5 bullets)
4. Main Risks (3 bullets)

Keep short.
"""

        result = ask_ai(prompt)

        score = get_score(result)

        if score >= 80:
            health = "Strong"
        elif score >= 65:
            health = "Moderate"
        else:
            health = "Weak"

        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(f"""
            <div class='metric-box'>
            <div class='metric-title'>BRIEF SCORE</div>
            <div class='metric-value'>{score}/100</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class='metric-box'>
            <div class='metric-title'>HEALTH</div>
            <div class='metric-value'>{health}</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown("""
            <div class='metric-box'>
            <div class='metric-title'>STATUS</div>
            <div class='metric-value'>Needs Review</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📊 Brief Review", expanded=True):
            st.write(result)

# ==========================================================
# PLAN
# ==========================================================
if plan_btn:

    with st.spinner("Generating plan..."):

        prompt = f"""
Create a practical campaign execution plan from this brief.

{brief}

Return exactly:

1. Best Channels
2. Audience Segments
3. 4 Week Timeline
4. Messaging by Channel
5. KPI Metrics
6. Launch Checklist

Use bullets only.
Short output.
"""

        result = ask_ai(prompt)

        st.success("🚀 Plan Ready")

        with st.expander("🚀 Execution Plan", expanded=True):
            st.write(result)

# ==========================================================
# QA
# ==========================================================
if qa_btn:

    with st.spinner("Checking campaign risks..."):

        prompt = f"""
QA review this campaign brief.

{brief}

Return exactly:

Risk Score: X/100

1. Budget Risks
2. Timeline Risks
3. Audience Risks
4. Channel Risks
5. Top 5 Fixes Before Launch

Short bullets only.
"""

        result = ask_ai(prompt)

        st.success("✅ QA Completed")

        with st.expander("✅ QA Risk Report", expanded=True):
            st.write(result)

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption("Hackathon Build • AI for Marketing Operations")
