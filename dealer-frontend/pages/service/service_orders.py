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
    # RESET CURRENT ORDER
    # -------------------------
    if "selected_vin_prev" not in st.session_state:
        st.session_state["selected_vin_prev"] = selected_vin

    if selected_vin != st.session_state["selected_vin_prev"]:
        st.session_state["current_order_id"] = None
        st.session_state["selected_vin_prev"] = selected_vin

    # -------------------------
    # CREATE ORDER
    # -------------------------
    if st.button("🆕 Create New Order"):
        try:
            payload = {"vehicle_id": int(selected_vehicle["id"])}
            r = requests.post(f"{API_URL}/service-orders", json=payload)

            if r.status_code == 200:
                order_id = r.json().get("order_id")
                st.success(f"Order created! ID: {order_id}")
                st.session_state["current_order_id"] = order_id
            else:
                st.error(r.text)
        except Exception as e:
            st.error(e)

    # -------------------------
    # ADD ITEMS
    # -------------------------
    if st.session_state.get("current_order_id"):
        order_id = st.session_state["current_order_id"]
        st.subheader(f"Add Items to Order #{order_id}")

        try:
            catalog = requests.get(f"{API_URL}/catalog-items").json()
            df_catalog = pd.DataFrame(catalog if isinstance(catalog, list) else [])
        except:
            df_catalog = pd.DataFrame()

        if df_catalog.empty:
            st.warning("No catalog items available")
        else:
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
                    min_value=1,
                    value=1,
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
                        st.error(r.text)

                st.rerun()

    # -------------------------
    # ORDER HISTORY
    # -------------------------
    st.subheader("Vehicle Orders History")

    try:
        vehicle_orders = requests.get(
            f"{API_URL}/service-orders",
            params={"vehicle_id": int(selected_vehicle["id"])}
        ).json()

        if not isinstance(vehicle_orders, list):
            vehicle_orders = []

        if not vehicle_orders:
            st.info("No orders for this vehicle yet.")

        else:
            for order in vehicle_orders:
                order_id = order.get("id")
                current_status = order.get("status", "pending")

                title = f"🧾 Order #{order_id} • ${order.get('total_cost', 0)} • {current_status}"

                with st.expander(title):

                    col1, col2 = st.columns([3,1])

                    status_options = ["pending", "in_progress", "completed"]

                    selected_status = col1.selectbox(
                        "Status",
                        status_options,
                        index=status_options.index(current_status)
                        if current_status in status_options else 0,
                        key=f"status_{order_id}"
                    )

                    changed = selected_status != current_status

                    if col2.button("💾", key=f"save_{order_id}", disabled=not changed):
                        st.session_state["update_order"] = {
                            "id": order_id,
                            "status": selected_status
                        }

                    st.divider()

                    # -------------------------
                    # DETAILS
                    # -------------------------
                    try:
                        details = requests.get(
                            f"{API_URL}/order-details",
                            params={"order_id": int(order_id)}
                        ).json()

                        df_details = pd.DataFrame(details if isinstance(details, list) else [])

                        if df_details.empty:
                            st.info("No items in this order yet.")
                        else:
                            catalog_items = requests.get(f"{API_URL}/catalog-items").json()
                            df_catalog = pd.DataFrame(catalog_items)

                            id_to_name = df_catalog.set_index("id")["name"].to_dict()
                            df_details["Item"] = df_details["catalog_item_id"].map(id_to_name)

                            for _, row in df_details.iterrows():

                                did = row["id"]

                                col1, col2, col3, col4, col5, col6 = st.columns([3,1,1,1,1,1])

                                col1.write(row["Item"])

                                col2.number_input(
                                    "Qty",
                                    value=int(row["quantity"]),
                                    min_value=1,
                                    key=f"qty_{did}"
                                )

                                col3.number_input(
                                    "Price",
                                    value=float(row["unit_price"]),
                                    min_value=0.0,
                                    step=0.01,
                                    key=f"price_{did}"
                                )

                                qty = st.session_state.get(f"qty_{did}")
                                price = st.session_state.get(f"price_{did}")

                                col4.write(f"${(qty or 0) * (price or 0):.2f}")

                                if col5.button("✏️", key=f"upd_{did}"):
                                    st.session_state["update_detail_id"] = did

                                if col6.button("🗑️", key=f"del_{did}"):
                                    st.session_state["delete_detail_id"] = did

                    except Exception as e:
                        st.error(e)

    except Exception as e:
        st.error(e)

    # -------------------------
    # ACTION HANDLERS
    # -------------------------

    # UPDATE ORDER
    if "update_order" in st.session_state:
        data = st.session_state["update_order"]

        r = requests.put(
            f"{API_URL}/service-orders/{data['id']}",
            json={"status": data["status"]}
        )

        if r.status_code == 200:
            st.success("Order updated")
        else:
            st.error(r.text)

        del st.session_state["update_order"]
        st.rerun()

    # UPDATE DETAIL
    if "update_detail_id" in st.session_state:
        did = st.session_state["update_detail_id"]

        qty = st.session_state.get(f"qty_{did}")
        price = st.session_state.get(f"price_{did}")

        if qty is not None and price is not None:
            r = requests.put(
                f"{API_URL}/order-details/{did}",
                json={
                    "quantity": int(qty),
                    "unit_price": float(price)
                }
            )

            if r.status_code == 200:
                st.success("Detail updated")
            else:
                st.error(r.text)

        del st.session_state["update_detail_id"]
        st.rerun()

    # DELETE DETAIL
    if "delete_detail_id" in st.session_state:
        did = st.session_state["delete_detail_id"]

        r = requests.delete(f"{API_URL}/order-details/{did}")

        if r.status_code == 200:
            st.success("Detail deleted")
        else:
            st.error(r.text)

        del st.session_state["delete_detail_id"]
        st.rerun()
