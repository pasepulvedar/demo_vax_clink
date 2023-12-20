# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")

st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

hide_decoration_bar_style = '<style> header {visibility: hidden;} </style>'
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

### CARGA DE LOS DATOS ###

st.sidebar.header('Upload D4D File')
file = st.sidebar.file_uploader("Choose a file")

st.header('Consolidated Monthly Data to access to the 3% of discount')


if file is None:
    st.warning('Upload a file')
    st.stop()  
else:
    df = pd.read_csv(file,encoding='latin-1',sep=';')
    st.subheader('Data Sell Out Gardasil 9')
    st.write(df, use_container_width=True)
