# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 12:16:00 2020

@author: travmat
"""

import requests as req
import pandas as pd
import os 
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs


'''This script will grab the covid-19 data from the Minnesota Department of
Health Website and must be updated daily to create a dashboard'''

mnURL = 'https://www.health.state.mn.us/diseases/coronavirus/situation.html#exp'
covid19MN = req.get(mnURL)

covid19MNtext = covid19MN.text

#Daily Update Table
covid19MNdailyUpdate = pd.read_html(covid19MNtext,attrs={'id':'dailycase'})[0]
covid19MNdailyUpdate['Date'] = dt.now().date()
covid19MNdailyUpdate = covid19MNdailyUpdate[['Date','County','Number of newly reported cases']]
