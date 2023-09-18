import pandas as pd
import re
from haversine import haversine
import plotly.express as px
import folium
import streamlit as st
from datetime import datetime

df_og = pd.read_csv('train.csv')
df = df_og.copy()
#====================================================================#
# 1 LIMPEZA DOS DADOS                                                #
#====================================================================#
# 1.1 Coluna Time_taken(min)
df['Time_taken(min)'] = (df['Time_taken(min)']
                         .apply(lambda x: x.split(' ')[1])
                         .astype(int))

# 1.2 Retirada 'NaN ' e espaços
for col in df.columns:
    df = df.loc[df.loc[:,col] != 'NaN ',:]

cols_to_clean = ['ID',
                 'Delivery_person_ID',
                 'Road_traffic_density',
                 'Type_of_order',
                 'Type_of_vehicle',
                 'Festival',
                 'City']

for col in cols_to_clean:
        df[col] = df[col].str.strip()

# 1.3 Conversão de tipo
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

# 1.4 Criação coluna Week_Year
    # .dt == transforma a série em data para strftime
    # strftime == string format time
df['Week_Year'] = df['Order_Date'].dt.strftime('%U')

#====================================================================#
# 2 Streamlit                                                        #
#====================================================================#
# 2.1 Main Page
st.header('Cury Co. Ltd.')
st.write('Fast and savory food! Curry is the best food!😋')

# 2.2 Sidebar
with st.sidebar:
    st.markdown('# Cury Co. Ltd.')
    st.markdown("""---""")

filter_date = st.sidebar.slider('Choose dates:',
                                value=datetime(2022, 4, 13),
                                min_value=datetime(2022, 2, 11),
                                max_value=datetime(2022, 4, 6),
                                format='DD-MM-YY')
filter_traffic = st.sidebar.multiselect('Choose traffic conditions:',
                                        ['Low','Medium','High','Jam'],
                                        default=['Low','Medium','High','Jam'])
filtered_lines = ((df['Order_Date'] < filter_date)
                  & (df['Road_traffic_density'].isin(filter_traffic)))
df = df.loc[filtered_lines,:]

st.sidebar.markdown('Powered by Taniomi')

# 2.3 Tabs
tab1, tab2, tab3 = st.tabs(['Management View', 'Tactical View', 'Map'])

# 2.3.1 Management View
with tab1:
    with st.container():
        orders_day = (df.loc[:,['ID','Order_Date']]
                      .groupby('Order_Date')['ID']
                      .count().reset_index())
        chart_day = px.bar(orders_day,
                           title='Orders per day',
                           x='Order_Date',y='ID',
                           height=350)
        st.plotly_chart(chart_day)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            entregas_por_trafego = (df.loc[:,['ID','Road_traffic_density','City']]
                                    .groupby(['Road_traffic_density','City'])
                                    .count().reset_index())
            entregas_por_trafego = (entregas_por_trafego.loc[
                                    entregas_por_trafego.loc[:,'Road_traffic_density'] != 'NaN',
                                    :])
            entregas_por_trafego['Order_%'] = entregas_por_trafego['ID'] / entregas_por_trafego['ID'].sum()

            chart_traffic = px.pie(entregas_por_trafego,
                                   title='Orders by traffic (%)',
                                   values='Order_%',names='Road_traffic_density',
                                   height=350,width=350)
            st.plotly_chart(chart_traffic)

        with col2:
            entregas_por_city_e_traffic = (df.loc[:,['ID','City','Road_traffic_density']]
                                           .groupby(['City','Road_traffic_density'])
                                           .count().reset_index())
            entregas_por_city_e_traffic = (entregas_por_city_e_traffic.loc[
                                           entregas_por_city_e_traffic.loc[:,'City'] != 'NaN',
                                           :])
            entregas_por_city_e_traffic = (entregas_por_city_e_traffic.loc[
                                           entregas_por_city_e_traffic.loc[:,'Road_traffic_density'] != 'NaN',
                                           :])

            chart_city_traffic = px.bar(entregas_por_city_e_traffic,
                                        title='Orders by city and traffic',
                                        x='City',y='ID',
                                        height=350,width=350,
                                        color='Road_traffic_density')

            st.plotly_chart(chart_city_traffic,use_container_witdh=True)

# 2.3.2 Tactical View
with tab2:
    with st.container():
        pedidos_por_semana = (df.loc[:,['ID','Week_Year']]
                              .groupby('Week_Year')['ID']
                              .count().reset_index())

        chart_week = px.line(pedidos_por_semana,title='Orders per week',
                             x='Week_Year',y='ID',
                             height=350)

        st.plotly_chart(chart_week)

    with st.container():

        entregas_por_semana = (df.loc[:,['ID','Week_Year']]
                               .groupby('Week_Year')
                               .count().reset_index())
        entregadores_por_semana = (df.loc[:,['Delivery_person_ID','Week_Year']]
                                   .groupby('Week_Year')
                                   .nunique().reset_index())

        df_merge = pd.merge(entregas_por_semana, entregadores_por_semana, how='inner')
        df_merge['Order_by_deliverer'] = df_merge['ID'] / df_merge['Delivery_person_ID']

        chart_deliverer_wk = px.line(df_merge,title='Orders by deliverer per week',
                                     x='Week_Year',y='Order_by_deliverer',
                                     height=350)

        st.plotly_chart(chart_deliverer_wk)

# 2.3.3 Map
with tab3:
    city_location_traffic = (df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                             .groupby(['City','Road_traffic_density'])
                             .median().reset_index())
    city_location_traffic = (city_location_traffic.loc[
                             city_location_traffic.loc[:,'City'] != 'NaN',
                             :])
    city_location_traffic = (city_location_traffic.loc[
                             city_location_traffic.loc[:,'Road_traffic_density'] != 'NaN',
                             :])

    st.markdown('##### City location traffic')
    st.map(city_location_traffic,
           latitude='Delivery_location_latitude',
           longitude='Delivery_location_longitude',)
