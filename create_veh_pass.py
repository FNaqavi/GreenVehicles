# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:12:56 2022

This file is used to create the vehicles data from passages data


@author: naqavi
"""

from set_price import set_price
import pandas as pd

def create_veh_pass():
    passages = set_price()
    
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
    return veh_year, pass_veh

