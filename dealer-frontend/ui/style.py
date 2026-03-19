import streamlit as st

def load_css():

    st.markdown("""
    <style>

    /* dropdown text color */
    div[data-baseweb="select"] span {
        color: #111 !important;
    }

    /* dropdown background */
    div[data-baseweb="popover"] {
        background-color: white !important;
    }

    /* dropdown options text */
    div[data-baseweb="popover"] * {
        color: #111 !important;
    }

    /* selectbox input */
    .stSelectbox label {
        color: #EAEAEA !important;
    }

    /* buttons */
    .stButton button {
        color: white !important;
        background-color: #2563eb !important;
        border-radius: 6px;
        border: none;
    }

    .stButton button:hover {
        background-color: #1d4ed8 !important;
    }

    </style>
    """, unsafe_allow_html=True)
