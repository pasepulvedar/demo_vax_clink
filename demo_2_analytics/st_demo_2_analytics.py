# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

### DISENO ###
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

#####
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
######

hide_decoration_bar_style = '<style> header {visibility: hidden;} </style>'
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

fig_palette =  ['#00857C', '#6ECEB2', '#0C2340', '#BFED33', '#FFF063', '#69B8F7', '#688CE8', '#5450E4']

st.header('Analytics & Recommendations')

tab1, tab2 = st.tabs(['Analytics', "Recommendations"])

### FUNCIONES ###
def df_clean(df):
    df.columns = ['fecha', 'especialidad', 'region', 'id_region', 'comuna', 'sexo', 'edad', 'dosis', 'cantidad']
    df['fecha'] = pd.to_datetime(df.fecha, format='%d-%m-%Y')
    return df

def df_charts(df, fig_palette):
    df1 = df.groupby(['sexo','edad']).cantidad.sum().reset_index()
    fig1 = px.bar(df1, x="edad", y="cantidad", color='sexo', barmode='group',title='Vacunacion por sexo y rango etario', color_discrete_sequence=fig_palette)
    df2 = df.groupby('comuna').cantidad.sum().reset_index()
    fig2 = px.pie(df2, values='cantidad', names='comuna', title='Distribucion comunas vacunados', color_discrete_sequence=fig_palette)
    df3 = df.groupby('especialidad').cantidad.sum().reset_index().sort_values(by='cantidad')
    fig3 = px.bar(df3, x='cantidad', y='especialidad', title='Especialidad prescriptores', color_discrete_sequence=fig_palette)
    df4 = df.groupby('dosis').cantidad.sum().reset_index().sort_values(by='cantidad')
    fig4 = px.bar(df4, x='dosis', y='cantidad', title='Vacunados por dosis', color_discrete_sequence=fig_palette)
    return fig1, fig2, fig3, fig4

def df_dosis(df):
    dosis1_n = df[df.dosis=='1ra'].cantidad.sum()
    dosis1_p = 1
    dosis2_n = df[df.dosis=='2da'].cantidad.sum()
    dosis2_p = dosis2_n/dosis1_n
    dosis3_n = df[df.dosis=='3ra'].cantidad.sum()
    dosis3_p = dosis3_n/dosis1_n
    return dosis1_n, dosis1_p, dosis2_n, dosis2_p, dosis3_n, dosis3_p     


### ANALYTICS ###

with tab1:
    st.subheader('Your personalized analytics with your own data')

    df = pd.read_csv('g9_data_example.csv',encoding='latin-1',sep=';')
    df = df_clean(df)

    fig1, fig2, fig3, fig4 = df_charts(df, fig_palette)

    with st.container():
        col_21, col_22 = st.columns([1,1])
        with col_21:
            st.plotly_chart(fig1 ,use_container_width=True)
        with col_22:
            st.plotly_chart(fig2 ,use_container_width=True, theme=None)
    with st.container():
        col_23, col_24 = st.columns(2)
        with col_23:
            st.plotly_chart(fig3 ,use_container_width=True)
        with col_24:
            st.plotly_chart(fig4 ,use_container_width=True)