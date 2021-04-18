import pandas as pd
import io
import streamlit as st

myfile = st.file_uploader('Get the tree data file')

try:
    with st.spinner('Please wait while your file is uploaded...'):
        if myfile is not None:
            # df = pd.read_csv(myfile,encoding='cp1252')
            text_io = io.TextIOWrapper(myfile)
            df = pd.read_csv(text_io)
            st.write(df)
            
except:
    st.error("Oops, this isn't a valid file")
    