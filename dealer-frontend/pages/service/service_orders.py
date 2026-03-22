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
    # CREAR NUEVA ORDEN
    # -------------------------
    if "current_order_id" not in st.session_state:
        st.session_state["current_order_id"] = None

    if st.button("🆕 Create New Order"):
        try:
            r = requests.post(
                f"{API_URL}/service-orders",
                json={"vehicle_id": selected_vehicle["id"]}
            )
            if r.status_code == 200:
                order_id = r.json().get("order_id")
                st.session_state["current_order_id"] = order_id
                st.success(f"✅ Order created! Order ID: {order_id}")
            else:
                st.error(f"Error creating order: {r.text}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    # -------------------------
    # AGREGAR ITEMS DE CATALOGO
    # -------------------------
    if st.session_state["current_order_id"]:
        order_id = st.session_state["current_order_id"]
        st.subheader(f"Add Items to Order #{order_id}")

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
            added_any = False
            for item_name in selected_items:
                item = df_catalog[df_catalog["display_name"] == item_name].iloc[0]
                payload = {
                    "order_id": order_id,
                    "catalog_item_id": item["id"],
                    "quantity": quantity_inputs[item_name],
                    "unit_price": item.get("base_price", 0)
                }
                try:
                    r = requests.post(f"{API_URL}/order-details", json=payload)
                    if r.status_code != 200:
                        st.error(f"❌ Failed to add {item_name}: {r.text}")
                    else:
                        st.success(f"✅ Added {item_name} x {quantity_inputs[item_name]}")
                        added_any = True
                except Exception as e:
                    st.error(f"❌ Error adding {item_name}: {e}")
            if added_any:
                st.experimental_rerun()

    # -------------------------
    # HISTORIAL DE ÓRDENES DEL VEHÍCULO
    # -------------------------
    st.subheader("Vehicle Orders History")
    try:
        vehicle_orders = requests.get(
            f"{API_URL}/service-orders",
            params={"vehicle_id": selected_vehicle["id"]}
        ).json()
    except Exception as e:
        st.error(f"Failed to fetch vehicle orders: {e}")
        return

    if vehicle_orders:
        df_orders = pd.DataFrame(vehicle_orders)
        if not df_orders.empty:
            # Mostrar con colores según status
            def color_status(val):
                if val == "pending":
                    color = "orange"
                elif val == "in_progress":
                    color = "blue"
                elif val == "completed":
                    color = "green"
                else:
                    color = "grey"
                return f"color: {color}; font-weight: bold"

            st.dataframe(
                df_orders[["id", "status", "total_cost", "created_at"]].style.applymap(color_status, subset=["status"])
            )
        else:
            st.info("No orders for this vehicle yet.")
    else:
        st.info("No orders for this vehicle yet.")
