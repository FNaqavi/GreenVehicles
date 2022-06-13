# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 11:08:33 2022

@author: naqavi
"""
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns


df = pd.read_csv('test_veh.csv',',', index_col=False, encoding='latin1')
x = df.totalprice
y = [df.FuelCat == 'AFV']

maskAFV_exepmt_2012 = df[df['expgrp']=='Paying in 2012']
data_2012 = maskAFV_exepmt_2012[maskAFV_exepmt_2012['Year']==2012].pivot(columns = 'FuelCat', values = 'totalprice')
#data_2012 = df[df['Year']==2012].pivot(columns = 'FuelCat', values = 'totalprice')
data_2012.plot.kde(figsize = (8, 6), linewidth = 1)
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2012')

maskAFV_exepmt_2013 = df[df['expgrp']=='Paying in 2012']
data_2013 = maskAFV_exepmt_2013[maskAFV_exepmt_2013['Year']==2013].pivot(columns = 'FuelCat', values = 'totalprice')
#data_2013 = df[df['Year']==2013].pivot(columns = 'FuelCat', values = 'totalprice')
data_2013.plot.kde(figsize = (8, 6), linewidth = 1 )
plt.xlim(-100,600)
plt.xlabel('total nominal price of crossing 2013')




