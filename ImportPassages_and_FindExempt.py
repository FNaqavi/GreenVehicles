# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 08:51:06 2022

@author: naqavi
"""
import pandas as pd
from datetime import datetime
from datetime import time
import matplotlib.pyplot as plt

#Import data
pass_cv_12 = pd.read_csv("KTH_KontrollGruppPassager_2012.txt",',', index_col = False, encoding = 'latin1')
pass_cv_13 = pd.read_csv("KTH_KontrollGruppPassager_2013.txt", ',', index_col = False, encoding = 'latin1')
pass_gv_12 = pd.read_csv("KTH_BehandlingsGruppPassager_2012.txt", ',', index_col = False, encoding = 'latin1')
pass_gv_13 = pd.read_csv("KTH_BehandlingsGruppPassager_2013.txt", ',', index_col = False, encoding = 'latin1')

localities = pd.read_csv("Localities.csv",',', index_col = False, encoding = 'latin1')

# Add columns for data-collection year and vehicle type
pass_cv_12['year'] = 2012
pass_cv_13['year'] = 2013
pass_gv_12['year'] = 2012
pass_gv_13['year'] = 2013

# Create experimental group variable
pass_cv_12['expgrp'] = 'cv'
pass_cv_13['expgrp'] = 'cv'
pass_gv_12['expgrp'] = 'gv'
pass_gv_13['expgrp'] = 'gv'

# Merge and unite data
df = [pass_cv_12, pass_cv_13, pass_gv_12, pass_gv_13]
passages = pd.concat(df)
#passages.reset_index(drop = True, inplace = True)

# Create unified fuel variable
#passages['expgrp'] = passages['expgrp'].astype('category')
passages['Drivmedel'] = passages['Drivmedel 1']
passages['Drivmedel'] = passages['Drivmedel 1'] + '.' + passages['Drivmedel 2']
passages['Drivmedel'] = passages['Drivmedel']
passages['Drivmedel'] = passages['Drivmedel'].astype(str)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Okänd', 'Petrol', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Diesel.Okänd', 'Diesel', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('El.Okänd', 'Electric', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.El', 'Electric_Hybrid', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Etanol.Okänd', 'Ethanol', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Etanol', 'Ethanol', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Metangas', 'Natural_Gas', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Metangas.Metangas', 'Natural_Gas', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Metangas.Okänd', 'Natural_Gas', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('Motorgas.Okänd', 'Other', regex = True)
passages['Drivmedel'] = passages['Drivmedel'].str.replace('nan', 'Other', regex = True)
passages['FuelCat'] = passages['Drivmedel']
#passages['FuelCat'].loc[passages['Drivmedel'].isin(["Electric","Electric_Hybrid","Ethanol","Natural_Gas","Other"])] = 'AFV'
#passages['FuelCat'].loc[passages['Drivmedel'].isin(["Petrol","Diesel"])] = 'CV'

passages['FuelCat'] = passages['FuelCat'].mask(passages['FuelCat'].isin(["Electric","Electric_Hybrid","Ethanol","Natural_Gas","Other"]), 'AFV')
passages['FuelCat'] = passages['FuelCat'].mask(passages['FuelCat'].isin(["Petrol","Diesel"]), 'CV')


# Add municipalities to Passages based on localities
passages['Ort'] = passages['Ägare ort'].copy()
passages['Ort'] = [x.strip() for x in passages['Ort']]
localities['Ort'] = [x.upper() for x in localities['Ort']]
localities['Kommun'] = [x.upper() for x in localities['Kommun']]

passages = pd.merge(passages, localities, how='left', on='Ort')

#%% This part is in file FindExempt 

passages['passagetime'] = [datetime.strptime(passages.Passagetid[i], '%H:%M:%S').time() for i in range(len(passages))]
passages['passagedate'] = [datetime.strptime(passages.Passagedatum[i], '%Y-%m-%d').date() for i in range(len(passages))]

# Compute nominal charges
passages['price'] = 0
def set_price(start, end, price_series, price):
    idx = [start <= passages.passagetime[i] < end for i in range(len(passages))]
    idx = [int(idx[i]) for i in range(len(passages))]
    price_series = [i * price for i in idx] + price_series 
    return price_series

price1 = set_price(time(6, 30), time(7), passages['price'], 10)
price2 = set_price(time(7), time(7,30), price1, 15)
price3 = set_price(time(7, 30), time(8,30), price2, 20)
price4 = set_price(time(8, 30), time(9), price3, 15)
price5 = set_price(time(9), time(15,30), price4, 10)
price6 = set_price(time(15, 30), time(16), price5, 15)
price7 = set_price(time(16), time(17,30), price6, 20)
price8 = set_price(time(17,30), time(18), price7, 15)
price9 = set_price(time(18), time(18,30), price8, 10)
passages['price'] = price9
del price1, price2, price3, price4, price5, price6, price7, price8, price9

# Since 2013 observations only seem to exist during charging periods, filter out 
# the same for 2012.
passages = passages[passages['price'] > 0]

# Extract vehicle-specific information
x = passages.groupby(by = 'AnonymRegno').first()
cols = {'Juridisk eller fysisk','Ny ägare mellan period 1 och 2',
            'Drivmedel 1', 'Drivmedel 2','C02 Driv 1','C02 Driv 2',
            'Ägare postnr','Ägare ort','Drivmedel', 'FuelCat','Ort',
            'Kommun','expgrp'}
vehicles = pd.DataFrame(x[cols])
del x, cols

# Also create the first long vehicles table (separate rows for each Year)
veh_year_2012 = vehicles.copy()
veh_year_2012['year'] = 2012
veh_year_2013 = vehicles.copy()
veh_year_2013['year'] = 2013
veh_year = veh_year_2012.append(veh_year_2013)

# relabel experimental group variable
#vehicles['expgrp'] = ''
#veh_year['expgrp'] = ''
vehicles['expgrp'].loc[vehicles['FuelCat'] == 'CV'] = 'Paying in 2012'
vehicles['expgrp'].loc[vehicles['FuelCat'] == 'AFV'] = 'Exempt in 2012'
veh_year['expgrp'].loc[veh_year['FuelCat'] == 'CV'] = 'Paying in 2012'
veh_year['expgrp'].loc[veh_year['FuelCat'] == 'AFV'] = 'Exempt in 2012'

# Aggregate passages to unique vehicles
mask1 = passages[passages['year'] == 2012]
pass_trips_2012 = mask1.groupby(by = 'AnonymRegno').price.sum()
mask2 = passages[passages['year'] == 2013]
pass_trips_2013 = mask2.groupby(by = 'AnonymRegno').price.sum()
del mask1, mask2

# Alternatively ...
pass_trips = passages.groupby(by = ['AnonymRegno' , 'year']).price.sum()

# # Merge back into vehicles
vehicles = vehicles.join(pass_trips_2012, on = 'AnonymRegno', how = 'left', lsuffix='_12', rsuffix='_13')
vehicles = vehicles.join(pass_trips_2013, on = 'AnonymRegno', how = 'left', lsuffix='_12', rsuffix='_13')
vehicles.rename(columns = {'price_12':'totalprice_12', 'price_13':'totalprice_13'}, inplace = True)

# # Alternatively ...
veh_year = veh_year.join(pass_trips, on = ['AnonymRegno' , 'year'])
veh_year.rename(columns = {'price':'totalprice'}, inplace = True)

# Set NAs in total price to zero
vehicles['totalprice_12'].fillna(0, inplace=True)
vehicles['totalprice_13'].fillna(0, inplace=True)
veh_year['totalprice'].fillna(0, inplace=True)

# Filter out vehicles that are suspect, put OK data in new df
pass_veh = vehicles.copy()
x = [isinstance(pass_veh['Kommun'][i],type(None)) for i in range(len(pass_veh))]
pass_veh.drop(pass_veh[x].index, inplace = True)
pass_veh.drop(pass_veh[pass_veh['Ny ägare mellan period 1 och 2'] != 'Nej'].index, inplace = True)
pass_veh.drop(pass_veh[pass_veh['Juridisk eller fysisk'] != 'F'].index, inplace = True)
del x

# Same for long table
veh_year.drop(veh_year[veh_year['Ny ägare mellan period 1 och 2'] != 'Nej'].index, inplace = True)
veh_year.drop(veh_year[veh_year['Juridisk eller fysisk'] != 'F'].index, inplace = True)
x = [isinstance(veh_year['Kommun'][i],type(None)) for i in range(len(veh_year))]
veh_year.drop(veh_year[x].index, inplace = True)
del x

# Compute change in nominal price
pass_veh['totalprice_diff'] = pass_veh['totalprice_13'] - pass_veh['totalprice_12'] 

# Do some density plots
# Nominal price for 2012/2013, using long table
df = veh_year.copy()
x = df.totalprice
y = [df.FuelCat == 'AFV']

maskAFV_exepmt_2012 = df       # for all 2012 data
#maskAFV_exepmt_2012 = df[df['expgrp']=='Paying in 2012']        #only for people who are paying in 2012
data_2012 = maskAFV_exepmt_2012[maskAFV_exepmt_2012['year']==2012].pivot(columns = 'FuelCat', values = 'totalprice')
data_2012.plot.kde(figsize = (8, 6), linewidth = 1)
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2012')

maskAFV_exepmt_2013 = df       # for all 2013 data
#maskAFV_exepmt_2013 = df[df['expgrp']=='Paying in 2012']        #only for people who are paying in 2012
data_2013 = maskAFV_exepmt_2013[maskAFV_exepmt_2013['year']==2013].pivot(columns = 'FuelCat', values = 'totalprice')
data_2013.plot.kde(figsize = (8, 6), linewidth = 1 )
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2013')

del maskAFV_exepmt_2012, maskAFV_exepmt_2013, x, y, data_2012, data_2013, df

#%% 
veh_year['count'] = 1
x = veh_year.groupby(['Kommun','FuelCat']).count()
x = x['count']
ax = x.unstack(level=1).plot(kind='bar', subplots=False,  figsize=(9, 7))
plt.tight_layout()
del x

veh_year_AFV = veh_year[veh_year['FuelCat'] == 'AFV']
x1 = veh_year_AFV[{'totalprice','Kommun'}]
x1 = x1.groupby(['Kommun']).sum()
x1 = x1.unstack()
ax = x1.unstack(level=1).plot(kind='bar', subplots=False, rot = 0, figsize=(9, 7))
plt.tight_layout()





#from sklearn.cluster import KMeans
#mask = veh_year[veh_year['FuelCat'] == 'AFV']
#X = mask[{'totalprice','Kommun'}]
#kmeans = KMeans(n_clusters=2, random_state=0).fit(X, y=None, sample_weight=None)

# def Kommun_to_numeric(x):
#         if x=='STOCKHOLM': return 1
#         if x=='SOLLENTUNA':   return 2
#         if x=='VÄRMDÖ': return 
#         if x=='TÄBY': return 
#         if x=='NACKA': return 
#         if x=='DANDERYD': return 
#         if x=='VALLENTUNA': return 
#         if x=='LIDINGÖ': return 
#         if x=='EKERÖ': return 
#         if x=='JÄRFÄLLA': return 
#         if x=='HUDDINGE': return 
#         if x=='TYRESÖ': return 
#         if x=='SALEM': return 
#         if x=='SOLNA': return 
#         if x=='VAXHOLM': return 
#         if x=='ÖSTERÅKER': return 
#         if x=='NYNÄSHAMN': return
#         if x=='HANINGE': return
#         if x=='BOTKYRKA': return
#         if x=='SÖDERTÄLJE': return
#         if x=='UPPLANDS-BRO': return
#         if x=='SUNDBYBERG': return
#         if x=='SIGTUNA': return
#         if x=='NORRTÄLJE': return
#         if x=='NYKVARN': return
#         if x=='UPPLANDS VÄSBY': return

