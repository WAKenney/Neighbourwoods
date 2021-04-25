
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash
import dash_table
from PIL import Image
import os

st.set_page_config(layout="wide")

st.header('__Neighbour_woods_ Analytics 3.0__')
st.markdown("___")

# nwHeader = Image.open("https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/NWAnalyticsTitleTransparent.png")
# st.image(nwHeader)

currentDir = "https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/"

tableFrame = st.empty()
mapFrame = st.empty()
filterDashBoard = st.sidebar.empty()

@st.cache(allow_output_mutation=True)
def getData():

    '''
    **************************
    Load and arrange the data
    ************************** 
    '''
    
    with st.spinner('Please wait while your file is uploaded...'):
        # df = pd.read_csv(myFile,encoding='cp1252')
        speciesFile = currentDir + 'NWspecies180321.csv'
        speciesTable = pd.read_csv(speciesFile)
        
        codesFile = currentDir + 'NWcodes180321.csv'
        codesTable = pd.read_csv(codesFile,encoding='cp1252')
        
        dfFile = currentDir + 'LargeDataSummary.csv'
        df = pd.read_csv(dfFile,encoding='cp1252')
        
    df=df.rename(columns = {'Tree Name':'tree_name','Description':'description','Longitude':'longitude',
                                      'Latitude':'latitude','Date':'date','Block ID':'block','Tree Number':'tree_number',
                                      'Species':'species','Genus':'genus','Family':'family','Street':'street',
                                      'Address':'address','Location Code':'location_code','Ownership Code':'ownership_code',
                                      'Crown Width':'crown_width','Number of Stems':'number_of_stems','DBH':'dbh',
                                      'Hard Surface':'hard_surface','Ht to Crown Base':'height_to_crown_base',
                                      'Total Height':'total_height','Reduced Crown':'reduced_crown','Unbalanced Crown':'unbalanced_crown',
                                      'Defoliation':'defoliation','Weak or Yellowing Foliage':'weak_or_yellow_foliage',
                                      'Dead or Broken Branch':'dead_or_broken_branch','Lean':'lean','Poor Branch Attachment':'poor_branch_attachment',
                                      'Branch Scars':'branch_scars','Trunk Scars':'trunk_scars','Conks':'conks','Rot or Cavity - Branch':'branch_rot_or_cavity',
                                      'Rot or Cavity - Trunk':'trunk_rot_or_cavity','Confined Space':'confined_space',
                                      'Crack':'crack','Girdling Roots':'girdling_roots','Recent Trenching':'recent_trenching',
                                      'Cable or Brace':'cable_or_brace','Conflict with Wires':'wire_conflict',
                                      'Conflict with Sidewalk':'sidewalk_conflict','Conflict with Structure':'structure_conflict',
                                      'Conflict with Another Tree':'tree_conflict','Conflict with Traffic Sign':'sign_conflict',
                                      'Comments':'comments', 'Total Demerits':'demerits','Simple Rating':'simple_rating',
                                     'Crown Projection Area (CPA)':'cpa', 'Relative DBH':'rdbh','Relative DBH Class':'rdbh_class',
                                      'DBH class':'dbh_class','Native':'native','Species Suitability':'suitability','Structural Defect':'structural', 'Health Defect':'health'})
    
    def defect_setup(df):
        if ((df['structural'] == 'no') & (df['health'] =='no')):
            return 'No major defects'
        elif ((df['structural'] == 'yes') & (df['health'] =='no')):
            return 'Major structural defect(s)'
        elif ((df['structural'] == 'no') & (df['health'] =='yes')):
            return 'Major health defect(s)'
        elif ((df['structural'] == 'yes') & (df['health'] =='yes')):
            return 'Major structural AND health defect(s)'
        else:
            return 'Condition was not assessed'
    
    df['defects'] = df.apply(defect_setup, axis = 1)
    
    df = pd.merge(df, speciesTable[['species', 'diversity_level']], on="species", how="left", sort=False)
        
    df2 = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).copy()
    
    df2 = df2[['tree_name','description','species', 'genus', 'family', 'address', 'ownership_code', 'location_code', 'native', 'crown_width',
               'cpa', 'dbh_class', 'defects', 'diversity_level', 'latitude', 'longitude']]
    
    return df2

##################################################### Show data table ##########################################
def showTable(data, selectedCols):
    
    
   # cols = data.columns
    
    # if 'latitude'in cols:
    #     data = data.drop(['latitude', 'longitude'], axis =1, inplace=True)
    #     cols.remove('latitude')
    cols = ['tree_name','description'] + selectedCols
    fig = go.Figure(go.Table(
        
        columnwidth = [20,80],
        
        header=dict(values=list(cols),
                    fill_color='lightgreen',
                    align='center'),
        cells=dict(values=[data[col] for col in cols],
                    fill_color='lavender',
                    # line_color ='black',
                    align='center')))
         
    tableWidth = st.sidebar.slider('Set table width',min_value=500, max_value=1400, step = 100, value = 500)
    fig.layout.width=tableWidth
    fig.layout.height=800
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig

# ###################################################   Select data for mapping and analysis

def getSelection(data):
    ''' 
    This allows the user to filter the data with an output dataframe called select_df.
    This is also where the dashboard is setup in the sidebar.
    '''
       
    data_columns = data.columns.values.tolist()
    paramColumns = ['tree_name','species', 'genus', 'family', 'address', 'ownership_code', 
                    'location_code', 'native', 'crown_width','dbh_class', 'defects', 'diversity_level']
    
    st.sidebar.subheader("Do you want to FILTER the tree data?")
    filtYesOrNo = st.sidebar.radio("", options =('No, use all the data', 'Yes, filter the data'))
    
    if filtYesOrNo == 'Yes, filter the data':
        
        
        filterType = st.sidebar.radio("", options =('Simple Filter?', 'Detailed Filter?'))
        
        if filterType == 'Simple Filter?':
            
            select_param = st.sidebar.selectbox('Select a parameter for filtering', paramColumns)
            value_list = data[select_param]
            value_list =pd.unique(value_list)
            select_value = st.sidebar.multiselect('Now, select a value for filtering within ' + select_param, value_list)
            select_df = data[data[select_param].isin(select_value)].copy()       
            st.sidebar.subheader("Number of matches = " + str(select_df.shape[0]))
            
        else:
            
            def buildQstring():
                
                keyCount = 0
                
                def addFilter(qString, keyCount):
                    
                    keyCount = keyCount+1
                    
                    qString = '(' + qString + ')'
                    
                    logOp = st.sidebar.selectbox('Select a logical Operator', (" and ", " or "), key = 'logOpKey' + str(keyCount))
                    qString = qString + logOp
                    st.sidebar.write('So far the qstring is: ' + qString)
                    
                    newSelectParam = st.sidebar.selectbox('Select a parameter for filtering', 
                                                        options = paramColumns, key = 'newSelectParamKey' + str(keyCount))            
                    compMethod = st.sidebar.selectbox('Select a method of camparison', 
                                                      options = ['==', '!=', '<', '>'], key = 'compMethodKey' + str(keyCount))
                    value_list = data[newSelectParam]
                    value_list =pd.unique(value_list)
                    select_value = st.sidebar.selectbox('Now, select a value for filtering within ' + newSelectParam, value_list, 
                                                        key = 'select_valueKey' + str(keyCount))
                    select_value = '"' + select_value + '"' 
                    
                    # newQstring = newSelectParam + compMethod + select_value
                    newQstring = '(' + newSelectParam + compMethod + select_value +')'
                    # st.sidebar.write("compMethod = ", compMethod)
                    qString = qString + newQstring
                    
                    st.subheader('The results are based on the following search string: ' + qString)
                    # st.sidebar.write('So far the qstring is: ' + qString)
                    
                    submitYesNo = st.sidebar.radio("",options = ("Submit", 'Add to Filter'), key = 'submitYesNoKey' + str(keyCount))
                
                    if submitYesNo == 'Add to Filter':
                    
                        qString = addFilter(qString, keyCount)
                    else:
                        return qString
                    
                select_param = st.sidebar.selectbox('Select a parameter for filtering', paramColumns)            
                compMethod = st.sidebar.selectbox('Select a method of camparison', 
                                                  options = ['==', '!=', '<', '>'])
                value_list = data[select_param]
                value_list =pd.unique(value_list)
                select_value = st.sidebar.selectbox('Now, select a value for filtering within ' + select_param, value_list)
                select_value = '"' + select_value + '"' 
                
                qString = select_param + compMethod + select_value
                st.sidebar.write('So far the qstring is: ' + qString)
                
                submitYesNo = st.sidebar.radio("",options = ("Submit", 'Add to Filter'))
                
                if submitYesNo == 'Add to Filter':
                    qString = addFilter(qString, keyCount)
                
                # else:
                #     return qstring
                                
                return qString
                    
            # try:
            #     qString = buildQstring()
            #     filteredDf = data.query(qString)
            #     st.sidebar.subheader("Number of matches = " + str(filteredDf.shape[0]))
            #     st.write(filteredDf.head())
            # except Exception as error:
            #     st.error(error)    
            
            qString = buildQstring()
            filteredDf = data.query(qString)
            st.sidebar.subheader("Number of matches = " + str(filteredDf.shape[0]))
            st.write(filteredDf.head())
        
    else:
        select_df = data
        
    



    
gdf = getData()

codes={'No major defects':"#006400", 'Major health defect':'#7CFC00', 'Major structural defect(s)':'#ADFF2F',
           'Major structural AND health defect(s)':'#FFFF00', 'N/A':'#708090' } #steup colour codes for levels of tree condition

CondcolorOrder = {'defects' : ['No major defects', 'Major health defect', 'Major structural defect(s)',
                               'Major structural AND health defect(s)', 'Condition was not assessed']}# setup order for legend

select_df = getSelection(gdf)

 