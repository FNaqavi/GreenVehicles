# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 09:12:08 2022

@author: naqavi
"""

import pandas as pd
import numpy as np

df = pd.read_csv("personbilaritrafik.csv", encoding = 'latin1')

# produce long file with total fleet
cols = ['Bensin','Diesel','El','Etanol.hybrid','Bensin.El','Gas','Övriga','Totalt','Miljöbil']
x = df['Bensin'].append(df['Diesel']).append(df['El']).append(
    df['Etanol.hybrid']).append(df['Bensin.El']).append(df['Gas']).append(
    df['Övriga']).append(df['Totalt']).append(df['Miljöbil']).reset_index(drop = True)
new_cols = ['Year', 'Komkod','Kommun','ee.index','rr.index']
new = df.filter(new_cols, axis=1)
Registry_tot = pd.DataFrame(data = np.tile(new,(9,1)), columns = new_cols) 
Registry_tot['Drivmedel'] = np.repeat(cols,182)
Registry_tot['tot_veh'] = x
del x, new_cols

# produce long file with fleet subset from 2009 onward
x = df['Bensin.from09'].append(df['Diesel.from09']).append(df['El.from09']).append(
    df['Etanol.hybrid.from09']).append(df['Bensin.El.from09']).append(df['Gas.from09']).append(
    df['Övriga.from09']).append(df['Totalt.from09']).append(df['Miljöbil.from09']).reset_index(drop = True)
new_cols = ['Year', 'Komkod','Kommun']
new = df.filter(new_cols, axis=1)
Registry_f09 = pd.DataFrame(data = np.tile(new,(9,1)), columns = new_cols) 
Registry_f09['Drivmedel'] = np.repeat(cols,182)
Registry_f09['f09_veh'] = x
del x, new_cols, new

# merge
registry = pd.merge(Registry_tot, Registry_f09, how='left', on=["Year","Komkod","Kommun","Drivmedel"])
registry['f09_pv'] = registry['f09_veh']/registry['tot_veh']
registry['t08_pv'] = (registry['tot_veh']-registry['f09_veh'])/registry['tot_veh']

# Modify Drivmedel in "registry" to conform to "passages"
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Bensin', 'Petrol', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Diesel', 'Diesel', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('El', 'Electric', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Bensin.El', 'Electric.Hybrid', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Etanol.hybrid', 'Ethanol', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Bensin', 'Petrol', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Gas', 'Natural.Gas', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Övriga', 'Other', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Totalt', 'Total', regex = True)
registry['Drivmedel'] = registry['Drivmedel'].str.replace('Miljöbil', 'AFV', regex = True)

# Get share of clean vehicles pre-2008 for all-county
x = registry['t08_pv'].loc[registry['Drivmedel'] == 'AFV']
w = registry['tot_veh'].loc[registry['Drivmedel'] == 'AFV']
share_clean_t08 = sum(x*w)/(sum(w))

x = registry['f09_pv'].loc[registry['Drivmedel'] == 'AFV']
w = registry['tot_veh'].loc[registry['Drivmedel'] == 'AFV']
share_clean_f09 = sum(x*w)/(sum(w))






