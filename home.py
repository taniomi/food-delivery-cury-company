import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=""
)

image_path = "C:/Users/Milena/Documents/PythonScripts/CDS/food-delivery-dataset/"
image = Image.open(image_path + "cury-rice.png")
st.sidebar.image(image, width=120)

with st.sidebar:
    st.markdown('# Cury Co. Ltd.')
    st.markdown("""---""")

    st.write('Cury Company Growth Dashboard')
    st.markdown('Powered by Taniomi')

st.markdown(
    """
    Growth Dashboard was built to monitor the growth indicators of Deliverers and Restaurants.
    ### How to use the Dashboard?
    - Company View:
        - Management: behaviour metrics
        - Tactical: weekly growth indicators
        - Geographical: map view
    - Deliverer View:
        - Weekly growth indicators
    - Restaurant View:
        - Weekly restaurant growth indicators
    ### Questions or suggestions? Feel free to contact us!
    ✉️ taniomi@mockupmail.com
    """
)
