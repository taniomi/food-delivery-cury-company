import pandas as pd
import numpy as np
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
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
st.header('Cury Co. Ltd. - Restaurant View')
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
        col1, col2, col3 = st.columns(3, gap='large')
        
        with col1:
            delivery_unique = df.loc[:,'Delivery_person_ID'].nunique()
            col1.metric('Deliverers', delivery_unique)

        with col2:
            dfaux = (df.loc[:, 
                           ['Restaurant_latitude', 
                            'Restaurant_longitude', 
                            'Delivery_location_latitude', 
                            'Delivery_location_longitude']])
            dfaux['Distance'] = (dfaux.apply(lambda x: 
                                haversine((x['Restaurant_latitude'], 
                                           x['Restaurant_longitude']), 
                                          (x['Delivery_location_latitude'], 
                                           x['Delivery_location_longitude'])), 
                                axis=1))
            mean_dist = dfaux['Distance'].mean()
            col2.metric('Mean distance', mean_dist)

        with col3:
            mean_time_festival = (df.loc[df.loc[:, 'Festival'] == 'Yes', 
                                         'Time_taken(min)']
                                    .mean())
            col3.metric('Mean time festival', mean_time_festival)

    with st.container():
        col4, col5, col6 = st.columns(3, gap='small')
        with col4:
            std_time_festival = (df.loc[df.loc[:, 'Festival'] == 'Yes', 
                                        'Time_taken(min)']
                                    .std())
            col4.metric('Std deviation time festival', std_time_festival)

        with col5:
            mean_time_no_festival = (df.loc[df.loc[:, 'Festival'] == 'No', 
                                            'Time_taken(min)']
                                       .mean())
            col5.metric('Mean time no festival', mean_time_no_festival)

        with col6:
            std_time_no_festival = (df.loc[df.loc[:, 'Festival'] == 'No', 
                                           'Time_taken(min)']
                                      .std())
            col6.metric('Std deviation time no festival', std_time_no_festival)

    with st.container():
        st.markdown("""---""")
        st.title('Mean distance')

        dfaux = (df.loc[:, 
                        ['City',
                         'Restaurant_latitude', 
                         'Restaurant_longitude', 
                         'Delivery_location_latitude', 
                         'Delivery_location_longitude']])
        dfaux['Distance'] = (dfaux.apply(lambda x: 
                             haversine((x['Restaurant_latitude'], 
                                        x['Restaurant_longitude']), 
                                       (x['Delivery_location_latitude'], 
                                        x['Delivery_location_longitude'])),
                             axis=1))
        avg_dist = (dfaux.loc[:, ['City', 'Distance']]
                         .groupby('City')
                         .mean()
                         .reset_index())
        fig_avg_dist = go.Figure(data=[go.Pie(labels=avg_dist['City'],
                                              values=avg_dist['Distance'],
                                              hole=0.5)])
        st.plotly_chart(fig_avg_dist)

    with st.container():
        st.markdown("""---""")
        st.title('Mean delivery time by city')
        dfaux = (df.loc[:, ['City', 'Time_taken(min)']]
                   .groupby('City')
                   .agg({'Time_taken(min)': ['mean', 'std']})
                   .reset_index())
        dfaux.columns = ['City', 'Mean_time', 'Std_deviation_time']
        fig_time_city = go.Figure()
        fig_time_city.add_trace(go.Bar(name='Control',
                                       x=dfaux['City'],
                                       y=dfaux['Mean_time'],
                                       error_y=dict(type='data',
                                       array=dfaux['Std_deviation_time'])))
        fig_time_city.update_layout(barmode='group')
        st.plotly_chart(fig_time_city)

    with st.container():
        st.markdown("""---""")
        st.title('Time distribution')
        dfaux = (df.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
                   .groupby(['City', 'Road_traffic_density'])
                   .agg({'Time_taken(min)': ['mean', 'std']}))
        dfaux.columns = ['Time_mean', 'Time_std']
        dfaux = dfaux.reset_index()
        fig_sun = px.sunburst(dfaux,path=['City', 'Road_traffic_density'],
                                    values='Time_mean',color='Time_std',
                                    color_continuous_scale='icefire',
                                    color_continuous_midpoint=np.average(dfaux['Time_std']))
        st.plotly_chart(fig_sun)

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
    city_location_traffic = (df.loc[:,['City',
                                       'Road_traffic_density',
                                       'Delivery_location_latitude',
                                       'Delivery_location_longitude']]
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
