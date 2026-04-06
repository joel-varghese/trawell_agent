import streamlit as st
import requests

API_URL = "http://localhost:8000/tools/call"

st.set_page_config(page_title="AI Travel Concierge", layout="centered")

st.title("✈️ AI Travel Concierge Demo")

member_id = st.text_input("Enter Member ID", "123")

if st.button("Get Recommendations"):

    payload = {
        "name": "get_travel_recommendations",
        "arguments": {"member_id": member_id}
    }

    with st.spinner("Fetching recommendations..."):
        res = requests.post(API_URL, json=payload)

    if res.status_code == 200:
        data = res.json()

        st.subheader("👤 Member Info")
        st.json(data["member"])

        st.subheader("⚙️ Applied Rules")
        st.json(data["rules"])

        st.subheader("🌍 Recommendations")

        for rec in data["recommendations"]:
            st.card = st.container()
            with st.card:
                st.markdown(f"### {rec['destination']}")
                st.write(f"Type: {rec['type']}")
                st.write(f"Score: {rec['score']}")

    else:
        st.error("Something went wrong")