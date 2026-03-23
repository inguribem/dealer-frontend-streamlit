import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():

    st.title("📊 Vehicle Report")

    # -------------------------
    # LOAD VEHICLES
    # -------------------------
    vehicles = requests.get(f"{API_URL}/vehicles/inventory").json()

    if not vehicles:
        st.warning("No vehicles found")
        return

    df = pd.DataFrame(vehicles)

    vin = st.selectbox("Select Vehicle", df["vin"].tolist())

    if not vin:
        return

    # -------------------------
    # FETCH REPORT
    # -------------------------
    try:
        data = requests.get(f"{API_URL}/reports/vehicle/{vin}").json()
    except:
        st.error("Error loading report")
        return

    if "error" in data:
        st.error(data["error"])
        return

    vehicle = data["vehicle"]
    orders = data["orders"]

    # =========================
    # VEHICLE INFO
    # =========================
    st.subheader("🚗 Vehicle Info")

    col1, col2, col3 = st.columns(3)

    col1.metric("VIN", vehicle["vin"])
    col2.metric("Make / Model", f"{vehicle['make']} {vehicle['model']}")
    col3.metric("Year", vehicle["year"])

    col4, col5 = st.columns(2)

    col4.metric("Purchase Price", f"${vehicle['price_purchase']:,.0f}")
    col5.metric("Status", vehicle["status"].capitalize())

    st.divider()

    # =========================
    # SUMMARY
    # =========================
    total_orders = len(orders)
    total_spent = sum(o["total_cost"] for o in orders)

    col1, col2 = st.columns(2)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Service Cost", f"${total_spent:,.0f}")

    st.divider()

    # =========================
    # ORDERS DETAIL
    # =========================
    st.subheader("🧾 Orders")

    if not orders:
        st.info("No orders found for this vehicle.")
        return

    for order in orders:

        title = f"Order #{order['id']} • ${order['total_cost']:,.0f} • {order['status']}"

        with st.expander(title):

            details = order["details"]

            if not details:
                st.info("No items in this order")
                continue

            df_details = pd.DataFrame(details)

            df_details = df_details[[
                "item", "quantity", "unit_price", "subtotal"
            ]]

            df_details.columns = [
                "Item", "Qty", "Unit Price", "Subtotal"
            ]

            st.dataframe(df_details, use_container_width=True)