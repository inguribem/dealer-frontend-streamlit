import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
ROWS_PER_PAGE = 10

def app():

    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # LOAD ALL DATA FOR FILTERS
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
    # SESSION STATE INIT
    # -------------------------
    if "filters" not in st.session_state:
        st.session_state.filters = {}
    if "edit_vehicle" not in st.session_state:
        st.session_state.edit_vehicle = None
    if "delete_vehicle" not in st.session_state:
        st.session_state.delete_vehicle = None
    if "page" not in st.session_state:
        st.session_state.page = 1
    if "sort_column" not in st.session_state:
        st.session_state.sort_column = "year"
        st.session_state.sort_ascending = False

    # -------------------------
    # FILTERS UI
    # -------------------------
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("🔍 Search", value=st.session_state.filters.get("search",""))
    with col2:
        makes = sorted(df_all["make"].dropna().unique())
        selected_make = st.selectbox("Make", ["All"] + list(makes),
                                     index=(["All"] + list(makes)).index(st.session_state.filters.get("make","All")))
    with col3:
        years = sorted(df_all["year"].dropna().unique())
        selected_year = st.selectbox("Year", ["All"] + list(years),
                                     index=(["All"] + list(years)).index(str(st.session_state.filters.get("year","All"))))
    with col4:
        apply_filters = st.button("Apply")
        clear_filters = st.button("Clear")

    # -------------------------
    # APPLY FILTERS
    # -------------------------
    if apply_filters:
        st.session_state.filters = {"search": search, "make": selected_make, "year": selected_year}
        st.session_state.page = 1  # reset page
    if clear_filters:
        st.session_state.filters = {}
        st.session_state.page = 1
        st.rerun()

    # -------------------------
    # BUILD PARAMS
    # -------------------------
    params = {}
    filters = st.session_state.filters
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
    # SORTING
    # -------------------------
    cols = ["vin", "year", "make", "model", "price", "miles"]
    st.write("Sort by:")
    col_sort = st.selectbox("Column", cols, index=cols.index(st.session_state.sort_column))
    asc_sort = st.radio("Order", ["Ascending", "Descending"],
                        index=0 if st.session_state.sort_ascending else 1)
    st.session_state.sort_column = col_sort
    st.session_state.sort_ascending = True if asc_sort=="Ascending" else False

    df = df.sort_values(by=st.session_state.sort_column, ascending=st.session_state.sort_ascending)

    # -------------------------
    # PAGINATION
    # -------------------------
    total_pages = (len(df) - 1) // ROWS_PER_PAGE + 1
    start_idx = (st.session_state.page - 1) * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE
    df_page = df.iloc[start_idx:end_idx]

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()
    with col2:
        st.markdown(f"Page {st.session_state.page} of {total_pages}")
    with col3:
        if st.button("Next") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

    # -------------------------
    # FORMAT TABLE
    # -------------------------
    df_table = df_page[["vin","year","make","model","price","miles"]].copy()
    df_table.columns = ["VIN","Year","Make","Model","Price","Miles"]
    df_table["Edit"] = False
    df_table["Delete"] = False

    edited_df = st.data_editor(
        df_table,
        use_container_width=True,
        hide_index=True,
        key="data_editor",
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
        original_row = df[df["vin"]==vin].iloc[0]
        if row["Delete"]:
            st.session_state.delete_vehicle = vin
        if row["Edit"]:
            st.session_state.edit_vehicle = original_row

    # -------------------------
    # EDIT FORM
    # -------------------------
    if st.session_state.edit_vehicle is not None:
        v = st.session_state.edit_vehicle
        st.divider()
        st.subheader(f"Edit Vehicle {v['vin']}")
        col1, col2 = st.columns(2)
        with col1:
            year = st.text_input("Year", v["year"])
            make = st.text_input("Make", v["make"])
            model = st.text_input("Model", v["model"])
        with col2:
            price = st.text_input("Price", v.get("price",""))
            miles = st.text_input("Miles", v.get("miles",""))

        if st.button("Update Vehicle"):
            payload = {
                "year": year,
                "make": make,
                "model": model,
                "trim": v.get("trim",""),
                "price": price or None,
                "miles": miles or None,
                "dealer_name": v.get("dealer_name",""),
                "city": v.get("city",""),
                "state": v.get("state","")
            }
            requests.put(f"{API_URL}/vehicles/{v['vin']}", json=payload)
            st.success("Vehicle updated")
            st.session_state.edit_vehicle = None
            st.rerun()

    # -------------------------
    # DELETE CONFIRMATION
    # -------------------------
    if st.session_state.delete_vehicle is not None:
        vin = st.session_state.delete_vehicle
        st.warning(f"Are you sure you want to delete vehicle {vin}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete"):
                requests.delete(f"{API_URL}/vehicles/{vin}")
                st.success("Vehicle deleted")
                st.session_state.delete_vehicle = None
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.delete_vehicle = None
                st.rerun()
