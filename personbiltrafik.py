# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 09:05:38 2022

@author: naqavi
"""
import pandas as pd


#%% Clean the registry data to create "personbilaritrafik.xlsx" file (in trafik and new registered)

# import data
bil_i_trafik_2006 = pd.read_excel('kommun-2007.xls', sheet_name='RSK-Tabell 3-2006')
bil_i_trafik_2007 = pd.read_excel('kommun-2007.xls', sheet_name='RSK-Tabell 3-2007')
bil_i_trafik_2008 = pd.read_excel('kommun-2008.xls', sheet_name='RSK-Tabell 3-2008')
bil_i_trafik_2009 = pd.read_excel('kommun-2009.xls', sheet_name='RSK-Tabell 3-2009')
bil_i_trafik_2010 = pd.read_excel('kommun-2010.xls', sheet_name='RSK-Tabell 3-2010')
bil_i_trafik_2011 = pd.read_excel('kommun-2011.xls', sheet_name='RSK-Tabell 3-2011')
bil_i_trafik_2012 = pd.read_excel('kommun-2012.xls', sheet_name='RSK-Tabell 3 2012')
bil_i_trafik_2013 = pd.read_excel('kommun-2013.xls', sheet_name='RSK-Tabell 3 2013')
nyreg_2006 = pd.read_excel('kommun-2007.xls', sheet_name='RSK-Tabell 4-2006')
nyreg_2007 = pd.read_excel('kommun-2007.xls', sheet_name='RSK-Tabell 4-2007')
nyreg_2008 = pd.read_excel('kommun-2008.xls', sheet_name='RSK-Tabell 4-2008')
nyreg_2009 = pd.read_excel('kommun-2009.xls', sheet_name='RSK-Tabell 4-2009')
nyreg_2010 = pd.read_excel('kommun-2010.xls', sheet_name='RSK-Tabell 4-2010')
nyreg_2011 = pd.read_excel('kommun-2011.xls', sheet_name='RSK-Tabell 4-2011')
nyreg_2012 = pd.read_excel('kommun-2012.xls', sheet_name='RSK-Tabell 4 2012')
nyreg_2013 = pd.read_excel('kommun-2013.xls', sheet_name='RSK-Tabell 4 2013')

# convert kommun codes from string to integer and cleaning dataframes
def clean_df(df, year, kod1, kod2):
    kommun_kods = ['0114', '0115', '0117', '0120', '0123', '0125', '0126', '0127', 
               '0128', '0136', '0138', '0139', '0140', '0160', '0162', '0163', 
               '0180', '0181', '0182', '0183', '0184', '0186', '0187', '0188', 
               '0191', '0192']
    kommun_kods1 = [114, 115, 117, 120, 123, 125, 126, 127, 128, 136, 138, 139, 140,
               160, 162, 163, 180, 181, 182, 183, 184, 186, 187, 188, 191, 192]
    
    df.loc[4,'Unnamed: 0'] = 'kommun_kod'
    df.rename(columns=df.iloc[4], inplace = True)
    df.drop([5], inplace = True)
    df = df.tail(df.shape[0] -5)
    df = df.dropna(axis = 0, how = 'all')
    df = df[df.isnull().sum(axis=1) < 5]
    df = df[df['kommun_kod'].notna()]
    df['year'] = year
    df['Kommun'].replace({'UPPLANDS-VÄSBY' : 'UPPLANDS VÄSBY'}, regex=True, inplace = True)
    df.dropna(axis=1, how='all', inplace = True)
    df.rename(columns=lambda x: x.replace(" ", ""), inplace = True)  
    if kod1 == 0:
        df = df[df['kommun_kod'].isin(kommun_kods)]
    if kod1 == 1:
        df = df[df['kommun_kod'].isin(kommun_kods1)]
    df.rename(columns = {'Etanol-hybrid/E85':'Etanol_hybrid',
                        'Övriga hybrider':'Övriga_hybrider',
                        'Övrigahybrider': 'Övriga_hybrider',
                        'Naturgas/Biogas':'Naturgas_Biogas',
                        'Etanol/etanolhybrid':'Etanol_hybrid' ,
                        'Elhybrider/Laddhybrider':'Övriga_hybrider' ,
                        'Gas':'Naturgas_Biogas',
                        'Elhybrider':'Övriga_hybrider' ,
                        'Laddhybrider':'Övriga_hybrider',
                        'Etanol/etanolflexifuel':'Etanol_hybrid',
                        'Gas/gasflexifuel':'Naturgas_Biogas'}, inplace = True)      
        
    df['kommun_kod'] = df['kommun_kod'].astype(int)
    df['komkod_year'] = df['kommun_kod'].astype(str) + df['year'].astype(str) 
    cols = pd.Index.tolist(df.columns)
    cols = [s for s in cols if s != 'Kommun']
    Kommun = df['Kommun']
    df.drop('Kommun', axis = 1, inplace = True)
    df = df.astype('int')
    df.insert(0, 'Kommun', Kommun)
    df.reset_index(drop = True, inplace = True) 
    df = df.drop(['däravmiljöbilar*', 'däravMB2007', 'däravMB2013', 'däravmiljöbilar'], axis=1, errors='ignore')
    if year == 2013:
        Övriga_hybrider_all= df.iloc[:, 5:7].sum(axis=1)
        df.drop('Övriga_hybrider',axis = 1, inplace=True)
        df['Övriga_hybrider'] = Övriga_hybrider_all
    return df

bil_i_trafik_2006 = clean_df(bil_i_trafik_2006, 2006, 0, 0)
bil_i_trafik_2007 = clean_df(bil_i_trafik_2007, 2007, 0, 0)
bil_i_trafik_2008 = clean_df(bil_i_trafik_2008, 2008, 1, 0)
bil_i_trafik_2009 = clean_df(bil_i_trafik_2009, 2009, 1, 0)
bil_i_trafik_2010 = clean_df(bil_i_trafik_2010, 2010, 1, 0)
bil_i_trafik_2011 = clean_df(bil_i_trafik_2011, 2011, 1, 1)
bil_i_trafik_2012 = clean_df(bil_i_trafik_2012, 2012, 1, 1)
bil_i_trafik_2013 = clean_df(bil_i_trafik_2013, 2013, 1, 1)
nyreg_2006 =  clean_df(nyreg_2006, 2006, 0, 0)
nyreg_2007 =  clean_df(nyreg_2007, 2007, 0, 0)
nyreg_2008 =  clean_df(nyreg_2008, 2008, 1, 0)
nyreg_2009 =  clean_df(nyreg_2009, 2009, 1, 0)
nyreg_2010 =  clean_df(nyreg_2010, 2010, 1, 0)
nyreg_2011 =  clean_df(nyreg_2011, 2011, 1, 1)
nyreg_2012 =  clean_df(nyreg_2012, 2012, 1, 1)
nyreg_2013 =  clean_df(nyreg_2013, 2013, 1, 0)

# merge in traffic and new registered cars. left columns are in trafik cars.
def merge_itrafik_nyreg(df_itrafik, df_nyreg, kod1):
    res = pd.merge(df_itrafik, df_nyreg, on=['year','Kommun','kommun_kod','komkod_year'], suffixes=('', '_ny'))
    return res

res_2006 = merge_itrafik_nyreg(bil_i_trafik_2006, nyreg_2006, 0)
res_2007 = merge_itrafik_nyreg(bil_i_trafik_2007, nyreg_2007, 0)
res_2008 = merge_itrafik_nyreg(bil_i_trafik_2008, nyreg_2008, 0)
res_2009 = merge_itrafik_nyreg(bil_i_trafik_2009, nyreg_2009, 0)
res_2010 = merge_itrafik_nyreg(bil_i_trafik_2010, nyreg_2010, 0)
res_2011 = merge_itrafik_nyreg(bil_i_trafik_2011, nyreg_2011, 1)
res_2012 = merge_itrafik_nyreg(bil_i_trafik_2012, nyreg_2012, 1)
res_2013 = merge_itrafik_nyreg(bil_i_trafik_2013, nyreg_2013, 2)
frames1 = [res_2006, res_2007, res_2008, res_2009, res_2010, res_2011, res_2012, res_2013]

# this is the registry data of vehicles
data = pd.concat(frames1, ignore_index=True, sort=False)
del frames1

# sort based on Kommun and year
data.sort_values(by=['Kommun','year'], inplace = True)
data['Miljöbil']= data.iloc[:, 4:9].sum(axis=1)      
data['Miljöbil_ny']= data.iloc[:, 14:19].sum(axis=1)      
data.loc[:,'CV'] = data['Bensin'] + data['Diesel']
data.loc[:,'CV_ny'] = data['Bensin_ny'] + data['Diesel_ny']

# defining variables from 2009 (f09) anf up to 2008 (t08)
data['Bensin_f09'] = 0
data['Diesel_f09'] = 0
data['El_f09'] = 0
data['Etanol_hybrid_f09'] = 0
data['Övriga_hybrider_f09'] = 0
data['Naturgas_Biogas_f09'] = 0
data['Övriga_f09'] = 0
data['Totalt_f09'] = 0
data['Bensin_t08'] = 0
data['Diesel_t08'] = 0
data['El_t08'] = 0
data['Etanol_hybrid_t08'] = 0
data['Övriga_hybrider_t08'] = 0
data['Naturgas_Biogas_t08'] = 0
data['Övriga_t08'] = 0
data['Totalt_t08'] = 0
data['CV_f09'] = 0
data['AFV_f09'] = 0
data['CV_t08'] = 0
data['AFV_t08'] = 0

def cumsum_f09_t08 (data):
    d= data
    idx = d['Kommun'].unique()
    condition = d.year.gt(2008)
    d['Reset'] = condition.groupby(d.Bensin).cumsum()
    for i in range(len(idx)):    
        x = d[d['Kommun'] == idx[i]] 
        x.loc[:,'Bensin_f09']  = (x['Bensin_ny'] * x['Reset']).cumsum()
        x.loc[:,'Diesel_f09'] = (x['Diesel_ny'] * x['Reset']).cumsum() 
        x.loc[:,'El_f09'] = (x['El_ny'] * x['Reset']).cumsum() 
        x.loc[:,'Etanol_hybrid_f09'] = (x['Etanol_hybrid_ny'] * x['Reset']).cumsum() 
        x.loc[:,'Övriga_hybrider_f09'] = (x['Övriga_hybrider_ny'] * x['Reset']).cumsum() 
        x.loc[:,'Naturgas_Biogas_f09']= (x['Naturgas_Biogas_ny'] * x['Reset']).cumsum() 
        x.loc[:,'Övriga_f09'] = (x['Övriga_ny'] * x['Reset']).cumsum() 
        x.loc[:,'Totalt_f09'] = (x['Totalt_ny'] * x['Reset']).cumsum() 
        x.loc[:,'CV_f09'] = (x['CV_ny']* x['Reset']).cumsum()
        x.loc[:,'AFV_f09'] = (x['Miljöbil_ny']* x['Reset']).cumsum()  
        
        d[d['Kommun'] == idx[i]]  = x
    d.drop('Reset', axis = 1, inplace = True)   
    return d        
        
data = cumsum_f09_t08 (data)

data['Bensin_t08'] = data['Bensin'] - data['Bensin_f09']
data['Diesel_t08'] = data['Diesel'] - data['Diesel_f09']
data['El_t08'] = data['El'] - data['El_f09']
data['Etanol_hybrid_t08'] = data['Etanol_hybrid'] - data['Etanol_hybrid_f09']
data['Övriga_hybrider_t08'] = data['Övriga_hybrider'] - data['Övriga_hybrider_f09']
data['Naturgas_Biogas_t08'] = data['Naturgas_Biogas'] - data['Naturgas_Biogas_f09']
data['Övriga_t08'] = data['Övriga'] - data['Övriga_f09']
data['Totalt_t08'] = data['Totalt'] - data['Totalt_f09']
data['AFV_t08'] = data['Miljöbil'] - data['AFV_f09']
data['CV_t08'] = data['CV'] - data['CV_f09']


# replace negative numbers in t08 with 0
d = data.drop('Kommun', axis = 1)
d[d<0] = 0
data = pd.merge(data['Kommun'], d , left_index=True, right_index = True)

# removing extras
del d, res_2006, res_2007, res_2008, res_2009, res_2010, res_2011, res_2012, res_2013
del bil_i_trafik_2006, bil_i_trafik_2007, bil_i_trafik_2008, bil_i_trafik_2009, bil_i_trafik_2010
del bil_i_trafik_2011, bil_i_trafik_2012, bil_i_trafik_2013
del nyreg_2006, nyreg_2007, nyreg_2008, nyreg_2009, nyreg_2010, nyreg_2011, nyreg_2012, nyreg_2013

data['ee_index'] = data['Miljöbil'] / data['Totalt']
data['rr_index'] = data['Totalt_ny'] / data['Totalt']

mask = data[(data['year'] == 2012) | (data['year'] == 2013)]
d = mask[{'Kommun','year','AFV_t08','CV_t08', 'Totalt_f09','Totalt_t08','CV_f09','AFV_f09'}].reset_index(drop = True)
del mask

d.to_csv(r'C:\Users\naqavi\OneDrive - KTH\!Joel\Passages\GreenVehicles\registry_data.csv', encoding = 'latin1')

#%% Import vehicle data (from excel file of registry)

veh_year = pd.read_csv('veh_year.csv', encoding='latin 1')
data_veh = veh_year[{'AnonymRegno','Kommun','FuelCat','expgrp','year','totalprice'}]
del veh_year

#data_veh['expgrp'].replace({'Exempt in 2012' : 0, 'Paying in 2012' :1}, regex=True, inplace = True)
mask = data_veh.groupby(['FuelCat','year','Kommun']).count().rename(columns = {'totalprice':'count'}).iloc[:,-1]
mask_price = data_veh.groupby(['FuelCat','year','Kommun']).sum()
mask_price['count'] = mask
df = mask_price.reset_index()  
del mask, mask_price


#%% plot share of AFVfrom 2009 and up to 2008 in personbiltrafik
import matplotlib.pyplot as plt

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
plt.xlabel('share of AFV in 2012 in the personbil data')

x = AFV_mask_f09_2012['Kommun']
y3 = AFV_mask_f09_2013['p_AFV_f09']
y4 = AFV_mask_t08_2013['p_AFV_t08']
plt.figure(figsize=(20, 3))
plt.bar(x,y3, color = 'navy', alpha=1, label = 'AFV share after 2009')
plt.bar(x,y4, bottom=y3, color = 'darkred', alpha=1, label = 'AFV share before 2008')
plt.xticks(rotation=90)
plt.legend(loc = 'upper right')
plt.xlabel('share of AFV in 2013 in the personbil data')

del x, y1, y2, y3, y4, df_AFV, AFV_mask_f09_2012, AFV_mask_f09_2013
del AFV_mask_t08_2012, AFV_mask_t08_2013, AFV_mask_f09, AFV_mask_t08  


#%%
import importPassages
from datetime import datetime
from datetime import time
import numpy as np

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

# remove nan values in Kommun column
passages['Kommun'] = passages['Kommun'].astype(str)
passages = passages[passages['Kommun'] != 'nan']

# Extract vehicle-specific information
x = passages.groupby(by = 'AnonymRegno').first()
cols = {'FuelCat','Kommun','year','price'}
vehicles = pd.DataFrame(x[cols])
total_price = passages.groupby(by = 'AnonymRegno').price.sum()
vehicles['price'] = total_price
del x, total_price


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

count = passages1_CV.groupby('Kommun').count()

#%%
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

# total_price = p_assigned.groupby(by = 'AnonymRegno').price.sum()


#%%

# p_df = pd.read_csv('test_veh.csv',',', index_col=False, encoding='latin1')
p_df = p_assigned
x = p_df.price
y = [p_df.FuelCat == 'AFV']

maskAFV_exepmt_2012 = p_df[p_df['expgrp']=='Paying in 2012']
#data_2012 = maskAFV_exepmt_2012[maskAFV_exepmt_2012['year']==2012].pivot(columns = 'FuelCat', values = 'price')
data_2012 = p_df[p_df['year']==2012].pivot(columns = 'FuelCat', values = 'price')
data_2012.plot.kde(figsize = (8, 6), linewidth = 1)
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2012')

maskAFV_exepmt_2013 = p_df[p_df['expgrp']=='Paying in 2012']
#data_2013 = maskAFV_exepmt_2013[maskAFV_exepmt_2013['year']==2013].pivot(columns = 'FuelCat', values = 'price')
data_2013 = p_df[p_df['year']==2013].pivot(columns = 'FuelCat', values = 'price')
data_2013.plot.kde(figsize = (8, 6), linewidth = 1)
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2013')


#%%
# compute avg price weights for 2012 and 2013 for CV vehicles
x = pd.DataFrame()

veh_price_by_kommun_FuelCat = vehicles.groupby(by = ['Kommun','FuelCat','year']).price.sum()
veh_price_by_kommun_FuelCat = veh_price_by_kommun_FuelCat.reset_index()
veh_count_by_kommun_FuelCat = vehicles.groupby(by = ['Kommun','FuelCat','year']).price.count()
veh_count_by_kommun_FuelCat  = veh_count_by_kommun_FuelCat.reset_index()  
x['avg_price'] = veh_price_by_kommun_FuelCat['price'] / veh_count_by_kommun_FuelCat['price']
x['FuelCat'] = veh_price_by_kommun_FuelCat['FuelCat']
x['Kommun'] = veh_price_by_kommun_FuelCat['Kommun']  
x['year'] = veh_price_by_kommun_FuelCat['year']
pass_CV_mask = x[x['FuelCat'] == 'CV']
pass_CV_mask_2012 = pass_CV_mask[pass_CV_mask['year'] == 2012].reset_index(drop = True)
pass_CV_mask_2013 = pass_CV_mask[pass_CV_mask['year'] == 2013].reset_index(drop = True)
pass_CV_mask_2013 = pass_CV_mask_2013[pass_CV_mask_2013['Kommun'] !='NORRTÄLJE'].reset_index(drop = True)

pass_AFV_mask = x[x['FuelCat'] == 'AFV']          
pass_AFV_mask_2012 = pass_AFV_mask[pass_AFV_mask['year'] == 2012].reset_index(drop = True)
pass_AFV_mask_2013 = pass_AFV_mask[pass_AFV_mask['year'] == 2013].reset_index(drop = True)
pass_AFV_mask_2013 = pass_AFV_mask_2013[pass_AFV_mask_2013['Kommun'] !='NORRTÄLJE'].reset_index(drop = True)


pass_CV_mask_2012.sort_values(by=['Kommun'], inplace = True)
pass_CV_mask_2013.sort_values(by=['Kommun'], inplace = True)
pass_CV_mask_2012['price_share_2012'] =  pass_CV_mask_2012['avg_price'] / (pass_CV_mask_2012['avg_price'] + pass_CV_mask_2013['avg_price'])
pass_CV_mask_2013['price_share_2013'] =  pass_CV_mask_2013['avg_price'] / (pass_CV_mask_2012['avg_price'] + pass_CV_mask_2013['avg_price'])
x = pass_CV_mask_2012['Kommun']
y1 = pass_CV_mask_2012['price_share_2012']
y2 = pass_CV_mask_2013['price_share_2013']
plt.figure(figsize=(20, 3))
plt.bar(x,y1, color = 'navy', alpha=1, label = '2012')
plt.bar(x,y2, bottom=y1, color = 'darkcyan', alpha=1, label = '2013')
plt.xticks(rotation=90)
plt.legend(loc = 'upper right')
plt.xlabel('Price share for CV')

pass_AFV_mask_2012.sort_values(by=['Kommun'], inplace = True)
pass_AFV_mask_2013.sort_values(by=['Kommun'], inplace = True)
pass_AFV_mask_2012['price_share_2012'] =  pass_AFV_mask_2012['avg_price'] / (pass_AFV_mask_2012['avg_price'] + pass_AFV_mask_2013['avg_price'])
pass_AFV_mask_2013['price_share_2013'] =  pass_AFV_mask_2013['avg_price'] / (pass_AFV_mask_2012['avg_price'] + pass_AFV_mask_2013['avg_price'])
x = pass_AFV_mask_2012['Kommun']
y1 = pass_AFV_mask_2012['price_share_2012']
y2 = pass_AFV_mask_2013['price_share_2013']
plt.figure(figsize=(20, 3))
plt.bar(x,y1, color = 'navy', alpha=1, label = '2012')
plt.bar(x,y2, bottom=y1, color = 'darkcyan', alpha=1, label = '2013')
#plt.grid(axis = 'y')
plt.xticks(rotation=90)
plt.legend(loc = 'upper right')
plt.xlabel('Price share for AFV')

del x, y1, y2, cols, veh_count_by_kommun_FuelCat, veh_price_by_kommun_FuelCat
del pass_AFV_mask, pass_AFV_mask_2012, pass_AFV_mask_2013
del pass_CV_mask, pass_CV_mask_2012, pass_CV_mask_2013




# %% Trun dataframe to sql table 

# from sqlalchemy import create_engine
# # First create a db in postgresql (pdAdmin)
# # second make a connection here
# Conn = create_engine("postgresql://Fatemeh:Fatemeh@localhost:5432/bilar_test")
# # third make a schema in postgresql (pgAdmin)
# # fourth make the table in schema postgresql here
# result1.to_sql('res_2006_2010', con = Conn, schema = 'all_cars')



