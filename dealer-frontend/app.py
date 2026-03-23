import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import importlib
import os

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Dealer Dashboard",
    page_icon="🚗",
    layout="wide"
)

# -------------------------
# STYLE
# -------------------------
from ui.style import load_css
load_css()

# -------------------------
# AUTH CONFIG
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

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
        # HOME / DASHBOARD (NEW FIRST SECTION)
        # -------------------------
        st.markdown("### 📊 Home")

        if st.button("Dashboard", use_container_width=True):
            st.session_state.page = "pages.dashboard"

        st.divider()

        # -------------------------
        # NAVIGATION
        # -------------------------
        st.markdown("### 📋 Inventory")

        if st.button("View Inventory", use_container_width=True):
            st.session_state.page = "pages.vehicle.inventory"

        if st.button("Add Vehicle", use_container_width=True):
            st.session_state.page = "pages.vehicle.add_vehicle"

        st.divider()

        st.markdown("### 🛠 Service Management")

        if st.button("Service Orders", use_container_width=True):
            st.session_state.page = "pages.service.service_orders"
        
        st.divider()

        st.markdown("### 🏷 Auctions")

        if st.button("Auction Calendar", use_container_width=True):
            st.session_state.page = "pages.auction.auction_calendar"

        if st.button("Auction Inventory", use_container_width=True):
            st.session_state.page = "pages.auction.auction_inventory"

#        if st.button("Auction Analytics", use_container_width=True):
#            st.session_state.page = "pages.auction.auction_analytics"

        st.divider()

        st.markdown("### 📊 Reports")

        if st.button("Vehicle Report", use_container_width=True):
            st.session_state.page = "pages.reports.vehicle_report"
        
        st.divider()

        st.markdown("### 🧰 Tools")

        if st.button("Profit Estimator", use_container_width=True):
            st.session_state.page = "pages.dealer.profit_estimator"
        
        if st.button("Market Search", use_container_width=True):
            st.session_state.page = "pages.market.market_search"

        if st.button("Price Trends", use_container_width=True):
            st.session_state.page = "pages.market.price_trends"

        st.divider()

        authenticator.logout("🚪 Logout", "sidebar")


# -------------------------
# MAIN APP
# -------------------------
if st.session_state.get("authentication_status"):

    # DEFAULT PAGE
    if "page" not in st.session_state:
        # st.session_state.page = "pages.vehicle.inventory"
        st.session_state.page = "pages.dashboard"

    # RENDER SIDEBAR
    sidebar_navigation()

    # -------------------------
    # LOAD PAGE MODULE
    # -------------------------
    try:
        module = importlib.import_module(st.session_state.page)
        module.app()

    except ModuleNotFoundError:
        st.error(f"Module '{st.session_state.page}' not found.")

    except AttributeError:
        st.error(f"Module '{st.session_state.page}' must have an app() function.")

    except Exception as e:
        st.error("Unexpected error loading page")
        st.exception(e)

else:
    st.warning("Please log in to continue")
