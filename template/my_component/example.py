from my_component import my_component
import streamlit as st

num_clicks = my_component("test", key="foo1")
st.write(num_clicks)
