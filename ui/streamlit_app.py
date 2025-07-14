import json

import requests
import streamlit as st

st.title("Crew Scheduler App")
mode = st.sidebar.selectbox("Select Role", ["Admin", "Crew"])

API = st.sidebar.text_input("API Endpoint", value="http://localhost:8000")
API_KEY = st.sidebar.text_input("API Key", type="password", value="secret123")

HEADERS = {"x-api-key": API_KEY}

if mode == "Admin":
    st.header("Add Crew Member")
    name = st.text_input("Crew Name")
    prefs_input = st.text_area("Preferences (JSON or natural language)")

    if st.button("Submit Crew"):
        try:
            prefs = json.loads(prefs_input)
        except json.JSONDecodeError:
            prefs = prefs_input  # Send raw string

        payload = {"name": name, "preferences": prefs}
        response = requests.post(f"{API}/admin/crew", headers=HEADERS, json=payload)
        if response.status_code == 200:
            st.success("Crew member added.")
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

    st.header("Add Scheduling Rule")
    rule_text = st.text_area("Rule in Natural Language")

    if st.button("Add Rule"):
        response = requests.post(f"{API}/admin/rule", headers=HEADERS, json={"rule_text": rule_text})
        if response.status_code == 200:
            st.success("Rule added.")
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

    if st.button("Generate Schedule"):
        response = requests.get(f"{API}/schedule", headers=HEADERS)
        if response.status_code == 200:
            sched = response.json()
            st.subheader("Generated Schedule")
            st.json(sched)
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

else:
    st.header("Crew Portal")
    cid = st.number_input("Enter Crew ID", min_value=1, step=1)

    if st.button("View My Schedule"):
        response = requests.get(f"{API}/schedule", headers=HEADERS)
        if response.status_code == 200:
            sched = response.json()
            user_sched = sched.get("assignments", {}).get(str(cid))
            if user_sched:
                st.write(f"Hello {user_sched.get('name')}, your assigned shift is:")
                st.success(user_sched.get("shift"))
            else:
                st.warning("No schedule found for this Crew ID.")
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

    fb_input = st.text_area("Feedback (JSON or natural language)")

    if st.button("Submit Feedback"):
        try:
            fb = json.loads(fb_input)
        except json.JSONDecodeError:
            fb = fb_input  # send as plain string

        payload = {"crew_id": int(cid), "feedback": fb}
        response = requests.post(f"{API}/feedback", headers=HEADERS, json=payload)
        if response.status_code == 200:
            st.success("Feedback submitted.")
            st.json(response.json())
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
