import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def app():

    st.title("🏷️ Auction Calendar")

    # -------------------------
    # SEARCH
    # -------------------------
    city = st.text_input("Enter city", "Miami")

    if st.button("Search Auctions"):

        try:
            r = requests.get(f"{API_URL}/auctions/nearby", params={"city": city})
            data = r.json()
        except:
            st.error("Error loading auctions")
            return

        if not data:
            st.warning("No auctions found")
            return

        st.subheader(f"Auctions in {city}")

        for auction in data:

            with st.container():

                col1, col2 = st.columns([3,1])

                with col1:
                    st.markdown(f"### {auction['name']}")
                    st.write(auction["address"])

                    if auction.get("rating"):
                        st.write(f"⭐ Rating: {auction['rating']}")

                with col2:
                    if st.button("View Map", key=auction["name"]):
                        lat = auction["location"]["lat"]
                        lng = auction["location"]["lng"]

                        st.map([{"lat": lat, "lon": lng}])

                st.divider()