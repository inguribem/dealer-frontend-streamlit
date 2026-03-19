import streamlit as st

def vehicle_card(vehicle):

    with st.container():

        col1, col2 = st.columns([1,3])

        with col1:

            if "image_url" in vehicle:
                st.image(vehicle["image_url"], width=120)

        with col2:

            st.markdown(
                f"### {vehicle.get('year','')} {vehicle.get('make','')} {vehicle.get('model','')}"
            )

            if "price" in vehicle:
                st.write(f"Price: ${vehicle['price']}")

            if "miles" in vehicle:
                st.write(f"Miles: {vehicle['miles']}")

            if "vdp_url" in vehicle:
                st.link_button("View Listing", vehicle["vdp_url"])
