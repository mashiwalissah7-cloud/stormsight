"""StormSight's first interface. Data and model connections come next."""

import streamlit as st

st.set_page_config(page_title="StormSight", page_icon="🌀", layout="wide")

st.title("StormSight")
st.write("Explore hurricane flood insurance losses with public data and AI explanations.")
st.warning("Research and education only. StormSight is not a commercial catastrophe model.")
st.caption("Development preview. No datasets, trained loss model, or AI service are connected yet.")

briefing, portfolio, validation = st.tabs(["Storm briefing", "Portfolio", "Does it work?"])

with briefing:
    st.header("Storm briefing")
    st.info("Verified storm tracks and county loss estimates will appear here after the data and model are ready.")

with portfolio:
    st.header("Portfolio exposure")
    st.info("Portfolio uploads will be enabled after the county matching and exposure calculations are tested.")

with validation:
    st.header("Does it work?")
    st.info("Results will appear here after testing on storms excluded from model training. No accuracy claims are available yet.")
