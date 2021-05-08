# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 14:20:13 2021

@author: W.A. Kenney
"""

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

st.title('***Neighbourwoods Analytics 3.0***')

mainScreen = st.empty()
mainScreen.write('')

# nwHeader = Image.open("https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/NWAnalyticsTitleTransparent.png")
# st.image(nwHeader)

currentDir = "https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/"

filterDashBoard = st.sidebar.empty()
tableFrame = st.empty()
mapFrame = st.empty()
# ShowDataMenu = st.sidebar.empty()
# MapItMenu= st.sidebar.empty()
# DiversityMenu = st.sidebar.empty()
# OriginMenu = st.sidebar.empty()

colTitles=['tree_name', 'species', 'genus', 'family', 'street', 'address', 'location_code', 'ownership_code', 'number_of_stems', 'dbh',
   'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'reduced_crown', 'unbalanced_crown', 'defoliation',
   'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean', 'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks',
   'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space','crack', 'girdling_roots', 'recent_trenching', 'cable_or_brace',
   'wire_conflict', 'sidewalk_conflict', 'structure_conflict', 'tree_conflict', 'sign_conflict', 'comments', 'demerits',
   'simple_rating', 'cpa', 'rdbh', 'rdbh_class', 'dbh_class', 'native', 'suitability', 'defects']
       

stringColumns=['tree_name','description', 'species', 'genus', 'family', 'street', 'address','location_code',
                'ownership_code', 'cable_or_brace','wire_conflict', 'sidewalk_conflict','structure_conflict',
                'tree_conflict', 'sign_conflict', 'comments', 'simple_rating', 'rdbh_class',
                'dbh_class', 'native','suitability', 'defects']

numericalColumns = ['number_of_stems', 'dbh', 'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'demerits','cpa', 'rdbh']

condColumns = ['reduced_crown', 'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean',
                     'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space',
                     'crack', 'girdling_roots', 'recent_trenching']

codes={'No major defects':"#006400", 'Major health defect':'#7CFC00', 'Major structural defect(s)':'#ADFF2F',
           'Major structural AND health defect(s)':'#FFFF00', 'N/A':'#708090' } #steup colour codes for levels of tree condition

CondcolorOrder = {'defects' : ['No major defects', 'Major health defect', 'Major structural defect(s)',
                               'Major structural AND health defect(s)', 'Condition was not assessed']}# setup order for legend

# paramColumns = ['tree_name','species', 'genus', 'family', 'address', 'ownership_code', 
                    # 'location_code', 'native', 'crown_width','dbh_class', 'defects', 'diversity_level']


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
    
    st.write(df.columns)
    
    
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
        
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).copy()
    
    # df = df[['tree_name','description','species', 'genus', 'family', 'address', 'ownership_code', 'location_code', 'native', 'crown_width',
    #            'cpa', 'dbh_class', 'defects', 'diversity_level', 'latitude', 'longitude']]
    
    return df


#############################################################################
def simpleFilter(data):
    
    filterMenu3 =st.sidebar.empty()
    with filterMenu3:
        select_param = st.sidebar.selectbox('Select a parameter for filtering', colTitles, index = 1)
        value_list = data[select_param]
        value_list =pd.unique(value_list)    
        # defaultValue = value_list[0]
        
        if len(value_list) ==0:
            st.warning('Please select a value for filtering within ' + select_param)
        
            
        select_value = st.sidebar.multiselect('Now, select a value for filtering within ' + select_param, value_list)
    
    select_df = data[data[select_param].isin(select_value)].copy()       
    
    filterMenu4 =st.sidebar.empty()
    with filterMenu4:
        st.sidebar.subheader("Number of matches = " + str(select_df.shape[0]))

    return select_df

#############################################################################

def oneParameterFilter(data, keyCount):
    
    filterMenu3 =st.sidebar.empty()
    with filterMenu3:
        oneSelectParam = st.sidebar.selectbox('Select a parameter for filtering', options = colTitles, index = 2, key = 'oneSelectParam' + str(keyCount))            
    
    if oneSelectParam in stringColumns:
        oneCompMethodOption = ['==', '!=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
    
    elif oneSelectParam in numericalColumns:
        oneCompMethodOption = ['==', '!=', '<', '<=', '>', '>=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
    
    else:
        oneCompMethodOption = ['==', '!=', '<', '<=', '>', '>=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
        
    value_list = data[oneSelectParam]
    value_list =pd.unique(value_list)
    
    filterMenu5 =st.sidebar.empty()
    with filterMenu5:
        
        if oneCompMethod in ['==', '!=']:
            select_value = st.sidebar.selectbox('Now, select a value for filtering within ' + oneSelectParam, value_list, index = 0, key = 'select_value' + str(keyCount))
        else:
            minValue = int(data[oneSelectParam].min())
            maxValue = int(data[oneSelectParam].max())
            
            if oneSelectParam in condColumns:
                select_value = st.sidebar.slider('Now, select a value for filtering within ' + oneSelectParam, minValue, maxValue, step = 1, key = 'select_value' + str(keyCount))
            else:
                select_value = st.sidebar.slider('Now, select a value for filtering within ' + oneSelectParam, minValue, maxValue, key = 'select_value' + str(keyCount))
    
    if oneCompMethod == '==':
        select_df = data.loc[(data[oneSelectParam] ==  select_value)]
    elif oneCompMethod == '!=':
        select_df = data.loc[(data[oneSelectParam] !=  select_value)]
    elif oneCompMethod == '<':
        select_df = data.loc[(data[oneSelectParam] <  select_value)]
    elif oneCompMethod == '<=':
        select_df = data.loc[(data[oneSelectParam] <=  select_value)]
    elif oneCompMethod == '>':
        select_df = data.loc[(data[oneSelectParam] >  select_value)]
    else:
        select_df = df.loc[(data[oneSelectParam] >=  select_value)]
    
    oneQstring =  oneSelectParam + oneCompMethod + str(select_value)
    st.subheader('The results are based on the following search string: ' + oneQstring + ' with ' + str(select_df.shape[0]) + ' matches.'  )
    
    # with filterMenu4:
    #     st.sidebar.subheader("Number of matches = " + str(select_df.shape[0]))
    
    return select_df
        

#############################################################################
def twoParameterFilter(data):
    
    tempdf1 = oneParameterFilter(data, 0)
    
    filterMenu3 = st.sidebar.empty()
    with filterMenu3:
        logOperator = st.sidebar.selectbox('Now select a logical operator', options = ['AND', 'OR']) 
    
    if logOperator == 'AND':
        
        select_df = oneParameterFilter(tempdf1, 1)
      
    else:
        tempdf2 = oneParameterFilter(data, 1)
    
        select_df = tempdf1.append(tempdf2, ignore_index = True)
    
    filterMenu4 = st.sidebar.empty()
    with filterMenu4:
        st.sidebar.subheader("The combined number of matches = " + str(select_df.shape[0]))
    
    return select_df
    
##################################################### Show data table ##########################################
def showTable(data):
        
    # st.write('')
    
    selectedCols = st.multiselect('Select the ADDITIONAL columns to show in the table', data_columns)

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
         
    tableWidth = st.slider('Set table width',min_value=500, max_value=1400, step = 100, value = 500)
    fig.layout.width=tableWidth
    fig.layout.height=800
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig)
    
################################################### Map the selected data

def mapIt(mapData):
    avLat = mapData['latitude'].mean()  #calculate the average Latitude value and average Longitude value to use to centre the map
    avLon = mapData['longitude'].mean()
    
    mapData['condColor'] = mapData['defects'].map(codes) # create a column called conColor and map the color values based on 
                                                                #the condition code in the dictionary called condColor

    map_df = mapData[mapData['latitude'].notna()]
    
    fig = px.scatter_mapbox(data_frame = map_df, lat="latitude", lon="longitude", 
                            hover_name='tree_name',
                            hover_data={"tree_name": False,
                                        "description": False,
                                        'address': True,
                                        'species': True,
                                        'defects': True,
                                        'latitude': False,
                                        'longitude': False     
                                        }, 
                            color=map_df.defects,
                            color_discrete_map  = codes,
                            category_orders = CondcolorOrder,
                            center=dict(lat=avLat, lon=avLon), 
                            zoom=16, height=300)
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(autosize=False, width=1200, height=600)
    
    base_map_type = st.radio('Select the type of basemap', options= ['Map', 'Photo'])

    if base_map_type == 'Map':       
        fig.update_layout(mapbox_style = 'open-street-map')
    else:    
        # useSatellite(fig)
        st.write('To use Google satelite images you will need a free Google Maps API Key.  Go to https://elfsight.com/blog/2018/06/how-to-get-google-maps-api-key-guide/ ')
        token = st.text_input('Enter your Google Maps API Key')
        fig.update_layout(mapbox_style = 'satellite', mapbox_accesstoken = token )
        
        
    fig.layout.width=1500
    fig.layout.height=1500
    
    fig.update_layout(legend=dict(yanchor="top",
                                  y=0.99,
                                  xanchor="left",
                                  x=0.01
                                  ))
    
    size_slider = st.slider('Select the size of the marker on the map', min_value = 5, max_value = 20, value = 10)
    fig.update_traces(marker_size = size_slider)
    
    st.plotly_chart(fig)
    
    
    
    return fig


# ########################################## Diversity ############################################
    
def diversity(data):
    
    divLevel = st.radio('Select a level of diversity', ('species', 'genus', 'family'))
    
    st.header('Tree Diversity Summary by ' + divLevel)
        
    if divLevel == 'species':
       # data = data[data.diversity_level == divLevel]
        data = data.loc[(data.diversity_level == divLevel)]
    else:
        # data = data[data.diversity_level != divLevel]
        data = data.loc[(data.diversity_level != 'other')]
                   
    totalCount = len(data.index)
    topTenSpecies = data.loc[: , [divLevel, 'tree_name']]
    topTenSpeciesPT = pd.pivot_table(topTenSpecies, index=[divLevel], aggfunc='count')
    topTenSpeciesPT.reset_index(inplace=True)
    topTenSorted = topTenSpeciesPT.sort_values(by='tree_name',ascending=False).head(10)
    topTenTotal = topTenSorted['tree_name'].sum()
    otherTotal = totalCount - topTenTotal
    topTenPlusOther = topTenSorted.append({divLevel:'Other', 'tree_name': otherTotal}, ignore_index =True)
    topTenPlusOther.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    speciesPie = px.pie(topTenPlusOther, values='frequency', names = divLevel)
    speciesPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    speciesPie.update_layout(showlegend=False)
    
    
    TopTenTable = go.Figure(go.Table(
    header=dict(values=list(topTenPlusOther.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[topTenPlusOther[divLevel], topTenPlusOther.frequency],
                fill_color='lavender',
                align='left')))
    
    
    sppTable, sppChart =st.beta_columns (2)
    
    st.header('Tree Diversity Summary by Crown Projection Area')
    
    with sppTable:
        st.plotly_chart(TopTenTable)
    
    with sppChart:
        st.plotly_chart(speciesPie)
 
        
 
    totalCpa = data['cpa'].sum()
    
    topTenCpa = data.loc[: , [divLevel, 'cpa']]
    topTenCpaPT = pd.pivot_table(topTenCpa, index=[divLevel], aggfunc='sum')
    topTenCpaPT.reset_index(inplace=True)
    topTenCpaSorted = topTenCpaPT.sort_values(by='cpa',ascending=False).head(10)
    topTenCpaTotal = topTenCpaSorted['cpa'].sum()
    otherCpaTotal = totalCpa - topTenCpaTotal
    topTenCpaPlusOther = topTenCpaSorted.append({divLevel:'Other', 'cpa': otherCpaTotal}, ignore_index =True)
    topTenCpaPlusOther.rename(columns = {'cpa': 'Crown Projection Area'},inplace = True)
    
    CpaPie = px.pie(topTenCpaPlusOther, values='Crown Projection Area', names = divLevel)
    CpaPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    CpaPie.update_layout(showlegend=False)
    
    
    TopTenCpaTable = go.Figure(go.Table(
    header=dict(values=list(topTenCpaPlusOther.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[topTenCpaPlusOther[divLevel], topTenCpaPlusOther['Crown Projection Area']],
                fill_color='lavender',
                align='left')))
    
    
    sppTable, sppChart =st.beta_columns (2)
    
    with sppTable:
        st.plotly_chart(TopTenCpaTable)
    
    with sppChart:
        st.plotly_chart(CpaPie)
     
########################### Species origin analysis ###########################

def speciesOrigin(data):
    
    originData = data.loc[: , ['native', 'tree_name']]
    originPT = pd.pivot_table(originData, index='native', aggfunc='count')
    originPT.reset_index(inplace=True)
    
    originPT.rename(columns = {'native' : 'origin' , 'tree_name': 'frequency'},inplace = True)
    
    originPie = px.pie(originPT, values='frequency', names = 'origin')
    
    originPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    originPie.update_layout(showlegend=False)
    
    st.header('Tree Species Origin Summary')
    st.plotly_chart(originPie)
        
########################### Tree condition analysis###########################

def treeCondition(data):
    conditionData = data.loc[: , ['defects', 'tree_name']]
    conditionPT = pd.pivot_table(conditionData, index='defects', aggfunc='count')
    conditionPT.reset_index(inplace=True)
    
    conditionPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    conditionPie = px.pie(conditionPT, values='frequency', names = 'defects')
    
    conditionPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    conditionPie.update_layout(showlegend=False)
    
    st.header('Tree Condition Summary')
    st.plotly_chart(conditionPie)
                    
    

########################### Relative DBH Analysis  ###########################





########################### Species Suitability Analysis ###########################






########################### Backup tree table  ###########################
   
################################# setup up the filtering and function selection  ##################################

gdf = getData()

codes={'No major defects':"#006400", 'Major health defect':'#7CFC00', 'Major structural defect(s)':'#ADFF2F',
           'Major structural AND health defect(s)':'#FFFF00', 'N/A':'#708090' } #steup colour codes for levels of tree condition

CondcolorOrder = {'defects' : ['No major defects', 'Major health defect', 'Major structural defect(s)',
                               'Major structural AND health defect(s)', 'Condition was not assessed']}# setup order for legend

df = getData()
data_columns = df.columns.values.tolist()

st.sidebar.header('Select the function(s) you want to display ')
selectFunction = st.sidebar.multiselect('',['Show Data', 'Map Trees', 'Tree Diversity', 'Species Origin', 'Tree Condition', 'Ralative DBH', 'Species Suitability'])

####################################### Filter Menu

st.sidebar.header("Do you want to FILTER the tree data?")
filterMenu1 = st.sidebar.empty()
with filterMenu1:
    
    filtYesOrNo = st.radio("", options =('No, use all the data', 'Yes, filter the data'))

if filtYesOrNo == 'Yes, filter the data':
    
    filterMenu2 = st.sidebar.empty()
    
    with filterMenu2:         
        filterType = st.radio("Select the type of filter you want to use", options =('Filter by List?', 'One Parameter Filter?', 'Two Parameter Filter?'))
        
    if filterType == 'Filter by List?':
        select_df = simpleFilter(df)
        
    elif filterType == 'One Parameter Filter?':
        select_df = oneParameterFilter(df, 0)
    
    else:
        select_df = twoParameterFilter(df)

else:  #Don't filter
    select_df = df
    
########################## setup function selection ##########################

if len(selectFunction) == 0:
    st.warning("Please select which function(s) you want to use from the sidebar at the right")

if 'Show Data' in selectFunction:
    showTable(select_df)
    
if 'Map Trees' in selectFunction:
    mapIt(select_df)

if 'Tree Diversity' in selectFunction:
    diversity(select_df)    

if 'Species Origin' in selectFunction:
    speciesOrigin(select_df)

if 'Tree Condition' in selectFunction:
    treeCondition(select_df)
    
if 'Ralative DBH' in selectFunction:
    st.header("Relative DBH analysis is coming soon!")

if 'Species Suitability' in selectFunction:
    st.header("Species Suitability analysis is coming soon!")
    
    
##############################################
   


    