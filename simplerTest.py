# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 11:19:34 2021

@author: HP
"""

import streamlit as st

st.sidebar.header('Hi, just testing')

dashBoard = st.sidebar.empty()

with dashBoard:
    st.write('Hello again')
    
with dashBoard:
    st.write('Bye for now')

