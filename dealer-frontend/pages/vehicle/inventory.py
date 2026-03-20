import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():

    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # LOAD ALL DATA (for filters)
    # -------------------------
    try:
        all_data = requests.get(f"{API_URL}/vehicles/inventory").json()
        df_all = pd.DataFrame(all_data)
    except:
        st.error("Failed to load inventory")
        return

    if df_all.empty:
        st.warning("No vehicles found")
        return

    # -------------------------
    # FILTERS UI
    # -------------------------
    st.subheader("Filters")

    col1, col2, col3, col4 = st.columns(4)

    search = col1.text_input("🔍 Search")

    makes = sorted(df_all["make"].dropna().unique())
    selected_make = col2.selectbox("Make", ["All"] + list(makes))

    years = sorted(df_all["year"].dropna().unique())
    selected_year = col3.selectbox("Year", ["All"] + list(years))

    if col4.button("Clear"):
        st.rerun()

    # -------------------------
    # BUILD PARAMS FOR BACKEND
    # -------------------------
    params = {}

    if search:
        params["search"] = search

    if selected_make != "All":
        params["make"] = selected_make

    if selected_year != "All":
        params["year"] = selected_year

    # -------------------------
    # FETCH FILTERED DATA
    # -------------------------
    try:
        r = requests.get(f"{API_URL}/vehicles/inventory", params=params)
        vehicles = r.json()
        df = pd.DataFrame(vehicles)
    except:
        st.error("Error fetching filtered data")
        return

    if df.empty:
        st.info("No vehicles found with the given filters.")
        return

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
            st.session_state["edit_vehicle"] = df.iloc[i]  # 🔥 importante

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

