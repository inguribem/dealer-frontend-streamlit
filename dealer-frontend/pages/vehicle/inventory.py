import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
ROWS_PER_PAGE = 10


def safe_avg(df, column):
    if column not in df.columns:
        return 0
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    return int(s.mean()) if not s.empty else 0


def app():
    st.set_page_config(layout="wide")
    st.title("🚗 Vehicle Inventory")

    # -------------------------
    # LOAD DATA
    # -------------------------
    try:
        data = requests.get(f"{API_URL}/vehicles/inventory").json()
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to load inventory: {e}")
        return

    if df.empty:
        st.warning("No vehicles found")
        return

    # -------------------------
    # SIDEBAR FILTERS
    # -------------------------
    st.sidebar.header("🔍 Filters")

    search = st.sidebar.text_input("Search")

    makes = ["All"] + sorted(df["make"].dropna().unique().tolist())
    selected_make = st.sidebar.selectbox("Make", makes)

    years = ["All"] + sorted(df["year"].dropna().astype(str).unique().tolist())
    selected_year = st.sidebar.selectbox("Year", years)

    # Apply filters
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    if selected_make != "All":
        df = df[df["make"] == selected_make]

    if selected_year != "All":
        df = df[df["year"] == int(selected_year)]

    # -------------------------
    # METRICS
    # -------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Vehicles", len(df))
    col2.metric("Avg Price", f"${safe_avg(df, 'price'):,}")
    col3.metric("Avg Miles", f"{safe_avg(df, 'miles'):,}")

    st.divider()

    # -------------------------
    # SORTING
    # -------------------------
    col_sort1, col_sort2 = st.columns(2)

    sort_col = col_sort1.selectbox("Sort by", ["year", "price", "miles"])
    sort_order = col_sort2.radio("Order", ["Desc", "Asc"], horizontal=True)

    df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
    df = df.sort_values(by=sort_col, ascending=(sort_order == "Asc"))

    # -------------------------
    # PAGINATION
    # -------------------------
    if "page" not in st.session_state:
        st.session_state.page = 1

    total_pages = (len(df) - 1) // ROWS_PER_PAGE + 1
    page = st.session_state.page

    start = (page - 1) * ROWS_PER_PAGE
    df_page = df.iloc[start:start + ROWS_PER_PAGE]

    # -------------------------
    # INVENTORY LIST (CARD STYLE)
    # -------------------------
    st.subheader("Inventory")

    for _, row in df_page.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            col1.markdown(f"**{row.get('year','')} {row.get('make','')} {row.get('model','')}**")
            col2.write(f"${row.get('price','-')}")
            col3.write(f"{row.get('miles','-')} mi")

            if col4.button("✏️", key=f"edit_{row['vin']}"):
                st.session_state.edit_vehicle = row

            if col5.button("🗑", key=f"delete_{row['vin']}"):
                st.session_state.delete_vehicle = row["vin"]

            st.divider()

    # -------------------------
    # PAGINATION CONTROLS
    # -------------------------
    col1, col2, col3 = st.columns(3)

    if col1.button("⬅️ Prev") and page > 1:
        st.session_state.page -= 1
        st.rerun()

    col2.markdown(f"### Page {page} / {total_pages}")

    if col3.button("Next ➡️") and page < total_pages:
        st.session_state.page += 1
        st.rerun()

    # -------------------------
    # EDIT VEHICLE
    # -------------------------
    if st.session_state.get("edit_vehicle") is not None:
        v = st.session_state.edit_vehicle

        with st.expander(f"✏️ Editing {v['vin']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                year = st.text_input("Year", v.get("year", ""))
                make = st.text_input("Make", v.get("make", ""))
                model = st.text_input("Model", v.get("model", ""))

            with col2:
                price = st.text_input("Price", v.get("price", ""))
                miles = st.text_input("Miles", v.get("miles", ""))

            if st.button("Save Changes"):
                payload = {
                    "year": year,
                    "make": make,
                    "model": model,
                    "price": price or None,
                    "miles": miles or None,
                }

                requests.put(f"{API_URL}/vehicles/{v['vin']}", json=payload)

                st.success("Vehicle updated")
                st.session_state.edit_vehicle = None
                st.rerun()

    # -------------------------
    # DELETE CONFIRMATION
    # -------------------------
    if st.session_state.get("delete_vehicle"):
        vin = st.session_state.delete_vehicle

        st.warning(f"Delete vehicle {vin}?")

        col1, col2 = st.columns(2)

        if col1.button("Confirm Delete"):
            requests.delete(f"{API_URL}/vehicles/{vin}")
            st.success("Vehicle deleted")
            st.session_state.delete_vehicle = None
            st.rerun()

        if col2.button("Cancel"):
            st.session_state.delete_vehicle = None
            st.rerun()