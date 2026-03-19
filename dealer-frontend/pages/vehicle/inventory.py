import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():

    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # GET INVENTORY
    # -------------------------

    r = requests.get(f"{API_URL}/vehicles/inventory")

    vehicles = r.json()

    if not vehicles:
        st.warning("No vehicles found")
        return

    df = pd.DataFrame(vehicles)

    # -------------------------
    # FORMAT TABLE
    # -------------------------

    df_table = df[[
        "vin",
        "year",
        "make",
        "model",
        "price",
        "miles"
    ]].copy()

    df_table.columns = [
        "VIN",
        "Year",
        "Make",
        "Model",
        "Price",
        "Miles"
    ]

    # columnas de acción
    df_table["Edit"] = False
    df_table["Delete"] = False

    st.subheader("Inventory")

    edited_df = st.data_editor(
        df_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Edit": st.column_config.CheckboxColumn("Edit"),
            "Delete": st.column_config.CheckboxColumn("Delete")
        }
    )

    # -------------------------
    # HANDLE ACTIONS
    # -------------------------

    for i, row in edited_df.iterrows():

        vin = row["VIN"]

        if row["Delete"]:

            st.session_state["delete_vehicle"] = vin

        if row["Edit"]:

            st.session_state["edit_vehicle"] = df.iloc[i]

    # -------------------------
    # EDIT FORM
    # -------------------------

    if "edit_vehicle" in st.session_state:

        v = st.session_state["edit_vehicle"]

        st.divider()
        st.subheader(f"Edit Vehicle {v['vin']}")

        col1, col2 = st.columns(2)

        with col1:
            year = st.text_input("Year", v["year"])
            make = st.text_input("Make", v["make"])
            model = st.text_input("Model", v["model"])

        with col2:
            price = st.text_input("Price", v["price"])
            miles = st.text_input("Miles", v["miles"])

        if st.button("Update Vehicle"):

            payload = {
                "year": year,
                "make": make,
                "model": model,
                "trim": v.get("trim", ""),
                "price": price,
                "miles": miles,
                "dealer_name": v.get("dealer_name", ""),
                "city": v.get("city", ""),
                "state": v.get("state", "")
            }

            requests.put(
                f"{API_URL}/vehicles/{v['vin']}",
                json=payload
            )

            st.success("Vehicle updated")

            del st.session_state["edit_vehicle"]

            st.rerun()

    # -------------------------
    # DELETE CONFIRMATION
    # -------------------------

    if "delete_vehicle" in st.session_state:

        vin = st.session_state["delete_vehicle"]

        st.warning(f"Are you sure you want to delete vehicle {vin}?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirm Delete"):

                requests.delete(f"{API_URL}/vehicles/{vin}")

                st.success("Vehicle deleted")

                del st.session_state["delete_vehicle"]

                st.rerun()

        with col2:
            if st.button("Cancel"):

                del st.session_state["delete_vehicle"]

                st.rerun()
