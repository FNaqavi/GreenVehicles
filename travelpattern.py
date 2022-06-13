# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 11:05:52 2022

@author: naqavi
"""


from GV_exepmtion_kommun_assignment import GV_share_assignment
from create_veh_pass import create_veh_pass
import pandas as pd
import matplotlib.pyplot as plt
from get_price_p import get_prices
# import datetime as dt
# import plotly.express as px
# import matplotlib.dates as md
from fitter import Fitter
from fitter import get_common_distributions
# import numpy as np
# import scipy.stats
# from scipy.stats import norm

p_assigned, passages = GV_share_assignment()
veh_year, pass_veh = create_veh_pass(passages)
p_assigned = get_prices(passages,p_assigned)

pass1 = passages
pass1.sort_values(by = ['passagedate', 'passagetime'], inplace = True)
pass1.reset_index(inplace = True, drop = True)
days = [pass1['passagedate'][i].day for i in range(len(pass1))]
pass1['days'] = pd.Series(days)


def secs(df):
    hour = pd.Series([df['passagetime'][i].hour for i in range(len(df))])
    minute = pd.Series([df['passagetime'][i].minute for i in range(len(df))])
    second = pd.Series([df['passagetime'][i].second for i in range(len(df))])
    return (hour * 60 + minute) * 60 + second

seconds = secs(pass1)
pass1['secs'] = seconds
del seconds
pass1.replace({'In':'IN'},inplace = True)
pass1.sort_values(by = ['AnonymRegno','days','secs','year'], inplace = True)

idx = pass1['AnonymRegno'].unique()
# for i in idx:
idx = '00039B95B8F425DA2E44DE9A8895B5'      # has data in both years
# idx = '0015E918FFB13DC56E2A6B89A5B6B3'
# idx = '000415C7FAE63EAAD90AC9FD1C2231'

# x1idx = '002870E82D45201CD1B3D2B37B0F5B'


x_idx = pass1[pass1['AnonymRegno'] == idx]

def get_day_year(year):
    p = x_idx[x_idx['year'] == year]
    # p = x_idx[x_idx['days'] == day]
    return p      


x12 = get_day_year(2012)
x13 = get_day_year(2013)

def get_x(df):
    # df = df[df['Riktning'] =='IN']
    x1 = df.secs[df['price'] == 10]
    x2 = df.secs[df['price'] == 15]
    x3 = df.secs[df['price'] == 20]
    return x1,x2,x3

x1,x2,x3 = get_x(x12)           # for 2012
plt.hist([x1,x2,x3],bins = 24, alpha = 1, color=['C9','C0','navy'], label=['pr10', 'pr15','pr20'])#,density = True)
# plt.hist([x1,x2,x3],bins = 24, alpha = 0.8, color=['C0','C0','C0'], label=['pr10', 'pr15','pr20'],density = True)
x11,x12,x13 = get_x(x13)        # for 2013
plt.hist([x11,x12,x13],bins = 24, alpha = 1, color=['C1','C3','C6'], label=['pr10', 'pr15','pr20'])#, density = True)
# plt.hist([x11,x12,x13],bins = 24, alpha = 0.8, color=['C1','C1','C1'], label=['pr10', 'pr15','pr20'], density = True)

del x1,x11,x2,x12,x3,x13


