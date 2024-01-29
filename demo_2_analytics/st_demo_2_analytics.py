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

hide_decoration_bar_style = '<style> header {visibility: hidden;} </style>'
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

fig_palette =  ['#00857C', '#6ECEB2', '#0C2340', '#BFED33', '#FFF063', '#69B8F7', '#688CE8', '#5450E4']

st.header('Analytics & Recommendations')

tab1, tab2, tab3 = st.tabs(['Your Analytics', 'Regional Analytics', "Recommendations"])

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
    df4 = df.groupby('dosis').cantidad.sum().reset_index().sort_values(by='cantidad', ascending=False)
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
            st.plotly_chart(fig2 ,use_container_width=True)
    with st.container():
        col_23, col_24 = st.columns(2)
        with col_23:
            st.plotly_chart(fig3 ,use_container_width=True)
        with col_24:
            st.plotly_chart(fig4 ,use_container_width=True)

with tab2:
    st.subheader('Regional analytics for benchmarking and opportunities')

    df = pd.read_csv('g9_data_region.csv',encoding='latin-1',sep=';')
    df = df_clean(df)

    fig1, fig2, fig3, fig4 = df_charts(df, fig_palette)

    with st.container():
        col_21, col_22 = st.columns([1,1])
        with col_21:
            st.plotly_chart(fig1 ,use_container_width=True)
        with col_22:
            st.plotly_chart(fig2 ,use_container_width=True)
    with st.container():
        col_23, col_24 = st.columns(2)
        with col_23:
            st.plotly_chart(fig3 ,use_container_width=True)
        with col_24:
            st.plotly_chart(fig4 ,use_container_width=True)

with tab3:
    st.subheader('Purchase recommendation based on historical data')
    _ = df.copy()
    _['period'] = _.fecha.dt.strftime('%Y-%m') 
    _ = _.groupby('period').cantidad.sum().reset_index().rename(columns={'cantidad':'units'})
    col_25, col_26 = st.columns(2)
    with col_25:
        fig5 = px.line(_, x="period", y="units", color_discrete_sequence=fig_palette)
        fig5.update_traces(mode='markers+lines')
        fig5.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig5 ,use_container_width=True)
    with col_26:
        st.markdown("#")
        st.markdown("#")
        st.markdown('<div style="font-size:24px"> Based on our records, your historical data and projected demand we recommend you to buy for the current month:</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:50px;color:#00857C"> <b>18</b></div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:24px"> units</div>', unsafe_allow_html=True)
        st.markdown("#")
        col_b1, col_b2, col_b3 = st.columns([1,2,1])
        with col_b2:
            st.link_button("Add it to your shopping cart! :shopping_trolley:", url='https://orders.msdcustomerlink.cl', type='primary', use_container_width=True)