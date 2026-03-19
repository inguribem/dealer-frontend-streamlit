import streamlit as st
import requests

API_URL = st.secrets["API_URL"]

def app():

    st.title("🚗 Add Vehicle")

    vin = st.text_input("VIN")

    if "vehicle_data" not in st.session_state:
        st.session_state["vehicle_data"] = {}

    # -------------------------
    # VIN LOOKUP
    # -------------------------

    if st.button("Decode VIN") and vin:

        r = requests.get(f"{API_URL}/vehicles/vin/{vin}")

        if r.status_code == 200:
            st.session_state["vehicle_data"] = r.json()
        else:
            st.error("VIN lookup failed")

    data = st.session_state["vehicle_data"]

    # -------------------------
    # FORM
    # -------------------------

    year = st.text_input("Year", data.get("year", ""))
    make = st.text_input("Make", data.get("make", ""))
    model = st.text_input("Model", data.get("model", ""))
    trim = st.text_input("Trim", data.get("trim", ""))

    price = st.text_input("Price")
    miles = st.text_input("Miles")

    # -------------------------
    # SAVE
    # -------------------------

    if st.button("Save Vehicle"):

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
            st.session_state["vehicle_data"] = {}
        else:
            st.error(f"Error: {r.text}")
