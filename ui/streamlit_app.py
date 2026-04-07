from app.services.member_service import get_member
from app.services.partner_config import get_partner_config
from app.services.recommendation import generate_recommendations
import streamlit as st

st.set_page_config(page_title="AI Travel Concierge", layout="centered")

st.title("✈️ AI Travel Concierge Demo")

member_id = st.text_input("Enter Member ID", "123")

if st.button("Get Recommendations"):

    with st.spinner("Fetching recommendations..."):

        member = get_member(member_id)
        rules = get_partner_config(member["partner_id"])
        recs = generate_recommendations(member, rules)

    if member and rules and recs:

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

    else:
        st.error("Something went wrong")