from utils import *

if __name__ == "__main__":

    df = pd.read_csv('dataset/train.csv')
    df = clean_df(df)

    # 2 Streamlit
    # 2.3 Tabs
    tab1, tab2, tab3 = st.tabs(['Management View', '_', '_'])

    # 2.3.1 Management View
    with tab1:
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3, col4 = st.columns(4, gap='large')
            
            with col1:
                oldest = df.Delivery_person_Age.max()
                col1.metric('Oldest', oldest)

            with col2:
                youngest = df.Delivery_person_Age.min()
                col2.metric('Youngest', youngest)

            with col3:
                best_vehicle_cond = df.Vehicle_condition.max()
                col3.metric('Best vehicle', best_vehicle_cond)

            with col4:
                worst_vehicle_cond = df.Vehicle_condition.min()
                col4.metric('Worst vehicle', worst_vehicle_cond)

        with st.container():
            st.markdown("""---""")
            st.title('Ratings')
            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Mean ratings by deliverer')
                df_mean_rating_by_deliv(df)

            with col2:
                st.subheader('Mean ratings by traffic conditions')
                df_mean_rating_by_traffic(df)
                st.subheader('Mean ratings by climate conditions')
                df_mean_rating_by_climate(df)

        with st.container():
            st.markdown("""---""")
            st.title('Delivery speed')
            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Fastest deliverers')
                df_speed_deliverers(df, asc=True)
     
            with col2:
                st.subheader('Slowest deliverers')
                df_speed_deliverers(df, asc=False)
