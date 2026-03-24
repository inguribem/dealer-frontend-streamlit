import streamlit as st
import requests
import pandas as pd
import os
from fpdf import FPDF

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.write("API_URL:", os.getenv("API_URL"))

# =========================
# PDF GENERATOR
# =========================
def clean_text(text):
    if text is None:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")


def generate_pdf(vehicle, orders):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, clean_text("Vehicle Report"), ln=True, align="C")
    pdf.ln(5)

    pdf.cell(200, 8, clean_text(f"VIN: {vehicle.get('vin')}"), ln=True)
    pdf.cell(200, 8, clean_text(f"{vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}"), ln=True)
    pdf.cell(200, 8, clean_text(f"Status: {vehicle.get('status')}"), ln=True)
    pdf.cell(200, 8, clean_text(f"Purchase Price: ${vehicle.get('price_purchase', 0):,.0f}"), ln=True)

    pdf.ln(5)

    for order in orders:
        pdf.cell(
            200,
            8,
            clean_text(f"Order #{order['id']} - {order['status']} - ${order['total_cost']:.0f}"),
            ln=True
        )

        for d in order.get("details", []):
            pdf.cell(
                200,
                6,
                clean_text(
                    f"- {d['name']} ({d['type']}) | Qty: {d['quantity']} | ${d['subtotal']:.2f}"
                ),
                ln=True
            )

        pdf.ln(2)

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
    # VIN DROPDOWN
    # =========================
    vin_list = df_vehicles["vin"].dropna().tolist()
    selected_vin = st.selectbox("Select Vehicle VIN", vin_list)

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
    # VEHICLE INFO (MISMO FORMATO)
    # =========================
    st.subheader("🚗 Vehicle Info")

    st.write(f"**VIN:** {vehicle.get('vin')}")
    st.write(f"**Make:** {vehicle.get('make')}")
    st.write(f"**Model:** {vehicle.get('model')}")
    st.write(f"**Year:** {vehicle.get('year')}")
    st.write(f"**Status:** {vehicle.get('status')}")
    st.write(f"**Purchase Price:** ${vehicle.get('price_purchase', 0):,.0f}")

    # =========================
    # SUMMARY (MISMO FORMATO)
    # =========================
    st.subheader("📈 Summary")

    col1, col2 = st.columns(2)
    col1.metric("Total Orders", summary.get("total_orders", 0))
    col2.metric("Total Invested", f"${summary.get('total_spent', 0):,.0f}")

    # =========================
    # EXPORT (NUEVO)
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
            "⬇️ Download CSV",
            data=csv,
            file_name=f"vehicle_report_{selected_vin}.csv",
            mime="text/csv"
        )
    else:
        col1.info("No data to export")

    # PDF
    pdf_bytes = generate_pdf(vehicle, orders)

    col2.download_button(
        "📄 Download PDF",
        data=pdf_bytes,
        file_name=f"vehicle_report_{selected_vin}.pdf",
        mime="application/pdf"
    )

    # =========================
    # ORDERS (MISMO FORMATO)
    # =========================
    st.subheader("🧾 Service Orders")

    if not orders:
        st.info("No orders found")
        return

    for order in orders:

        title = f"Order #{order['id']} • ${order['total_cost']:.0f} • {order['status']}"

        with st.expander(title):

            st.write(f"Created: {order['created_at']}")

            details = order.get("details", [])

            if not details:
                st.info("No details in this order")
            else:
                for d in details:
                    st.write(
                        f"- {d['name']} ({d['type']}) | "
                        f"Qty: {d['quantity']} | "
                        f"${d['unit_price']} → ${d['subtotal']}"
                    )