import streamlit as st
import requests

API_URL = st.secrets["API_URL"]

def app():

    st.title("🚗 Add Vehicle")

    vin = st.text_input("VIN")

    # -------------------------
    # SESSION STATE
    # -------------------------

    if "vin_raw" not in st.session_state:
        st.session_state["vin_raw"] = {}

    if "vin_summary" not in st.session_state:
        st.session_state["vin_summary"] = {}

    # -------------------------
    # HELPER: SAVE VEHICLE
    # -------------------------

    def save_vehicle(year, make, model, trim, price, miles):

        payload = {
            "vin": vin,
            "year": int(year) if year else None,
            "make": make,
            "model": model,
            "trim": trim,
            "price": float(price) if price else None,
            "miles": int(miles) if miles else None,
            "dealer_name": "",
            "city": "",
            "state": ""
        }

        r = requests.post(f"{API_URL}/vehicles", json=payload)

        if r.status_code == 200:
            st.success("Vehicle saved")
        else:
            st.error(f"Error: {r.text}")

    # -------------------------
    # TABS
    # -------------------------

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 VIN Decode",
        "📊 Vehicle Data",
        "🏭 Manufacturer Info",
        "🧾 Raw Data"
    ])

    # =========================
    # TAB 1: VIN DECODE
    # =========================

    with tab1:

        if st.button("Decode VIN") and vin:

            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

            r = requests.get(url)
            data = r.json()

            resultados = {
                item['Variable']: item['Value']
                for item in data['Results']
                if item['Value']
            }

            st.session_state["vin_raw"] = resultados

            resumen = {
                "year": resultados.get("Model Year"),
                "make": resultados.get("Make"),
                "model": resultados.get("Model"),
                "trim": resultados.get("Trim"),
                "vehicle_type": resultados.get("Vehicle Type"),
                "body_class": resultados.get("Body Class"),
                "engine": resultados.get("Engine Model"),
                "fuel": resultados.get("Fuel Type - Primary"),
                "transmission": resultados.get("Transmission Style"),
                "manufacturer": resultados.get("Manufacturer Name"),
                "plant_city": resultados.get("Plant City"),
                "plant_country": resultados.get("Plant Country"),
                "plant_company": resultados.get("Plant Company Name"),
            }

            st.session_state["vin_summary"] = resumen

        s = st.session_state.get("vin_summary", {})

        if s:

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Make", s.get("make"))
                st.metric("Model", s.get("model"))
                st.metric("Year", s.get("year"))

            with col2:
                st.metric("Body", s.get("body_class"))
                st.metric("Fuel", s.get("fuel"))
                st.metric("Transmission", s.get("transmission"))

        # Save button aquí también
        if st.button("💾 Save Vehicle (Quick)"):

            save_vehicle(
                s.get("year"),
                s.get("make"),
                s.get("model"),
                s.get("trim"),
                None,
                None
            )

    # =========================
    # TAB 2: VEHICLE DATA
    # =========================

    with tab2:

        s = st.session_state.get("vin_summary", {})

        year = st.text_input("Year", s.get("year", ""))
        make = st.text_input("Make", s.get("make", ""))
        model = st.text_input("Model", s.get("model", ""))
        trim = st.text_input("Trim", s.get("trim", ""))

        price = st.text_input("Price")
        miles = st.text_input("Miles")

        if st.button("💾 Save Vehicle"):

            save_vehicle(year, make, model, trim, price, miles)

    # =========================
    # TAB 3: MANUFACTURER
    # =========================

    with tab3:

        s = st.session_state.get("vin_summary", {})

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Manufacturer**")
            st.write(s.get("manufacturer"))

            st.write("**Plant Company**")
            st.write(s.get("plant_company"))

        with col2:
            st.write("**Plant City**")
            st.write(s.get("plant_city"))

            st.write("**Plant Country**")
            st.write(s.get("plant_country"))

        if st.button("💾 Save Vehicle (From Manufacturer Tab)"):

            save_vehicle(
                s.get("year"),
                s.get("make"),
                s.get("model"),
                s.get("trim"),
                None,
                None
            )

    # =========================
    # TAB 4: RAW DATA
    # =========================

    with tab4:

        st.subheader("Raw VIN Data")

        st.json(st.session_state.get("vin_raw", {}))

        s = st.session_state.get("vin_summary", {})

        if st.button("💾 Save Vehicle (Raw)"):

            save_vehicle(
                s.get("year"),
                s.get("make"),
                s.get("model"),
                s.get("trim"),
                None,
                None
            )

