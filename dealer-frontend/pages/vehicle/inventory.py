import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
ROWS_PER_PAGE = 10

STATUS_OPTIONS = ["new", "diagnostic", "repair", "ready", "sold"]


def app():

    st.title("🚗 Vehicle Inventory")

    # =========================
    # SESSION STATE
    # =========================
    if "inventory_page" not in st.session_state:
        st.session_state.inventory_page = 1

    if "filters" not in st.session_state:
        st.session_state.filters = {}

    if "sort_column" not in st.session_state:
        st.session_state.sort_column = "year"
        st.session_state.sort_ascending = False

    # =========================
    # LOAD DATA
    # =========================
    try:
        all_data = requests.get(f"{API_URL}/vehicles/inventory").json()
        df_all = pd.DataFrame(all_data)
    except:
        st.error("Failed to load inventory")
        return

    if df_all.empty:
        st.warning("No vehicles found")
        return

    # =========================
    # FILTERS
    # =========================
    st.subheader("🔎 Filters")

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
        statuses = ["All"] + STATUS_OPTIONS
        selected_status = st.selectbox(
            "Status",
            statuses,
            index=statuses.index(
                st.session_state.filters.get("status", "All")
            )
        )

    col_apply, col_clear = st.columns(2)

    with col_apply:
        apply_filters = st.button("Apply Filters")

    with col_clear:
        clear_filters = st.button("Clear")

    # APPLY
    if apply_filters:
        st.session_state.filters = {
            "search": search,
            "make": selected_make,
            "year": selected_year,
            "status": selected_status
        }
        st.session_state.inventory_page = 1
        st.rerun()

    # CLEAR
    if clear_filters:
        st.session_state.filters = {}
        st.session_state.inventory_page = 1
        st.rerun()

    st.divider()

    # =========================
    # API PARAMS
    # =========================
    params = {}
    filters = st.session_state.filters

    if filters.get("search"):
        params["search"] = filters["search"]

    if filters.get("make") and filters["make"] != "All":
        params["make"] = filters["make"]

    if filters.get("year") and filters["year"] != "All":
        params["year"] = int(float(filters["year"]))

    if filters.get("status") and filters["status"] != "All":
        params["status"] = filters["status"]

    # =========================
    # FETCH DATA
    # =========================
    try:
        r = requests.get(f"{API_URL}/vehicles/inventory", params=params)
        df = pd.DataFrame(r.json())
    except:
        st.error("Error fetching filtered data")
        return

    if df.empty:
        st.info("No vehicles found with the given filters.")
        return

    # =========================
    # SORTING
    # =========================
    cols = ["vin", "year", "make", "model", "price_purchase", "status"]

    col_sort = st.selectbox(
        "Sort by",
        cols,
        index=cols.index(st.session_state.sort_column)
        if st.session_state.sort_column in cols else 0
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

    # =========================
    # PAGINATION
    # =========================
    total_pages = max(1, (len(df) - 1) // ROWS_PER_PAGE + 1)

    start_idx = (st.session_state.inventory_page - 1) * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE

    df_page = df.iloc[start_idx:end_idx]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Previous") and st.session_state.inventory_page > 1:
            st.session_state.inventory_page -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"Page **{st.session_state.inventory_page}** of **{total_pages}**"
        )

    with col3:
        if st.button("Next") and st.session_state.inventory_page < total_pages:
            st.session_state.inventory_page += 1
            st.rerun()

    # =========================
    # TABLE HEADER
    # =========================
    st.subheader("📋 Inventory")

    header = st.columns([2, 2, 2, 1, 2, 2, 1, 1])

    header[0].markdown("**VIN**")
    header[1].markdown("**Make**")
    header[2].markdown("**Model**")
    header[3].markdown("**Year**")
    header[4].markdown("**Status**")
    header[5].markdown("**Price**")
    header[6].markdown("**Edit**")
    header[7].markdown("**Delete**")

    st.divider()

    # =========================
    # ROWS
    # =========================
    for _, v in df_page.iterrows():

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 2, 1, 2, 2, 1, 1])

        col1.write(v.get("vin", ""))
        col2.write(v.get("make", ""))
        col3.write(v.get("model", ""))
        col4.write(v.get("year", ""))

        col5.write(str(v.get("status", "new")).capitalize())

        price = v.get("price_purchase", 0)
        col6.write(f"${price:,.0f}" if price else "$0")

        if col7.button("✏️", key=f"edit_{v['vin']}"):
            st.session_state["edit_vehicle"] = v.to_dict()

        if col8.button("🗑", key=f"delete_{v['vin']}"):
            st.session_state["delete_vehicle"] = v["vin"]

    # =========================
    # DELETE
    # =========================
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

    # =========================
    # EDIT
    # =========================
    if "edit_vehicle" in st.session_state:

        v = st.session_state["edit_vehicle"]

        st.divider()
        st.subheader(f"Edit Vehicle: {v['vin']}")

        col1, col2 = st.columns(2)

        with col1:
            year = st.text_input("Year", v.get("year", ""))
            make = st.text_input("Make", v.get("make", ""))
            model = st.text_input("Model", v.get("model", ""))

        with col2:
            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(
                    v.get("status", "new")
                    if v.get("status") in STATUS_OPTIONS else "new"
                )
            )

            price = st.text_input("Price", v.get("price_purchase", ""))

        # SAFE CAST
        def safe_int(val):
            try:
                return int(float(val))
            except:
                return None

        def safe_float(val):
            try:
                return float(val)
            except:
                return None

        if st.button("Update Vehicle"):

            payload = {
                "year": safe_int(year),
                "make": make,
                "model": model,
                "price_purchase": safe_float(price),
                "status": status
            }

            requests.put(
                f"{API_URL}/vehicles/{v['vin']}",
                json=payload
            )

            del st.session_state["edit_vehicle"]

            st.success("Updated successfully")
            st.rerun()