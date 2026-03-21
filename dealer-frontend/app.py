# frontend/app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import importlib
import os

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Dealer Dashboard", page_icon="🚗", layout="wide")

# -------------------------
# LOAD CSS
# -------------------------
from ui.style import load_css
load_css()

# -------------------------
# LOAD CONFIG
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# -------------------------
# AUTH
# -------------------------
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

authenticator.login(location="main")

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
def sidebar_navigation():
    with st.sidebar:
        st.markdown("## 🚗 Dealer Dashboard")

        name = st.session_state.get("name", "User")
        st.markdown(f"👤 **{name}**")

        st.divider()

        # -------------------------
        # INVENTORY FILTERS (ONLY ON INVENTORY PAGE)
        # -------------------------
        if st.session_state.get("page") == "pages.vehicle.inventory":
            st.markdown("### 🔍 Inventory Filters")

            st.text_input("Search (Inventory)", key="inv_search")
            st.selectbox(
                "Make",
                ["All", "Toyota", "BMW", "Ford"],
                key="inv_make"
            )
            st.selectbox(
                "Year",
                ["All", "2024", "2023", "2022"],
                key="inv_year"
            )

            st.divider()

        # -------------------------
        # QUICK ACTIONS
        # -------------------------
        st.markdown("### ⚡ Quick Actions")

        if st.button("➕ Add Vehicle", use_container_width=True):
            st.session_state.page = "pages.vehicle.add_vehicle"

        st.divider()

        # -------------------------
        # NAVIGATION
        # -------------------------
        st.markdown("### 📋 Inventory")

        if st.button("View Inventory", use_container_width=True):
            st.session_state.page = "pages.vehicle.inventory"

        st.divider()

        st.markdown("### 🏷 Auctions")

        if st.button("Auction Inventory", use_container_width=True):
            st.session_state.page = "pages.auction.auction_inventory"

        if st.button("Auction Analytics", use_container_width=True):
            st.session_state.page = "pages.auction.auction_analytics"

        st.divider()

        st.markdown("### 📊 Insights")

        if st.button("Market Trends", use_container_width=True):
            st.session_state.page = "pages.market.market_search"

        if st.button("Price Trends", use_container_width=True):
            st.session_state.page = "pages.market.price_trends"

        st.divider()

        st.markdown("### 🧰 Tools")

        if st.button("Profit Estimator", use_container_width=True):
            st.session_state.page = "pages.dealer.profit_estimator"

        st.divider()

        authenticator.logout("🚪 Logout", "sidebar")


# -------------------------
# MAIN APP
# -------------------------
if st.session_state.get("authentication_status"):

    # DEFAULT PAGE
    if "page" not in st.session_state:
        st.session_state.page = "pages.vehicle.inventory"

    # LOAD SIDEBAR
    sidebar_navigation()

    # LOAD PAGE
    try:
        module = importlib.import_module(st.session_state.page)
        module.app()
    except ModuleNotFoundError:
        st.error(f"Module {st.session_state.page} not found. Check structure.")
    except AttributeError:
        st.error(f"Module {st.session_state.page} does not have an app() function.")
    except Exception as e:
        st.error("Unexpected error loading page")
        st.exception(e)

else:
    st.warning("Enter user and password")
