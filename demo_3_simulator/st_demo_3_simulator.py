# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import datetime
from dateutil.relativedelta import relativedelta

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

st.header('Financial Simulator & Adherence Tools')

#tab1, tab2, tab3 = st.tabs(['Financial Simulator', "Adherence Tools", "Credit Notes"])
tab1, tab2 = st.tabs(['Financial Simulator', "Adherence Tools"])

### FUNCIONES ###
def df_clean(df):
    df.columns = ['fecha', 'especialidad', 'region', 'id_region', 'comuna', 'sexo', 'edad', 'dosis', 'cantidad']
    df['fecha'] = pd.to_datetime(df.fecha, format='%d-%m-%Y')
    return df

def df_dosis(df):
    dosis1_n = df[df.dosis=='1ra'].cantidad.sum()
    dosis1_p = 1
    dosis2_n = df[df.dosis=='2da'].cantidad.sum()
    dosis2_p = dosis2_n/dosis1_n
    dosis3_n = df[df.dosis=='3ra'].cantidad.sum()
    dosis3_p = dosis3_n/dosis1_n
    return dosis1_n, dosis1_p, dosis2_n, dosis2_p, dosis3_n, dosis3_p     


### SIMULATOR ###

df = pd.read_csv('g9_data_example.csv',encoding='latin-1',sep=';')
df = df_clean(df)

with tab1:
    st.subheader('Revenue simulator base on change in adhrence')
    dosis1_n, dosis1_p, dosis2_n, dosis2_p, dosis3_n, dosis3_p = df_dosis(df)      
    st.subheader(':gray[Estimated adherence]')

    # KPIS
    with st.container():
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric(label="1st dose", delta=str(dosis1_n)+' vaccinated', value=f"{dosis1_p:.0%}")
        with col4:
            st.metric(label="2nd dose", delta=str(dosis2_n)+' vaccinated', value=f"{dosis2_p:.0%}")
        with col5:
            st.metric(label="3rd dose", delta=str(dosis3_n)+' vaccinated', value=f"{dosis3_p:.0%}")
        st.write("---")
        
    # CALCULADORA###
    with st.container():
        st.subheader(':gray[Simulator]')
        # inputs
        col_31, col_32 = st.columns(2)
        with col_31:
            precio = st.number_input(label="Sales price", format='%d', step=1000, value=130000, help='Enter the gross sales price of each dose of Gardasil 9') 
            costo = st.number_input(label="Net cost", step=1000, value=89500, help = 'Enter the net cost of each dose')
            dcto = st.text_input(label='Discount percentage on cost', value='3%', help='Enter the percentage discount that each dose has on the cost, if applicable')
            dcto = float(dcto.strip('%'))/100
        with col_32:
            adh2 = st.text_input('Adherence goal 2nd dose', value='80%', help='Enter adherence target in second dose')
            adh2 = float(adh2.strip('%'))/100
            adh3 = st.text_input('Adherence goal 3rd dose', value='70%', help='Enter adherence target in third dose')
            adh3 = float(adh3.strip('%'))/100
    with st.container():
        col_33, col_34 = st.columns(2)
        with col_33:
            _ = pd.DataFrame.from_dict({
                'Price':[precio, precio/precio],
                'Tax':[precio*.19, .19],
                'Cost':[costo, costo/precio]
                }, columns = ['CLP', '%'], orient='index')
            _['%']=(_['%']*100).round(1).astype(str)+'%' 
            _['CLP']=_['CLP'].apply(lambda x: '{:,}'.format(int(x)))
            st.dataframe(_, use_container_width=True)
        with col_34:
            _ = pd.DataFrame.from_dict({
                'Margin':[precio-precio*.19-costo, (precio-precio*.19-costo)/precio],
                'Discount':[costo*dcto, dcto],
                'Post discount margin':[(precio-precio*.19-costo+costo*dcto), (precio-precio*.19-costo+costo*dcto)/precio]
                }, columns = ['CLP', '%'], orient='index')
            _['%']=(_['%']*100).round(1).astype(str)+'%' 
            _['CLP']=_['CLP'].apply(lambda x: '{:,}'.format(int(x)))
            st.dataframe(_, use_container_width=True)
    with st.container():
        col_35, col_36 = st.columns(2)
        with col_35:
            st.subheader(':gray[Current scenario]')
            _ = pd.DataFrame.from_dict({
                'Adherence [%]':[dosis1_p, dosis2_p, dosis3_p],
                'Sales [doses]':[dosis1_n, dosis2_n, dosis3_n],
                'Sales [CLP]':[dosis1_n*precio, dosis2_n*precio, dosis3_n*precio],
                'Margin [CLP]':[(precio-precio*.19-costo+costo*dcto)*dosis1_n, (precio-precio*.19-costo+costo*dcto)*dosis2_n,(precio-precio*.19-costo+costo*dcto)*dosis3_n]
                }, columns = ['1st dose', '2nd dose', '3rd dose'], orient='index')
            _.loc['Adherence [%]']=(_.loc['Adherence [%]']*100).round(1).astype(str)+'%'  
            _.loc['Sales [doses]']=_.loc['Sales [doses]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Sales [CLP]']=_.loc['Sales [CLP]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Margin [CLP]']=_.loc['Margin [CLP]'].apply(lambda x: '{:,}'.format(int(x)))  
            st.dataframe(_, use_container_width=True)
        with col_36:
            st.subheader(':gray[Potencial scenario]')
            _ = pd.DataFrame.from_dict({
                'Adherence [%]':[1, adh2, adh3],
                'Sales [doses]':[dosis1_n, dosis1_n*adh2, dosis1_n*adh3],
                'Sales [CLP]':[dosis1_n*precio, dosis1_n*adh2*precio, dosis1_n*adh3*precio],
                'Margin [CLP]':[(precio-precio*.19-costo+costo*dcto)*dosis1_n, (precio-precio*.19-costo+costo*dcto)*dosis1_n*adh2,(precio-precio*.19-costo+costo*dcto)*dosis1_n*adh3]
                }, columns = ['1st dose', '2nd dose', '3rd dose'], orient='index')
            _.loc['Adherence [%]']=(_.loc['Adherence [%]']*100).round(1).astype(str)+'%'  
            _.loc['Sales [doses]']=_.loc['Sales [doses]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Sales [CLP]']=_.loc['Sales [CLP]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Margin [CLP]']=_.loc['Margin [CLP]'].apply(lambda x: '{:,}'.format(int(x)))    
            st.dataframe(_, use_container_width=True)
        with st.container():
            st.subheader(':gray[Income Opportunity]')
            _ = pd.DataFrame.from_dict({
                'Sales [doses]':[dosis1_n+dosis2_n+dosis3_n, dosis1_n+dosis1_n*adh2+dosis1_n*adh3, ((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))],
                'Sales [CLP]':[(dosis1_n+dosis2_n+dosis3_n)*precio, (dosis1_n+dosis1_n*adh2+dosis1_n*adh3)*precio,  ((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))*precio],
                'Margin [CLP]':[(dosis1_n+dosis2_n+dosis3_n)*(precio-precio*.19-costo+costo*dcto), (dosis1_n+dosis1_n*adh2+dosis1_n*adh3)*(precio-precio*.19-costo+costo*dcto),((dosis1_n+dosis1_n*adh2+dosis1_n*adh3)-(dosis1_n+dosis2_n+dosis3_n))*(precio-precio*.19-costo+costo*dcto)]
                }, columns = ['Current', 'Potencial', 'Opportunity'], orient='index')  
            _.loc['Sales [doses]']=_.loc['Sales [doses]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Sales [CLP]']=_.loc['Sales [CLP]'].apply(lambda x: '{:,}'.format(int(x)))  
            _.loc['Margin [CLP]']=_.loc['Margin [CLP]'].apply(lambda x: '{:,}'.format(int(x)))              
            st.dataframe(_, use_container_width=True)

        st.write("---")

with tab2:
    # col1, col2 = st.columns(2, gap='large')
    # with col1:
        ### SEGUIMIENTO ###
    st.subheader('Tracking - Detail of next doses')
    
    list_periodos = (df.fecha.apply(lambda x: x+relativedelta(months=2)).dt.strftime('%Y%m')).unique()
    list_periodos[::-1].sort()
    periodo = st.selectbox('Choose period to consult ',list_periodos)
    periodo_dt = datetime.date(int(periodo[:4]),int(periodo[4:]),1)
    # max periodo + 2 meses
    col12, col13 = st.columns(2)
    with col12:
        df_seg2 = df[(df.dosis=='1ra')&(df.fecha>=str(periodo_dt-relativedelta(months=2)))&(df.fecha<str(periodo_dt-relativedelta(months=1)))]
        st.metric(label="2nd dose", value=len(df_seg2))
        st.write(df_seg2)
    with col13:
        df_seg3 = df[(df.dosis=='2da')&(df.fecha>=str(periodo_dt-relativedelta(months=4)))&(df.fecha<str(periodo_dt-relativedelta(months=3)))]
        st.metric(label="3rd dose", value=len(df_seg3))
        st.write(df_seg3)
    # with col2:
    #     ### SEGUIMIENTO ###
    #     st.subheader('Scheduling QR')
    #     st.write('Make this QR available to your patients so they can schedule their next dose!')
    #     left_co, cent_co,last_co = st.columns(3)
    #     with cent_co:
    #         st.image('qr.png')       

# with tab3:
#     col3, col4 = st.columns(2, gap='large')
#     with col3:
#         _ = df.copy()
#         _['period'] = _.fecha.dt.strftime('%Y-%m') 
#         _ = _.groupby('period').cantidad.sum().reset_index().rename(columns={'cantidad':'units'})
#         _['sellin'] = _.units*89550
#         _['d4d'] = (_.sellin*3/100).astype(int)
#         _['rebate'] = (_.sellin*5/100).astype(int)
#         _['total_cn'] = _.d4d+_.rebate
#         _ = _.sort_values(by='period', ascending=False)
#         del _['units']
#         cn = _.sort_values(by='period').iloc[-1].total_cn
#         cn = '$ '+'{:,}'.format(cn)   
#         _ = _.style.apply(lambda x: ['background-color: #E2F5F0' if (i == x.size-1 or i==0) else '' for i in range(x.size)], axis=1)
#         st.dataframe(_, hide_index=True, 
#                     column_config={
#                         'period': 'Period',
#                         'sellin': st.column_config.NumberColumn('Sell in',format="$ %d"),
#                         'd4d': st.column_config.NumberColumn('Discount for data',format="$ %d"),
#                         'rebate': st.column_config.NumberColumn('Rebate',format="$ %d"),
#                         'total_cn': st.column_config.NumberColumn('Total credit notes',format="$ %d")
#                         }, use_container_width=True)
#     with col4:
#         st.markdown("#")
#         st.markdown("#")
#         st.markdown('<div style="text-align:center;font-size:24px"> This month you are going to receive:</div>', unsafe_allow_html=True)
#         st.markdown(f'<div style="text-align:center;font-size:50px;color:#00857C"> <b>{cn}</b></div>', unsafe_allow_html=True)
#         st.markdown('<div style="text-align:center;font-size:24px"> in credit notes for discounts.</div>', unsafe_allow_html=True)
#         st.markdown("#")