import streamlit as st
from ui.layout import page_header

def app():

    page_header("Dealer Profit Estimator")

    auction_price = st.number_input("Auction Price")

    transport = st.number_input("Transport Cost")

    recon = st.number_input("Reconditioning")

    retail = st.number_input("Retail Market Price")

    profit = retail - (auction_price + transport + recon)

    st.metric("Estimated Profit", f"${profit:,.0f}")

