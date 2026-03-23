import streamlit as st
import requests
import pandas as pd
import os
from fpdf import FPDF

API_URL = os.getenv("API_URL", "http://localhost:8000")


def generate_pdf(vehicle, orders):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    # =========================
    # TITLE
    # =========================
    pdf.cell(200, 10, txt="Vehicle Report", ln=True, align="C")

    pdf.ln(5)

    # =========================
    # VEHICLE INFO
    # =========================
    pdf.cell(200, 10, txt=f"VIN: {vehicle.get('vin')}", ln=True)
    pdf.cell(200, 10, txt=f"{vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {vehicle.get('status')}", ln=True)
    pdf.cell(200, 10, txt=f"Purchase Price: ${vehicle.get('price_purchase', 0):,.0f}", ln=True)

    pdf.ln(5)

    # =========================
    # ORDERS
    # =========================
    for order in orders:
        pdf.cell(200, 10, txt=f"Order #{order['id']} - {order['status']} - ${order['total_cost']:.0f}", ln=True)

        for d in order.get("details", []):
            line = f"  - {d['name']} ({d['type']}), Qty: {d['quantity']}, ${d['subtotal']:.2f}"
            pdf.cell(200, 8, txt=line, ln=True)

        pdf.ln(3)

    return pdf.output(dest="S").encode("latin-1")


def app():

    st.title("📊 Vehicle Report")

    # =========================
    # LOAD VEHICLES
    # =========================
    try:
        vehicles = requests.get(f"{API_URL}/vehicles/inventory").json()
        df_vehicles = pd.DataFrame(vehicles if isinstance(vehicles, list) else [])
    except Exception as e:
        st.error(f"Error loading vehicles: {e}")
        return

    if df_vehicles.empty:
        st.warning("No vehicles available")
        return

    # =========================
    # VIN SELECTOR
    # =========================
    vin_list = df_vehicles["vin"].dropna().tolist()

    selected_vin = st.selectbox("Select Vehicle VIN", vin_list)

    selected_vehicle = df_vehicles[df_vehicles["vin"] == selected_vin].iloc[0]

    st.markdown(
        f"**{selected_vehicle.get('year')} "
        f"{selected_vehicle.get('make')} "
        f"{selected_vehicle.get('model')}**"
    )

    # =========================
    # FETCH REPORT
    # =========================
    try:
        r = requests.get(
            f"{API_URL}/reports/vehicle",
            params={"vin": selected_vin}
        )

        if r.status_code != 200:
            st.error(f"API Error: {r.text}")
            return

        data = r.json()

    except Exception as e:
        st.error(f"Request failed: {e}")
        return

    if not isinstance(data, dict) or "vehicle" not in data:
        st.error("Invalid response from backend")
        st.write(data)
        return

    vehicle = data.get("vehicle", {})
    orders = data.get("orders", [])
    summary = data.get("summary", {})

    # =========================
    # VEHICLE INFO
    # =========================
    st.subheader("🚗 Vehicle Info")

    col1, col2, col3 = st.columns(3)

    col1.metric("Year", vehicle.get("year"))
    col2.metric("Make", vehicle.get("make"))
    col3.metric("Model", vehicle.get("model"))

    col4, col5 = st.columns(2)

    col4.metric("Status", vehicle.get("status"))
    col5.metric("Purchase Price", f"${vehicle.get('price_purchase', 0):,.0f}")

    # =========================
    # SUMMARY
    # =========================
    st.subheader("📈 Summary")

    col1, col2 = st.columns(2)

    col1.metric("Total Orders", summary.get("total_orders", 0))
    col2.metric("Total Invested", f"${summary.get('total_spent', 0):,.0f}")

    # =========================
    # EXPORT
    # =========================
    st.subheader("📥 Export Report")

    export_rows = []

    for order in orders:
        for d in order.get("details", []):
            export_rows.append({
                "VIN": vehicle.get("vin"),
                "Order ID": order.get("id"),
                "Order Status": order.get("status"),
                "Item": d.get("name"),
                "Type": d.get("type"),
                "Qty": d.get("quantity"),
                "Unit Price": d.get("unit_price"),
                "Subtotal": d.get("subtotal")
            })

    col1, col2 = st.columns(2)

    # CSV
    if export_rows:
        df_export = pd.DataFrame(export_rows)

        csv = df_export.to_csv(index=False).encode("utf-8")

        col1.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"vehicle_report_{selected_vin}.csv",
            mime="text/csv"
        )

    # PDF
    pdf_bytes = generate_pdf(vehicle, orders)

    col2.download_button(
        label="📄 Download PDF",
        data=pdf_bytes,
        file_name=f"vehicle_report_{selected_vin}.pdf",
        mime="application/pdf"
    )

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