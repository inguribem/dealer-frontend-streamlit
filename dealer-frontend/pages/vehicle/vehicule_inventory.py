import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets["API_URL"]

def app():

    st.title("🚗 Vehicle Inventory")

    r = requests.get(f"{API_URL}/vehicles/inventory")
    vehicles = r.json()

    if not vehicles:
        st.warning("No vehicles found")
        return

    st.subheader("Inventory")

    # HEADER
    header = st.columns([3,1,1,2,2,2,2])

    header[0].markdown("**VIN**")
    header[1].markdown("**Year**")
    header[2].markdown("**Make**")
    header[3].markdown("**Model**")
    header[4].markdown("**Price**")
    header[5].markdown("**Miles**")
    header[6].markdown("**Actions**")

    st.divider()

    # ROWS
    for v in vehicles:

        col1, col2, col3, col4, col5, col6, col7 = st.columns([3,1,1,2,2,2,2])

        col1.write(v["vin"])
        col2.write(v["year"])
        col3.write(v["make"])
        col4.write(v["model"])
        col5.write(v["price"])
        col6.write(v["miles"])

        a1, a2 = col7.columns(2)

        # EDIT
        if a1.button("✏️", key=f"edit_{v['vin']}", help="Edit"):
            st.session_state["edit_vehicle"] = v

        # DELETE
        if a2.button("🗑", key=f"delete_{v['vin']}", help="Delete"):
            st.session_state["delete_vehicle"] = v["vin"]

    # -------------------------
    # DELETE CONFIRMATION
    # -------------------------

    if "delete_vehicle" in st.session_state:

        vin = st.session_state["delete_vehicle"]

        st.warning(f"Delete vehicle {vin}?")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Confirm Delete"):
                requests.delete(f"{API_URL}/vehicles/{vin}")
                del st.session_state["delete_vehicle"]
                st.success("Deleted")
                st.rerun()

        with c2:
            if st.button("Cancel"):
                del st.session_state["delete_vehicle"]
                st.rerun()

    # -------------------------
    # EDIT FORM
    # -------------------------

    if "edit_vehicle" in st.session_state:

        v = st.session_state["edit_vehicle"]

        st.divider()
        st.subheader(f"Edit {v['vin']}")

        col1, col2 = st.columns(2)

        with col1:
            year = st.text_input("Year", v["year"])
            make = st.text_input("Make", v["make"])
            model = st.text_input("Model", v["model"])

        with col2:
            price = st.text_input("Price", v["price"])
            miles = st.text_input("Miles", v["miles"])

        if st.button("Update"):

            payload = {
                "vin": v["vin"],
                "year": int(year) if year else None,
                "make": make,
                "model": model,
                "trim": v.get("trim",""),
                "price": float(price) if price else None,
                "miles": int(miles) if miles else None,
                "dealer_name": "",
                "city": "",
                "state": ""
            }

            requests.put(
                f"{API_URL}/vehicles/{v['vin']}",
                json=payload
            )

            del st.session_state["edit_vehicle"]

            st.success("Updated")

            st.rerun()
