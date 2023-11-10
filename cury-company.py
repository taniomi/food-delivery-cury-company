import streamlit as st
from utils import *

if __name__ == "__main__":

    df_og = pd.read_csv('train.csv')
    df = df_og.copy()
    df = clean_df(df)
    
    # 2 Streamlit
    ## 2.1 Main Page
    st.header('Cury Co. Ltd. - Restaurant View')
    st.write('Fast and savory food! Curry is the best food!😋')

    ## 2.2 Sidebar
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
    
    ## 2.3 Tabs
    tab1, tab2, tab3 = st.tabs(['Management', 'Tactical', 'Map'])
    
    ### 2.3.1 Management View
    with tab1:
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3 = st.columns(3, gap='large')
            
            with col1:
                delivery_unique = df.loc[:,'Delivery_person_ID'].nunique()
                col1.metric('Deliverers', delivery_unique)
    
            with col2:
                mean_dist = calc_mean_dist(df)
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
            fig_mean_dist = plot_fig_mean_dist(df)
            st.plotly_chart(fig_mean_dist)
    
        with st.container():
            st.markdown("""---""")
            st.title('Mean delivery time by city')
            fig_time_city = plot_fig_time_city(df)
            st.plotly_chart(fig_time_city)
    
        with st.container():
            st.markdown("""---""")
            st.title('Time distribution')
            fig_sun = plot_fig_sun(df)
            st.plotly_chart(fig_sun)
    
    ### 2.3.2 Tactical View
    with tab2:
        with st.container():
            st.title('Week')
            chart_week = plot_chart_week(df)
            st.plotly_chart(chart_week)
    
        with st.container():
            st.title('Orders by deliverer per week')
            chart_deliverer_wk = plot_chart_deliverer_wk(df)
            st.plotly_chart(chart_deliverer_wk)
    

    ### 2.3.4 Map
    with tab3:
        st.markdown('##### City location traffic')
        city_location_traffic = plot_city_location_traffic(df)
        st.map(city_location_traffic,
               latitude='Delivery_location_latitude',
               longitude='Delivery_location_longitude')
