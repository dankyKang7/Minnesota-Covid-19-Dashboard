# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 19:45:21 2020

@author: travm
"""

import os 
import numpy as np
import pandas as pd
from datetime import datetime as dt

import seaborn as sns
import matplotlib.pyplot as plt

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
nyTimesData = pd.read_csv(url)

nyTimesData[['county','state']] = nyTimesData[['county','state']].astype('str')

os.chdir('C:/Users/travm/Desktop/covid19_Analysis')

usCounties = pd.read_csv('covid19_Analysis.csv')
usCounties2019pop = pd.read_csv('estimatedpop2019byCounty.csv',\
                                names = ['County','State','pop2019'])
usCounties2019pop['County'] = usCounties2019pop['County'].astype('str').\
    apply(lambda x: str.replace(x,' County',''))    
usCounties2019pop['State'] = usCounties2019pop['State'].astype('str').\
    apply(lambda x: str.replace(x,' ',''))

usCounties2019pop['pop2019'] = usCounties2019pop['pop2019'].astype('str').\
    apply(lambda x: str.replace(x,',',''))
usCounties2019pop=usCounties2019pop.iloc[0:3141,:]

#Join the 2 DF
totalData = nyTimesData.merge(usCounties2019pop,left_on=['county','state'],\
                              right_on=['County','State'],how='left').\
                                drop(columns=['County','State'])
totalData['date'] = totalData['date'].apply(lambda x: dt.strptime(x,'%Y-%m-%d'))
                                
totalData['weekOyear'] = totalData['date'].apply(lambda x:\
                            dt.strftime(x,'%V'))
    
# totalData['CummalitiveSumCase'] = totalData.groupby(['county','state'])['cases'].\
#     cumsum()
countyUrbanCluster = pd.read_csv('countyData.csv')

#Create the daily change column
totalData_Sorted = totalData.sort_values('date')

#Mask Wearing Data
maskUrl = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/mask-use/mask-use-by-county.csv'
maskData = pd.read_csv(maskUrl)

#Join Mask Data to Total Data
totalMaskData = pd.merge(totalData_Sorted,maskData,left_on='fips',right_on='COUNTYFP')
# totalMaskData['pop2019'] = totalMaskData['pop2019'].astype('int')
#Minnesota Data
minnesotaData = totalMaskData[totalMaskData['state'].isin(['Minnesota','North Dakota','South Dakota','Iowa','Wisconsin'])]
stLouisCT = 199070

duluthData = minnesotaData[minnesotaData['county']=='St. Louis']
duluthData['pop2019'] = stLouisCT

minnesotaDataState = list(minnesotaData['state'].unique())

def countyBlock(stateListList,dataframe):
    stateFrameList = []
    for state in stateListList:
        countyList = list(dataframe['county'].unique())
        cntyFrameList=[]
        for cnty in countyList:
            stateFrame = dataframe[dataframe['state']==state]
            cntyFrame = stateFrame[stateFrame['county']==cnty]
            cntyFrameSorted = cntyFrame.sort_values('date')
            cntyFrameSorted['caseShift']  = cntyFrameSorted['cases'].shift(1)
            cntyFrameSorted['deathShift'] = cntyFrameSorted['deaths'].shift(1)
            cntyFrameSorted['dailyCaseGrowth'] = cntyFrameSorted['cases'] -\
                cntyFrameSorted['caseShift'] 
            cntyFrameSorted['dailyDeathGrowth'] = cntyFrameSorted['deaths'] -\
                cntyFrameSorted['deathShift']
            cntyFrame_1 = cntyFrameSorted[['date','county','state','pop2019','weekOyear',\
                                           'NEVER','RARELY','SOMETIMES','FREQUENTLY',\
                                               'ALWAYS','cases','dailyCaseGrowth','deaths',\
                                                   'dailyDeathGrowth']]
            if cntyFrame_1.shape[0]>1:
                cntyFrameList.append(cntyFrame_1)
            else:
                continue
        stateFrameList.append(cntyFrameList)
    return stateFrameList

minnesotaData_Growth = countyBlock(minnesotaDataState,minnesotaData)
minnesotaGrowthData1 = [pd.concat(x) for x in minnesotaData_Growth] 
minnesotaGrowthData = pd.concat(minnesotaGrowthData1)

minnesotaGrowthData['pop2019'] = minnesotaGrowthData['pop2019'].fillna(stLouisCT)
minnesotaGrowthData_1 = minnesotaGrowthData.copy()
minnesotaGrowthData_2 = pd.concat([minnesotaGrowthData_1,duluthData])
minnesotaGrowthData_2['pop2019'] = minnesotaGrowthData_2['pop2019'].astype(int)
# minnesotaGrowthData_3 = pd.merge(minnesotaGrowthData_2,countyUrbanCluster,left_on='county',right_on='County ',how='left')


minnesotaGrowthData_2['case%'] = minnesotaGrowthData_2['cases'] / minnesotaGrowthData_2['pop2019']
minnesotaGrowthData_2['caseGrowth%'] = minnesotaGrowthData_2['dailyCaseGrowth'] / minnesotaGrowthData_2['cases']
minnesotaGrowthData_2['death%'] = minnesotaGrowthData_2['deaths'] / minnesotaGrowthData_2['pop2019']
minnesotaGrowthData_2['deathGrowth%'] = minnesotaGrowthData_2['dailyDeathGrowth'] / minnesotaGrowthData_2['deaths']
minnesotaGrowthData_2['caseper100K'] = minnesotaGrowthData_2['case%']*100000
minnesotaGrowthData_2['deathper100K'] = minnesotaGrowthData_2['death%']*100000
minnesotaGrowthData_2['date'] = minnesotaGrowthData_2['date'].apply(lambda x: dt.date(x))

def urbanRuralCluster(pop2019Col):
    if pop2019Col < 50000:
        return 'rural'
    elif pop2019Col >=50000:
        return 'urban'



minnesotaGrowthData_2['ruralUrban'] = minnesotaGrowthData_2.apply(lambda x: urbanRuralCluster(x.pop2019),axis=1)

#Filter to today
latestData = max(minnesotaGrowthData_2['date'])
minnesotaDataToday = minnesotaGrowthData_2[minnesotaGrowthData_2['date'] == latestData]

dailyColList = pd.DataFrame(minnesotaDataToday.columns)
dailyColList = dailyColList[~dailyColList[0].isin(['NEVER','RARELY','SOMETIMES','FREQUENTLY','ALWAYS'])]
varList = ['NEVER','RARELY','SOMETIMES','FREQUENTLY','ALWAYS']
meltList = list(dailyColList[0])

minnesotaDataTodayMelt = minnesotaDataToday.melt(id_vars=meltList,\
value_vars=['NEVER','RARELY','SOMETIMES','FREQUENTLY','ALWAYS'])

minnesotaGrowthData_2 = minnesotaGrowthData_2.drop_duplicates(subset=['county','date'])
minnesotaDataTodayMelt = minnesotaDataTodayMelt.drop_duplicates(subset=['county','date','variable'],keep='first')

minnesotaGrowthData_2.to_csv('dailyCoronaVirusCasesbyCounty.csv')
minnesotaDataTodayMelt.to_csv('todayCovid19casesMN.csv')

# #Timeline
# def minGovResponse(dateCol):
#     if dateCol

#Create scatter plot
#Plot the hourly weather data for MPLS (55408)
sns.set_theme(style='darkgrid')

sns.scatterplot(x='NEVER',y='caseper100K',data=minnesotaDataToday,\
                hue='county',size='pop2019',alpha=0.5)
    