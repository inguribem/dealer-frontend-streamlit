import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def app():
    st.title("🛠 Service Orders")

    # -------------------------
    # LOAD VEHICLES
    # -------------------------
    try:
        vehicles = requests.get(f"{API_URL}/vehicles/inventory").json()
        df_vehicles = pd.DataFrame(vehicles)
    except:
        st.error("Failed to load vehicles from backend")
        return

    if df_vehicles.empty:
        st.warning("No vehicles available")
        return

    st.subheader("Select Vehicle")
    selected_vin = st.selectbox("Vehicle VIN", df_vehicles["vin"].tolist())
    selected_vehicle = df_vehicles[df_vehicles["vin"] == selected_vin].iloc[0]
    st.markdown(f"**{selected_vehicle['year']} {selected_vehicle['make']} {selected_vehicle['model']}**")

    # -------------------------
    # CREATE NEW ORDER
    # -------------------------
    if st.button("🆕 Create New Order"):
        try:
            payload = {"vehicle_id": selected_vehicle["id"]}
            r = requests.post(f"{API_URL}/service-orders", json=payload)
            if r.status_code == 200:
                order_id = r.json().get("order_id")
                st.success(f"Order created! Order ID: {order_id}")
                st.session_state["current_order_id"] = order_id
            else:
                st.error(f"Error creating order: {r.text}")
                return
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            return

    # -------------------------
    # ADD ITEMS TO ORDER
    # -------------------------
    if "current_order_id" in st.session_state:
        order_id = st.session_state["current_order_id"]
        st.subheader(f"Add Items to Order #{order_id}")

        try:
            catalog = requests.get(f"{API_URL}/catalog-items").json()
            df_catalog = pd.DataFrame(catalog)
        except:
            st.error("Failed to load catalog items")
            return

        if df_catalog.empty:
            st.warning("No catalog items available")
            return

        df_catalog["display_name"] = df_catalog["name"] + " (" + df_catalog["type"] + ")"
        selected_items = st.multiselect("Select Items", df_catalog["display_name"].tolist())

        quantity_inputs = {}
        for item_name in selected_items:
            quantity_inputs[item_name] = st.number_input(f"Quantity for {item_name}", min_value=1, value=1, step=1)

        if st.button("➕ Add Selected Items"):
            for item_name in selected_items:
                item = df_catalog[df_catalog["display_name"] == item_name].iloc[0]
                payload = {
                    "order_id": order_id,
                    "catalog_item_id": item["id"],
                    "quantity": quantity_inputs[item_name],
                    "unit_price": item.get("base_price", 0)
                }
                r = requests.post(f"{API_URL}/order-details", json=payload)
                if r.status_code != 200:
                    st.error(f"Failed to add {item_name}: {r.text}")
                else:
                    st.success(f"Added {item_name} x {quantity_inputs[item_name]}")

    # -------------------------
    # VEHICLE ORDER HISTORY
    # -------------------------
    st.subheader("Vehicle Orders History")
    try:
        vehicle_orders = requests.get(f"{API_URL}/service-orders", params={"vehicle_id": selected_vehicle["id"]}).json()
        if vehicle_orders:
            df_orders = pd.DataFrame(vehicle_orders)
            st.dataframe(df_orders[["id", "status", "total_cost", "created_at"]])
        else:
            st.info("No orders for this vehicle yet.")
    except Exception as e:
        st.error(f"Failed to fetch orders: {e}")

