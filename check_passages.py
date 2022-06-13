# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 15:08:32 2022

@author: naqavi
"""


from GV_exepmtion_kommun_assignment import GV_share_assignment
from create_veh_pass import create_veh_pass
import pandas as pd
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')

p_assigned, passages = GV_share_assignment()
veh_year, pass_veh = create_veh_pass(passages)

passages.reset_index(drop = True, inplace = True)
passages['d']  = [datetime.combine(passages['passagedate'][i], passages['passagetime'][i])  for i in range(len(passages))]

pass_new = pd.DataFrame()
idx_unq = passages.AnonymRegno.unique()

def get_toll_days(passages, i):    
    idx = idx_unq[i]
    df = passages[passages['AnonymRegno'] == idx]
    df.sort_values(by = ['d'],inplace = True, ascending=True)
    # x = df.groupby(by = ['passagedate']).year.count().rename('count').reset_index()
    if len(df)>1:
    # df.count = 0
        df['day_dif'] = df['passagedate'].diff().dt.days
        df.loc[0,'day_dif'] = 0 
        df.loc[df['day_dif'] == 0, 'hour_dif'] =  df['d'].diff()#.astype(str)
        df.replace({pd.NaT: 0}, inplace=True)   
        df.loc[0,'hour_dif'] = 0
        df['hour_dif'] = df['hour_dif'].replace('nan', '0')
        lst = df[df['hour_dif'] != 0]
        lst['hour_dif1'] = [lst['hour_dif'].iloc[j].seconds/3600 for j in range(len(lst))]
        df1 = pd.merge(df, lst, how="left", on=["AnonymRegno",'Passagedatum', 'Passagetid', 'Betalstation', 'Riktning',
               'Juridisk eller fysisk', 'Ny ägare mellan period 1 och 2',
               'Drivmedel 1', 'C02 Driv 1', 'Drivmedel 2', 'C02 Driv 2',
               'Ägare postnr', 'Ägare ort', 'year', 'expgrp', 'Drivmedel', 'FuelCat',
               'Ort', 'Kommun', 'passagetime', 'passagedate', 'price', 'd', 'day_dif',
               'hour_dif','day_dif','hour_dif'])
        df1.drop(columns =['hour_dif','day_dif'], inplace = True)
        df1 = df1.replace(np.nan,0)
    if len(df) == 1:
        df1 = df
    return df1
    
for i in range(len(idx_unq)):
    # print(i)
    df1 = get_toll_days(passages, i)
    pass_new = pd.concat([df1,pass_new])
    
# pass_new.to_csv('pass_new.csv',encoding = 'latin1')