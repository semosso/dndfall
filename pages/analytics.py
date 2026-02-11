import streamlit.components.v1 as components
import os

GA_ID = os.environ.get("GA_MEASUREMENT_ID")


def init_analytics():
    """Initialize Google Analytics on page load"""
    if GA_ID:
        components.html(
            f"""
            <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){{dataLayer.push(arguments);}}
                gtag('js', new Date());
                gtag('config', '{GA_ID}', {{
                    'anonymize_ip': true,
                    'cookie_flags': 'SameSite=None;Secure'
                }});
            </script>
        """,
            height=0,
        )


def track_search(query):
    """Track search query event"""
    if GA_ID:
        escaped_query = query.replace("'", "\\'")
        components.html(
            f"""
            <script>
                gtag('event', 'search', {{
                    'search_term': '{escaped_query}'
                }});
            </script>
        """,
            height=0,
        )
