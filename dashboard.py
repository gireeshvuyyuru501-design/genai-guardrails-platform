import pandas as pd
import streamlit as st

from app.core.config import get_settings
from app.services.audit import read_events, summarize_events


settings = get_settings()

st.set_page_config(
    page_title="GenAI Guardrails Dashboard",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ GenAI Guardrails Dashboard")
st.caption(
    "Local safety metrics for blocked requests, redactions, rewrites, and latency."
)

events = read_events(settings.audit_file)
stats = summarize_events(events)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total requests", stats.total_requests)
c2.metric("Allowed", stats.allowed)
c3.metric("Blocked", stats.blocked)
c4.metric("Rewritten", stats.rewritten)

c5, c6, c7, c8 = st.columns(4)
c5.metric("PII events", stats.pii_events)
c6.metric("Injection events", stats.injection_events)
c7.metric("Secret events", stats.secret_events)
c8.metric("Average latency", f"{stats.average_latency_ms:.2f} ms")

if events:
    df = pd.DataFrame(events)

    st.subheader("Request outcomes")
    st.bar_chart(df["status"].value_counts())

    st.subheader("Recent audit events")
    columns = [
        column
        for column in [
            "timestamp",
            "request_id",
            "session_id",
            "user_id",
            "status",
            "provider",
            "model",
            "latency_ms",
            "pii_detected",
            "injection_detected",
            "secret_detected",
        ]
        if column in df.columns
    ]
    st.dataframe(
        df[columns].sort_values("timestamp", ascending=False),
        use_container_width=True,
    )
else:
    st.warning("No audit events yet. Call POST /chat or POST /evaluate first.")
