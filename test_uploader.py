import pandas as pd
import streamlit as st

# st.set_option('deprecation.showfileUploaderEncoding', False)

myfile = st.file_uploader('Get the data file')
if myfile is not None:
    df = pd.read_csv(myfile,encoding='cp1252')
    # df = pd.read_csv(myfile)
    st.write(df)