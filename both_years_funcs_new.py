# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 13:04:23 2022

@author: naqavi
"""

# -*- coding: utf-8 -*-


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

#%% box plot to find outliars

#outliers, boxes, medians, whiskers = box_plot_inc(df_m)
# print("Outliers: ", outliers)
# print("Boxes: ", boxes)
# print("Medians: ", medians)
# print("Whiskers: ", whiskers)

#frq_out = min(outliers[0])    


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



# %% GV sum(frequencies) for the cars available in both years mornings, no outliar freq

def plt_freq_sum(df, title):
    df_grp = df.groupby(by=['AnonymRegno', 'year']).count().secs.rename('frq')
    df_grp = df_grp.reset_index()
    df12 = df_grp[df_grp['year'] == 2012]
    df13 = df_grp[df_grp['year'] == 2013]
    plt.grid(which='major', axis='y', zorder=-1.0, alpha = 0.3)
    y1 = sum(df12['frq'])
    y2 = sum(df13['frq'])
    plt.bar('2012', y1, label='2012')
    plt.bar('2013', y2, label='2013')
    plt.title(title)
    plt.xlabel('year')
    plt.ylabel('sum')
    return plt.show()


# plt_freq(pass1)
plt_freq_sum(df_mh, 'freq for high income GVs available in both years')
plt_freq_sum(df_ml, 'freq for low income GVs available in both years')


# %% plot histogram of frequencies based on time for non-repeated GV in both years

def get_np_cars_both_years(df):
    df_12 = df[df['year'] == 2012].reset_index(drop=True)
    df_13 = df[df['year'] == 2013].reset_index(drop=True)
    return df_12, df_13

df_mh12, df_mh13 = get_np_cars_both_years(df_mh)
df_ml12, df_ml13 = get_np_cars_both_years(df_ml)

# np_cars_12.sort_values(by=['secs'], inplace = True)
# np_cars_13.sort_values(by=['secs'], inplace = True)


def plt_hist_freq_time(df12, df13, title):
    plt.hist(df12['secs']/3600, bins=100, alpha=0.5, label='2012')
    plt.hist(df13['secs']/3600, bins=100, alpha=0.5, label='2013')
    plt.title(title)
    plt.xlabel('time of day')
    plt.ylabel('frequency')
    return plt.show()

plt_hist_freq_time(df_mh12, df_mh13, 'Histogram of time of day for high income group')
plt_hist_freq_time(df_ml12, df_ml13, 'Histogram of time of day for low income group')

# %% try to plot

def get_pdf_y_to_plot(x, time, unequality):
    if unequality == 'smaller':
        x = x[x['secs'] <= time]        
        x = x['secs']/(1*1)  # change to two minutes
        n, xedges, patches = plt.hist(x, bins=100, alpha=0.5)
        xcenters = (xedges[:-1] + xedges[1:]) / 2
        y = n
        f = Fitter((xcenters, y), distributions=get_common_distributions())
        f.fit(y)
        f.summary()
        f.get_best(method='sumsquare_error')
        # y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
        y = f.fitted_pdf['norm']     
    if unequality == 'larger':
        x = x[x['secs'] > time]
        x = x['secs']/(1*1)  # change to two minutes
        n, xedges, patches = plt.hist(x, bins=100, alpha=0.5)
        xcenters = (xedges[:-1] + xedges[1:]) / 2
        y = n
        f = Fitter((xcenters, y), distributions=get_common_distributions())
        f.fit(y)
        f.summary()
        f.get_best(method='sumsquare_error')
        # y = f.fitted_pdf[list(f.get_best(method='sumsquare_error').keys())[0]]
        y = f.fitted_pdf['norm']
    return xcenters*1, y, f

# dir(f)
# type(f.fitted_pdf)
# f.fitted_pdf.keys()

# %% get best fit for mornings and evenings 2012 and 2013

x_mh12, y_mh12, f1 = get_pdf_y_to_plot(df_mh12, 36000, 'smaller')    # high inc morning 2012 
x_ml12, y_ml12, f2 = get_pdf_y_to_plot(df_ml12, 36000, 'smaller')    # low inc morning 2012 
x_mh13, y_mh13, f3 = get_pdf_y_to_plot(df_mh13, 36000, 'smaller')    # high inc morning 2013 
x_ml13, y_ml13, f4 = get_pdf_y_to_plot(df_ml13, 36000, 'smaller')    # low inc morning 2013 
plt.show()

#%% plot the fitted normal pdfs

plt.plot(x_mh12/60, y_mh12, color = 'C0', label = 'high income 2012')
plt.plot(x_ml12/60, y_ml12, color = 'C1', label = 'low income 2012')
plt.plot(x_mh13/60, y_mh13, color = 'C0', linestyle='dashed', label = 'high income 2013')
plt.plot(x_ml13/60, y_ml13, color = 'C1', linestyle='dashed', label = 'low income 2013')
plt.grid(axis='both', zorder=-1.0, alpha = 0.3)
plt.legend(loc = 'best')
# scale_price(0.0001)
plt.show()

#%% check peak point for a fitted pdf
# idx  = np.where(f1m.fitted_pdf['norm'] == max(f1m.fitted_pdf['norm']))
# print(x_mh12[idx[0][0]]/60)


#%% for evenings

# df = pass1
# df_e = df[df['secs']>55800]
# df_e = get_both_year_data(df_m, df)
# df_e = df[df['secs']>55800]
# df_eh = df_e[df_e['inc']>=366800]
# df_el = df_e[df_e['inc']<366800]
# outliers, boxes, medians, whiskers = box_plot_inc(df_e)
# frq_out_e= min(outliers[0])    

# y1e, y2e= plt_freq(df_e)

# df_eh = df_eh[df_eh['AnonymRegno'].isin(y1e.AnonymRegno)]
# df_el = df_el[df_el['AnonymRegno'].isin(y1e.AnonymRegno)]
# plt_freq_sum(df_eh, 'freq for high income GVs available in both years')
# plt_freq_sum(df_el, 'freq for low income GVs available in both years')
# df_eh12, df_eh13 = get_np_cars_both_years(df_eh)
# df_el12, df_el13 = get_np_cars_both_years(df_el)
# plt_hist_freq_time(df_eh12, df_eh13, 'Histogram of time of day for high income group')
# plt_hist_freq_time(df_el12, df_el13, 'Histogram of time of day for low income group')

# x_eh12, y_eh12, f1e = get_pdf_y_to_plot(df_eh12, 55800, 'larger')    # high inc morning 2012 
# x_el12, y_el12, f2e = get_pdf_y_to_plot(df_el12, 55800, 'larger')    # low inc morning 2012 
# x_eh13, y_eh13, f3e = get_pdf_y_to_plot(df_eh13, 55800, 'larger')    # high inc morning 2013 
# x_el13, y_el13, f4e = get_pdf_y_to_plot(df_el13, 55800, 'larger')    # low inc morning 2013 
# plt.show()



#%% plot pdf for evenings


# plt.plot(x_eh12/60, y_eh12, color = 'C0', label = 'high income 2012')
# plt.plot(x_el12/60, y_el12, color = 'C1', label = 'low income 2012')
# plt.plot(x_eh13/60, y_eh13, color = 'C0', linestyle='dashed', label = 'high income 2013')
# plt.plot(x_el13/60, y_el13, color = 'C1', linestyle='dashed', label = 'low income 2013')
# plt.grid(axis='both', zorder=-1.0, alpha = 0.3)
# plt.legend(loc = 'best')
# # scale_price(0.0001)
# plt.show()


# %%
# CDF plot for frequencies both years non-repeated cars

def CDF_sorted(df1, df2, title):
    frq1 = df1.groupby(by=['AnonymRegno']).count().secs.rename('frq')
    frq2 = df2.groupby(by=['AnonymRegno']).count().secs.rename('frq')
    x1 = range(len(frq1))
    y1 = np.sort(np.array(frq1))
    x = range(len(frq2))
    y = np.sort(np.array(frq2))
    plt.plot(x1, np.cumsum(y1), color='C0', label='2012')
    plt.plot(x, np.cumsum(y), color='C1', label='2013')
    plt.xlabel('number of observations')
    plt.ylabel('CDF of crossings')
    plt.title(title)
    plt.legend(loc='best')
    return plt.show()

CDF_sorted(df_mh12, df_mh13, 'CDF of morning crossings for cars in both years')
# CDF_sorted(df_eh12, df_eh13, 'CDF of evening crossings for cars in both years')

# %% scaled price plot

def scale_price(sc):
    tm = [6.5, 7, 7.5, 8.5, 9, 12]#15.5, 16, 17.5, 18, 18.5, 18.51]
    nprice = [0, 10, 15, 20, 15, 10]#, 15, 20, 15, 10, 0]
    nprice = [i*sc for i in nprice]
    plt.step(tm, nprice)
    return plt.show()

# scale_price(1)

# %% income overlaps perfectly (they are the same cars)

def get_incs(df1, df2):
    inch12 = df1[~df1.index.duplicated(keep='first')].inc
    incl12 = df2[~df2.index.duplicated(keep='first')].inc
    return inch12, incl12


inch12, incl12 = get_incs(df_mh12, df_ml12)

plt.hist(inch12, bins = 100, label = 'high income',color = 'C0', alpha = 0.5)
plt.hist(incl12, bins = 100, label = 'low income', color = 'C1', alpha = 0.5)
plt.title('income histogram for high and low incomce groups in 2012')
plt.xlabel('income')
plt.ylabel('frequency')
plt.legend(loc = 'best')
plt.show()

# plt.plot(np.sort(inc12), label = 'income sorted')
# plt.show()

# %%

x_upincm12 = df_mh12
x_upincm13 = df_mh13

x_lowincm12 = df_ml12
x_lowincm13 = df_ml13

# x_upince = x_upinc[x_upinc['secs'] > 55800]

x_upincm12 = x_upincm12.reset_index()
x1 = x_upincm12.groupby(by=['AnonymRegno', 'inc']
                        ).secs.mean().rename('secs_up12m')
x2 = x_upincm13.groupby(by=['AnonymRegno', 'inc']
                        ).secs.mean().rename('secs_up13m')
x3 = x_lowincm12.groupby(by=['AnonymRegno', 'inc']
                         ).secs.mean().rename('secs_low12m')
x4 = x_lowincm13.groupby(by=['AnonymRegno', 'inc']
                         ).secs.mean().rename('secs_low13m')

df = pd.concat([x1, x2], axis=1).dropna(axis=0).reset_index()
plt.hist(df['secs_up12m']/3600, alpha=0.5, label='2012')
plt.hist(df['secs_up13m']/3600, alpha=0.5, label='2013')
plt.legend()
plt.title('average crossing time in the morning for high income cars in both years')
scale_price(10)
plt.show()


df1 = pd.concat([x3, x4], axis=1).dropna(axis=0).reset_index()
plt.hist(df1['secs_low12m']/3600, alpha=0.5, label='2012')
plt.hist(df1['secs_low13m']/3600, alpha=0.5, label='2013')
plt.legend()
plt.title('average crossing time in the morning for low income cars in both years')
scale_price(10)
plt.show()

#%% check how many cars from mornings are seen in the evening from low/high income

y1, y2= get_freq(df_m)
# y1e, y2e= plt_freq(df_e)

x1 = df_mh12.groupby(by=['AnonymRegno']).count().secs.rename('frq').reset_index().set_index('AnonymRegno')
x2 = df_ml12.groupby(by=['AnonymRegno']).count().secs.rename('frq').reset_index().set_index('AnonymRegno')
# x3 = df_eh12.groupby(by=['AnonymRegno']).count().secs.rename('frq1').reset_index().set_index('AnonymRegno')
# x4 = df_el12.groupby(by=['AnonymRegno']).count().secs.rename('frq1').reset_index().set_index('AnonymRegno')

xh = pd.concat([x1, x3], axis =1).dropna()
xl = pd.concat([x2, x4], axis =1).dropna()

xh_srt = xh.sort_values(by = 'frq')


# import seaborn as sns
# dif = np.abs(xh_srt.frq - xh_srt.frq1)
# sns.scatterplot(data=xh_srt, x="frq", y="frq1", size =dif , legend=False, sizes=(20, 2000))
# plt.show()

#%%

x1 = df_mh12.groupby(by=['AnonymRegno']).mean().secs.reset_index().set_index('AnonymRegno')
x2 = df_ml12.groupby(by=['AnonymRegno']).mean().secs.reset_index().set_index('AnonymRegno')
x11 = df_mh13.groupby(by=['AnonymRegno']).mean().secs.rename('secs1').reset_index().set_index('AnonymRegno')
x22 = df_ml13.groupby(by=['AnonymRegno']).mean().secs.rename('secs1').reset_index().set_index('AnonymRegno')

xh1 = pd.concat([x1, x11], axis =1).dropna()
xl1 = pd.concat([x2, x22], axis =1).dropna()

def box_plt(x):
    plt.boxplot(x)
    _, bp = pd.DataFrame.boxplot(x, return_type='both')
    return plt.show()

# box_plt(xh1.secs/60 - xh1.secs1/60)
# box_plt(xh1.secs1)
# box_plt(xl1.secs/60 - xl1.secs1/60)
# box_plt(xl1.secs1)

# Set the figure size
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

# Pandas dataframe
# data = pd.DataFrame({"change avg high income":xh1.secs/60 - xh1.secs1/60, "change avg low income": xl1.secs/60 - xl1.secs1/60})
data = pd.DataFrame({'highinc_12':xh1.secs/3600, 'highinc_13': xh1.secs1/3600, 'lowinc_12': xl1.secs/3600 ,'lowinc_13':xl1.secs1/3600})

# Plot the dataframe
ax = data[['highinc_12', 'highinc_13','lowinc_12','lowinc_13']].plot(kind='box', title='boxplot', grid = 'both')

# Display the plot
plt.show()