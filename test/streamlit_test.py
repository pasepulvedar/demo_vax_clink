# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
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

fig_palette =  ['#00857C', '#6ECEB2', '#0C2340', '#BFED33', '#FFF063', '#69B8F7', '#688CE8', '#5450E4']


st.sidebar.header('Carga tus datos para utilizar el Dashboard de Gardasil 9')
file = st.sidebar.file_uploader("Elige un archivo")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Carga archivo D4D", "Analitica y Recomendaciones", "Calculadora Adherencia", "Seguimiento", "Herramientas"])

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

### CARGA DE LOS DATOS ###
with tab1:
    st.header('Carga archivo D4D')

    if file is None:
        st.warning('Cargue un archivo de D4D')
        st.stop()
    else:
        df = pd.read_csv(file,encoding='latin-1',sep=';')
        st.subheader('Data Sell Out Gardasil 9')
        st.write(df)
        df = df_clean(df)

### ANALYTICS AND RECOMMENDATIONS ###
with tab2:
    if file is None:
        st.warning('Cargue un archivo de D4D')
        st.stop()
    else:
        fig1, fig2, fig3, fig4 = df_charts(df, fig_palette)
        st.header('Analitica y Recomendaciones')
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

with tab3:
    if file is None:
        st.warning('Cargue un archivo de D4D')
        st.stop()
    else:
        dosis1_n, dosis1_p, dosis2_n, dosis2_p, dosis3_n, dosis3_p = df_dosis(df)      
        st.header('Adherencia estimada')
        # KPIS
        with st.container():
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric(label="1ra dosis", delta=str(dosis1_n)+' vacunados', value=f"{dosis1_p:.0%}")
            with col4:
                st.metric(label="2da dosis", delta=str(dosis2_n)+' vacunados', value=f"{dosis2_p:.0%}")
            with col5:
                st.metric(label="3ra dosis", delta=str(dosis3_n)+' vacunados', value=f"{dosis3_p:.0%}")
            st.write("---")

        # CALCULADORA
        with st.container():
            st.header('Calculadora mejora de adherencia')
            # inputs
            col_31, col_32 = st.columns(2)
            with col_31:
                precio = st.number_input(label="Precio de venta", format='%d', step=1000, value=130000, help='Ingresa el precio bruto de venta de cada dosis de Gardasil 9') 
                costo = st.number_input(label="Costo neto", step=1000, value=89500, help = 'Ingresa el costo neto que tiene cada dosis')
                dcto = st.text_input(label='Porcentaje descuento sobre el costo', value='3%', help='Ingresa el porcentaje de descuento que tiene cada dosis sobre el costo, si es que aplica')
                dcto = float(dcto.strip('%'))/100
            with col_32:
                adh2 = st.text_input('Objetivo adherencia 2da dosis', value='100%', help='Ingresa objetivo de adherencia en segunda dosis')
                adh2 = float(adh2.strip('%'))/100
                adh3 = st.text_input('Objetivo adherencia 3da dosis', value='100%', help='Ingresa objetivo de adherencia en tercera dosis')
                adh3 = float(adh3.strip('%'))/100
        with st.container():
            col_33, col_34 = st.columns(2)
            with col_33:
                st.dataframe(pd.DataFrame.from_dict({
                    'Precio':[precio, precio/precio],
                    'IVA':[precio*.19, .19],
                    'Costo':[costo, costo/precio]
                    }, columns = ['CLP', '%'], orient='index'), use_container_width=True)
            with col_34:
                st.dataframe(pd.DataFrame.from_dict({
                    'Margen':[precio-precio*.19-costo, (precio-precio*.19-costo)/precio],
                    'Descuento':[costo*dcto, dcto],
                    'Margen Post Descuento':[(precio-precio*.19-costo+costo*dcto), (precio-precio*.19-costo+costo*dcto)/precio]
                    }, columns = ['CLP', '%'], orient='index'), use_container_width=True)
        with st.container():
            col_35, col_36 = st.columns(2)
            with col_35:
                st.subheader('Escenario actual')
                df_curr = pd.DataFrame.from_dict({
                    'Adherencia [%]':[dosis1_p, dosis2_p, dosis3_p],
                    'Venta [dosis]':[dosis1_n, dosis2_n, dosis3_n],
                    'Venta [CLP]':[dosis1_n*precio, dosis2_n*precio, dosis3_n*precio],
                    'Margen [CLP]':[(precio-precio*.19-costo+costo*dcto)*dosis1_n, (precio-precio*.19-costo+costo*dcto)*dosis2_n,(precio-precio*.19-costo+costo*dcto)*dosis3_n]
                    }, columns = ['1ra dosis', '2da dosis', '3ra dosis'], orient='index')   
                st.dataframe(df_curr, use_container_width=True)
            with col_36:
                st.subheader('Escenario potencial')
                df_pot = pd.DataFrame.from_dict({
                    'Adherencia [%]':[1, adh2, adh3],
                    'Venta [dosis]':[dosis1_n, dosis1_n*adh2, dosis1_n*adh3],
                    'Venta [CLP]':[dosis1_n*precio, dosis1_n*adh2*precio, dosis1_n*adh3*precio],
                    'Margen [CLP]':[(precio-precio*.19-costo+costo*dcto)*dosis1_n, (precio-precio*.19-costo+costo*dcto)*dosis1_n*adh2,(precio-precio*.19-costo+costo*dcto)*dosis1_n*adh3]
                    }, columns = ['1ra dosis', '2da dosis', '3ra dosis'], orient='index')   
                st.dataframe(df_pot, use_container_width=True)
            with st.container():
                st.subheader('Oportunidad de ingresos')
                df_opp = pd.DataFrame.from_dict({
                    'Venta [dosis]':[dosis1_n+dosis2_n+dosis3_n, dosis1_n+dosis1_n*adh2+dosis1_n*adh3, ((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))],
                    'Venta [CLP]':[(dosis1_n+dosis2_n+dosis3_n)*precio, (dosis1_n+dosis1_n*adh2+dosis1_n*adh3)*precio,  ((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))*precio],
                    'Margen [CLP]':[(dosis1_n+dosis2_n+dosis3_n)*(precio-precio*.19-costo+costo*dcto), (dosis1_n+dosis1_n*adh2+dosis1_n*adh3)*(precio-precio*.19-costo+costo*dcto),((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))*(precio-precio*.19-costo+costo*dcto)]
                    }, columns = ['Actual', 'Potencial', 'Oportunidad'], orient='index')   
                st.dataframe(df_opp, use_container_width=True)

            st.write("---")

with tab4:
    if file is None:
        st.warning('Cargue un archivo de D4D')
        st.stop()
    else:
        ### SEGUIMIENTO ###
        st.header('Seguimiento')
        #periodo = str(int(st.number_input(label="Ingresa el periodo a consultar"))) 
        list_periodos = (df.fecha.apply(lambda x: x+relativedelta(months=2)).dt.strftime('%Y%m')).unique()
        periodo = st.selectbox('Elige el periodo a consultar',list_periodos)
        periodo_dt = datetime.date(int(periodo[:4]),int(periodo[4:]),1)
        # max periodo + 2 meses
        col12, col13 = st.columns(2)
        with col12:
            df_seg2 = df[(df.dosis=='1ra')&(df.fecha>=str(periodo_dt-relativedelta(months=2)))&(df.fecha<str(periodo_dt-relativedelta(months=1)))]
            st.metric(label="2da dosis", value=len(df_seg2))
            st.write(df_seg2)
        with col13:
            df_seg3 = df[(df.dosis=='2da')&(df.fecha>=str(periodo_dt-relativedelta(months=4)))&(df.fecha<str(periodo_dt-relativedelta(months=3)))]
            st.metric(label="3da dosis", value=len(df_seg3))
            st.write(df_seg3)

with tab5:
    if file is None:
        st.warning('Cargue un archivo de D4D')
        st.stop()
    else:
        ### SEGUIMIENTO ###
        st.header('QR agendamiento')            
        st.image('qr.png')
            
            
