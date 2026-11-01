"""Streamlit shell for the targeting dashboard.

ISSUE-05: wire the uplift deciles, the budget curve and the profit waterfall.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rasoi offer targeting", layout="wide")
st.title("Rasoi Express - offer targeting")
st.caption("Uplift deciles, budget allocation and the incremental-profit waterfall")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Incremental orders by decile")
    placeholder = pd.DataFrame({"decile": range(1, 11), "lift": [0.0] * 10}).set_index("decile")
    st.bar_chart(placeholder, height=280)
    st.info("ISSUE-05: plot the true/predicted lift deciles from the trial.")

with col2:
    st.subheader("Discount budget curve")
    st.line_chart(placeholder, height=280)
    st.info("ISSUE-05: plot incremental profit against spend and mark the budget.")

st.subheader("Profit waterfall")
st.empty()
st.caption("ISSUE-05: show blanket 20% vs targeted plan vs no-offer.")
