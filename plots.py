# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:22:41 2022

This file is used to create plots

@author: naqavi
"""




import pandas as pd
import matplotlib.pyplot as plt
from set_price import set_price
from create_veh_pass import create_veh_pass


d = pd.read_csv('registry_data.csv', encoding='latin 1')
passages = set_price()
veh_year, pass_veh = create_veh_pass()
#veh_year = pd.read_csv('veh_year.csv', encoding='latin 1')
data_veh = veh_year[{'AnonymRegno','Kommun','FuelCat','expgrp','year','totalprice'}]
del veh_year
mask = data_veh.groupby(['FuelCat','year','Kommun']).count().rename(columns = {'totalprice':'count'}).iloc[:,-1]
mask_price = data_veh.groupby(['FuelCat','year','Kommun']).sum()
mask_price['count'] = mask
df = mask_price.reset_index()  
del mask, mask_price

#%% Plots share of AFV (before 2008 and after 2009) in 2012 and 2013 

# share of AFV vehicles in 2012 and 2013 for vehcile and Kommun data
d['p_AFV_f09'] = 100* d['AFV_f09'] /(d['AFV_f09'] + d['AFV_t08'])     # gives warning
d['p_AFV_t08'] = 100* d['AFV_t08'] /(d['AFV_f09'] + d['AFV_t08'])    # gives warning

AFV_mask_f09 = d[{'Kommun','year','p_AFV_f09'}]
AFV_mask_t08 = d[{'Kommun','year','p_AFV_t08'}]

AFV_mask_f09_2012 = AFV_mask_f09[AFV_mask_f09['year'] == 2012]
AFV_mask_t08_2012 = AFV_mask_t08[AFV_mask_t08['year'] == 2012]
AFV_mask_f09_2013 = AFV_mask_f09[AFV_mask_f09['year'] == 2013]
AFV_mask_t08_2013 = AFV_mask_t08[AFV_mask_t08['year'] == 2013]

# share of AFV vehicles up to 2008 and after 2009 for passages data
df_AFV = df[df['FuelCat'] == 'AFV']
df_AFV = df_AFV[df_AFV['year'] == 2013].reset_index()

x = AFV_mask_f09_2012['Kommun']
y1 = AFV_mask_f09_2012['p_AFV_f09']
y2 = AFV_mask_t08_2012['p_AFV_t08']
plt.figure(figsize=(20, 3))
plt.bar(x,y1, color = 'navy', alpha=1, label = 'AFV share after 2009')
plt.bar(x,y2, bottom=y1, color = 'darkred', alpha=1, label = 'AFV share before 2008')
plt.xticks(rotation=90)
plt.legend(loc = 'upper right')
plt.xlabel('share of AFV in 2012 in the registry data')

x = AFV_mask_f09_2012['Kommun']
y3 = AFV_mask_f09_2013['p_AFV_f09']
y4 = AFV_mask_t08_2013['p_AFV_t08']
plt.figure(figsize=(20, 3))
plt.bar(x,y3, color = 'navy', alpha=1, label = 'AFV share after 2009')
plt.bar(x,y4, bottom=y3, color = 'darkred', alpha=1, label = 'AFV share before 2008')
plt.xticks(rotation=90)
plt.legend(loc = 'upper right')
plt.xlabel('share of AFV in 2013 in the registry data')

del x, y1, y2, y3, y4, df_AFV, AFV_mask_f09_2012, AFV_mask_f09_2013
del AFV_mask_t08_2012, AFV_mask_t08_2013, AFV_mask_f09, AFV_mask_t08  

#%%

