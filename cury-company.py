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
    
        df = filters_df(df)

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
                mean_time_festival = fest_time(df, festival='Yes').mean()
                col3.metric('Mean time festival', mean_time_festival)
    
        with st.container():
            col4, col5, col6 = st.columns(3, gap='small')
            with col4:
                std_time_festival = fest_time(df, festival='Yes').std()
                col4.metric('Std deviation time festival', std_time_festival)
    
            with col5:
                mean_time_no_festival = fest_time(df, festival='No').mean()
                col5.metric('Mean time no festival', mean_time_no_festival)
    
            with col6:
                std_time_no_festival = fest_time(df, festival='No').std()
                col6.metric('Std deviation time no festival', std_time_no_festival)
    
        with st.container():
            st.markdown("""---""")
            st.title('Mean distance')
            plot_fig_mean_dist(df)
    
        with st.container():
            st.markdown("""---""")
            st.title('Mean delivery time by city')
            plot_fig_time_city(df)
    
        with st.container():
            st.markdown("""---""")
            st.title('Time distribution')
            plot_fig_sun(df)
    
    ### 2.3.2 Tactical View
    with tab2:
        with st.container():
            st.title('Week')
            plot_chart_week(df)
    
        with st.container():
            st.title('Orders by deliverer per week')
            plot_chart_deliverer_wk(df)
    
    ### 2.3.4 Map
    with tab3:
        st.markdown('##### City location traffic')
        map_city_loc_traffic(df)
