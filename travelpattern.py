# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 11:05:52 2022

@author: naqavi
"""


from GV_exepmtion_kommun_assignment import GV_share_assignment
# from create_veh_pass import create_veh_pass
import pandas as pd
import matplotlib.pyplot as plt
from get_price_p import get_prices
from income_merge import get_income
from secs import secs
from home_cordon import home_cordon

p_assigned, passages = GV_share_assignment()
# veh_year, pass_veh = create_veh_pass(passages)
p_assigned = get_prices(passages, p_assigned)
df_inc = get_income(passages)


#%% Prepare pass1 with seconds as "secs" and income as "inc"

pass11 = passages
pass11.rename(columns = {'Ägare postnr':'postnr'}, inplace =True)
pass_inc = pd.merge(df_inc, pass11, on ="postnr", how ="outer", validate ="one_to_many")
pass1 = pass_inc.dropna()

pass1.sort_values(by = ['passagedate', 'passagetime'], inplace = True)
pass1.reset_index(inplace = True, drop = True)
days = [pass1['passagedate'][i].day for i in range(len(pass1))]
pass1['days'] = pd.Series(days)

seconds = secs(pass1)
pass1['secs'] = seconds
del seconds, days
del pass11, pass_inc, df_inc


#%% >>> check if all kommuns are included (NORRTÄLJE is not in 2012)

incsum = pass1.groupby(by = ['year','Kommun']).inc.sum().reset_index()
incsum2012 = incsum[incsum['year'] == 2012]
incsum2013 = incsum[incsum['year'] == 2013]

del incsum2012, incsum2013, incsum

#%% find if cars were available in both years or just one year

p_assigned1 = p_assigned.drop(columns = ['price', 'year', 'Kommun','FuelCat'])
pass1 = pd.merge(pass1, p_assigned1, on ="AnonymRegno", how ="outer", validate ="many_to_one")
pass1.dropna(inplace = True)

## seperate data available in both years vs. one year
years = pass1.groupby(by = 'AnonymRegno').year.unique()
years = years.reset_index()
length = years.apply(lambda year: year.str.len())
years['yrs'] = length['year']
years = years.drop(columns = ['year'])

pass1 = pd.merge(years, pass1, on ="AnonymRegno", how ="outer", validate ="one_to_many")
pass1.dropna(inplace = True)

del length, years


#%% remove CV vehicles from calculation (plots)

pass1 = pass1[pass1['FuelCat'] != 'CV']

#%% get total price per day for each car (aggeragate)

freq = pass1.groupby(by = ['AnonymRegno','year','dayFromStart']).count().secs.rename('freq')
price = pass1.groupby(by = ['AnonymRegno','year','dayFromStart']).price.sum()
avg_npr_tripsPerday = price/freq
tnpr= price.groupby(by = ['AnonymRegno','year']).sum()

#%% TO DO 

# check total nomial price for cars available in both years based on in and out of cordon
# also based on income group >>> categorize income group 

# high income (income > 35000?)
pass1['high_inc'] = 0
pass1['high_inc'][pass1['inc']>=420000] = 1

#%% Assign in_cordon or out_cordon based on "postnr" (Ägare postnr)

pass1 = home_cordon(pass1)
pass1.sort_values(by = ['in_cordon','AnonymRegno','passagedate'], inplace = True, ascending = False)

#%% Assign workTime (6-10 mornings and 14-18 afternoons) as x12, x13. >>> check FuelCat

wrk_freq= freq[freq == 2].reset_index()

pass12 = pass1[pass1['year'] == 2012]
pass13 = pass1[pass1['year'] == 2013]

def get_wkTime(x):
    x['td'] = -1                                    # outside time range
    x['td'][x['secs'] < 37800] = 0                  # morning
    x['td'][x['secs'].between(52199, 66599)] = 1    # afternoon
    return x

pass12 = get_wkTime(pass12)
pass13 = get_wkTime(pass13)
x12 = pass12[pass12['td']!=-1]
x13 = pass13[pass13['td']!=-1]

x12_ut = pass12[pass12['td']==-1]
x13_ut = pass13[pass13['td']==-1]



#%% Check frequencies of cars in the two years withtin work time limit

count_pass12_freq = x12.groupby(by = ['AnonymRegno','dayFromStart']).count().secs.rename('freq12')
count_pass13_freq = x13.groupby(by = ['AnonymRegno','dayFromStart']).count().secs.rename('freq13')
result = pd.concat([count_pass12_freq, count_pass13_freq], axis=1)
x12 = result[result['freq12'] == 2].reset_index()
x13 = result[result['freq13'] == 2].reset_index()

x12 = x12.groupby(by = ['AnonymRegno']).freq12.count()
arr12 = plt.hist(x12, bins = 7, alpha = 0.8)
x13 = x13.groupby(by = ['AnonymRegno']).freq13.count()
arr13 = plt.hist(x13, bins = 7, alpha = 0.5)
plt.xlabel('days from strat of data collection')
plt.ylabel('frequency')
plt.title('aggregate frequencies of cars, available in each year')
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

# find same indeces in both years
idx = pd.concat([x12, x13], 1)
idx.fillna(0, inplace = True)
x12 = idx[idx['freq12']>0]
x13 = idx[idx['freq13']>0]

plt.hist(x12['freq12'], bins = 7, alpha = 0.8)
plt.hist(x13['freq13'], bins = 7, alpha = 0.5)
plt.xlabel('days from strat of data collection')
plt.ylabel('frequency')
plt.title('frequency of cars, available in both years- within wkTime range')
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

pass_x = pass1.set_index('AnonymRegno')
pass_x = pass_x.filter(['AnonymRegno','inc'])
pass_x = pass_x[~pass_x.index.duplicated(keep='first')]
x12 = pd.concat([x12, pass_x], axis=1, join='inner')
x13 = pd.concat([x13, pass_x], axis=1, join='inner')
plt.hist(x12['inc'], bins = 200, alpha = 0.8)
plt.hist(x13['inc'], bins = 200, alpha = 0.5)
plt.xlabel('income')
plt.ylabel('frequency')
plt.title('frequency of incomes, both years- within wkTime range')
labels= ["2012","2013"]
plt.legend(labels)
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

# from fitter import Fitter
# from fitter import get_common_distributions
import numpy as np
import scipy.stats as stats
x = np.linspace(100000, 650000)

s = 0.03648273955598076
lc = -1340632.2113040518
sc = 1706365.5115661183
y1 = stats.lognorm.pdf(x, s, loc=lc, scale= sc)

s1 = 0.05057650497049722
lc1 = -888476.3534780542
sc1 = 1250011.571274607
y2 = stats.lognorm.pdf(x, s1, loc=lc1, scale= sc1)

plt.plot(x, y1, alpha = 0.9)
plt.plot(x, y2, alpha = 0.5)
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

a = x12['inc']
x = np.sort(a)
y = np.arange(len(x))/float(len(x))
a1 = x13['inc']
plt.plot(x, y)
x1 = np.sort(a1)
y1 = np.arange(len(x1))/float(len(x1))
plt.plot(x1, y1)
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

# x = x12['inc']
# f = Fitter(x, distributions= get_common_distributions())
# f.fit(x)
# f.summary()
# f.get_best(method = 'sumsquare_error')

# {'lognorm': {'s': 0.03648273955598076,
#   'loc': -1340632.2113040518,
#   'scale': 1706365.5115661183}}

# x1 = x13['inc']
# f = Fitter(x1, distributions= get_common_distributions())
# f.fit(x1)
# f.summary()
# f.get_best(method = 'sumsquare_error')
# {'lognorm': {'s': 0.05057650497049722,
#   'loc': -888476.3534780542,
#   'scale': 1250011.571274607}}

#%% output is the cars that are available in both years, freq>0, withtin wkTime hrs
# del price, result, wrk_freq, pass12, pass13, oneyear_idx, years, bothyears_idx, arr12, arr13
# del days, idx, length, count_pass12_freq, count_pass13_freq

## selects pass1 rows that have same indices as x12, x13
pass1.set_index('AnonymRegno', inplace = True)
x12_pass = x12.merge(pass1, left_index=True, right_index=True).reset_index()
x13_pass = x13.merge(pass1, left_index=True, right_index=True).reset_index()

x = x12_pass['dayFromStart'][x12_pass['freq12']>0]
plt.xlabel('days of 2012')
plt.ylabel('frequency')
plt.title('frequency of cars, available in both years')
plt.hist(x, bins = 6)
x1 = x13_pass['dayFromStart'][x13_pass['freq13']>0]
plt.hist(x1, bins = 6, alpha = 0.5)
plt.xlabel('days from strat of data collection')
plt.ylabel('frequency')
plt.title('frequency of cars, available in both years, including out of wkTime hrs')
labels= ["2012","2013"]
plt.legend(labels)
plt.show()

x12_pass = get_wkTime(x12_pass)
x13_pass = get_wkTime(x13_pass)
x12 = x12_pass[x12_pass['td']!=-1]
x13 = x13_pass[x13_pass['td']!=-1]
#%% 
def get_plot_freq_allDays(x, freq, text):
    plt.hist(x[freq][x['dayFromStart'] == 0], bins = 7, alpha = 0.9)
    plt.hist(x[freq][x['dayFromStart'] == 1], bins = 7, alpha = 0.8)
    plt.hist(x[freq][x['dayFromStart'] == 2], bins = 7, alpha = 0.7)
    plt.hist(x[freq][x['dayFromStart'] == 3], bins = 7, alpha = 0.6)
    plt.hist(x[freq][x['dayFromStart'] == 4], bins = 7, alpha = 0.5)
    plt.hist(x[freq][x['dayFromStart'] == 5], bins = 7, alpha = 0.4)
    plt.hist(x[freq][x['dayFromStart'] == 6], bins = 7, alpha = 0.3)
    labels = plt.hist(x[freq][x['dayFromStart'] == 7], bins = 7, alpha = 0.2)
    plt.xlabel('days')
    plt.ylabel('frequency')
    plt.title(text)
    plt.show()
    return (labels)

labels12 = get_plot_freq_allDays(x12, 'freq12', 'frequencies per day in 2012 (6:30-10:30 and 14:30-18:30)')    
labels13 = get_plot_freq_allDays(x13, 'freq13', 'frequencies per day in 2013 (6:30-10:30 and 14:30-18:30)')
dif = labels12[0]-labels13[0]
plt.bar(range(1,len(dif)+1), dif)
plt.xlabel('days')
plt.ylabel('frequency')
plt.title('freq12-freq13 of two yrs (mornings and afternoons)')
plt.show()

x12_wkh = x12[x12['freq12']==2]
x13_wkh = x13[x13['freq13']==2]


#%% 




