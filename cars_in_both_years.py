# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 10:00:17 2022

@author: naqavi
"""

import warnings
warnings.filterwarnings('ignore')

    
import numpy as np
from GV_exepmtion_kommun_assignment import GV_share_assignment
# from create_veh_pass import create_veh_pass
import pandas as pd
import matplotlib.pyplot as plt
from get_price_p import get_prices
from income_merge import get_income
from secs import secs
from fitter import Fitter
from fitter import get_common_distributions

#from home_cordon import home_cordon


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

## only keep the values of pass1 that are in both years
pass1 = pass1[pass1['yrs']==2]

#%% remove CV vehicles from calculation (plots)

pass1 = pass1[pass1['FuelCat'] != 'CV']

#%% get total price per day for each car (aggeragate)

freq = pass1.groupby(by = ['AnonymRegno','year','dayFromStart']).count().secs.rename('frq')
freq1 = pass1.groupby(by = ['AnonymRegno','year']).count().secs.rename('frq')
price = pass1.groupby(by = ['AnonymRegno','year','dayFromStart']).price.sum()
avg_npr_tripsPerday = price/freq
tnpr= price.groupby(by = ['AnonymRegno','year']).sum()

#%% GV sum(frequencies) for the cars available in both years

freq1 = freq1.reset_index()
freq1_12 = freq1[freq1['year'] == 2012]
freq1_13 = freq1[freq1['year'] == 2013]
y1 = sum(freq1_12['frq'])
y2 = sum(freq1_13['frq'])
plt.bar('2012', y1, label = '2012')
plt.bar('2013', y2, label = '2013')
plt.title('freq for GVs available in both years')
plt.xlabel('year')
plt.ylabel('sum')
plt.show()


#%% Plot GV avg(freq) for different all days for the cars in both years  

freq = freq.reset_index()
freq_12 = freq[freq['year'] == 2012]
freq_13 = freq[freq['year'] == 2013]

freq12_d = freq_12.groupby(by = ['dayFromStart']).count().frq.rename('frq')
freq13_d = freq_13.groupby(by = ['dayFromStart']).count().frq.rename('frq')

plt.bar('2012', np.mean(freq12_d), alpha = 0.8, label = '2012')
plt.bar('2013', np.mean(freq13_d), alpha = 0.8, label = '2013')
plt.title('GV avg(freq) for different all days for the cars in both years')
plt.xlabel('year')
plt.ylabel('avg')
plt.show()
#%% find GV cars with repeated (same) and non-repeated (different) frequencies in both years 

freq_n = freq
# freq = freq_n
freq = freq.drop(['dayFromStart'], axis=1)
freq = freq.groupby(by = ['AnonymRegno','year']).sum()

freq = freq.reset_index()
freq1 = freq.set_index('AnonymRegno', drop = True)

freq1['prev_row'] = freq1.frq.shift(1)-freq1.frq
odd_rows = freq1['prev_row'].loc[freq1.reset_index().index % 2 == 1] 
mask = odd_rows[odd_rows == 0]
freq_repeated = freq1.loc[mask.index]
freq_repeated.drop(['prev_row'], axis =1, inplace = True)

mask1 = odd_rows[odd_rows != 0]
freq_non_repeated = freq1.loc[mask1.index]
freq_non_repeated.drop(['prev_row'], axis =1, inplace = True)

y1 = np.sum(freq_non_repeated['frq'][freq_non_repeated['year']==2012])
y2 = np.sum(freq_non_repeated['frq'][freq_non_repeated['year']==2013])
plt.bar('2012', y1, alpha = 0.8, label = '2012')
plt.bar('2013', y2, alpha = 0.8, label = '2013')
plt.title('GV cars with non-repeated (different) frequencies in both years')
plt.xlabel('year')
plt.ylabel('sum')
plt.show()

all_cars = pass1.set_index(['AnonymRegno'], drop = True)
np_cars = all_cars.loc[mask1.index]
np_cars_12 = all_cars[all_cars['year'] == 2012]
np_cars_13 = all_cars[all_cars['year'] == 2013]
np_cars_12.sort_values(by=['secs'], inplace = True)
np_cars_13.sort_values(by=['secs'], inplace = True)

plt.hist(np_cars_12['secs'],bins = 100, alpha = 0.5, label = '2012')
plt.hist(np_cars_13['secs'],bins = 100, alpha = 0.5, label = '2013')
plt.title('Histogram of time of day for GV cars in both years')
plt.xlabel('seconds')
plt.ylabel('frequency')
plt.show()

#%% try to plot

def get_pdf_y_to_plot(x, time, unequality):     
    if unequality == 'smaller':
        x = x[x['secs'] < time]
        x = x['secs']/60        #change to minutes
        n, bins, patches = plt.hist(x, bins = 100, alpha = 0.5)
        x = bins
        x_even = x[1] - x[0]
        x_odd = x[2] - x[1]
        a = np.arange(100.0)
        a[a % 2 == 0] = x_even
        a[a % 2 == 1] = x_odd
        y = n
        x_new = x[0:-1] + a
        x_new1 = x_new-min(x_new)
        f = Fitter((x_new1,y), distributions= get_common_distributions())
        f.fit(y)
        f.summary()
        f.get_best(method = 'sumsquare_error')
        y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
    if unequality == 'larger':
        x = x[x['secs'] > time]
        x = x['secs']/60
        n, bins, patches = plt.hist(x, bins = 100, alpha = 0.5)
        x = bins
        x_even = x[1] - x[0]
        x_odd = x[2] - x[1]
        a = np.arange(100.0)
        a[a % 2 == 0] = x_even
        a[a % 2 == 1] = x_odd
        y = n
        x_new = x[0:-1] + a
        x_new1 = x_new-min(x_new)
        f = Fitter((x_new1,y), distributions= get_common_distributions())
        f.fit(y)
        f.summary()
        f.get_best(method = 'sumsquare_error')
        y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
    return x_new, y, f
# # dir(f)
# # type(f.fitted_pdf)
# # f.fitted_pdf.keys()

#%%
x_np12_m, y_np12_m, f1 = get_pdf_y_to_plot(np_cars_12, 43200, 'smaller')    # non-repeated cars 2012 morning
x_np13_m, y_np13_m, f2 = get_pdf_y_to_plot(np_cars_13, 43200, 'smaller')
x_np12_e, y_np12_e, f3 = get_pdf_y_to_plot(np_cars_12, 55800, 'larger')     # non_repeates cars 2012 evening
x_np13_e, y_np13_e, f4 = get_pdf_y_to_plot(np_cars_13, 55800, 'larger')



#%% what is the freq of non-repeated cars (how many days) for 2012 and 2013

freq = freq_n
freq.set_index('AnonymRegno', drop = True, inplace = True)
freq_np = freq.loc[freq.index.intersection(freq_non_repeated.index)]
freq_np12 = freq_np[freq_np['year'] == 2012].reset_index()
freq_np13 = freq_np[freq_np['year'] == 2013].reset_index()
freq_np12 = freq_np12.groupby(by = ['AnonymRegno','year']).sum()
freq_np13 = freq_np13.groupby(by = ['AnonymRegno','year']).sum()
plt.show()
#%%
## CDF plot for frequencies both years non-repeated cars
x1 = range(len(freq_np12))
y1 = np.sort(np.array(freq_np12['frq']))
x = range(len(freq_np13))
y = np.sort(np.array(freq_np13['frq']))
plt.plot(x1, np.cumsum(y1), color = 'C0', label = '2012')
plt.plot(x, np.cumsum(y), color = 'C1', label = '2013' )
plt.xlabel('number of observations')
plt.ylabel('CDF of crossings')
plt.title('CDF of crossings for non repeated cars in both years')
plt.legend(loc = 'best')
plt.show()

## plot for frequencies both years non-repeated cars
x = range(len(freq_np12))
y = np.sort(np.array(freq_np12['frq']))
plt.plot(x, y, label = '2012', color = 'C0')
x = range(len(freq_np13))
y = np.sort(np.array(freq_np13['frq']))
plt.plot(x, y, label = '2013', color = 'C1')
plt.xlabel('number of crossings')
plt.ylabel('number of observations')
plt.title('number of crossings for non repeated cars in both years')
plt.legend(['2012','2013'], loc = 'best')
plt.show()

# x = np.array(np_cars_12['secs']/3600).reshape(-1,1)
# from sklearn.mixture import GaussianMixture
# gm = GaussianMixture(n_components=1, covariance_type='full').fit(x)
# gm.means_
# plt.plot(x)
# #plt.plot(np_cars_12['secs'])

# x = np.array(np_cars_13['secs']/3600).reshape(-1,1)
# from sklearn.mixture import GaussianMixture
# gm = GaussianMixture(n_components=1, covariance_type='full').fit(x)
# gm.means_
# plt.plot(x)

#%%
plt.plot(x_np12_m/60, y_np12_m, label = '2012 morning')
plt.plot(x_np13_m/60, y_np13_m, label = '2013 morning')     
plt.plot(x_np12_e/60, y_np12_e, label = '2012 evening', color = 'C0')
plt.plot(x_np13_e/60, y_np13_e, label = '2013 evening', color = 'C1')    
plt.xlabel('time of day')
plt.ylabel('pdf')
plt.title('peak time pdf for non-repeated cars in both years')
plt.legend(loc = 'best')
plt.show()
# price plot
tm = [6.5, 7, 7.5, 8.5, 9, 15.5, 16, 17.5, 18, 18.5, 18.51]
nprice = [0, 10, 15, 20, 15, 10, 15, 20, 15, 10, 0]
nprice = [i*10 for i in nprice]
plt.step(tm,nprice)
plt.show()

#%% income overlaps perfectly (they are the same cars)
inc12 = np_cars_12[~np_cars_12.index.duplicated(keep='first')].inc
inc13 = np_cars_13[~np_cars_13.index.duplicated(keep='first')].inc

plt.hist(inc12, bins = 100, label = 'income_2012',color = 'C0', alpha = 0.5)
plt.hist(inc13, bins = 100, label = 'income_2013', color = 'C1', alpha = 0.5)
plt.title('income histogram for non repeated cars in 2012 and 2013')
plt.xlabel('income')
plt.ylabel('frequency')
plt.legend(loc = 'best')
plt.show()

plt.plot(np.sort(inc12), label = 'income sorted')
plt.show()

#%% income boxplot  >>> we can set 410000 as high income
plt.boxplot(inc12)
_, bp = pd.DataFrame.boxplot(inc12, return_type='both')
outliers = [flier.get_ydata() for flier in bp["fliers"]]
boxes = [box.get_ydata() for box in bp["boxes"]]
medians = [median.get_ydata() for median in bp["medians"]]
whiskers = [whiskers.get_ydata() for whiskers in bp["whiskers"]]
print("Outliers: ", outliers)
print("Boxes: ", boxes)
print("Medians: ", medians)
print("Whiskers: ", whiskers)
plt.show()

x = np_cars_12[np_cars_12['inc']>366800]
x_rich = x[x['inc']<400000]
x.reset_index(inplace = True)
y = x_rich['inc']
x = x_rich['secs']/3600
plt.hist(y)
plt.xticks(rotation='vertical')
plt.show()

plt.hist(x)
plt.step(tm, nprice)
plt.show()


# test = np_cars_12.groupby(['AnonymRegno','inc']).sum()
# test = test['price','1-exempt_assigned']
# test = test.reset_index()
# test1 = np_cars_13.groupby(['AnonymRegno','inc']).sum()
# test1 = test1['price']
# test1 = test1.reset_index()
# # plt.hist(test['inc'],color = 'C0', alpha = 0.5)
# plt.hist(test['price'],color = 'C0', alpha = 0.5)
# # plt.hist(test1['inc'],color = 'C0', alpha = 0.5)
# plt.hist(test1['price'],color = 'C1', alpha = 0.5)
# plt.show()

