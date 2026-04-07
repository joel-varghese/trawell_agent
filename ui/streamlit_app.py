import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.member_service import get_member
from app.services.partner_config import get_partner_config
from app.services.recommendation import generate_recommendations
import streamlit as st

st.set_page_config(page_title="AI Travel Concierge", layout="centered")

st.title("✈️ AI Travel Concierge Demo")

if "show_recs" not in st.session_state:
    st.session_state.show_recs = False
if "data" not in st.session_state:
    st.session_state.data = None

member_id = st.text_input("Enter Member ID", "123")

if st.button("Get Recommendations"):

    with st.spinner("Fetching recommendations..."):

        member = get_member(member_id)
        rules = get_partner_config(member["partner_id"])
        recs = generate_recommendations(member, rules)

        st.session_state.data = {
            "member": member,
            "rules": rules,
            "recs": recs
        }

        st.session_state.show_recs = True

if st.session_state.data:
    toggle_label = "❌ Hide Recommendations" if st.session_state.show_recs else "✅ Show Recommendations"

    if st.button(toggle_label):
        st.session_state.show_recs = not st.session_state.show_recs

if st.session_state.show_recs and st.session_state.data:

    member = get_member(member_id)
    rules = get_partner_config(member["partner_id"])
    recs = generate_recommendations(member, rules)


    st.subheader("👤 Member Info")
    st.json(member)

    st.subheader("⚙️ Applied Rules")
    st.json(rules)

    st.subheader("🌍 Recommendations")

    for rec in recs:
        with st.container():
            st.markdown(f"### {rec['destination']}")
            st.write(f"Type: {rec['type']}")
            st.write(f"Score: {rec['score']}")
            st.divider()
