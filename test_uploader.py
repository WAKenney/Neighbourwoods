









# import pandas as pd
# import geopandas as gpd
# import streamlit as st
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import dash
# import dash_table
# from PIL import Image
# import os

# st.set_page_config(layout="wide")

# token = ("pk.eyJ1Ijoid2FrZW5uZXkiLCJhIjoiY2tqMGZtZzhkMGFuNjJxcGJ2MWo5eGwzZyJ9.7vGo7j5cHb4iBX0Vse4ieQ")

# # currentDir = "https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/"

# currentDir = 'https://github.com/WAKenney/Neighbourwoods'

# NWTitleFile = '(r"' +  currentDir + 'NWTitle2.png")'

# st.write(NWTitleFile)




# #################### THIS WORKS *******************************
# import pandas as pd
# import io
# import streamlit as st
# import os

# currentDir = "https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/"

# with st.spinner('Please wait while your file is uploaded...'):
#     # df = pd.read_csv(myFile,encoding='cp1252')
#     speciesFile = currentDir + 'NWspecies180321.csv'
#     speciesTable = pd.read_csv(speciesFile)
    
#     codesFile = currentDir + 'NWcodes180321.csv'
#     codesTable = pd.read_csv(codesFile,encoding='cp1252')
    
#     dfFile = currentDir + 'LargeDataSummary.csv'
#     dfTable = pd.read_csv(dfFile,encoding='cp1252')
    
#     st.write(speciesTable)
#     st.write(codesTable)
#     st.write(dfTable)

# def getData():
#     fileDownload = st.empty()
    
#     fileDownload.write("")
    
#     myfile = fileDownload.file_uploader('Get the tree data file from your hard drive')
    
#     with fileDownload:
#         if myfile is not None:
#             df = pd.read_csv(myfile,encoding='cp1252')
    
#             st.write("")
#             st.write(df)
                  
# tryAgain = st.radio("try another file?", ('Yes', 'No'))
# if tryAgain =='Yes':
#     getData()
# else:
#     st.write('OK, by then')          

                    
    


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
  