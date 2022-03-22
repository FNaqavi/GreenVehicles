# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 13:56:07 2022

@author: naqavi
"""

from datetime import datetime
from datetime import time
import importPassages
import pandas as pd
import matplotlib.pyplot as plt


passages = importPassages.get_passages()

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
del x

# Also create the first long vehicles table (separate rows for each Year)
veh_year_2012 = vehicles.copy()
veh_year_2012['year'] = 2012
veh_year_2013 = vehicles.copy()
veh_year_2013['year'] = 2013
veh_year = veh_year_2012.append(veh_year_2013)

# relabel experimental group variable
vehicles['expgrp'] = ''
veh_year['expgrp'] = ''
vehicles['expgrp'].loc[vehicles['FuelCat'] == 'cv'] = 'Paying in 2012'
vehicles['expgrp'].loc[vehicles['FuelCat'] == 'gv'] = 'Exempt in 2012'
veh_year['expgrp'].loc[veh_year['FuelCat'] == 'cv'] = 'Paying in 2012'
veh_year['expgrp'].loc[veh_year['FuelCat'] == 'gv'] = 'Exempt in 2012'

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

#maskAFV_exepmt_2012 = df       # for all 2012 data
maskAFV_exepmt_2012 = df[df['expgrp']=='Paying in 2012']        #only for people who are paying in 2012
data_2012 = maskAFV_exepmt_2012[maskAFV_exepmt_2012['year']==2012].pivot(columns = 'FuelCat', values = 'totalprice')
data_2012.plot.kde(figsize = (8, 6), linewidth = 1)
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2012')

#maskAFV_exepmt_2013 = df       # for all 2013 data
maskAFV_exepmt_2013 = df[df['expgrp']=='Paying in 2012']        #only for people who are paying in 2012
data_2013 = maskAFV_exepmt_2013[maskAFV_exepmt_2013['year']==2013].pivot(columns = 'FuelCat', values = 'totalprice')
data_2013.plot.kde(figsize = (8, 6), linewidth = 1 )
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2013')

del maskAFV_exepmt_2012, maskAFV_exepmt_2013






