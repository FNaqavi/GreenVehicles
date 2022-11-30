# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 10:00:17 2022

@author: naqavi
"""
import numpy as np
from GV_exepmtion_kommun_assignment import GV_share_assignment
# from create_veh_pass import create_veh_pass
import pandas as pd
import matplotlib.pyplot as plt
from get_price_p import get_prices
from income_merge import get_income
from secs import secs
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

#%%
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

from fitter import Fitter
from fitter import get_common_distributions


# x1_12 = np_cars_12['secs']<45000
# x1_12 = np_cars_12['secs'].loc[x1_12 ==True]
# n, bins, patches = plt.hist(x1_12, bins = 100, alpha = 0.5)
# plt.show()
# f = Fitter(x1_12, distributions= get_common_distributions())
# f.fit(x1_12)
# f.summary()
# f.get_best(method = 'sumsquare_error')
# loc_12 = 22967.669409206886
# sc_12 = 5645.081843815768

# x1_13 = np_cars_13['secs']<40000
# x1_13 = np_cars_13['secs'].loc[x1_13 ==True]
# plt.hist(x1_13, bins = 100, alpha = 0.5)
# plt.show()
# f = Fitter(x1_13)#, distributions= get_common_distributions())
# #f.fit(x1_13)
# f.fit()
# f.summary()
# f.get_best(method = 'sumsquare_error')
#'rayleigh': {'loc': 22775.6778072676, 'scale': 6724.343996394615}
#'rayleigh': {'loc': 22743.807359451937, 'scale': 6813.693560518693}






x1 = np_cars_12['secs']
n, bins, patches = plt.hist(x1, bins = 100, alpha = 0.5)
x = bins
x_even = x[1] - x[0]
x_odd = x[2] - x[1]
a = np.arange(100.0)
a[a % 2 == 0] = x_even
a[a % 2 == 1] = x_odd
y = n
x_new = x[0:-1] + a
#plt.plot(x_new, y, 'ro')


x2 = np_cars_13['secs']
n1, bins1, patches1 = plt.hist(x2, bins = 100, alpha = 0.5)
xx = bins
xx_even = xx[1] - xx[0]
xx_odd = xx[2] - xx[1]
a1 = np.arange(100.0)
a1[a1 % 2 == 0] = xx_even
a1[a1 % 2 == 1] = xx_odd
y1 = n1
xx_new = xx[0:-1] + a1


from scipy.interpolate import UnivariateSpline


spl = UnivariateSpline(x_new, y)
xs = np.linspace(x_new[0], x_new[-1], 8)
#plt.plot(xs, spl(xs), 'g', lw=1)

plt.plot(x_new, y, 'ro')
plt.plot(xs, spl(xs), 'g', lw=1)
spl.set_smoothing_factor(0.1)
plt.plot(xs, spl(xs), 'b', lw=1)
#plt.title('Histogram of time of day for GV cars in 2012 (non-repeated)')
# plt.xlabel('seconds')
# plt.ylabel('frequency')
# plt.show()


from scipy.interpolate import CubicSpline
X = x_new
Y = y
cs = CubicSpline(X, Y)
# plt.plot(x_new, y, 'ro')
plt.plot(X, cs(X), 'b', lw=1)


spl1 = UnivariateSpline(xx_new, y1)
xs1 = np.linspace(xx_new[0], xx_new[-1], 100)
plt.plot(xx_new, y1, 'ro')
plt.plot(xs1, spl1(xs1), 'g', lw=1)
spl.set_smoothing_factor(0.1)
plt.plot(xs1, spl1(xs1), 'b', lw=1)
#plt.title('Histogram of time of day for GV cars in 2013 (non-repeated)')
plt.xlabel('seconds')
plt.ylabel('frequency')
plt.show()


# import scipy.stats as stats
# lc_12 = 22775.6778072676
# sc_12 = 6724.343996394615
# lc_13 = 22743.807359451937
# sc_13 = 6813.693560518693

# y1_12 = stats.rayleigh.pdf(x1_12, loc = lc_12, scale = sc_12)
# y1_13 = stats.rayleigh.pdf(x1_13, loc = lc_13, scale = sc_13)
# plt.plot(x1_12, y1_12,'r-', lw=5, alpha=0.6, label='rayleigh pdf')
# plt.plot(x1_13, y1_13,'b-', lw=5, alpha=0.6, label='rayleigh pdf')

# x2 = (np_cars_12['secs']<50000) * (np_cars_12['secs']>40000)
# x2 = np_cars_12['secs'].loc[x2 ==True]
# plt.hist(x2, bins = 100, alpha = 0.5)
# plt.show()
# f = Fitter(x2, distributions= get_common_distributions())
# f.fit(x2)
# f.summary()
# f.get_best(method = 'sumsquare_error')

# x3 = np_cars_12['secs']>50000
# x3 = np_cars_12['secs'].loc[x3 ==True]
# plt.hist(x3, bins = 100, alpha = 0.5)
# plt.show()
# f = Fitter(x3, distributions= get_common_distributions())
# f.fit(x3)
# f.summary()
# f.get_best(method = 'sumsquare_error')

# x1 = np_cars_12['secs']
# x2 = np_cars_13['secs']
# f = Fitter(x1, distributions= get_common_distributions())
# f.fit(x1)
# f.summary()
# f.get_best(method = 'sumsquare_error')
# f = Fitter(x2, distributions= get_common_distributions())
# f.fit(x2)
# f.summary()
# f.get_best(method = 'sumsquare_error')


# n, bins, patches = plt.hist(x3, bins = 100, alpha = 0.5)

# from pylab import *
# from scipy.optimize import curve_fit

# data=x1
# y,x,_=plt.hist(data,100,alpha=.3,label='data')

# x=(x[1:]+x[:-1])/2 # for len(x)==len(y)

# def gauss(x,mu,sigma,A):
#     return A*exp(-(x-mu)**2/2/sigma**2)

# def bimodal(x,mu1,sigma1,A1,mu2,sigma2,A2):
#     return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)

# expected=(1,.2,250,2,.2,125)
# params,cov=curve_fit(bimodal,x,y,expected)
# sigma=np.sqrt(diag(np.cov))
# plt.plot(x,bimodal(x,*params),color='red',lw=3,label='model')
# legend()
# print(params,'\n',sigma)

#%% what is the freq of non-repeated cars (how many days) for 2012 and 2013

freq = freq_n

freq.set_index(['AnonymRegno'], drop = True, inplace = True)
freq_np = [freq_n.loc[i] for i in freq_non_repeated.index]
[freq_np[i].reset_index(inplace = True) for i in range(len(freq_np))]
from functools import reduce
df = reduce(lambda df1,df2: pd.merge(df1,df2,on='AnonymRegno'), freq_np)
