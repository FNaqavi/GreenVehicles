# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:34:43 2022

@author: naqavi
"""

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
price = pass1.groupby(by = ['AnonymRegno','year','dayFromStart']).price.sum()
avg_npr_tripsPerday = price/freq
tnpr= price.groupby(by = ['AnonymRegno','year']).sum()

#%% find GV cars with repeated (same) and non-repeated (different) frequencies in both years 

# freq_n = freq
# freq = freq.reset_index()
# freq = freq.drop(['dayFromStart'], axis=1)
# freq = freq.groupby(by = ['AnonymRegno','year']).sum()
freq = pass1.groupby(by = ['AnonymRegno','year']).count().secs.rename('frq')
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
freq_non_repeated = pass1.loc[pass1['AnonymRegno'].isin(freq_non_repeated.index)]

#%% GV sum(frequencies) for the cars available in both years

def plt_freq_sum(df):
    df_grp = df.groupby(by = ['AnonymRegno','year']).count().secs.rename('frq')
    df_grp = df_grp.reset_index()
    df12 = df_grp[df_grp['year'] == 2012]
    df13 = df_grp[df_grp['year'] == 2013]
    y1 = sum(df12['frq'])
    y2 = sum(df13['frq'])
    plt.bar('2012', y1, label = '2012')
    plt.bar('2013', y2, label = '2013')
    plt.title('freq for GVs available in both years')
    plt.xlabel('year')
    plt.ylabel('sum')
    return plt.show() 
    
#plt_freq(pass1)
plt_freq_sum(freq_non_repeated)

#%% plot histogram of frequencies based on time for non-repeated GV in both years

def get_np_cars_both_years(df):
    np_cars_12 = df[df['year'] == 2012].reset_index(drop = True)
    np_cars_13 = df[df['year'] == 2013].reset_index(drop = True)
    return np_cars_12, np_cars_13

np_cars_12, np_cars_13 = get_np_cars_both_years(freq_non_repeated)
#np_cars_12.sort_values(by=['secs'], inplace = True)
#np_cars_13.sort_values(by=['secs'], inplace = True)

def plt_hist_freq_time(df12, df13):
    plt.hist(df12['secs']/3600,bins = 100, alpha = 0.5, label = '2012')
    plt.hist(df13['secs']/3600,bins = 100, alpha = 0.5, label = '2013')
    plt.title('Histogram of time of day for GV cars in both years')
    plt.xlabel('time of day')
    plt.ylabel('frequency')
    return plt.show()
   
plt_hist_freq_time(np_cars_12, np_cars_13)


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
        # y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
        y = f.fitted_pdf['norm']
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
        # y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
        y = f.fitted_pdf['norm']
    return x_new, y, f

## dir(f)
## type(f.fitted_pdf)
## f.fitted_pdf.keys()
#%% get best fit for mornings and evenings 2012 and 2013

x_np12_m, y_np12_m, f1 = get_pdf_y_to_plot(np_cars_12, 43200, 'smaller')    # non-repeated cars 2012 morning
x_np13_m, y_np13_m, f2 = get_pdf_y_to_plot(np_cars_13, 43200, 'smaller')
x_np12_e, y_np12_e, f3 = get_pdf_y_to_plot(np_cars_12, 55800, 'larger')     # non_repeates cars 2012 evening
x_np13_e, y_np13_e, f4 = get_pdf_y_to_plot(np_cars_13, 55800, 'larger')
plt.show()

#%% what is the freq of non-repeated cars (how many days) for 2012 and 2013

def freq_nr_prep(df, unequlaity, inc):
    if unequlaity == 'larger':
        freq_non_repeated = df[df['inc']>inc]
        freq_np12 = freq_non_repeated[freq_non_repeated['year'] == 2012]
        freq_np13 = freq_non_repeated[freq_non_repeated['year'] == 2013]
        freq_np12 = freq_np12.groupby(by = ['AnonymRegno','year']).count().yrs.rename('frq').reset_index()
        freq_np13 = freq_np13.groupby(by = ['AnonymRegno','year']).count().yrs.rename('frq').reset_index()
        freq_np12 = freq_np12.sort_values(by = 'frq')
        freq_np13 = freq_np13.sort_values(by = 'frq')
    if unequlaity == 'smaller':
        freq_non_repeated = df[df['inc']<inc]
        freq_np12 = freq_non_repeated[freq_non_repeated['year'] == 2012]
        freq_np13 = freq_non_repeated[freq_non_repeated['year'] == 2013]
        freq_np12 = freq_np12.groupby(by = ['AnonymRegno','year']).count().yrs.rename('frq').reset_index()
        freq_np13 = freq_np13.groupby(by = ['AnonymRegno','year']).count().yrs.rename('frq').reset_index()
        freq_np12 = freq_np12.sort_values(by = 'frq')
        freq_np13 = freq_np13.sort_values(by = 'frq')
    return freq_np12, freq_np13

freq_np12, freq_np13 = freq_nr_prep(freq_non_repeated, 'larger', 0)


#%% plot freqency of corssings
def plt_crossings(df1, df2):
    plt.hist(df1['frq'], bins = 100, alpha = 0.8, label = '2012')
    plt.hist(df2['frq'], bins = 100, alpha = 0.8, label = '2013')
    plt.xlabel('number of crossings')
    plt.ylabel('count')
    plt.legend()
    return plt.show()

plt_crossings(freq_np12, freq_np13)

#%%
## CDF plot for frequencies both years non-repeated cars
def CDF_sorted(df1, df2):
    x1 = range(len(df1))
    y1 = np.sort(np.array(df1['frq']))
    x = range(len(df2))
    y = np.sort(np.array(df2['frq']))
    plt.plot(x1, np.cumsum(y1), color = 'C0', label = '2012')
    plt.plot(x, np.cumsum(y), color = 'C1', label = '2013' )
    plt.xlabel('number of observations')
    plt.ylabel('CDF of crossings')
    plt.title('CDF of crossings for non repeated cars in both years')
    plt.legend(loc = 'best')
    return plt.show()

CDF_sorted(freq_np12, freq_np13)

## plot for frequencies both years non-repeated cars

def freq_sorted(df1, df2):
    x = range(len(df1))
    y = np.sort(np.array(df1['frq']))
    plt.plot(x, y, label = '2012', color = 'C0')
    x = range(len(df2))
    y = np.sort(np.array(df2['frq']))
    plt.plot(x, y, label = '2013', color = 'C1')
    plt.xlabel('number of observations')
    plt.ylabel('number of crossings')
    plt.title('number of crossings for non repeated cars in both years')
    plt.legend(['2012','2013'], loc = 'best')
    return plt.show()

freq_sorted(freq_np12, freq_np13)

#%% pdf of morning and evening peak times

def pdf_peak(df1, time1, uneq1, df2, time2, uneq2, grp):
    x_np12_m, y_np12_m, f1 = get_pdf_y_to_plot(df1, time1, uneq1)    # non-repeated cars 2012 morning
    x_np13_m, y_np13_m, f2 = get_pdf_y_to_plot(df2, time1, uneq1)
    x_np12_e, y_np12_e, f3 = get_pdf_y_to_plot(df1, time2, uneq2)     # non_repeates cars 2012 evening
    x_np13_e, y_np13_e, f4 = get_pdf_y_to_plot(df2, time2, uneq2)
    plt.show()
    plt.plot(x_np12_m/60, y_np12_m, label = '2012 morning' + grp)
    plt.plot(x_np13_m/60, y_np13_m, label = '2013 morning' + grp)     
    plt.plot(x_np12_e/60, y_np12_e, label = '2012 evening' + grp, color = 'C0')
    plt.plot(x_np13_e/60, y_np13_e, label = '2013 evening' + grp , color = 'C1')    
    plt.xlabel('time of day')
    plt.ylabel('pdf')
    plt.title('peak time pdf for non-repeated cars in both years')
    plt.legend(loc = 'best')
    plt.show()
    return x_np12_m, y_np12_m, f1, x_np13_m, y_np13_m, f2, x_np12_e,\
        y_np12_e, f3, x_np13_e, y_np13_e, f4

x_np12_m, y_np12_m, f1, x_np13_m, y_np13_m, f2, \
    x_np12_e, y_np12_e, f3, x_np13_e, y_np13_e, f4 = \
        pdf_peak(np_cars_12, 43200, 'smaller', np_cars_13, 55800, 'larger', '_all')

#%% scaled price plot

def scale_price(sc):
    tm = [6.5, 7, 7.5, 8.5, 9, 15.5, 16, 17.5, 18, 18.5, 18.51]
    nprice = [0, 10, 15, 20, 15, 10, 15, 20, 15, 10, 0]
    nprice = [i*sc for i in nprice]
    plt.step(tm,nprice)
    return plt.show()
scale_price(1)

#%% income overlaps perfectly (they are the same cars)
def get_incs(df1, df2):
    inc12 = df1[~df1.index.duplicated(keep='first')].inc
    inc13 = df2[~df2.index.duplicated(keep='first')].inc
    return inc12, inc13

inc12, inc13 = get_incs(np_cars_12, np_cars_13)

# plt.hist(inc12, bins = 100, label = 'income_2012',color = 'C0', alpha = 0.5)
# plt.hist(inc13, bins = 100, label = 'income_2013', color = 'C1', alpha = 0.5)
# plt.title('income histogram for non repeated cars in 2012 and 2013')
# plt.xlabel('income')
# plt.ylabel('frequency')
# plt.legend(loc = 'best')
# plt.show()

# plt.plot(np.sort(inc12), label = 'income sorted')
# plt.show()

#%% income boxplot  >>> we can set 410000 as high income
def box_plot_inc(inc):
    plt.boxplot(inc)
    _, bp = pd.DataFrame.boxplot(inc, return_type='both')
    outliers = [flier.get_ydata() for flier in bp["fliers"]]
    boxes = [box.get_ydata() for box in bp["boxes"]]
    medians = [median.get_ydata() for median in bp["medians"]]
    whiskers = [whiskers.get_ydata() for whiskers in bp["whiskers"]]
    print("Outliers: ", outliers)
    print("Boxes: ", boxes)
    print("Medians: ", medians)
    print("Whiskers: ", whiskers)
    return plt.show()

box_plot_inc(inc12)

#%% checking the upper half of income group
"""
f1_upinc: morning 2012
f2_upinc: evening 2012
f3_upinc: morning 2013
f4_upinc: evening 2013

f1_lowinc: morning 2012
f2_lowinc: evening 2012
f3_lowinc: morning 2013
f4_lowinc: evening 2013

"""

x_upinc = freq_non_repeated[freq_non_repeated['inc']>=366800]
# x_upinc = x[x['inc']<max(x['inc'])]
plt_freq_sum(x_upinc)
x_upinc12, x_upinc13 = get_np_cars_both_years(x_upinc)
plt_hist_freq_time(x_upinc12, x_upinc13)
freq_upinc12, freq_upinc13 = freq_nr_prep(x_upinc, 'larger', 366800)
plt_crossings(freq_upinc12, freq_upinc13)
CDF_sorted(freq_upinc12, freq_upinc13)
freq_sorted(freq_upinc12, freq_upinc13)
#pdf_peak(x_upinc12, 43200, 'smaller', x_upinc13, 55800, 'larger', '_upinc')
inc12_up, inc13_up= get_incs(x_upinc12, x_upinc13)
box_plot_inc(inc12_up)

x_upinc12_m, y_upinc12_m, f1_upinc, x_upinc13_m, y_upinc13_m, f2_upinc, \
    x_upinc12_e, y_upinc12_e, f3_upinc, x_upinc13_e, y_upinc13_e, f4_upinc =\
        pdf_peak(x_upinc12, 43200, 'smaller', x_upinc13, 55800, 'larger', '_upinc')


def compare_pdf(f1, f2, title, lbl):
    # y1 = f1.fitted_pdf[list(f1.get_best(method='sumsquare_error').keys())[0]]
    y1 = f1.fitted_pdf['norm']
    # y1_upinc = f2.fitted_pdf[list(f2.get_best(method='sumsquare_error').keys())[0]]
    y1_upinc = f2.fitted_pdf['norm']
    plt.plot(x_np13_m/60, y1, label = 'all')
    plt.plot(x_np13_m/60, y1_upinc, label = lbl)
    plt.xlabel('time')
    plt.ylabel('pdf of frequencies')
    plt.title(title)
    plt.legend()
    # scale_price(0.0001)
    return plt.show()

# compare_pdf(f1, f1_upinc, '2012', 'high income')
# compare_pdf(f2, f2_upinc, '2013', 'high income')



#%% checking the lower half of income group

x_lowinc = freq_non_repeated[freq_non_repeated['inc']<366800]       # sepereate the years
# x_upinc = x[x['inc']<max(x['inc'])]
plt_freq_sum(x_lowinc)
x_lowinc12, x_lowinc13 = get_np_cars_both_years(x_lowinc)
plt_hist_freq_time(x_lowinc12, x_lowinc13)
freq_lowinc12, freq_lowinc13 = freq_nr_prep(x_lowinc, 'smaller', 366800)
plt_crossings(freq_lowinc12, freq_lowinc13)
CDF_sorted(freq_lowinc12, freq_lowinc13)
freq_sorted(freq_lowinc12, freq_lowinc13)
#pdf_peak(x_lowinc12, 43200, 'smaller', x_lowinc13, 55800, 'larger','_lowinc')
inc12_low, inc13_low= get_incs(x_lowinc12, x_lowinc13)
box_plot_inc(inc12_low)

x_lowinc12_m, y_lowinc12_m, f1_lowinc, x_lowinc13_m, y_lowinc13_m, f2_lowinc, \
    x_lowinc12_e, y_lowinc12_e, f3_lowinc, x_lowinc13_e, y_lowinc13_e, f4_lowinc =\
        pdf_peak(x_lowinc12, 43200, 'smaller', x_lowinc13, 55800, 'larger','_lowinc')

compare_pdf(f1_upinc, f1_lowinc, '2012', 'low income')
compare_pdf(f2_upinc, f2_lowinc, '2013', 'low income')

y1 = f1_upinc.fitted_pdf['norm'] 
y2 = f1_lowinc.fitted_pdf['norm']
y3 = f3_upinc.fitted_pdf['norm'] 
y4 = f3_lowinc.fitted_pdf['norm']
# y5 = f1.fitted_pdf['norm']
# y6 = f3.fitted_pdf['norm']
# x = x_lowinc12_m
plt.plot(x_np13_m/60, y1)#, label = 'high income, 2012')
plt.plot(x_np13_m/60, y2)#, label = 'low income, 2012')
plt.plot(x_np13_e/60, y3, label = 'high income, 2012', color = 'C0')
plt.plot(x_np13_e/60, y4, label = 'low income, 2012', color = 'C1')
# plt.plot(x_np13_m/60, y5, label = 'All, 2012', color = 'C8')
# plt.plot(x_np13_e/60, y6, label = 'All, 2012', color = 'C8')
y1 = f2_upinc.fitted_pdf['norm'] 
y2 = f2_lowinc.fitted_pdf['norm']
y3 = f4_upinc.fitted_pdf['norm'] 
y4 = f4_lowinc.fitted_pdf['norm']
# y5 = f2.fitted_pdf['norm']
# y6 = f4.fitted_pdf['norm']
# x = x_lowinc13_m
plt.plot(x_np13_m/60, y1, color = 'C7')#, label = 'high income, 2013')
plt.plot(x_np13_m/60, y2, color = 'C6')#, label = 'low income, 2013')
plt.plot(x_np13_e/60, y3, label = 'high income, 2013', color = 'C7' )
plt.plot(x_np13_e/60, y4, label = 'low income, 2013', color = 'C6')
# plt.plot(x_np13_m/60, y5, label = 'All, 2013', color = 'C9')
# plt.plot(x_np13_e/60, y6, label = 'All, 2013', color = 'C9')
plt.title('PDF of trip frequenciesin 2012 and 2013')
plt.legend()
scale_price(0.0001)
plt.show()

dif_m_lowinc = f1_lowinc.fitted_param['norm'][0] - f3_lowinc.fitted_param['norm'][0]   
dif_e_lowinc = f2_lowinc.fitted_param['norm'][0] - f4_lowinc.fitted_param['norm'][0]
dif_m_upinc = f1_upinc.fitted_param['norm'][0] - f3_upinc.fitted_param['norm'][0]
dif_e_upinc = f2_upinc.fitted_param['norm'][0] - f4_upinc.fitted_param['norm'][0]

print( 'difference in peak time for low income group in the morning 2012-2013:', dif_m_lowinc,\
      '\n difference in peak time for low income group in the evening:', dif_e_lowinc,\
          '\n difference in peak time for high income group in the morning:', dif_m_upinc,\
              '\n difference in peak time for low income group in the evening:', dif_e_upinc)

 

y = f2_upinc.fitted_pdf['norm'] - f1_upinc.fitted_pdf['norm']    
y1 = f4_upinc.fitted_pdf['norm'] - f3_upinc.fitted_pdf['norm']    
plt.plot(x_np13_m/60, y, color = 'C7')   
plt.plot(x_np13_e/60, y1, color = 'C7')   
scale_price(0.0001)


x_upincm = x_upinc[x_upinc['secs']<43200]
x_upincm12 = x_upincm[x_upincm['year'] == 2012]
x_upincm13 = x_upincm[x_upincm['year'] == 2013]

x_lowincm = x_lowinc[x_lowinc['secs']<43200]
x_lowincm12 = x_lowincm[x_lowincm['year'] == 2012]
x_lowincm13 = x_lowincm[x_lowincm['year'] == 2013]

x_upince = x_upinc[x_upinc['secs']>55800]
x_upince12 = x_upince[x_upince['year'] == 2012]
x_upince13 = x_upince[x_upince['year'] == 2013]

x_lowince = x_lowinc[x_lowinc['secs']>55800]
x_lowince12 = x_lowince[x_lowince['year'] == 2012]
x_lowince13 = x_lowince[x_lowince['year'] == 2013]


import statsmodels.api as sm
def cor_model(df):
    x = df['secs']/3600
    y = df['inc']/100000
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    return print(model.summary())

cor_model(x_upincm12)
cor_model(x_upincm13)

cor_model(x_lowincm12)
cor_model(x_lowincm13)



#find line of best fit
# a, b = np.polyfit(x_upincm12['secs'], x_upincm12['inc'], 1)
# #add points to plot
# # plt.scatter(x_upincm12['secs'], x_upincm12['inc'], color='purple')
# #add line of best fit to plot
# x = x_upincm12['secs']/60
# y = a*x_upincm12['inc']+b
# d = {'x': x, 'y':y}
# df = pd.DataFrame(data = d)
# df = df.sort_values(by = ['x'])
# plt.plot(df['x'],df['y'])
# plt.show()
# #add fitted regression equation to plot
# # plt.text(1, 90, 'y = ' + '{:.3f}'.format(b) + ' + {:.3f}'.format(a) + 'x', size=12)

# #add axis labels
# plt.xlabel('secs')
# plt.ylabel('inc')


x_upincm12['inc100K'] = x_upincm12['inc']/100000
x_upincm12['hr'] = x_upincm12['secs']/3600
x_upincm12.corr(method = 'pearson')['inc100K']['hr']            #correlation of inc and secs in morning 2012
# x_upincm13.corr(method = 'pearson')['inc']['secs']            #correlation of inc and secs in morning 2013

# x_upince = x_upinc[x_upinc['secs']>55800]
# x_upince12 = x_upince[x_upince['year'] == 2012]
# x_upince13 = x_upince[x_upince['year'] == 2013]
# x_upince12.corr(method = 'pearson')['inc']['secs']            #correlation of inc and secs in morning 2012
# x_upince13.corr(method = 'pearson')['inc']['secs']            #correlation of inc and secs in morning 2013

# import scipy.stats
# scipy.stats.pearsonr(x_upincm12['inc'], x_upincm12['secs'])     # high income morning 2012  

#%%
x_upincm12 = x_upincm12.reset_index()
x1 = x_upincm12.groupby(by = ['AnonymRegno','inc']).secs.mean().rename('secs_up12m')
x2 = x_upincm13.groupby(by = ['AnonymRegno','inc']).secs.mean().rename('secs_up13m')
x3 = x_lowincm12.groupby(by = ['AnonymRegno','inc']).secs.mean().rename('secs_low12m')
x4 = x_lowincm13.groupby(by = ['AnonymRegno','inc']).secs.mean().rename('secs_low13m')

df = pd.concat([x1, x2], axis=1).dropna(axis = 0).reset_index()
plt.hist(df['secs_up12m']/3600, alpha = 0.5, label = '2012')
plt.hist(df['secs_up13m']/3600, alpha = 0.5, label = '2013')
plt.legend()
plt.title('average crossing time in the morning for high income cars in both years')
scale_price(10)
plt.show()


df1 = pd.concat([x3, x4], axis=1).dropna(axis = 0).reset_index()
plt.hist(df1['secs_low12m']/3600, alpha = 0.5, label = '2012')
plt.hist(df1['secs_low13m']/3600, alpha = 0.5, label = '2013')
plt.legend()
plt.title('average crossing time in the morning for low income cars in both years')
scale_price(10)
plt.show()

