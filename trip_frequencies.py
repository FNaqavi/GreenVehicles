# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 16:45:29 2022

@author: naqavi
"""

from GV_exepmtion_kommun_assignment import GV_share_assignment
from create_veh_pass import create_veh_pass
import pandas as pd
import matplotlib.pyplot as plt
from get_price_p import get_prices
import numpy as np

p_assigned, passages = GV_share_assignment()
veh_year, pass_veh = create_veh_pass(passages)
p_assigned = get_prices(passages,p_assigned)


pass1 = passages
pass1.sort_values(by = ['passagedate', 'passagetime'], inplace = True)
pass1.reset_index(inplace = True, drop = True)
days = [pass1['passagedate'][i].day for i in range(len(pass1))]
pass1['days'] = pd.Series(days)
pass1 = pass1[pass1.stations != 'Lilla']
pass1.reset_index(inplace = True, drop = True)

def secs(df):
    hour = pd.Series([df['passagetime'][i].hour for i in range(len(df))])
    minute = pd.Series([df['passagetime'][i].minute for i in range(len(df))])
    second = pd.Series([df['passagetime'][i].second for i in range(len(df))])
    return (hour * 60 + minute) * 60 + second

seconds = secs(pass1)
pass1['secs'] = seconds
del seconds
# pass1.replace({'In':'IN'},inplace = True)
pass1.sort_values(by = ['AnonymRegno','days','secs','year'], inplace = True)

## time starts from 6:30 (23400 secs) and ends in 18:59:59
pass1['secs'] = pass1['secs']-min(pass1['secs'])

idx = pass1['AnonymRegno'].unique()

## seperate data available in both years vs. one year
years = pass1.groupby(by = 'AnonymRegno').year.unique()
years = years.reset_index()
length = years.apply(lambda year: year.str.len())
years['yrs'] = length['year']
bothyears_idx = years[years['yrs']>1]
oneyear_idx = years[years['yrs']==1]         


# number of INs and Uts for every vehicle in each year
riktning = pass1.groupby(by = ['AnonymRegno','year','Riktning']).count().reset_index()
riktning = riktning.iloc[: , :-20].rename(columns = {'Passagedatum':'count'})    # Drop last 21 columns of dataframe

riktning = pass1.groupby(by = ['Betalstation','year','Riktning']).count().reset_index()
riktning = riktning.iloc[: , :-21].rename(columns = {'AnonymRegno':'count'})    # Drop last 21 columns of dataframe

npr_betalstation = pass1.groupby(by = ['stations','year','Riktning']).price.sum().reset_index()
npr_betalstation = npr_betalstation.rename(columns = {'price':'sum_price'})    # Drop last 21 columns of dataframe


npr_betalstation2012 = npr_betalstation[npr_betalstation['year'] == 2012]
npr_betalstation2013 = npr_betalstation[npr_betalstation['year'] == 2013]
npr_betalstation2013_IN = npr_betalstation2013[npr_betalstation2013['Riktning'] == 'IN']
npr_betalstation2013_UT = npr_betalstation2013[npr_betalstation2013['Riktning'] == 'UT']
npr_betalstation2012_IN = npr_betalstation2012[npr_betalstation2012['Riktning'] == 'IN']
npr_betalstation2012_UT = npr_betalstation2012[npr_betalstation2012['Riktning'] == 'UT']

df2013 = pd.merge(npr_betalstation2013_IN, npr_betalstation2013_UT, on=["stations"],  suffixes = ('_IN', '_UT'))
df2012 = pd.merge(npr_betalstation2012_IN, npr_betalstation2012_UT, on=["stations"],  suffixes = ('_IN', '_UT'))



###
x1 = df2013['year_IN']
x2 = df2013['year_UT']
x3 = df2013['year_IN']
x4 = df2013['year_UT']

y1 = df2013['sum_price_IN']
y2 = df2013['sum_price_UT']
y3 = df2012['sum_price_IN']
y4 = df2012['sum_price_UT']
        
plt.bar(df2013['stations'], y1, color = 'cornflowerblue')
plt.bar(df2013['stations'], y2, bottom = y1, color = 'navy')
plt.legend(["2013_IN", "2013_UT"])
plt.xticks(rotation=90)
plt.show()

plt.bar(df2012['stations'], y3, color = 'black')
plt.bar(df2012['stations'], y4, bottom = y3 ,color = 'gray')
plt.legend(["2012_IN","2012_UT"])
plt.xticks(rotation=90)
plt.show()


y_diff_IN =  df2012['sum_price_IN'] - df2013['sum_price_IN']
y_diff_UT =  df2012['sum_price_UT'] - df2013['sum_price_UT']

plt.bar(df2012['stations'], y_diff_IN, color = 'green')
plt.bar(df2012['stations'], y_diff_UT, bottom = y_diff_IN ,color = 'blue')
plt.legend(["diff_IN","diff_UT"])
plt.xticks(rotation=90)
plt.show()


# comparison of payments to enter vs. to leave the city center in each year
nprc_riktning = pass1.groupby(by = ['AnonymRegno','year','Riktning']).price.sum().reset_index()
nprc_riktning = nprc_riktning.rename(columns = {'price':'sum_price'})    

nprc_riktning1 = pass1.groupby(by = ['year','Riktning','dayFromStart']).price.sum().reset_index()
nprc_riktning1 = nprc_riktning1.rename(columns = {'price':'sum_price'})   

nprc2012 = nprc_riktning1[nprc_riktning1['year'] == 2012]
nprc2013 = nprc_riktning1[nprc_riktning1['year'] == 2013]
nprc2013_IN = nprc2013[nprc2013['Riktning'] == 'IN']
nprc2013_UT = nprc2013[nprc2013['Riktning'] == 'UT']
nprc2012_IN = nprc2012[nprc2012['Riktning'] == 'IN']
nprc2012_UT = nprc2012[nprc2012['Riktning'] == 'UT']

plt.plot(nprc2013_IN['dayFromStart']+1, nprc2013_IN['sum_price'],'--o',color = 'cornflowerblue')
plt.plot(nprc2013_UT['dayFromStart']+1, nprc2013_UT['sum_price'],'--o',color = 'navy')
plt.plot(nprc2012_IN['dayFromStart']+1, nprc2012_IN['sum_price'],'--o',color = 'black')
plt.plot(nprc2012_UT['dayFromStart']+1, nprc2012_UT['sum_price'],'--o',color = 'gray')
plt.legend(["2013_IN", "2013_UT","2012_IN","2012_UT"])
plt.show()


pass1.sort_values(by = ['AnonymRegno','year','dayFromStart','secs'], inplace = True)
pass1.groupby(by = ['AnonymRegno','days'])

# # analyse data from both years
# idx = np.array(bothyears_idx['AnonymRegno'])

        
        