import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.member_service import get_member
from app.services.partner_config import get_partner_config
from app.services.recommendation import generate_recommendations
import streamlit as st
import uuid

st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/styles.css")

if "show_recs" not in st.session_state:
    st.session_state.show_recs = False
if "data" not in st.session_state:
    st.session_state.data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

st.markdown("""
<div class="concierge-header">
    <h1>✈️ AI Travel Concierge</h1>
    <p>Loyalty-Driven Personalization · MCP-Powered · Partner-Aware</p>
    <div class="gold-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    member_id = st.text_input("Member ID", value="123", placeholder="Try 123, 456, or 789")
    fetch_btn = st.button("Get Recommendations", use_container_width=True)
 
    st.markdown("""
    <div class="info-tip">
        <strong>Demo IDs:</strong><br>
        123 → Gold · Horizon Travel<br>
        456 → Platinum · Elite Voyages<br>
        789 → Silver · BudgetWings
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if fetch_btn:
        with st.spinner("Fetching recommendations…"):
            member = get_member(member_id)
            rules = get_partner_config(member["partner_id"])
            recs = generate_recommendations(member, rules)
            st.session_state.data = {"member": member, "rules": rules, "recs": recs}
            st.session_state.show_recs = True
 
    if st.session_state.data:
        toggle_lbl = "❌ Hide" if st.session_state.show_recs else "✅ Show"
        if st.button(f"{toggle_lbl} Results"):
            st.session_state.show_recs = not st.session_state.show_recs

if st.session_state.show_recs and st.session_state.data:
    d = st.session_state.data
    m, rules, recs = d["member"], d["rules"], d["recs"]
 
    tier = m.get("loyalty_tier", "Silver")
    tier_html = f'<span class="tier-badge tier-{tier}">{tier}</span>'
 
    left, mid, right = st.columns(3)
 
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**👤 Member Profile**")
        st.markdown(f"""
        <div class="kv-row"><span class="kv-key">Name</span><span class="kv-val">{m.get('name','—')}</span></div>
        <div class="kv-row"><span class="kv-key">ID</span><span class="kv-val">{m.get('member_id','—')}</span></div>
        <div class="kv-row"><span class="kv-key">Tier</span><span class="kv-val">{tier_html}</span></div>
        <div class="kv-row"><span class="kv-key">Partner</span><span class="kv-val">{m.get('partner_id','—')}</span></div>
        """, unsafe_allow_html=True)
        st.markdown("<br>**Recent Trips**", unsafe_allow_html=True)
        for h in m.get("travel_history", [])[:3]:
            st.markdown(f'<div class="kv-row"><span class="kv-key">🗺 {h["destination"]}</span><span class="kv-val">{h["booking_type"]}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
 
    with mid:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**⚙️ Partner Rules**")
        cap = rules.get("max_recommendations")
        cap_str = str(cap) if cap else "Unlimited"
        excl = ", ".join(rules.get("exclude_types", [])) or "None"
        cruise = "✅ Yes" if rules.get("allow_cruise_offers") else "🚫 No"
        st.markdown(f"""
        <div class="kv-row"><span class="kv-key">Partner</span><span class="kv-val">{rules.get('partner_name','—')}</span></div>
        <div class="kv-row"><span class="kv-key">Rec Cap</span><span class="kv-val">{cap_str}</span></div>
        <div class="kv-row"><span class="kv-key">Excluded Types</span><span class="kv-val">{excl}</span></div>
        <div class="kv-row"><span class="kv-key">Cruise Offers</span><span class="kv-val">{cruise}</span></div>
        <div class="kv-row"><span class="kv-key">Commission Tier</span><span class="kv-val">{rules.get('commission_tier','—').title()}</span></div>
        """, unsafe_allow_html=True)
        st.markdown(f'<br><div style="color:#7a95b0;font-size:0.8rem;font-style:italic;">{rules.get("notes","")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
 
    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"**🌍 Recommendations** ({len(recs)} results)")
        for rec in recs:
            score_color = "#4caf50" if rec["score"] >= 93 else "#c8a55f" if rec["score"] >= 88 else "#7a95b0"
            st.markdown(f"""
            <div class="rec-card">
                <span class="rec-score" style="color:{score_color}">{rec['score']}</span>
                <div class="rec-dest">{rec['destination']}</div>
                <div class="rec-meta">{rec['type'].title()} · {', '.join(rec.get('tags',[])[: 2])}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
 

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
 
# ─── Chat Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="chat-label">🤖 Concierge Chat</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-sublabel">Ask me anything about members, partner rules, or travel recommendations. I\'ll call the right tools automatically.</div>', unsafe_allow_html=True)

api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    st.warning("⚠️ Set the `GROQ_API_KEY` environment variable to enable the AI chat agent.")
else:
    # Lazy-load agent on first use
    if not st.session_state.agent_ready:
        try:
            from app.agent import get_graph
            get_graph()  # pre-warm
            st.session_state.agent_ready = True
        except Exception as e:
            st.error(f"Agent initialization failed: {e}")
 
    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center;padding:2rem;color:#4a6070;font-size:0.88rem;">
                💬 Start a conversation — try:<br><br>
                <em>"What's member 123's loyalty tier?"</em><br>
                <em>"Show me recommendations for member 456"</em><br>
                <em>"What are the rules for partner_beta?"</em>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="tag-user chat-label-tag">You</div>
                    <div class="chat-bubble-user">{msg['content']}</div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="tag-ai chat-label-tag">✈️ Concierge</div>
                    <div class="chat-bubble-ai">{msg['content'].replace(chr(10), '<br>')}</div>
                    """, unsafe_allow_html=True)
 
    # Input row
    inp_col, btn_col = st.columns([5, 1])
    with inp_col:
        user_input = st.text_input(
            "Message",
            key="chat_input",
            placeholder="e.g. Get recommendations for member 789",
            label_visibility="collapsed",
        )
    with btn_col:
        send_btn = st.button("Send", use_container_width=True)
 
    if send_btn and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
 
        with st.spinner("Thinking…"):
            try:
                from app.agent import run_agent
                response = run_agent(user_input.strip(), thread_id=st.session_state.thread_id)
                st.session_state.chat_history.append({"role": "ai", "content": response})
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"⚠️ Agent error: {str(e)}"
                })
 
        st.rerun()
 
    # Clear chat
    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()
 
