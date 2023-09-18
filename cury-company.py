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
st.header('Cury Co. Ltd. - Deliverer View')
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
tab1, tab2, tab3 = st.tabs(['Management View', '_', '_'])

# 2.3.1 Management View
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            oldest = df['Delivery_person_Age'].max()
            col1.metric('Oldest', oldest)

        with col2:
            youngest = df['Delivery_person_Age'].min()
            col2.metric('Youngest', youngest)

        with col3:
            best_vehicle_cond = df['Vehicle_condition'].max()
            col3.metric('Best vehicle', best_vehicle_cond)

        with col4:
            worst_vehicle_cond = df['Vehicle_condition'].min()
            col4.metric('Worst vehicle', worst_vehicle_cond)

    with st.container():
        st.markdown("""---""")
        st.title('Ratings')
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Mean ratings by deliverer')
            mean_rating_by_deliv = (df.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                                      .groupby('Delivery_person_ID')
                                      .mean()
                                      .reset_index())
            st.dataframe(mean_rating_by_deliv)

        with col2:
            st.subheader('Mean ratings by traffic conditions')
            mean_rating_by_traffic = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            mean_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            mean_rating_by_traffic.reset_index()
            st.dataframe(mean_rating_by_traffic)

            st.subheader('Mean ratings by climate conditions')
            mean_rating_by_climate = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                        .groupby('Weatherconditions')
                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            mean_rating_by_climate.columns = ['delivery_mean', 'delivery_std']
            mean_rating_by_climate.reset_index()
            st.dataframe(mean_rating_by_climate)

    with st.container():
        st.markdown("""---""")
        st.title('Delivery speed')
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Fastest deliverers')
            dfaux = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City', 'Delivery_person_ID']).min()
                       .sort_values(['City', 'Time_taken(min)']).reset_index())
            dfaux1 = dfaux.loc[dfaux['City'] == 'Metropolitian', :].head(10)
            dfaux2 = dfaux.loc[dfaux['City'] == 'Semi-Urban', :].head(10)
            dfaux3 = dfaux.loc[dfaux['City'] == 'Urban', :].head(10)
            fastest_deliverers = pd.concat([dfaux1, dfaux2, dfaux3]).reset_index(drop=True)
            st.dataframe(fastest_deliverers)
 
        with col2:
            st.subheader('Slowest deliverers')
            dfaux = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City', 'Delivery_person_ID']).max()
                       .sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index())
            dfaux1 = dfaux.loc[dfaux['City'] == 'Metropolitian', :].head(10)
            dfaux2 = dfaux.loc[dfaux['City'] == 'Semi-Urban', :].head(10)
            dfaux3 = dfaux.loc[dfaux['City'] == 'Urban', :].head(10)
            slowest_deliverers = pd.concat([dfaux1, dfaux2, dfaux3]).reset_index(drop=True)
            st.dataframe(slowest_deliverers)

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

# 2.3.4 Map
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
