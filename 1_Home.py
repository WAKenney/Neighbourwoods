import streamlit as st

currentDir = "https://raw.githubusercontent.com/WAKenney/NWAnalytics/main/"

titleCol1, titleCol2, titleCol3 =st.columns((1,4,1))
title = currentDir + 'NWAnalyticsTitle.jpg'
titleCol2.image(title, use_column_width=True)

st.markdown("""
        Neighbourwoods is a community-based program to assist community groups in the stewardship of the urban forest in their neighbourhood.
        Using NWAnalytics, you can map and analyze various aspects of the urban forest that will help you develop and implement stewardship strategies.
        At present, you must first have your Neighbourwoods tree inventory data in a Neighbourwoods MS excel workbook (version 2.6 or greater).

        To get started, select your Neighbourwoods MS excel workbook at the sidebar on the left. Once your data has been uploaded (this may take 
        a few minutes if you have a big file, be patient) you will be asked to select the functions you want to display.  Select as many as you 
        want from the dropdown list __AND CLICK ON CONTINUE__.  The selected analyses will be shown in the main frame.

        You can conduct these analyses on all the data, or you can filter the data for specific queries. For hints on filtering your data, click on the button below.

        In various places you will have opportunities to click on a box 
        for more information, just as you are reading this text.  To close these boxes, simply click on the header button again.

        Click on the following link to read more about Neighbourwoods: http://neighbourwoods.org/')

        For support, contact Andy Kenney at:     a.kenney@utoronto.ca
""")

st.markdown("___")



