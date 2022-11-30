# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 10:16:26 2022

@author: naqavi
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 10:08:39 2022

@author: naqavi
"""

from fitter import get_common_distributions
from fitter import Fitter
from secs import secs
from income_merge import get_income
from get_price_p import get_prices
import matplotlib.pyplot as plt
import pandas as pd
from GV_exepmtion_kommun_assignment import GV_share_assignment
import numpy as np
import warnings
warnings.filterwarnings('ignore')
# from create_veh_pass import create_veh_pass

#from home_cordon import home_cordon
p_assigned, passages = GV_share_assignment()
# veh_year, pass_veh = create_veh_pass(passages)
p_assigned = get_prices(passages, p_assigned)
df_inc = get_income(passages)

# %% Prepare pass1 with seconds as "secs" and income as "inc"

pass11 = passages
pass11.rename(columns={'Ägare postnr': 'postnr'}, inplace=True)
pass_inc = pd.merge(df_inc, pass11, on="postnr",
                    how="outer", validate="one_to_many")
pass1 = pass_inc.dropna()

pass1.sort_values(by=['passagedate', 'passagetime'], inplace=True)
pass1.reset_index(inplace=True, drop=True)
days = [pass1['passagedate'][i].day for i in range(len(pass1))]
pass1['days'] = pd.Series(days)

seconds = secs(pass1)
pass1['secs'] = seconds
del seconds, days
del pass11, pass_inc, df_inc

# %% remove CV vehicles from calculation (plots)

CV = pass1[pass1['FuelCat'] == 'CV']
pass1 = pass1[pass1['FuelCat'] != 'CV']

# %% >>> check if all kommuns are included (NORRTÄLJE is not in 2012)

incsum = pass1.groupby(by=['year', 'Kommun']).inc.sum().reset_index()
incsum2012 = incsum[incsum['year'] == 2012]
incsum2013 = incsum[incsum['year'] == 2013]
del incsum2012, incsum2013, incsum

# %% find if cars were available in both years or just one year

p_assigned1 = p_assigned.drop(columns=['price', 'year', 'Kommun', 'FuelCat'])
pass1 = pd.merge(pass1, p_assigned1, on="AnonymRegno",
                 how="outer", validate="many_to_one")
pass1.dropna(inplace=True)

# seperate data available in both years vs. one year
def get_boht_years(df):
    years = df.groupby(by='AnonymRegno').year.unique()
    years = years.reset_index()
    length = years.apply(lambda year: year.str.len())
    years['yrs'] = length['year']
    years = years.drop(columns=['year'])
    df = pd.merge(years, df, on="AnonymRegno",
                     how="outer", validate="one_to_many")
    df.dropna(inplace=True)
    del length, years
    return df


# %% only keep the values that are in both years (morning)
df = pass1
df_m = df[df['secs']<36000]
df_m = get_boht_years(df_m)
df_m = df_m[df_m['yrs'] == 2]

df_mh = df_m[df_m['inc']>=366800]
df_ml = df_m[df_m['inc']<366800]


#%% box plot of frequencies

def box_plot(df):
    df = df.groupby(by=['AnonymRegno', 'year']).count().secs.rename('frq')
    df = df.reset_index()
    plt.boxplot(df.frq)
    _, bp = pd.DataFrame.boxplot(df.frq, return_type='both')
    outliers = [flier.get_ydata() for flier in bp["fliers"]]
    boxes = [box.get_ydata() for box in bp["boxes"]]
    medians = [median.get_ydata() for median in bp["medians"]]
    whiskers = [whiskers.get_ydata() for whiskers in bp["whiskers"]]
    plt.show()
    return outliers, boxes, medians, whiskers

#%% Get cars with more than 3 and less than number of outliars frequencies in the mornings in both years

def get_freq(df):
    outliers, boxes, medians, whiskers = box_plot(df)
    frq_out = min(outliers[0])
    df_grp = df.groupby(by=['AnonymRegno', 'year']).count().secs.rename('frq')
    df_grp = df_grp.reset_index()
    df12 = df_grp[df_grp['year'] == 2012]
    df13 = df_grp[df_grp['year'] == 2013]
    y1 = df12[df12['frq']>2] 
    y1 = y1[y1.frq<frq_out]
    y2 = df13[df13['frq']>2] 
    y2 = y2[y2.frq<frq_out]
    return y1, y2

y1, y2= get_freq(df_m)

df_mh = df_mh[df_mh['AnonymRegno'].isin(y1.AnonymRegno)]
df_ml = df_ml[df_ml['AnonymRegno'].isin(y1.AnonymRegno)]

del y1, y2
#%%

x1 = df_mh.groupby(by=['AnonymRegno', 'year']).mean().secs.reset_index()
x2 = df_ml.groupby(by=['AnonymRegno', 'year']).mean().secs.reset_index()

x1_12= x1[x1['year'] == 2012]
x1_13= x1[x1['year'] == 2013]