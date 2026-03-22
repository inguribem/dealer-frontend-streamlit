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
    # CLEAN DATA (UPDATED SCHEMA)
    # -------------------------
    df["price_purchase"] = pd.to_numeric(df.get("price_purchase"), errors="coerce")
    df["year"] = pd.to_numeric(df.get("year"), errors="coerce")

    # -------------------------
    # KPIs
    # -------------------------
    st.subheader("📈 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Vehicles", len(df))

    avg_price = (
        int(df["price_purchase"].mean())
        if df["price_purchase"].notna().any()
        else 0
    )
    col2.metric("Avg Purchase Price", f"${avg_price:,}")

    top_make = df["make"].mode()[0] if "make" in df and not df["make"].empty else "N/A"
    col3.metric("Top Brand", top_make)

    top_status = df["status"].mode()[0] if "status" in df and not df["status"].empty else "N/A"
    col4.metric("Top Status", top_status)

    st.divider()

    # -------------------------
    # FILTERS
    # -------------------------
    st.subheader("🔎 Filters")

    makes = st.multiselect(
        "Select Make",
        df["make"].dropna().unique()
    )

    if makes:
        df = df[df["make"].isin(makes)]

    statuses = st.multiselect(
        "Select Status",
        df["status"].dropna().unique() if "status" in df else []
    )

    if statuses:
        df = df[df["status"].isin(statuses)]

    st.divider()

    # -------------------------
    # CHART 1: INVENTORY BY MAKE
    # -------------------------
    st.subheader("📊 Inventory by Make")

    if "make" in df:
        make_counts = df["make"].value_counts()

        fig1 = plt.figure()
        make_counts.plot(kind="bar")
        plt.xlabel("Make")
        plt.ylabel("Count")

        st.pyplot(fig1)

    # -------------------------
    # CHART 2: PRICE DISTRIBUTION
    # -------------------------
    st.subheader("💰 Purchase Price Distribution")

    if "price_purchase" in df:
        fig2 = plt.figure()
        df["price_purchase"].dropna().plot(kind="hist", bins=20)
        plt.xlabel("Purchase Price")

        st.pyplot(fig2)

    # -------------------------
    # CHART 3: VEHICLES BY YEAR
    # -------------------------
    st.subheader("📅 Vehicles by Year")

    if "year" in df:
        year_counts = df["year"].value_counts().sort_index()

        fig3 = plt.figure()
        year_counts.plot(kind="line")
        plt.xlabel("Year")

        st.pyplot(fig3)

    # -------------------------
    # TABLE
    # -------------------------
    st.subheader("📋 Inventory Table")

    display_cols = [
        col for col in [
            "vin",
            "year",
            "make",
            "model",
            "price_purchase",
            "miles",
            "status"
        ]
        if col in df.columns
    ]

    st.dataframe(df[display_cols], use_container_width=True)
