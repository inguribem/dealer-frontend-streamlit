import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")


def app():

    st.title("🏷️ Auction Calendar")

    # =========================
    # SEARCH
    # =========================
    city = st.text_input("Enter city", "Orlando")

    if st.button("Search Auctions"):

        try:
            r = requests.get(
                f"{API_URL}/auctions/nearby",
                params={"city": city}
            )
        except:
            st.error("❌ Cannot connect to backend")
            return

        # =========================
        # PARSE RESPONSE
        # =========================
        try:
            data = r.json()
        except:
            st.error("❌ Invalid response from server")
            return

        # =========================
        # VALIDATION (CRITICAL FIX)
        # =========================
        if not isinstance(data, list):
            st.error("❌ Error loading auctions")
            st.write("Response:", data)
            return

        if len(data) == 0:
            st.warning("No auctions found")
            return

        # =========================
        # DISPLAY RESULTS
        # =========================
        st.subheader(f"Auctions in {city}")

        map_data = []

        for auction in data:

            # SAFE ACCESS
            name = auction.get("name", "Unknown")
            address = auction.get("address", "No address")
            rating = auction.get("rating")
            location = auction.get("location", {})

            lat = location.get("lat")
            lng = location.get("lng")

            with st.container():

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {name}")
                    st.write(address)

                    if rating:
                        st.write(f"⭐ Rating: {rating}")

                with col2:
                    if lat and lng:
                        if st.button("View Map", key=f"map_{name}"):
                            st.map(pd.DataFrame([{
                                "lat": lat,
                                "lon": lng
                            }]))

                st.divider()

            # Collect for global map
            if lat and lng:
                map_data.append({"lat": lat, "lon": lng})

        # =========================
        # GLOBAL MAP
        # =========================
        if map_data:
            st.subheader("🗺 All Auctions Map")
            st.map(pd.DataFrame(map_data))