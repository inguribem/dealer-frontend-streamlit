import streamlit as st
import requests
import pandas as pd
from ui.layout import page_header

def app():

    page_header("Vehicle Listings")

    api_key = st.secrets.get("MARKETCHECK_API_KEY")

    make = st.text_input("Make")
    model = st.text_input("Model")

    if st.button("Search Listings"):

        url = "https://api.marketcheck.com/v2/search/car/active"

        params = {
            "api_key": api_key,
            "make": make,
            "model": model
        }

        with st.spinner("Searching listings..."):

            response = requests.get(url, params=params)
            data = response.json()

        listings = data.get("listings", [])

        if listings:

            df = pd.DataFrame(listings)

            st.dataframe(df, use_container_width=True)

        else:

            st.info("No listings found")
