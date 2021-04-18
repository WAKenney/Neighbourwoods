import pandas as pd
import io
import streamlit as st

# try:
#     myfile = st.file_uploader('Get the tree data file from your hard drive')

#     with st.spinner('Please wait while your file is uploaded...'):
#         if myfile is not None:
#             # df = pd.read_csv(myfile,encoding='cp1252')
#             text_io = io.TextIOWrapper(myfile)
#             df = pd.read_csv(text_io)
#             st.write(df)
            
# except:
#     st.error("Oops, this isn't a valid file")

myfile = st.file_uploader('Get the tree data file from your hard drive')

with st.spinner('Please wait while your file is uploaded...'):
    if myfile is not None:
        # df = pd.read_csv(myfile,encoding='cp1252')
        text_io = io.TextIOWrapper(myfile)
        df = pd.read_csv(text_io)
        st.write(df)
        
# st.error("Oops, this isn't a valid file")
    