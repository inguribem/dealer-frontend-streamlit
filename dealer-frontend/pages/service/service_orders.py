import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():
    st.title("🛠 Service Orders")

    # -------------------------
    # CARGAR VEHÍCULOS
    # -------------------------
    try:
        vehicles = requests.get(f"{API_URL}/vehicles/inventory").json()
        df_vehicles = pd.DataFrame(vehicles)
    except Exception as e:
        st.error(f"Failed to load vehicles from backend: {e}")
        return

    if df_vehicles.empty:
        st.warning("No vehicles available")
        return

    st.subheader("Select Vehicle")
    vehicle_vin_list = df_vehicles["vin"].tolist()
    selected_vin = st.selectbox("Vehicle VIN", vehicle_vin_list)

    selected_vehicle = df_vehicles[df_vehicles["vin"] == selected_vin].iloc[0]
    st.markdown(f"**{selected_vehicle['year']} {selected_vehicle['make']} {selected_vehicle['model']}**")

    # -------------------------
    # CREAR ORDEN
    # -------------------------
    if st.button("🆕 Create New Order"):
        try:
            r = requests.post(
                f"{API_URL}/service-orders",
                params={"vehicle_id": int(selected_vehicle["id"])}  # << CORRECTO: query param
            )
            if r.status_code == 200:
                resp_json = r.json()
                order_id = resp_json.get("order_id")
                if order_id is None:
                    st.error(f"Backend did not return order_id: {resp_json}")
                    return
                st.success(f"Order created! Order ID: {order_id}")
                st.session_state["current_order_id"] = order_id
            else:
                st.error(f"Error creating order: {r.text}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    # -------------------------
    # AGREGAR ITEMS DE CATALOGO
    # -------------------------
    if "current_order_id" in st.session_state:
        order_id = st.session_state["current_order_id"]

        st.subheader(f"Add Items to Order #{order_id}")

        # Traer catálogo
        try:
            catalog = requests.get(f"{API_URL}/catalog-items").json()
            df_catalog = pd.DataFrame(catalog)
        except Exception as e:
            st.error(f"Failed to load catalog items: {e}")
            return

        if df_catalog.empty:
            st.warning("No catalog items available")
            return

        df_catalog["display_name"] = df_catalog["name"] + " (" + df_catalog["type"] + ")"
        selected_items = st.multiselect(
            "Select Items",
            options=df_catalog["display_name"].tolist()
        )

        quantity_inputs = {}
        for item_name in selected_items:
            quantity_inputs[item_name] = st.number_input(
                f"Quantity for {item_name}",
                min_value=1, value=1, step=1
            )

        if st.button("➕ Add Selected Items"):
            for item_name in selected_items:
                item = df_catalog[df_catalog["display_name"] == item_name].iloc[0]
                payload = {
                    "order_id": int(order_id),
                    "catalog_item_id": int(item["id"]),
                    "quantity": int(quantity_inputs[item_name]),
                    "unit_price": float(item.get("base_price", 0))
                }
                r_item = requests.post(f"{API_URL}/order-details", json=payload)
                if r_item.status_code != 200:
                    st.error(f"Failed to add {item_name}: {r_item.text}")
                else:
                    st.success(f"Added {item_name} x {quantity_inputs[item_name]}")
