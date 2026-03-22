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
    except Exception as e:
        st.error(f"Failed to load vehicles from backend: {e}")
        return

    if df_vehicles.empty:
        st.warning("No vehicles available")
        return

    st.subheader("Select Vehicle")
    selected_vin = st.selectbox("Vehicle VIN", df_vehicles["vin"].tolist(), key="vehicle_select")
    selected_vehicle = df_vehicles[df_vehicles["vin"] == selected_vin].iloc[0]

    st.markdown(f"**{selected_vehicle['year']} {selected_vehicle['make']} {selected_vehicle['model']}**")

    # -------------------------
    # RESET CURRENT ORDER ON VEHICLE CHANGE
    # -------------------------
    if "selected_vin_prev" not in st.session_state:
        st.session_state["selected_vin_prev"] = selected_vin

    if selected_vin != st.session_state["selected_vin_prev"]:
        st.session_state["current_order_id"] = None
        st.session_state["selected_vin_prev"] = selected_vin

    # -------------------------
    # CREATE NEW ORDER
    # -------------------------
    if st.button("🆕 Create New Order"):
        try:
            payload = {"vehicle_id": int(selected_vehicle["id"])}
            r = requests.post(f"{API_URL}/service-orders", json=payload)
            if r.status_code == 200:
                order_id = r.json().get("order_id")
                st.success(f"Order created! Order ID: {order_id}")
                st.session_state["current_order_id"] = order_id
            else:
                st.error(f"Error creating order: {r.text}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    # -------------------------
    # ADD ITEMS TO CURRENT ORDER
    # -------------------------
    if "current_order_id" in st.session_state and st.session_state["current_order_id"]:
        order_id = st.session_state["current_order_id"]
        st.subheader(f"Add Items to Order #{order_id}")

        # Load catalog
        try:
            catalog = requests.get(f"{API_URL}/catalog-items").json()
            if not catalog or not isinstance(catalog, list):
                catalog = []
            df_catalog = pd.DataFrame(catalog)
        except Exception as e:
            st.error(f"Failed to load catalog items: {e}")
            df_catalog = pd.DataFrame()

        if df_catalog.empty:
            st.warning("No catalog items available")
        else:
            df_catalog["display_name"] = df_catalog["name"] + " (" + df_catalog["type"] + ")"
            selected_items = st.multiselect("Select Items", df_catalog["display_name"].tolist(), key="catalog_select")

            quantity_inputs = {}
            for item_name in selected_items:
                quantity_inputs[item_name] = st.number_input(
                    f"Quantity for {item_name}", min_value=1, value=1, step=1, key=f"qty_{item_name}"
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
        vehicle_orders = requests.get(
            f"{API_URL}/service-orders", params={"vehicle_id": int(selected_vehicle["id"])}
        ).json()

        if not vehicle_orders or not isinstance(vehicle_orders, list):
            vehicle_orders = []

        df_orders = pd.DataFrame(vehicle_orders)
        if df_orders.empty:
            st.info("No orders for this vehicle yet.")
        else:
            st.dataframe(df_orders[["id", "status", "total_cost", "created_at"]])

            # -------------------------
            # VIEW ORDER DETAILS PER ORDER
            # -------------------------
            st.subheader("Order Details")
            for order in vehicle_orders:
                order_id = order.get("id")
                st.markdown(f"**Order #{order_id} - Status: {order.get('status', '')}**")
                try:
                    details = requests.get(f"{API_URL}/order-details", params={"order_id": int(order_id)}).json()
                    if not details or not isinstance(details, list):
                        details = []
                    df_details = pd.DataFrame(details)

                    if df_details.empty:
                        st.info("No items in this order yet.")
                    else:
                        # Map catalog_item_id to catalog name
                        catalog_items = requests.get(f"{API_URL}/catalog-items").json()
                        df_catalog = pd.DataFrame(catalog_items)
                        id_to_name = df_catalog.set_index("id")["name"].to_dict()
                        df_details["Item"] = df_details["catalog_item_id"].map(id_to_name)
                        df_details["Total"] = df_details["quantity"] * df_details["unit_price"]

                        st.dataframe(df_details[["Item", "quantity", "unit_price", "Total"]])

                except Exception as e:
                    st.error(f"Failed to fetch order details for order #{order_id}: {e}")

    except Exception as e:
        st.error(f"Failed to fetch all service orders: {e}")
