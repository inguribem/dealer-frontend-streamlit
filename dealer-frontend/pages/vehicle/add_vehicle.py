import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():

    st.title("🚗 VIN Intelligence")

    vin = st.text_input("Enter VIN", max_chars=17)

    vehicle_data = {}

    # -------------------------
    # VIN LOOKUP
    # -------------------------

    if st.button("Decode VIN"):

        if vin:

            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

            r = requests.get(url)
            data = r.json()

            results = data.get("Results", [])

            vehicle_data = {
                item["Variable"]: item["Value"]
                for item in results
                if item["Value"]
            }

            st.session_state["vehicle_data"] = vehicle_data

    if "vehicle_data" in st.session_state:
        vehicle_data = st.session_state["vehicle_data"]

    # -------------------------
    # TABS
    # -------------------------

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Vehicle Overview",
        "Manufacturer Info",
        "Engine & Powertrain",
        "Safety Systems",
        "Raw VIN Data"
    ])

    # -------------------------
    # TAB 1 VEHICLE OVERVIEW
    # -------------------------

    with tab1:

        col1, col2 = st.columns(2)

        with col1:

            year = st.text_input(
                "Year",
                vehicle_data.get("Model Year", "")
            )

            make = st.text_input(
                "Make",
                vehicle_data.get("Make", "")
            )

            model = st.text_input(
                "Model",
                vehicle_data.get("Model", "")
            )

            trim = st.text_input(
                "Trim",
                vehicle_data.get("Trim", "")
            )

        with col2:

            body_class = vehicle_data.get("Body Class", "")
            vehicle_type = vehicle_data.get("Vehicle Type", "")

            st.metric("Vehicle Type", vehicle_type)
            st.metric("Body Class", body_class)

        st.divider()

        price = st.text_input("Price")
        miles = st.text_input("Miles")

        dealer_name = st.text_input("Dealer Name")
        city = st.text_input("City")
        state = st.text_input("State")

        if st.button("Save Vehicle"):

            payload = {
                "vin": vin,
                "year": year,
                "make": make,
                "model": model,
                "trim": trim,
                "price": price if price else None,
                "miles": miles if miles else None,
                "dealer_name": dealer_name,
                "city": city,
                "state": state
            }

            r = requests.post(f"{API_URL}/vehicles/", json=payload)

            if r.status_code == 200:
                st.success("Vehicle saved in inventory")
            else:
                st.error(r.text)

    # -------------------------
    # TAB 2 MANUFACTURER
    # -------------------------

    with tab2:

        manufacturer_name = vehicle_data.get("Manufacturer Name", "")
        plant_city = vehicle_data.get("Plant City", "")
        plant_country = vehicle_data.get("Plant Country", "")
        plant_company = vehicle_data.get("Plant Company Name", "")

        col1, col2 = st.columns(2)

        with col1:

            st.metric("Manufacturer", manufacturer_name)
            st.metric("Plant City", plant_city)

        with col2:

            st.metric("Plant Country", plant_country)
            st.metric("Plant Company", plant_company)

    # -------------------------
    # TAB 3 ENGINE
    # -------------------------

    with tab3:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Engine Cylinders",
                vehicle_data.get("Engine Cylinders", "")
            )

            st.metric(
                "Displacement (L)",
                vehicle_data.get("Displacement (L)", "")
            )

        with col2:

            st.metric(
                "Fuel Type",
                vehicle_data.get("Fuel Type - Primary", "")
            )

            st.metric(
                "Transmission",
                vehicle_data.get("Transmission Style", "")
            )

    # -------------------------
    # TAB 4 SAFETY
    # -------------------------

    with tab4:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "ABS",
                vehicle_data.get("Anti-lock Braking System (ABS)", "")
            )

            st.metric(
                "Traction Control",
                vehicle_data.get("Traction Control", "")
            )

        with col2:

            st.metric(
                "ESC",
                vehicle_data.get("Electronic Stability Control (ESC)", "")
            )

            st.metric(
                "Airbag Locations",
                vehicle_data.get("Air Bag Loc Front", "")
            )

    # -------------------------
    # TAB 5 RAW DATA
    # -------------------------

    with tab5:

        st.subheader("Raw NHTSA VIN Data")

        st.json(vehicle_data)