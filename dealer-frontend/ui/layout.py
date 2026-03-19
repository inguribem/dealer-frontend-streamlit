import streamlit as st

def page_header(title, subtitle=None):

    st.markdown(f"""
    <div style="padding-bottom:10px">
        <h1 style="margin-bottom:0">{title}</h1>
        <p style="color:gray">{subtitle if subtitle else ""}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_cards(metrics):

    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):

        col.metric(
            metric["label"],
            metric["value"],
            metric.get("delta", None)
        )
