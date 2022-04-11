# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 09:24:31 2022

This file is used to assign share of GV before 2008 and after 2009 to the 
vehicles in the passages data. 

@author: naqavi
"""


import pandas as pd
from set_price import set_price
import numpy as np



def GV_share_assignment():
    d = pd.read_csv('registry_data.csv', encoding='latin 1')
    d['p_AFV_f09'] = 100* d['AFV_f09'] /(d['AFV_f09'] + d['AFV_t08'])     # gives warning
    d['p_AFV_t08'] = 100* d['AFV_t08'] /(d['AFV_f09'] + d['AFV_t08'])    # gives warning
    
    passages = set_price()
    # filter columns in passages 
    passages1 = passages[{'AnonymRegno', 'year','FuelCat','Kommun','price'}]
    total_price = passages1.groupby(by = 'AnonymRegno').price.sum()
    passages1 = passages1.groupby('AnonymRegno').first()
    passages1.price[passages1.index == total_price.index ]= total_price
    passages1.reset_index()
    passages1['assigned'] = 0
    passages1 = passages1[passages1['Kommun'] != 'LIDINGÖ']
    # divide passages to CV and AFV dataframes
    passages1_CV = passages1[passages1['FuelCat'] == 'CV'].reset_index()
    passages1_AFV = passages1[passages1['FuelCat'] == 'AFV'].reset_index()
     
    # have same order for d(registry data) and passages_AFV
    d.sort_values(by = ['Kommun', 'year'], inplace = True)
    passages1_AFV.sort_values(by = ['Kommun','year'], inplace = True)
    
    # count number of AFV to create random binomial values based on AFVt08 shares on d
    mask = passages1_AFV.groupby(by = ['Kommun','year']).price.count().rename('count')
    mask = mask.reset_index().sort_values(by = ['Kommun','year']).reset_index(drop = True)
    
    s1 = []
    s2 = []
    d_2012_AFV = d[d['year'] == 2012].reset_index() 
    p_lst_2012_AFV = (d_2012_AFV['p_AFV_t08']/100).tolist()
    p_lst_2012_AFV.pop(8) # AFV of Nortälje is not available in 2012 for the passages data 
    mask_2012 = mask[mask['year'] == 2012].reset_index()
    count_2012 = (mask_2012['count']).tolist()
    mask_2012['AFVt08_2012_assigned'] = 0
    for i in range(len(count_2012)): 
        c = count_2012[i]
        s1 = np.random.binomial(1, p_lst_2012_AFV[i], c)
        s2.append(s1)  
    mask_2012['AFVt08_2012_assigned'] = pd.Series(s2)
    
    s1 = []
    s2 = []
    d_2013_AFV = d[d['year'] == 2013].reset_index() 
    p_lst_2013_AFV = (d_2013_AFV['p_AFV_t08']/100).tolist()
    mask_2013 = mask[mask['year'] == 2013].reset_index()
    count_2013 = (mask_2013['count']).tolist()
    mask_2013['AFVt08_2013_assigned'] = 0
    for i in range(len(count_2013)): 
        c = count_2013[i]
        s1 = np.random.binomial(1, p_lst_2013_AFV[i], c)
        s2.append(s1)     
    mask_2013['AFVt08_2013_assigned'] = pd.Series(s2)
    
    d_con = pd.concat([mask_2012, mask_2013])
    d_con['AFV_assign'] = d_con['AFVt08_2012_assigned'].fillna(0) + d_con['AFVt08_2013_assigned'].fillna(0)
    d_con.dropna(axis='columns', inplace = True)
    
    # convert seires of arrays to array object
    xx = np.array(d_con['AFV_assign']).flatten() 
    # convert array object to array, then to series 
    ser = pd.Series(np.concatenate(xx).astype(None))  
    passages1_AFV['assigned'] = ser
    
    # assigned (0: after 2009, 1: before 2008)
    p_assigned = pd.concat([passages1_AFV,passages1_CV]).reset_index(drop = True)
    
    
    del i, c, s1, p_lst_2012_AFV, count_2012
    del p_lst_2013_AFV, count_2013
    del xx, ser
    del s2, mask, mask_2012, mask_2013, d_con, 
    del d_2012_AFV, d_2013_AFV
    
    p_assigned['expgrp'] = 0
    p_assigned.expgrp[p_assigned['assigned']== 0] = 'Paying in 2012'
    p_assigned.expgrp[p_assigned['assigned']== 1] = 'Exempt in 2012'
    
    return p_assigned, passages







