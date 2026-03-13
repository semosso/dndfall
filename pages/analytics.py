import streamlit as st
import requests
import os
import time
import uuid
from typing import Optional, Dict, Any

# Ensure these are in your Streamlit Secrets (Settings > Secrets)
GA_ID = os.environ.get("GA_MEASUREMENT_ID")
API_SECRET = os.environ.get("GA_API_SECRET")


def initialize_tracking():
    """
    Initialize session tracking variables.
    Call this ONCE at the very start of your main app file.
    """
    # Unique identifier for this user across sessions
    if "client_id" not in st.session_state:
        st.session_state.client_id = str(uuid.uuid4())

    # Unique identifier for this specific session/visit
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Track current page and timing
    if "current_page" not in st.session_state:
        st.session_state.current_page = None

    if "previous_page" not in st.session_state:
        st.session_state.previous_page = None

    if "page_start_time" not in st.session_state:
        st.session_state.page_start_time = time.time()


def _send_ga4_event(event_name: str, params: Dict[str, Any]):
    """
    Internal helper to send events to Google Analytics 4.

    Args:
        event_name: GA4 event name
        params: Dictionary of event parameters
    """
    if not (GA_ID and API_SECRET):
        return

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_ID}&api_secret={API_SECRET}"

    payload = {
        "client_id": st.session_state.get("client_id", "anonymous"),
        "events": [
            {
                "name": event_name,
                "params": {
                    "session_id": st.session_state.get("session_id", "unknown"),
                    **params,
                },
            }
        ],
    }

    try:
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        print(f"GA Tracking Error: {e}")


def track_search(
    query: str,
    result_count: Optional[int] = None,
):
    """
    Track search queries with additional context.

    Args:
        query: The search query string
        result_count: Number of results returned (optional)
        filters_applied: Dictionary of active filters (optional)

    Example:
        track_search("fireball", result_count=15, filters_applied={"spell_level": 3})
    """
    if not query:
        return

    params = {
        "search_term": query,
        "engagement_time_msec": "100",
    }

    if result_count is not None:
        params["result_count"] = result_count

    _send_ga4_event("search", params)


def track_result_click(
    item_type: str, item_name: str, search_query: Optional[str] = None
):
    """
    Track when user clicks on a search result.

    Args:
        item_type: Type of content (e.g., "spell", "monster", "item")
        item_name: Name of the clicked item (e.g., "Fireball", "Ancient Red Dragon")
        search_query: The search query that led to this result (optional)

    Example:
        track_result_click("spell", "Fireball", search_query="fire damage")
    """
    params = {
        "content_type": item_type,
        "item_id": item_name,
    }

    if search_query:
        params["search_term"] = search_query

    _send_ga4_event("select_content", params)


def track_feature_usage(feature_name: str, feature_value: Optional[str] = None):
    """
    Track usage of specific features on your site.

    Args:
        feature_name: Name of the feature (e.g., "advanced_search", "export_results", "save_favorite")
        feature_value: Optional value/context for the feature

    Example:
        track_feature_usage("export_results", "csv")
        track_feature_usage("syntax_help_clicked")
    """
    params = {
        "feature_name": feature_name,
    }

    if feature_value:
        params["feature_value"] = feature_value

    _send_ga4_event("feature_used", params)


def track_error(error_type: str, error_message: str, page: Optional[str] = None):
    """
    Track errors users encounter.

    Args:
        error_type: Type of error (e.g., "search_error", "api_error", "validation_error")
        error_message: Error message or description
        page: Page where error occurred (optional)

    Example:
        track_error("search_error", "No results found for query", page="Search")
    """
    params = {
        "error_type": error_type,
        "error_message": error_message[:100],  # Limit length
    }

    if page:
        params["page_title"] = page

    _send_ga4_event("error", params)


def track_user_engagement(engagement_type: str, value: Optional[Any] = None):
    """
    Track general user engagement events.

    Args:
        engagement_type: Type of engagement (e.g., "scroll_depth", "time_threshold", "interaction")
        value: Optional value associated with engagement

    Example:
        track_user_engagement("scroll_depth", 75)  # Scrolled 75%
        track_user_engagement("time_threshold", "5min")  # Spent 5+ minutes
    """
    time_on_page_ms = int(
        (time.time() - st.session_state.get("page_start_time", time.time())) * 1000
    )

    params = {
        "engagement_type": engagement_type,
        "engagement_time_msec": str(time_on_page_ms),
    }

    if value is not None:
        params["engagement_value"] = str(value)

    _send_ga4_event("user_engagement", params)


def track_custom_event(event_name: str, params: Dict[str, Any]):
    """
    Track any custom event with custom parameters.

    Args:
        event_name: Name of your custom event
        params: Dictionary of event parameters

    Example:
        track_custom_event("spell_favorited", {"spell_name": "Fireball", "spell_level": 3})
    """
    _send_ga4_event(event_name, params)


# def track_search(query):
#     """Sends search event directly from Python to Google"""
#     if not (GA_ID and API_SECRET and query):
#         return

#     client_id = st.session_state.get("client_id", "anonymous")
#     url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_ID}&api_secret={API_SECRET}"

#     payload = {
#         "client_id": client_id,
#         "events": [
#             {
#                 "name": "search",
#                 "params": {"search_term": query, "engagement_time_msec": "100"},
#             }
#         ],
#     }

#     try:
#         # Use json= instead of data= for correct header formatting
#         requests.post(url, json=payload, timeout=2)
#     except Exception as e:
#         print(f"GA Tracking Error: {e}")
