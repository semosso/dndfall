import streamlit as st
import requests
import os

# Ensure these are in your Streamlit Secrets (Settings > Secrets)
GA_ID = os.environ.get("GA_MEASUREMENT_ID")
API_SECRET = os.environ.get("GA_API_SECRET")


def track_search(query):
    """Sends search event directly from Python to Google"""
    if not (GA_ID and API_SECRET and query):
        return

    client_id = st.session_state.get("client_id", "anonymous")
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_ID}&api_secret={API_SECRET}"

    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "search",
                "params": {"search_term": query, "engagement_time_msec": "100"},
            }
        ],
    }

    try:
        # Use json= instead of data= for correct header formatting
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        print(f"GA Tracking Error: {e}")
