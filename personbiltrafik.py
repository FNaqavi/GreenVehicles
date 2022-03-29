# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 09:05:38 2022

@author: naqavi
"""
import pandas as pd

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
    
    df['Unnamed: 0'][4] = 'kommun_kod'
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
    res['Miljöbil_itrafik']= res.iloc[:, 6:11].sum(axis=1)      ## check this
    res['Miljöbil_nyreg']= res.iloc[:, 14:19].sum(axis=1)       ## check this
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
data = pd.concat(frames1, ignore_index=True, sort=False)
del frames1

# sort based on Kommun and year
data.sort_values(by=['Kommun','year'], inplace = True)

#defining variables from 2009 (f09) anf up to 2008 (t08)
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

def cumsum_f09_t08 (data):
    d= data
    idx = d['Kommun'].unique()
    condition = d.year.gt(2008)
    d['Reset'] = condition.groupby(d.Bensin).cumsum()
    for i in range(len(idx)):    
        x = d[d['Kommun'] == idx[i]] 
        x['Bensin_f09']  = (x['Bensin_ny'] * x['Reset']).cumsum()
        x['Diesel_f09'] = (x['Diesel_ny'] * x['Reset']).cumsum() 
        x['El_f09'] = (x['El_ny'] * x['Reset']).cumsum() 
        x['Etanol_hybrid_f09'] = (x['Etanol_hybrid_ny'] * x['Reset']).cumsum() 
        x['Övriga_hybrider_f09'] = (x['Övriga_hybrider_ny'] * x['Reset']).cumsum() 
        x['Naturgas_Biogas_f09']= (x['Naturgas_Biogas_ny'] * x['Reset']).cumsum() 
        x['Övriga_f09'] = (x['Övriga_ny'] * x['Reset']).cumsum() 
        x['Totalt_f09'] = (x['Totalt_ny'] * x['Reset']).cumsum() 
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

# removing extras
del res_2006, res_2007, res_2008, res_2009, res_2010, res_2011, res_2012, res_2013
del bil_i_trafik_2006, bil_i_trafik_2007, bil_i_trafik_2008, bil_i_trafik_2009, bil_i_trafik_2010
del bil_i_trafik_2011, bil_i_trafik_2012, bil_i_trafik_2013
del nyreg_2006, nyreg_2007, nyreg_2008, nyreg_2009, nyreg_2010, nyreg_2011, nyreg_2012, nyreg_2013


# %% Trun dataframe to sql table 

# from sqlalchemy import create_engine
# # First create a db in postgresql (pdAdmin)
# # second make a connection here
# Conn = create_engine("postgresql://Fatemeh:Fatemeh@localhost:5432/bilar_test")
# # third make a schema in postgresql (pgAdmin)
# # fourth make the table in schema postgresql here
# result1.to_sql('res_2006_2010', con = Conn, schema = 'all_cars')



