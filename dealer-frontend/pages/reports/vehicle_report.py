import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def app():

    st.title("📊 Vehicle Report")

    # =========================
    # INPUT VIN
    # =========================
    vin = st.text_input("Enter VIN")

    if not vin:
        st.info("Please enter a VIN")
        return

    # =========================
    # FETCH REPORT
    # =========================
    try:
        r = requests.get(
            f"{API_URL}/reports/vehicle",
            params={"vin": vin}
        )

        if r.status_code != 200:
            st.error(f"API Error: {r.text}")
            return

        data = r.json()

    except Exception as e:
        st.error(f"Request failed: {e}")
        return

    # =========================
    # VALIDATE RESPONSE
    # =========================
    if not isinstance(data, dict):
        st.error("Invalid response from backend")
        st.write(data)
        return

    if "error" in data:
        st.error(data["error"])
        return

    if "vehicle" not in data:
        st.error("Backend response missing 'vehicle'")
        st.write(data)
        return

    # =========================
    # SAFE EXTRACTION
    # =========================
    vehicle = data.get("vehicle", {})
    orders = data.get("orders", [])
    summary = data.get("summary", {})

    # =========================
    # VEHICLE INFO
    # =========================
    st.subheader("🚗 Vehicle Info")

    st.write(f"**VIN:** {vehicle.get('vin')}")
    st.write(f"**Make:** {vehicle.get('make')}")
    st.write(f"**Model:** {vehicle.get('model')}")
    st.write(f"**Year:** {vehicle.get('year')}")
    st.write(f"**Status:** {vehicle.get('status')}")
    st.write(f"**Purchase Price:** ${vehicle.get('price_purchase', 0):,.0f}")

    # =========================
    # SUMMARY
    # =========================
    st.subheader("📈 Summary")

    col1, col2 = st.columns(2)

    col1.metric("Total Orders", summary.get("total_orders", 0))
    col2.metric("Total Invested", f"${summary.get('total_spent', 0):,.0f}")

    # =========================
    # ORDERS
    # =========================
    st.subheader("🧾 Service Orders")

    if not orders:
        st.info("No orders found")
        return

    for order in orders:

        title = f"Order #{order.get('id')} • ${order.get('total_cost', 0):.0f} • {order.get('status')}"

        with st.expander(title):

            st.write(f"Created: {order.get('created_at')}")

            details = order.get("details", [])

            if not details:
                st.info("No details in this order")
            else:
                for d in details:
                    st.write(
                        f"- {d.get('name')} ({d.get('type')}) | "
                        f"Qty: {d.get('quantity')} | "
                        f"${d.get('unit_price')} → ${d.get('subtotal')}"
                    )