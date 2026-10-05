import streamlit as st

st.set_page_config(page_title="Heart Disease Risk", page_icon="❤️", layout="centered")

page = st.navigation([
    st.Page("predict.py", title="Predict", icon="🩺"),
    st.Page("insights.py", title="Insights", icon="📊"),
    st.Page("about.py", title="About", icon="ℹ️"),
])

page.run()