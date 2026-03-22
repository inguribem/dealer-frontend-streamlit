import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets["API_URL"]

def app():
    st.title("🛠 Service Orders")

    # -------------------------
    # VEHICLE SEARCH
    # -------------------------
    vin = st.text_input("Enter VIN")

    if st.button("Find Vehicle"):
        r = requests.get(f"{API_URL}/vehicles/inventory", params={"search": vin})
        data = r.json()

        if data:
            st.session_state.vehicle = data[0]
            st.success("Vehicle found")
        else:
            st.error("Vehicle not found")

    v = st.session_state.get("vehicle")

    if v:
        st.write(f"**Vehicle:** {v['year']} {v['make']} {v['model']}")

        # -------------------------
        # CREATE ORDER
        # -------------------------
        if st.button("Create Service Order"):

            vehicle_id = v.get("id")

            # Validación básica
            if not vehicle_id:
                st.error("Vehicle ID not found. Check backend response.")
                st.stop()

            # Request al backend
            r = requests.post(
                f"{API_URL}/service-orders",
                params={"vehicle_id": vehicle_id}
            )

            # Debug de respuesta
            if r.status_code != 200:
                st.error(f"Backend error: {r.status_code}")
                st.text(r.text)
                st.stop()

            # Validar JSON
            try:
                data = r.json()
            except:
                st.error("Response is not valid JSON")
                st.text(r.text)
                st.stop()

            # Validar contenido
            order_id = data.get("order_id")

            if not order_id:
                st.error(f"Unexpected response: {data}")
                st.stop()

            # Guardar en session
            st.session_state.order_id = order_id

            st.success(f"Order {order_id} created")


    # -------------------------
    # ADD ITEMS
    # -------------------------
    if "order_id" in st.session_state:

        st.subheader("Add Items")

        catalog = requests.get(f"{API_URL}/catalog-items").json()
        df_catalog = pd.DataFrame(catalog)

        item = st.selectbox("Select Item", df_catalog["name"])
        quantity = st.number_input("Quantity", 1)

        if st.button("Add Item"):
            item_id = df_catalog[df_catalog["name"] == item]["id"].values[0]

            requests.post(
                f"{API_URL}/service-orders/{st.session_state.order_id}/items",
                params={"catalog_item_id": item_id, "quantity": quantity}
            )

            st.success("Item added")

        # -------------------------
        # VIEW ORDER
        # -------------------------
        order = requests.get(f"{API_URL}/service-orders/{st.session_state.order_id}").json()

        st.subheader("Order Details")
        st.json(order)

        if st.button("Complete Order"):
            requests.put(f"{API_URL}/service-orders/{st.session_state.order_id}/complete")
            st.success("Order completed")
