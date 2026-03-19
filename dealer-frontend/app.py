# frontend/app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import importlib
import sys
import os
from pages.vehicle_intelligence import app as intelligence_app

# st.write("Current path:", os.getcwd())
# st.write("Files here:", os.listdir())
# st.write("Frontend files:", os.listdir(os.path.dirname(__file__)))

# -----------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Dealer Dashboard", page_icon="🚗", layout="wide")

from ui.style import load_css
load_css()

API_URL = st.secrets["API_URL"]

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

if st.session_state.get("authentication_status"):

    name = st.session_state["name"]
    st.sidebar.title("🚗 Dealer Dashboard")
    st.sidebar.success(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")

    menu = {
        "Dashboard": "pages.dashboard",
        "Vehicle Intelligence": {
            "VIN Lookup": "pages.vehicle.vin_lookup",
            "Add Vehicle": "pages.vehicle.add_vehicle",
            "Inventory": "pages.vehicle.inventory",
            "Analytics Dashboard": "pages.vehicle.vehicle_intelligence"
        },
        "Market Intelligence": {
            "Market Search": "pages.market.market_search",
            "Price Trends": "pages.market.price_trends"
        },
        "Auction Intelligence": {
            "Auction Inventory": "pages.auction.auction_inventory",
            "Auction Analytics": "pages.auction.auction_analytics"
        },
        "Dealer Tools": {
            "Profit Estimator": "pages.dealer.profit_estimator"
        }
    }

    section = st.sidebar.selectbox("Module", list(menu.keys()))

    if isinstance(menu[section], dict):
        page = st.sidebar.radio("Tool", list(menu[section].keys()))
        module_path = menu[section][page]
    else:
        module_path = menu[section]

    try:
        module = importlib.import_module(module_path)
        module.app()
    except ModuleNotFoundError:
        st.error(f"Module {module_path} not found. Please check __init__.py")
    except AttributeError:
        st.error(f"Module {module_path} does not have an app() function.")

else:
    st.warning("Ingrese usuario y contraseña")

