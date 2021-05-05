# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 11:19:34 2021

@author: HP
"""

import streamlit as st

st.sidebar.header('Hi, just testing')


db1 = st.sidebar.empty()
db2 = st.sidebar.empty()
db3 =st.sidebar.empty()

with db1:
    st.write('This is db1')
    
with db2:
    st.write('')
    
with db3:
    st.write('This is db3')

