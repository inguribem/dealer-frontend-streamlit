import streamlit as st
from ui.layout import page_header, metric_cards

def app():

    page_header(
        "🚗 Auto Market Intelligence",
        "Vehicle market analytics platform"
    )

    metric_cards([
        {"label": "Vehicles Analyzed", "value": "842"},
        {"label": "Active Auctions", "value": "318"},
        {"label": "Average Market Price", "value": "$18,420"},
        {"label": "Dealer Margin", "value": "23%"}
    ])

    st.divider()

    st.subheader("Platform Overview")

    st.write(
        "Use the navigation panel to explore market data, auctions and dealer tools."
    )
