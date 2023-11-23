from utils import *

if __name__ == "__main__":

    df = pd.read_csv('dataset/train.csv')
    df = clean_df(df)
    
    # Streamlit
    ## 1 Main Page
    st.header('Cury Co. Ltd. - Restaurant View')
    st.write('Fast and savory food! Curry is the best food!😋')

    ## 2 Sidebar
    with st.sidebar:
        st.markdown('# Cury Co. Ltd.')
        st.markdown("""---""")
    
        df = filters_df(df)

        st.markdown('Powered by Taniomi')
    
    ## 3 Tabs
    tab1, tab2, tab3 = st.tabs(['Management', 'Tactical', 'Map'])
    
    with tab1:
        with st.container():
            st.title('Orders per day')
            orders_per_day = orders_per(df, 'Order_Date') 
            st.plotly_chart(px.bar(orders_per_day, x='Order_Date', y='ID',height=250))
            
            st.title('Orders per week') 
            orders_per_week = orders_per(df, 'Week_Year')
            st.plotly_chart(px.line(orders_per_week, x='Week_Year', y='ID',height=350))

            st.title('Orders per traffic (%)')
            orders_per_traffic = orders_per(df, 'Road_traffic_density')
            plot_fig_orders_per_traffic(orders_per_traffic)

            st.title('Orders per city and traffic')
            orders_per_city_traffic = orders_per(df, "'City','Road_traffic_density'")
            plot_fig_orders_per_city_traffic(df)

            st.title('Orders per week per single deliverer per week')
            plot_order_wk_per_deliverer_wk(df, orders_per_week)

            st.title('Central city per traffic')
            plot_central_city_per_traffic(df)
