
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash
import dash_table

st.set_page_config(page_title = ' Neighbourwoods', layout="wide")
token = ("pk.eyJ1Ijoid2FrZW5uZXkiLCJhIjoiY2tqMGZtZzhkMGFuNjJxcGJ2MWo5eGwzZyJ9.7vGo7j5cHb4iBX0Vse4ieQ")

st.title('Neighbourwoods Inventory Analytics 3.0')
st.title('April 2021')
tableFrame = st.empty()
mapFrame = st.empty()


##################################################  Load and arrange the data #################################################

# @st.cache
def getData():
    df = pd.read_csv(r"C:\Users\HP\Documents\Data\Files\Python Scripts\neighbourwoods\LargeDataSummary.csv")
    
    speciesTable = pd.read_csv(r"C:\Users\HP\Documents\Data\Files\Python Scripts\neighbourwoods\NWspecies180321.csv")
    codesTable = pd.read_csv(r"C:\Users\HP\Documents\Data\Files\Python Scripts\neighbourwoods\NWcodes180321.csv")
    
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
        
    df2 = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    
    df2 = df2[['tree_name','description','species', 'genus', 'family', 'address', 'ownership_code', 'location_code', 'native', 'crown_width',
               'cpa', 'dbh_class', 'defects', 'diversity_level', 'latitude', 'longitude']]
    
    return df2


gdf = getData()

codes={'No major defects':"#006400", 'Major health defect':'#7CFC00', 'Major structural defect(s)':'#ADFF2F',
           'Major structural AND health defect(s)':'#FFFF00', 'N/A':'#708090' } #steup colour codes for levels of tree condition

CondcolorOrder = {'defects' : ['No major defects', 'Major health defect', 'Major structural defect(s)',
                               'Major structural AND health defect(s)', 'Condition was not assessed']}# setup order for legend

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
            qString = st.sidebar.text_input('Enter your search string', value = 'species == "Norway Maple"')
            # qString = " ' "
            
            
            # def buildQstring():
                
            #     st.sidebar.write('So far the qstring is: ' + qString)               
                
            #     select_param = st.sidebar.selectbox('Select a parameter for filtering', paramColumns)            
            #     compMethod = st.sidebar.multiselect('Select a method of camparison', options = ['==', '!=', '<', '>'])
                            
            #     value_list = data[select_param]
            #     value_list =pd.unique(value_list)
            #     select_value = st.sidebar.multiselect('Now, select a value for filtering within ' + select_param, value_list)
                
            #     qString = qString + select_param + compMethod + ''' " ''' + select_value  + ''' " ''' + ''' ' '''
                
            #     st.sidebar.write(qString)
                
            #     return qString
                    
                    
            # qString = buildQstring()
            select_df = data.query(qString)        
    else:
        select_df = data
    
    
####################################### Show the tree data in a table
    
    st.sidebar.subheader("Do you want to SHOW the data in a table?")
    showYesOrNo = st.sidebar.radio("", options =('Show data', "Hide data"))
    
    if showYesOrNo == 'Show data':
        selectedCols = st.sidebar.multiselect('Select the ADDITIONAL columns to show in the table', data_columns)
        tableFrame.plotly_chart(showTable(select_df, selectedCols))
    else:
        tableFrame.write('')
    

##################################################  Map the tree data
    
    st.sidebar.subheader("Do you want to MAP the data?")
    mapYesOrNo = st.sidebar.radio("", options =('Map the data', "Hide the map"))
    
    if mapYesOrNo == 'Map the data':
        treeMap = mapIt(select_df)
        mapFrame.plotly_chart(treeMap)
    else:
        mapFrame.write('')
        
        
        
################################################ Analyze the diversity 
       
    st.sidebar.subheader("Do you want to analyze the tree DIVERSITY?")
    diversityYesOrNo = st.sidebar.radio("", options =('Analyze diversity', "Hide the diversity analysis"))
    
    if diversityYesOrNo == 'Analyze diversity':
        diversity(select_df)

        
############################################### Analyse the species origin 
      
    # if st.sidebar.checkbox('Analyze Species Origin'):
    #     speciesOrigin(select_df)
        
    st.sidebar.subheader("Do you want to analyze the tree ORIGIN?")
    originYesOrNo = st.sidebar.radio("", options =('Analyze origin', "Hide the origin analysis"))
    
    if originYesOrNo == 'Analyze origin':
        speciesOrigin(select_df)





# ################################################## Map the selected data
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
    
    base_map_type = st.sidebar.radio('Select the basemap', options= ['Map', 'Photo'])

    if base_map_type == 'Map':       
        fig.update_layout(mapbox_style = 'open-street-map')
    else:    
        # useSatellite(fig)
        
        fig.update_layout(mapbox_style = 'satellite', mapbox_accesstoken = token )
        
        
    fig.layout.width=1500
    fig.layout.height=1500
    
    fig.update_layout(legend=dict(yanchor="top",
                                  y=0.99,
                                  xanchor="left",
                                  x=0.01
                                  ))
    
    size_slider = st.sidebar.slider('Select the size of the marker on the map', min_value = 5, max_value = 20, value = 10)
    fig.update_traces(marker_size = size_slider)
    
    return fig


# ########################################## Diversity ############################################
    
def diversity(data):
    
    divLevel = st.sidebar.radio('Select a level of diversity', ('species', 'genus', 'family'))
        
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
    
    speciesPie = px.pie(topTenPlusOther, values='frequency', names = divLevel, title='Tree Diversity')
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
    
    CpaPie = px.pie(topTenCpaPlusOther, values='Crown Projection Area', names = divLevel, title='Tree Diversity by Crown Projectin Area')
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
    
    originPie = px.pie(originPT, values='frequency', names = 'origin', title='Tree Species Origin')
    
    originPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    originPie.update_layout(showlegend=False)
    
    st.plotly_chart(originPie)
        
########################### Tree condition analysis###########################




########################### Relative SBH Analysis  ###########################





########################### Species Suitability Analysis ###########################






########################### Backup tree table  ###########################
   
################################# setup up the function button across the top of the page ##################################
select_df = getSelection(gdf)


    

