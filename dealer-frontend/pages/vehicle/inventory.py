import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():

    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # LOAD ALL DATA (for dropdown filters)
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

    with col1:
        search = st.text_input("🔍 Search")

    with col2:
        makes = sorted(df_all["make"].dropna().unique())
        selected_make = st.selectbox("Make", ["All"] + list(makes))

    with col3:
        years = sorted(df_all["year"].dropna().unique())
        selected_year = st.selectbox("Year", ["All"] + list(years))

    with col4:
        apply_filters = st.button("Apply")
        clear_filters = st.button("Clear")

    # -------------------------
    # SESSION STATE FOR FILTERS
    # -------------------------
    if "filters" not in st.session_state:
        st.session_state.filters = {}

    if apply_filters:
        st.session_state.filters = {
            "search": search,
            "make": selected_make,
            "year": selected_year
        }

    if clear_filters:
        st.session_state.filters = {}
        st.rerun()

    # -------------------------
    # BUILD PARAMS
    # -------------------------
    params = {}
    filters = st.session_state.get("filters", {})

    if filters.get("search"):
        params["search"] = filters["search"]

    if filters.get("make") and filters["make"] != "All":
        params["make"] = filters["make"]

    if filters.get("year") and filters["year"] != "All":
        params["year"] = int(filters["year"])

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
        "vin", "year", "make", "model", "price", "miles"
    ]].copy()

    df_table.columns = ["VIN", "Year", "Make", "Model", "Price", "Miles"]

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
            make = st.text_input_


