
# coding: utf-8

# In[163]:

# Neighbourwoods


# In[164]:

import os
import pandas as pd
from pandas import Series
from pandastable import Table
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from easygui import *

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import folium
import mplleaflet
import webbrowser
#from pandasql import sqldf
#sqldf = lambda q: sqldf(q, globals())

pd.options.mode.chained_assignment = None

root=Tk()
root.state('zoomed')
root.title('Neighbourwoods 1.0')
root.iconbitmap('nw_logo.bmp')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(("%dx%d")%(screen_width,screen_height))


# In[165]:

def quit_nw():

    save_answer=messagebox.askyesno('Are you sure you want to exit Neighbourwoods?')
    if save_answer==True:
        root.quit()
        root.destroy()


# In[166]:

def get_spp_codes_scores():
    #this gets the NW species table from the excel workbook called nw_codes.xlsx and reads it in
    # as a dataframe called df_spp.  The sheets in this workbook are all standadrd for NW
    # and won't change from project to project. These should be hard coded at some point.
    
    global df_spp, df_codes, df_scores
    
    spp_xls = pd.ExcelFile(r"nw_codes.xlsx")
    df_spp = spp_xls.parse('species')
    df_spp.set_index('spp_code',drop=False,inplace=True)
    
    # as with the species table above, this gets the text descriptions for the condition codes
    # from the excel workbook nw_codes

    codes_xls = pd.ExcelFile(r"nw_codes.xlsx")
    df_codes = codes_xls.parse('codes')
    df_codes.set_index('score',drop=True,inplace=True)
    
    # as above, this gets the scores for the condition codes from the excel workbook nw_codes

    scores_xls = pd.ExcelFile(r"nw_codes.xlsx")
    df_scores = scores_xls.parse('scores')
    df_scores.set_index('score',drop=True,inplace=True)


# In[167]:

def get_xls_trees():
    
    global xls_data, df_blocks, df_streets
    
    # get Excel file name for the fiel with the project specific tree data and call it xls_data
    xls_file_name =filedialog.askopenfilename()
    xls_file = pd.ExcelFile(xls_file_name)
        
    #Load the xls file's "trees" sheet as a dataframe and set the index as 
    #Tree name and drop the tree index column from xls_data   
    xls_data = xls_file.parse('trees')
    
    
    ######
    
    #Put code to test variable (column) names for NW input file here. Code need to be written
    
    #####
    
    xls_data.set_index('Tree name', drop=False, inplace=True)
    xls_data.drop('tree index', axis=1, inplace=True)
    
    #make all values (not column titles) in selected columns lower case for standardization
    for c in ['Tree name', 'Block Id','street_code', 'species_code', 'location_code', 'ownership_code']:
        xls_data[c]=xls_data[c].str.lower()
        
    #standardize column names from the old Excel format (excel dataa input sheet) to the new one
    # these names are all lower case with blannks removed
    xls_data.index.names=['tree_name']
    xls_data=xls_data.rename(columns = {'Tree name':'tree_name','Crown Width':'crown_width',
                'House Number':'house_number','Date':'date','Block Id':'block_code',
                'Tree No':'tree_number','Number of Stems':'number_of_stems','DBH':'dbh',
                'Hard surface':'hard_surface','Ht to base':'height_to_crown_base',
                'Total Height':'total_height','Reduced Crown':'reduced_crown',
                'Unbalanced Crown':'unbalanced_crown','Defoliation':'defoliation',
                'Weak or Yellow Foliage':'weak_or_yellow_foliage',
                'Dead or Broken Branch':'dead_or_broken_branch','Lean':'lean',
                'Poor Branch Attachment':'poor_branch_attachment','Branch Scars':'branch_scars',
                'Trunk Scars':'trunk_scars','Conks':'conks',
                'Rot or Cavity - Branch':'branch_rot_or_cavity',
                'Rot or Cavity - Trunk':'trunk_rot_or_cavity','Confined Space':'confined_space',
                'Crack':'crack','Girdling Roots':'girdling_roots',
                'Recent Trenching':'recent_trenching','Cable or Brace':'cable_or_brace',
                'Conflict with Wires':'wire_conflict','Conflict with Sidewalk':'sidewalk_conflict',
                'Conflict with Structure':'structure_conflict',
                'Conflict with another tree':'tree_conflict',
                'Conflict with Traffic Sign':'sign_conflict','Comments':'comments',
                'X coordinate':'longitude','Y coordinate':'latitude'})
    
    #change various values to lower case strings
    xls_data['house_number']=xls_data['house_number'].astype(str)
    xls_data['street_code']=xls_data['street_code'].str.lower()
    xls_data['block_code']=xls_data['block_code'].str.lower()
    xls_data['species_code']=xls_data['species_code'].str.lower()
    xls_data['location_code']=xls_data['location_code'].str.lower()
    xls_data['ownership_code']=xls_data['ownership_code'].str.lower()
    
    #Load the xls file's "blocks" sheet as a dataframe.  This is project specific.
    df_blocks = xls_file.parse('blocks')
    df_blocks=df_blocks.rename(columns={'Block Id':'block_code','Block Description':'block_description'})
    df_blocks.set_index('block_code', drop=False, inplace=True)
    df_blocks.index = df_blocks.index.str.lower()
    df_blocks.block_code=df_blocks.block_code.str.lower()
    
    #Load the xls file's "streets" sheet as a dataframe.  This is project specific.
    df_streets = xls_file.parse('streets')
    df_streets=df_streets.rename(columns={'ADDRESS':'street_code','ADDRESSNAME':'street_name'})
    df_streets.set_index('street_code', drop=False, inplace=True)
    df_streets.index = df_streets.index.str.lower()
    df_streets.street_code=df_streets.street_code.str.lower()
    
    return

get_xls_trees()


# In[168]:

def trees_non_trees():
    #separates actual trees from non-tree (plantable spots, dead trees, etc.) entries
    # the non-tree entries don't havee all the variables included
    global df_trees, df_non_trees
    df_trees=xls_data[~xls_data['species_code'].isin(['dead', 'x', 'stump', 'hedge', 'forest'])]
    df_non_trees=xls_data[xls_data['species_code'].isin(['dead', 'x', 'stump', 'hedge', 'forest'])]
    
    return


# In[169]:

def fix_species():
    # this checks to see if the species codes usedin the trees table match those in the
    # species table.  If not, the user is given a chance to correct errors.
    
    bad_codes={x for x in df_trees.species_code if x not in df_spp.spp_code}
    bad_good = pd.DataFrame(columns=(('bad'),('good')),index=bad_codes)

    for incorrect in bad_codes:
        bad_good.loc[incorrect]=[incorrect,choicebox(incorrect, 'Fix incorrect species codes', 
                df_spp.spp_code)]
    
    for row in bad_codes:
        df_trees.species_code.replace(row, bad_good.ix[row,'good'] , inplace=True, regex=False)
    
    return df_trees


# In[170]:

def fix_streets():
    # this checks to see if the street codes used in the trees table match those in the
    # streets table.  If not, the user is given a chance to correct errors.
    
    bad_codes={x for x in df_trees.street_code if x not in df_streets.street_code}
    bad_good = pd.DataFrame(columns=(('bad'),('good')),index=bad_codes)
    
    for incorrect in bad_codes:
        bad_good.loc[incorrect]=[incorrect,choicebox(incorrect, 'Fix incorrect street codes', 
                df_streets.street_code)]
    
    for row in bad_codes:
        df_trees.street_code.replace(row, bad_good.ix[row,'good'] , inplace=True, regex=False)
    
    return df_trees


# In[171]:

def fix_blocks():
    # this checks to see if the block codes used in the trees table match those in the
    # blocks table.  If not, the user is given a chance to correct errors.
    bad_codes={x for x in df_trees['block_code'] if x not in df_blocks['block_code']}
    bad_good = pd.DataFrame(columns=(('bad'),('good')),index=bad_codes)
    
    for incorrect in bad_codes:
        bad_good.loc[incorrect]=[incorrect,choicebox(incorrect, 'Fix incorrect block codes', 
                df_blocks['block_code'])]
    
    for row in bad_codes:
        df_trees.block_code.replace(row, bad_good.ix[row,'good'] , inplace=True, regex=False)
    
    return df_trees


# In[172]:

def der_non_trees():
    
    #this stes up the summary dessccription for non-trees.  
    #Keep in mind that this summary will still call the entry a "tree".
    #for example, Tree number A-1 is a plantable spot at 123 Main Street etc.
    df_sum_non_trees=pd.merge(df_non_trees, df_spp.loc[:,['species_name']],
        left_on="species_code", right_index=True, how="left", sort=False)
    
    df_non_trees_place=pd.merge(df_non_trees.loc[:,['house_number','street_code']], 
        df_streets.loc[:,['street_name']],left_on="street_code", right_index=True, 
        how="left", sort=False)
    df_non_trees_place['full_address']=df_non_trees_place['house_number']+' '+df_non_trees_place['street_name']
    
    #set up string showing tree description
    df_sum_non_trees['desc']='Tree '+df_sum_non_trees['tree_name']+' is a '+df_sum_non_trees['species_name']+' at '        +df_non_trees_place['full_address']+'.'

    return df_sum_non_trees


# In[173]:

def taxonomy ():
    # this changes the species code to the common species name and adds the
    #tree family and genus from the species table based on the species code
    # the maximum dbh for the species is also read from the species table.
    #Maximum dbh is used to calculate relative dbh (RDBH) below.
    taxonomy=pd.merge(df_trees, df_spp.loc[:,['family', 'genus','species_name','max_dbh']],
            left_on="species_code", right_index=True, how="left", sort=False)
    
    return taxonomy


# In[174]:

def size(df_sum):
    # this calculates the crown projection area based on the crown width from the trees table
    df_sum['cpa']=3.14*((df_sum['crown_width']/2)**2)
    df_sum.cpa=df_sum.cpa.round(0)
    # this calculates relative dbh from the dbh in the trees table and maximumm dbh from Taxonomy above
    df_sum['rdbh']=df_sum['dbh']/df_sum['max_dbh']# calculate rdbh
    df_sum.rdbh=df_sum.rdbh.round(2)
    df_sum.drop('max_dbh', axis=1, inplace=True)#we needed max_dbh form df_spp to calculate rdbh, now we can get rid of it from df_sum.
    
    return df_sum


# In[175]:

def suitability ():
    # this determines the species suitability based on the ISAO supplement
    #to the 9th approximation of the CTLA stem formula method.
    
    suitability=pd.merge(df_sum, df_spp.loc[:,['suitability']],
            left_on="species_code", right_index=True, how="left", sort=False)
    
    return suitability


# In[176]:

def native ():
    # this determines if the species is native or non-native 
    native=pd.merge(df_sum, df_spp.loc[:,['native']],
            left_on="species_code", right_index=True, how="left", sort=False)
    
    return native


# In[177]:

def address():
    #this combines the house number and street name to form the address
    #the df_sum['desc'] or description is initiated with the tree name 
    #and address.  Various details are concatenated to the description (desc)
    # at later points.
    
    df_place=pd.merge(df_trees.loc[:,['house_number','street_code']], 
                  df_streets.loc[:,['street_name']],left_on="street_code", right_index=True, 
                  how="left", sort=False)
    df_place['full_address']=df_place['house_number']+' '+df_place['street_name']

    df_sum['desc']='Tree '+df_trees['tree_name']+' is a '+df_sum['species_name']+' at '+df_place['full_address']+'. '
    
    return df_sum['desc']


# In[178]:

#this determines if there are multiple stems, if so df_sum has the addition of 'It has x stems with and average dbh
#otherwise (one stem) df_sum has ' The dbh is' added to it.

def dbh_stems(stems, dbh):
    if stems>1:
        stems_and_dbh=' It has '+str(round(stems))+' stems with an average dbh of '+str(dbh)+' cm. '
    else:
        stems_and_dbh=' It has a dbh of '+str(dbh)+' cm.'
    return stems_and_dbh
    


# In[179]:

def h_surface(surface):
    #this creates the description of the amount of hard surface under the crown based on the
    #value in the trees table.  This is added to the description Desc later on.
    if surface==100:
        h_surface=' The area under the crown is all hard surface. '
    elif surface==0:
        h_surface=' The area under the crown is all soft surface.'
    else:
        h_surface=' Approximately '+str('{:.0f}'.format(surface))+'% of the area under the crown is hard surface.'
    return h_surface


# In[180]:

def crown(cw, ht):
    #This creates the description of the various crown size parameters
    if(pd.isnull(cw)& pd.isnull(ht)):
        ans=" The height and width of the crown were not recorded."
    elif (pd.isnull(cw)& pd.notnull(ht)):
       ans=' The total height of the tree is '+str('{:.0f}'.format(ht))+'m but the width of the crown was not recorded.'
    elif (pd.notnull(cw)& pd.isnull(ht)):
       ans=' The width of the crown is '+str('{:.0f}'.format(cw))+'m but the height of the tree was not recorded.'
    else:
       ans=' The width of the crown is '+str('{:.0f}'.format(cw))+'m and the height of the tree is '+str('{:.0f}'.format(ht))+'m.'
    return ans
       


# In[181]:

def rating():
    #This calculates the simple rating based on the condition codes from the trees table
    # and the corresponding scores from the scores table.  
    #Demerits scores are calculated for each tree as the sum of ALL condition scores.
    #THIS NEEDS TO BE CHANGED SO BLANK SCORES ARE NOT ADDED TO THE MAX_DEMERITS
    
    #max_demerits=df_scores.loc[3:].sum(axis=1)
    code_names=df_scores.columns
    df_demerits = pd.DataFrame(columns=code_names)
    
    #this changes each code to the corresponding score
    for column in code_names:
        df_demerits[column]=df_trees[column].map(df_scores[column]).fillna('')
        pd.to_numeric(df_demerits[column])

    df_demerits = df_demerits.apply(pd.to_numeric, errors='coerce')

    #This calclates the total demerits for each tree as the sum of all scores.
    df_demerits["sum"] = df_demerits.sum(axis=1)

    return df_demerits['sum']


# In[182]:

def rating_class(d):
    #This creates a rating class for each tree baseed on the total demerits
    #In the sores table defoliation score of 3 and reduced crown score of 3 have a weight
    # of 100 demerits.  This value results in a pvery poor rating.  All other scores are
    # proportional to these.  Any total demerits over 100 results in a class of very poor
    if d >= 80:
        demerits_class='very poor'
    elif d >=60:
        demerits_class='poor'
    elif d >= 40:
        demerits_class ='fair'
    elif d >= 20:
        demerits_class='good'
    else:
        demerits_class='excellent'
            
    return demerits_class


# In[183]:

def condition():
    # this creates a series called code_names holding the column 
    #names from df_codes and an empty df called df_cond 
    #which is then filled with the text from df_codes 
    #corresponding to each of the scores from df_trees for each column 
    #in code_names. The result is additon of condition descriptions to
    #df_sum['desc']

    code_names=df_codes.columns
    df_cond = pd.DataFrame(columns=code_names)
    for column in code_names:
        df_cond[column]=df_trees[column].map(df_codes[column]).fillna('')
        
    return df_cond.apply(lambda row: ''.join(map(str, row)), axis=1)


# In[184]:

def get_summary():#THIS DOESN'T WORK YET
        save_answer=messagebox.askyesno('Open Neighbourwoods Summary File',
        'Do you want to open an existing Neighbourwoods summary file (CSV)?')
        
        if save_answer==True:
            del df_sum
            df_sum =filedialog.askopenfile(mode='r', defaultextension=".csv")
            #df_sum = pd.read_csv('fname')
        return df_sum
    


# In[185]:

def pt_count(data,values,columns,index):
    #create a pivot table. The inputs are: data is the dataframe to use
    #values are the body of the pivot table, columns and index are the
    #columns and row headers for the resulting pivot table.
    
    table=None
    table=pd.pivot_table(data=data, values=values, columns=columns,index=index, 
                   aggfunc='count', fill_value=0)
    return table


# In[186]:

def pt_sum(data,values,columns,index):
    #create a pivot table. The inputs are: data is the dataframe to use
    #values are the body of the pivot table, columns and index are the
    #columns and row headers for the resulting pivot table.
    
    table=None
    table=pd.pivot_table(data=data, values=values, columns=columns,index=index, 
                   aggfunc='sum', fill_value=0)
    return table


# In[187]:

def top_ten(data):
    #determine top ten values of pivot table then calculte the 
    #sum of all remaining values and call it "other"
    #concatenate the top ten with other to create a new series
    #top_ten is a dataframe with the top ten species by name and
    # frequency including the other as described above
    
    data['total']=0
    grand_total=0
    sum_top_ten=0
    other_total=0
    data['total'] = data.sum(axis=1)
    grand_total=data.total.sum()
    top_ten=data['total'].nlargest(10)
    sum_top_ten=top_ten.sum()
    other_total=grand_total-sum_top_ten
    other=pd.Series({'other': other_total})
    top_ten=pd.concat((top_ten, other))
    
    return top_ten
   


# In[188]:

def pie_chart(data, pie_title):
    #generate pie chart of top_ten plus "other".  The second input 
    #is the title for the chart
    
    labels = data.index
    sizes=data
    colors=['red','orange', 'yellow','green','blue','indigo', 'violet',
    'yellowgreen', 'gold', 'lightskyblue', 'grey']
    
    pie_frame=Toplevel()

    figure=Figure(figsize=(5,5), dpi=100)
    
    plt=figure.add_subplot(111)
    plt.pie(sizes, autopct='%1.1f%%', colors=colors)

    plt.legend(labels, ncol=2,loc="upper left",fontsize=6, bbox_to_anchor=(1,1))
    
    plt.axis('equal')

    canvas=FigureCanvasTkAgg(figure,master=pie_frame)
    canvas.show()
    
    canvas.get_tk_widget().pack()
    canvas._tkcanvas.pack()
    
    pie_title = Label(pie_frame, text=pie_title, font=('', 18))
    pie_title.pack()
    
    close_button=Button(master=pie_frame, text="Close Window", command=pie_frame.destroy).pack()
    root.protocol("WM_DELETE_WINDOW", pie_frame.destroy)


# In[189]:

def view_summary():
    #answer=messagebox.askyesno('Do you want to view the summary table?')
    #if answer==True:
    
    frame_df_sum = Frame(master=root, width=screen_width, height=screen_height, highlightbackground="green", 
                         highlightcolor="green", highlightthickness=1)
    
    frame_df_sum.grid(row=1, column=1)
    df_sum_table = Table(frame_df_sum, dataframe=df_sum, width=screen_width*.93, height=screen_height*.8, showtoolbar=False, 
        showstatusbar=False, title="Neighbourwoods Summary")
    #close_button=Button(master=frame_df_sum, text="Close Window", command=frame_df_sum.destroy).pack(expand=True, fill='both')
    
    
    root.protocol("WM_DELETE_WINDOW", frame_df_sum.destroy)
    df_sum_table.show()


# In[190]:

def spp_freq(df_sum):
    #Calculate Relative Frequency (number of trees by species) using the
    # pivot table of street codes by species as the input
    # the result is then sent to pie_chart() for plotting
    
    pt_stxspp=pt_count(data=df_sum, columns=['block_code'], 
                   index=['species_name'], values='tree_name',)
    
    pie_chart(top_ten(pt_stxspp))
    


# In[191]:

def spp_freq_pie_chart():
    data=top_ten(pt_count(data=df_sum, columns=['block_code'], 
           index=['species_name'], values='cpa',))
    pie_title="Species Relative Frequency"
    pie_chart(data, pie_title) #pie_chart(data)


# In[192]:

def genus_freq_pie_chart():
    data=top_ten(pt_count(data=df_sum, columns=['block_code'], 
           index=['genus'], values='tree_name',))
    pie_title="Genus Relative Frequency"
    pie_chart(data,pie_title)


# In[193]:

def family_freq_chart():
    data=top_ten(pt_count(data=df_sum, columns=['block_code'], 
           index=['family'], values='tree_name',))
    pie_title="Family Relative Frequency"
    pie_chart(data, pie_title)


# In[194]:

def spp_cpa_pie_chart():
    data=top_ten(pt_sum(data=df_sum, columns=['block_code'], 
           index=['species_name'], values='cpa',))
    pie_title="Species Relative CPA"
    pie_chart(data, pie_title)


# In[195]:

def genus_cpa_pie_chart():
    data=top_ten(pt_sum(data=df_sum, columns=['block_code'], 
           index=['genus'], values='cpa',))
    pie_title="Genus Relative CPA"
    pie_chart(data, pie_title)


# In[196]:

def family_cpa_pie_chart():
    data=top_ten(pt_sum(data=df_sum, columns=['block_code'], 
           index=['family'], values='cpa',))
    pie_title="Family Relative CPA"
    pie_chart(data, pie_title)


# In[197]:

#plot the trees on a map
def map_trees(mapdata):
    
    avlat=mapdata['latitude'].mean()
    avlong=mapdata['longitude'].mean()

    map = folium.Map(location=[avlat, avlong], zoom_start=18)
    for index, tree in mapdata.iterrows():
        folium.CircleMarker(location=(tree['latitude'],tree['longitude']),radius=0.5,
        popup=tree['desc']).add_to(map)
    map.save(outfile='tree_map.html')
    


# In[198]:

def map_all_trees():
    map_trees(df_sum)
    


# In[199]:

def view_trees_map():
    
    if os.path.isfile('tree_map.html'):
        webbrowser.open('tree_map.html')
    else:
        map_trees(df_sum)
        messagebox.showinfo(message="OH NO!, it looks like the tree map file doesn't exist yet. Give me a minute to fix that")
        webbrowser.open('tree_map.html')


# In[200]:

def save_df_sum_csv():

    save_answer=messagebox.askyesno('Save Neighbourwoods Summary File',
        'Do you want to save the Neighbourwoods summary file as a CSV file?')

    if save_answer==True:
        try:
            save_csv_fname =filedialog.asksaveasfile(mode='w', defaultextension=".csv")
            df_sum.to_csv(save_csv_fname)
        except:
            messagebox.showinfo(message='Ooops, it looks like the file may be open. Close it and try again')
            save_df_sum_csv()
        else:
            save_csv_fname.close
        


# In[201]:

def query():
    #THIS NEEDS TO BE SET UP.  THIS IS JUST A PLACE HOLDER

    meats = load_meat()
    births = load_births()

    z = """SELECT
       meats.beef, meats.date, meats.beef, births.births
    FROM
        meats
    INNER JOIN
        births
           ON meats.date = births.date;"""
           
    joined = pysqldf(z)
    joined.head()


# In[202]:

#df_sum.query('(species_code=="oakbur" or species_code=="oakred") and cpa>71') # this works


# In[203]:

def callback():
    messagebox.showinfo(message="Sorry for the disappointmnet, this doesn't do anything yet!")


# In[204]:

get_spp_codes_scores()

trees_non_trees()

df_trees=fix_species()

df_trees=fix_streets()

df_trees=fix_blocks()

df_sum_non_trees=der_non_trees()

df_sum=taxonomy()

df_sum=size(df_sum)

df_sum=native()

df_sum=suitability()


# In[205]:

df_sum['demerits']=rating()


# In[206]:

df_sum['condition_class']= df_sum.demerits.apply(lambda x: rating_class(x))


# In[207]:

address=address()


# In[208]:

#df_sum['desc'] = df_sum['desc']+df_sum.apply(lambda x: dbh_stems(x['number_of_stems'], x['dbh']), axis=1)
stems = df_sum.apply(lambda x: dbh_stems(x['number_of_stems'], x['dbh']), axis=1)


# In[209]:

#df_sum['desc'] = df_sum['desc']+df_sum.apply(lambda x: h_surface(x['hard_surface']), axis=1)
surface = df_sum.apply(lambda x: h_surface(x['hard_surface']), axis=1)


# In[210]:

#df_sum['desc']=df_sum['desc']+df_sum.apply(lambda x: crown(x['crown_width'], x['total_height']), axis=1)
size=df_sum.apply(lambda x: crown(x['crown_width'], x['total_height']), axis=1)


# In[211]:

#df_sum['desc']=df_sum['desc']+'The tree is in '+ df_sum['condition_class']+ ' condition. '
cond_class='The tree is in '+ df_sum['condition_class']+ ' condition. '


# In[212]:

#df_sum['desc']=df_sum['desc']+condition()
condition=condition()


# In[213]:

df_sum['desc']=address+stems+surface+size+cond_class+condition


# In[214]:

#this reorders the columns in df_sum do the 'desc' appears last
df_sum=df_sum[['tree_name', 'date', 'block_code', 'tree_number', 'house_number',
       'street_code', 'species_code', 'location_code', 'ownership_code',
       'number_of_stems', 'dbh', 'hard_surface', 'crown_width',
       'height_to_crown_base', 'total_height', 'reduced_crown',
       'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage',
       'dead_or_broken_branch', 'lean', 'poor_branch_attachment',
       'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity',
       'trunk_rot_or_cavity', 'confined_space', 'crack', 'girdling_roots',
       'recent_trenching', 'cable_or_brace', 'wire_conflict',
       'sidewalk_conflict', 'structure_conflict', 'tree_conflict',
       'sign_conflict', 'comments', 'longitude', 'latitude', 'family', 'genus',
       'species_name', 'cpa', 'rdbh', 'suitability','native','demerits',
       'condition_class','desc']]

view_summary()


# In[ ]:

# create a menu
menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Import NW data from an Excel file", command=callback)
filemenu.add_command(label="Import NW Data from CSV files (3)", command=callback)
filemenu.add_separator()
filemenu.add_command(label="Open a NW Summary (CSV)", command=callback)
filemenu.add_separator()
filemenu.add_command(label="Save the NW summary file", command=save_df_sum_csv)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit_nw)

viewmenu=Menu(menu)
menu.add_cascade(label="View", menu=viewmenu)
viewmenu.add_command(label="View summary table of all data", command=view_summary)
viewmenu.add_command(label="View map of all trees in your webbrowser", command=view_trees_map)

analyzemenu=Menu(menu)
menu.add_cascade(label="Analyze", menu=analyzemenu)
analyzemenu.add_command(label="Species Relative Frequency", command=spp_freq_pie_chart)
analyzemenu.add_command(label="Genus Relative Frequency", command=genus_freq_pie_chart)
analyzemenu.add_command(label="Family Relative Frequency", command=family_freq_chart)
analyzemenu.add_separator()
analyzemenu.add_command(label="Species Relative CPA", command=spp_cpa_pie_chart)
analyzemenu.add_command(label="Genus Relative CPA", command=genus_cpa_pie_chart)
analyzemenu.add_command(label="Family Relative CPA", command=family_cpa_pie_chart)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=callback)
                     


# In[ ]:

root.mainloop()
root.destroy

