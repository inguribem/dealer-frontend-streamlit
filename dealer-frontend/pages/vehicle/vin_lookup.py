import streamlit as st
import requests
import pandas as pd


def app():

    st.title("VIN Decoder")

    tab1, tab2 = st.tabs(["Decode VIN", "Advanced Options"])

    with tab1:

        col1, col2 = st.columns([3,1])

        with col1:
            vin = st.text_input("Ingrese VIN")
            st.caption("Example: 1HGCM82637A000001")

        with col2:
            opcion = st.selectbox("Opciones rápidas", ["Decode", "Check History"])

        if vin and st.button("Procesar VIN"):

            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

            r = requests.get(url)
            data = r.json()

            resultados = {
                item['Variable']: item['Value']
                for item in data['Results']
                if item['Value']
            }

            campos = [
                "Make",
                "Model",
                "Model Year",
                "Vehicle Type",
                "Engine Cylinders",
                "Fuel Type - Primary",
                "Transmission Style",
                "Body Class"
            ]

            resumen = {c: resultados.get(c,"N/A") for c in campos}

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Marca", resumen["Make"])
                st.metric("Modelo", resumen["Model"])
                st.metric("Año", resumen["Model Year"])
                st.metric("Tipo Vehículo", resumen["Vehicle Type"])

            with col2:
                st.metric("Cilindros", resumen["Engine Cylinders"])
                st.metric("Combustible", resumen["Fuel Type - Primary"])
                st.metric("Transmisión", resumen["Transmission Style"])
                st.metric("Body Class", resumen["Body Class"])

            st.subheader("Datos completos")

            df = pd.DataFrame(resumen.items(), columns=["Variable","Valor"])

            st.dataframe(df, use_container_width=True)

    with tab2:

        st.write("Opciones avanzadas: historial, reportes PDF, etc.")

