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
                return
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            return

    # -------------------------
    # ADD ITEMS TO ORDER
    # -------------------------
    if "current_order_id" in st.session_state and st.session_state["current_order_id"]:
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
            df_catalog["display_name"].tolist(),
            key="catalog_select"
        )

        quantity_inputs = {}
        for item_name in selected_items:
            quantity_inputs[item_name] = st.number_input(
                f"Quantity for {item_name}",
                min_value=1, value=1, step=1,
                key=f"qty_{item_name}"
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
            f"{API_URL}/service-orders",
            params={"vehicle_id": int(selected_vehicle["id"])}
        ).json()

        if vehicle_orders:
            df_orders = pd.DataFrame(vehicle_orders)
            if not df_orders.empty:
                st.dataframe(df_orders[["id", "status", "total_cost", "created_at"]])
            else:
                st.info("No orders for this vehicle yet.")
        else:
            st.info("No orders for this vehicle yet.")
    except Exception as e:
        st.error(f"Failed to fetch orders: {e}")

    # -------------------------
    # ORDER DETAILS PER ORDER WITH EDIT & DELETE
    # -------------------------
    st.subheader("Order Details by Order")
    if vehicle_orders:
        for order in vehicle_orders:
            order_id = order.get("id")
            if not order_id:
                continue
            with st.expander(f"Order #{order_id} - Status: {order.get('status')}"):
                try:
                    details = requests.get(
                        f"{API_URL}/order-details",
                        params={"order_id": int(order_id)}
                    ).json()
                    if details:
                        df_details = pd.DataFrame(details)
                        if not df_details.empty:
                            df_details_display = df_details[["catalog_item_name", "type", "quantity", "unit_price"]].copy()
                            df_details_display.columns = ["Item", "Type", "Quantity", "Unit Price"]

                            # Editable quantities
                            edited_quantities = {}
                            for i, row in df_details.iterrows():
                                q_key = f"qty_{order_id}_{row['catalog_item_id']}"
                                edited_quantities[row["catalog_item_id"]] = st.number_input(
                                    f"{row['catalog_item_name']} (Order #{order_id})",
                                    min_value=1,
                                    value=int(row["quantity"]),
                                    step=1,
                                    key=q_key
                                )
                                # Delete checkbox
                                del_key = f"del_{order_id}_{row['catalog_item_id']}"
                                df_details.loc[i, "delete"] = st.checkbox(
                                    "Delete",
                                    value=False,
                                    key=del_key
                                )

                            # Update quantities
                            if st.button(f"💾 Update Order #{order_id}"):
                                for item_id, new_qty in edited_quantities.items():
                                    payload = {"quantity": int(new_qty)}
                                    r = requests.put(
                                        f"{API_URL}/order-details/{order_id}/{item_id}",
                                        json=payload
                                    )
                                    if r.status_code != 200:
                                        st.error(f"Failed to update item {item_id}: {r.text}")
                                st.success("Order updated")
                                st.experimental_rerun()

                            # Delete items
                            if st.button(f"🗑 Delete Selected Items from Order #{order_id}"):
                                for i, row in df_details.iterrows():
                                    if row.get("delete"):
                                        item_id = int(row["catalog_item_id"])
                                        r = requests.delete(
                                            f"{API_URL}/order-details/{order_id}/{item_id}"
                                        )
                                        if r.status_code != 200:
                                            st.error(f"Failed to delete item {item_id}: {r.text}")
                                st.success("Selected items deleted")
                                st.experimental_rerun()

                        else:
                            st.info("No items in this order yet.")
                    else:
                        st.info("No items in this order yet.")
                except Exception as e:
                    st.error(f"Failed to fetch order details for order #{order_id}: {e}")
