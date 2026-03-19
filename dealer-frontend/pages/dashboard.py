import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import get_connection
import seaborn as sns

# Configuración general
st.set_page_config(page_title="Dealer Dashboard", layout="wide")
sns.set_style("whitegrid")

def app():
    st.title("🚗 Dealer Intelligence Dashboard")

    # -------------------------
    # Traer datos de la DB
    # -------------------------
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vehicles", conn)
    conn.close()

    if df.empty:
        st.warning("No vehicles found in the database.")
        return

    # -------------------------
    # Limpieza y conversión
    # -------------------------
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["miles"] = pd.to_numeric(df["miles"], errors="coerce")

    # -------------------------
    # Filtros interactivos
    # -------------------------
    st.sidebar.subheader("Filters")
    makes = st.sidebar.multiselect("Select Make", df["make"].dropna().unique())
    years = st.sidebar.slider("Year Range", int(df["year"].min()), int(df["year"].max()), (int(df["year"].min()), int(df["year"].max())))
    price_range = st.sidebar.slider("Price Range", int(df["price"].min() or 0), int(df["price"].max() or 100000), (0, int(df["price"].max() or 100000)))

    # Aplicar filtros
    filtered_df = df.copy()
    if makes:
        filtered_df = filtered_df[filtered_df["make"].isin(makes)]
    filtered_df = filtered_df[(filtered_df["year"] >= years[0]) & (filtered_df["year"] <= years[1])]
    filtered_df = filtered_df[(filtered_df["price"].fillna(0) >= price_range[0]) & (filtered_df["price"].fillna(0) <= price_range[1])]

    # -------------------------
    # KPIs tipo tarjeta
    # -------------------------
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Vehicles", len(filtered_df))
    avg_price = int(filtered_df["price"].mean()) if filtered_df["price"].notna().any() else 0
    col2.metric("Average Price", f"${avg_price:,}")
    top_make = filtered_df["make"].mode()[0] if not filtered_df["make"].empty else "N/A"
    col3.metric("Top Make", top_make)
    avg_miles = int(filtered_df["miles"].mean()) if filtered_df["miles"].notna().any() else 0
    col4.metric("Avg Miles", f"{avg_miles:,}")

    st.divider()

    # -------------------------
    # Gráficos
    # -------------------------
    st.subheader("Inventory by Make")
    fig1, ax1 = plt.subplots(figsize=(8,4))
    sns.countplot(data=filtered_df, x="make", palette="Set2", order=filtered_df["make"].value_counts().index, ax=ax1)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    st.subheader("Price Distribution")
    fig2, ax2 = plt.subplots(figsize=(8,4))
    sns.histplot(filtered_df["price"].dropna(), bins=20, color="#1f77b4", kde=True, ax=ax2)
    st.pyplot(fig2)

    st.subheader("Vehicles by Year")
    year_counts = filtered_df["year"].value_counts().sort_index()
    fig3, ax3 = plt.subplots(figsize=(8,4))
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o", color="#ff7f0e", ax=ax3)
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Count")
    st.pyplot(fig3)

    # -------------------------
    # Tabla interactiva
    # -------------------------
    st.subheader("Inventory Table")
    st.dataframe(filtered_df.style.format({
        "price": "${:,.0f}",
        "miles": "{:,.0f}"
    }), use_container_width=True)
