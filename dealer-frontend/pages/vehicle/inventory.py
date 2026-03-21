import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
ROWS_PER_PAGE = 10


def app():

    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # SESSION STATE INIT
    # -------------------------
    if "page" not in st.session_state:
        st.session_state.page = 1

    if "filters" not in st.session_state:
        st.session_state.filters = {}

    if "sort_column" not in st.session_state:
        st.session_state.sort_column = "year"
        st.session_state.sort_ascending = False

    # -------------------------
    # LOAD DATA FOR FILTER OPTIONS
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

    # =========================================================
    # 🔥 FILTERS (NOW INSIDE PAGE - TOP SECTION)
    # =========================================================
    st.subheader("Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input(
            "Search",
            value=st.session_state.filters.get("search", "")
        )

    with col2:
        makes = sorted(df_all["make"].dropna().unique())
        selected_make = st.selectbox(
            "Make",
            ["All"] + list(makes),
            index=(["All"] + list(makes)).index(
                st.session_state.filters.get("make", "All")
            )
        )

    with col3:
        years = sorted(df_all["year"].dropna().unique())
        selected_year = st.selectbox(
            "Year",
            ["All"] + list(years),
            index=(["All"] + list(years)).index(
                str(st.session_state.filters.get("year", "All"))
            )
        )

    with col4:
        apply_filters = st.button("Apply Filters")
        clear_filters = st.button("Clear")

    # -------------------------
    # APPLY / CLEAR FILTERS
    # -------------------------
    if apply_filters:
        st.session_state.filters = {
            "search": search,
            "make": selected_make,
            "year": selected_year
        }
        st.session_state.page = 1
        st.rerun()

    if clear_filters:
        st.session_state.filters = {}
        st.session_state.page = 1
        st.rerun()

    st.divider()

    # =========================================================
    # BUILD API PARAMS
    # =========================================================
    params = {}
    filters = st.session_state.filters

    if filters.get("search"):
        params["search"] = filters["search"]

    if filters.get("make") and filters["make"] != "All":
        params["make"] = filters["make"]

    if filters.get("year") and filters["year"] != "All":
        params["year"] = int(filters["year"])

    # =========================================================
    # FETCH FILTERED DATA
    # =========================================================
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

    # =========================================================
    # SORTING
    # =========================================================
    cols = ["vin", "year", "make", "model", "price", "miles"]

    col_sort = st.selectbox(
        "Sort by",
        cols,
        index=cols.index(st.session_state.sort_column)
    )

    asc_sort = st.radio(
        "Order",
        ["Ascending", "Descending"],
        index=0 if st.session_state.sort_ascending else 1
    )

    st.session_state.sort_column = col_sort
    st.session_state.sort_ascending = (asc_sort == "Ascending")

    df = df.sort_values(
        by=st.session_state.sort_column,
        ascending=st.session_state.sort_ascending
    )

    # =========================================================
    # PAGINATION (FIXED TYPE ISSUE)
    # =========================================================
    total_pages = (len(df) - 1) // ROWS_PER_PAGE + 1

    start_idx = (int(st.session_state.page) - 1) * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE

    df_page = df.iloc[start_idx:end_idx]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    with col2:
        st.markdown(f"Page **{st.session_state.page}** of **{total_pages}**")

    with col3:
        if st.button("Next") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

    # =========================================================
    # TABLE
    # =========================================================
    df_table = df_page[["vin", "year", "make", "model", "price", "miles"]].copy()
    df_table.columns = ["VIN", "Year", "Make", "Model", "Price", "Miles"]

    st.dataframe(df_table, use_container_width=True)