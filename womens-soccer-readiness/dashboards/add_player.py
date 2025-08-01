import streamlit as st
import requests
import os

# Use environment variable if set, fallback to local dev
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/players/")

st.title("Add a Player")

name = st.text_input("Name")
position = st.text_input("Position")

if st.button("Add Player"):
    if name and position:
        response = requests.post(
            API_URL,
            json={"name": name, "position": position}
        )
        if response.status_code == 200:
            st.success(f"Player {response.json()['name']} added!")
        else:
            st.error(f"Error: {response.text}")
    else:
        st.warning("Please fill out all fields.")
