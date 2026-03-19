import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = st.secrets["API_URL"]

def app():

    st.title("📊 Vehicle Intelligence Dashboard")

    # -------------------------
    # LOAD DATA
    # -------------------------

    r = requests.get(f"{API_URL}/vehicles/inventory")

    if r.status_code != 200:
        st.error("Error loading data")
        return

    data = r.json()

    if not data:
        st.warning("No vehicles in inventory")
        return

    df = pd.DataFrame(data)

    # -------------------------
    # CLEAN DATA
    # -------------------------

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # -------------------------
    # KPIs
    # -------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Vehicles", len(df))

    avg_price = int(df["price"].mean()) if df["price"].notna().any() else 0
    col2.metric("Avg Price", f"${avg_price:,}")

    top_make = df["make"].mode()[0] if not df["make"].empty else "N/A"
    col3.metric("Top Brand", top_make)

    st.divider()

    # -------------------------
    # FILTERS
    # -------------------------

    st.subheader("Filters")

    makes = st.multiselect("Select Make", df["make"].dropna().unique())

    if makes:
        df = df[df["make"].isin(makes)]

    # -------------------------
    # CHART 1: INVENTORY BY MAKE
    # -------------------------

    st.subheader("Inventory by Make")

    make_counts = df["make"].value_counts()

    fig1 = plt.figure()
    make_counts.plot(kind="bar")
    plt.xlabel("Make")
    plt.ylabel("Count")

    st.pyplot(fig1)

    # -------------------------
    # CHART 2: PRICE DISTRIBUTION
    # -------------------------

    st.subheader("Price Distribution")

    fig2 = plt.figure()
    df["price"].dropna().plot(kind="hist", bins=20)

    st.pyplot(fig2)

    # -------------------------
    # CHART 3: VEHICLES BY YEAR
    # -------------------------

    st.subheader("Vehicles by Year")

    year_counts = df["year"].value_counts().sort_index()

    fig3 = plt.figure()
    year_counts.plot(kind="line")

    st.pyplot(fig3)

    # -------------------------
    # TABLE
    # -------------------------

    st.subheader("Inventory Table")

    st.dataframe(df)
