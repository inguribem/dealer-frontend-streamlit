# pages/dashboard.py

import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def app():

    st.title("📊 Dealer Dashboard")

    # =========================
    # LOAD DATA
    # =========================
    try:
        data = requests.get(f"{API_URL}/vehicles/inventory").json()
        df = pd.DataFrame(data)
    except:
        st.error("Failed to load dashboard data")
        return

    if df.empty:
        st.warning("No vehicles in inventory")
        return

    # =========================
    # CLEAN DATA
    # =========================
    df["price_purchase"] = pd.to_numeric(df["price_purchase"], errors="coerce").fillna(0)

    df["status"] = df["status"].fillna("new")

    # =========================
    # METRICS
    # =========================
    total = len(df)

    status_counts = df["status"].value_counts().to_dict()

    total_value = df["price_purchase"].sum()

    ready = status_counts.get("ready", 0)
    sold = status_counts.get("sold", 0)
    repair = status_counts.get("repair", 0)
    diagnostic = status_counts.get("diagnostic", 0)
    new = status_counts.get("new", 0)

    # =========================
    # KPI ROW
    # =========================
    st.subheader("📈 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Vehicles", total)
    col2.metric("Total Value", f"${total_value:,.0f}")
    col3.metric("Ready", ready)
    col4.metric("Sold", sold)

    st.divider()

    # =========================
    # STATUS BREAKDOWN
    # =========================
    st.subheader("🚗 Inventory Status Breakdown")

    col1, col2, col3 = st.columns(3)

    col1.metric("New", new)
    col2.metric("Diagnostic", diagnostic)
    col3.metric("Repair", repair)

    st.divider()

    # =========================
    # READY RATE
    # =========================
    ready_rate = (ready / total * 100) if total else 0

    st.subheader("📊 Performance")

    st.progress(ready_rate / 100)

    st.write(f"Inventory Ready Rate: **{ready_rate:.1f}%**")

    st.divider()

    # =========================
    # RECENT VEHICLES
    # =========================
    st.subheader("🆕 Recent Inventory")

    recent = df.sort_values(by="year", ascending=False).head(5)

    st.dataframe(
        recent[["vin", "make", "model", "year", "status", "price_purchase"]],
        use_container_width=True,
        hide_index=True
    )
