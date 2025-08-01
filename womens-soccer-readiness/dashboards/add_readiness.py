import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/")

st.title("Add Readiness Entry")

player_id = st.number_input("Player ID", min_value=1, step=1)
fatigue = st.slider("Fatigue (1-10)", 1, 10, 5)
sleep_hours = st.number_input("Sleep Hours", min_value=0.0, max_value=12.0, step=0.5)

if st.button("Submit Readiness"):
    response = requests.post(API_URL + "readiness/", json={
        "player_id": player_id,
        "fatigue": fatigue,
        "sleep_hours": sleep_hours
    })
    if response.status_code == 200:
        st.success("Readiness entry added!")
    else:
        st.error("Error: " + response.text)
