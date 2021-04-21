import pandas as pd
import io
import streamlit as st

def getData():
    fileDownload = st.empty()
    
    fileDownload.write("")
    
    myfile = fileDownload.file_uploader('Get the tree data file from your hard drive')
    
    with fileDownload:
        if myfile is not None:
            df = pd.read_csv(myfile,encoding='cp1252')
    
            st.write("")
            st.write(df)
            
            
tryAgain = st.radio("try another file?", ('Yes', 'No'))
if tryAgain =='Yes':
    getData()
else:
   st.write('OK, by then')          

                    
    


# with fileDownload:
#     with st.spinner('Please wait while your file is uploaded...'):
#         try:
#             myfile = st.file_uploader('Get the tree data file from your hard drive')
            
#             # with st.spinner('Please wait while your file is uploaded...'):
#             if myfile is not None:
#                 df = pd.read_csv(myfile,encoding='cp1252')
#                 with fileDownload:
#                     st.write(df)  
                
#                 # text_io = io.TextIOWrapper(myfile)
#                 # df = pd.read_csv(text_io)
                
                
#         except:        
#             fileDownload.error("Oops, this isn't a valid file")
  