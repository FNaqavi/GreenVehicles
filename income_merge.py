# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 10:53:17 2022

@author: naqavi
"""
import pandas as pd
from GV_exepmtion_kommun_assignment import GV_share_assignment


def get_income(passages):
    df = pd.read_csv("Copy of Postnummer till Emma.csv", encoding = 'latin1')  
    pass1 = passages
    pass1.rename(columns = {'Ägare postnr':'postnr'}, inplace =True)
    
    # strPostnr = df[df['Postnr'] == 'Restf']
    df1 = df.set_index('Postnr')
    df1.drop(index=('Restf'), inplace = True)
    df1.reset_index(inplace =True)
    df1['Postnr'] = df1['Postnr'].astype(int)
    
    df1 = df1.where((df1['Postnr'].astype(int)).isin(pass1['postnr'])).dropna()
    df1.sort_values('Postnr', inplace = True)
    
    
    postnr = df1['Postnr'].tolist()
    postnr_pass = pass1['postnr'].where(pass1['postnr'].isin(postnr))
    postnr_pass.sort_values(inplace = True)
    
    df2 = df1[['Postnr', 'Total_Lön_median']].copy()
    df2 = df2.rename(columns = {'Postnr':'postnr'})
    df2 = df2.rename(columns = {'Total_Lön_median':'inc'})
    df2 = df2.drop_duplicates(subset=['postnr']).dropna().reset_index(drop = True)

    return df2



