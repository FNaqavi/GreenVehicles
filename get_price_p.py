# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:36:49 2022

@author: naqavi
"""

import numpy as np
from GV_exepmtion_kommun_assignment import GV_share_assignment
from create_veh_pass import create_veh_pass
from sklearn.neighbors import KernelDensity
import pandas as pd
import matplotlib.pyplot as plt
from fitter import Fitter
from fitter import get_common_distributions
from scipy.stats import cauchy



p_assigned, passages = GV_share_assignment()
veh_year, pass_veh = create_veh_pass()

p = passages[passages['Kommun'] != 'LIDINGÖ']
p_ntpr = p.groupby(by = ['AnonymRegno', 'year','Kommun', 'FuelCat']).price.sum().reset_index()

# duplicate the records that were available only in one of the years and 
# assign price = 0 for the missing year to calculate the price difference.

dup = p_ntpr['AnonymRegno'].duplicated(keep='first')
p_ntpr['dup'] = dup
p_ntpr['dup1'] = p_ntpr['dup'].shift(-1)
p_ntpr['dup1'] = p_ntpr['dup1'].fillna(0)
p_ntpr['dups'] = (p_ntpr['dup'].astype(int) + p_ntpr['dup1'].astype(int)).copy()
p_ntpr.drop(columns = ['dup', 'dup1'], inplace = True)
dups1 = p_ntpr[p_ntpr['dups'] == 1]
dups0 = p_ntpr[p_ntpr['dups'] == 0]
dups0_1 = dups0.copy()
dups0_1.loc[:,'price'] = 0
dups0_1_2012 = dups0_1[dups0_1['year'] == 2012] 
dups0_1_2013 = dups0_1[dups0_1['year'] == 2013]
dups0_1_2012.loc[:,'year'] = 2013
dups0_1_2013.loc[:,'year'] = 2012
frames = [dups0_1_2012, dups0_1_2013]
dups0_1_new = pd.concat(frames)
frames = [dups0, dups0_1_new]
dups0 = pd.concat(frames)
frames = [dups0, dups1]
dups = pd.concat(frames)
dups.drop(columns = ['dups'], inplace = True)
del dup, dups0, dups0_1, dups0_1_2012, dups0_1_2013, dups0_1_new, dups1, frames
dups.sort_values(by = ['AnonymRegno', 'year'],inplace = True)
dups2012 = dups[dups['year'] == 2012].reset_index(drop = True)
dups2013 = dups[dups['year'] == 2013].reset_index(drop = True)
dups2012.loc[:,'price_13'] = dups2013['price'] 
dups = dups2012
dups['delta_ntpr'] = dups['price']-dups['price_13']
# dups['delta_ntpr_log'] = abs(min(dups['delta_ntpr'])) + dups['delta_ntpr']
del dups2012, dups2013


# Assign weights to AFV based on PDF of difference in nominal price in CV
p_ntpr1 = dups.drop(columns = ['year'])
p_CV = p_ntpr1[p_ntpr1['FuelCat'] == 'CV'].reset_index()
# idx_lst = p_CV.Kommun.unique()
p_AFV = p_ntpr1[p_ntpr1['FuelCat'] == 'AFV'].reset_index()
p_AFV.loc[:,'ntpr_CV'] = 0
p_CV.loc[:,'ntpr_CV'] = 0
# df_lst = []

x = p_CV.delta_ntpr
# f = Fitter(x, distributions= get_common_distributions())
# f.fit(x)
# f.summary()
# f.get_best(method = 'sumsquare_error')
loc = -9.022352452470182
scale = 39.37919633573871
# y = cauchy.pdf(x.sort_values(), loc, scale)
# plt.plot(x.sort_values(),y)

x1 = p_AFV.delta_ntpr
x2 = x1.sort_values()
y1 = cauchy.pdf(x2, loc, scale)
# plt.plot(x1.sort_values(),y1)
# plt.show()

y1 = pd.Series(y1)
y_series = pd.Series(y1, index= x2.index)
y1 = y1.reindex(x2.index).sort_index()
p_AFV.loc[:,'ntpr_CV'] = y1
p_ntpr1 = pd.concat([p_AFV, p_CV]).reset_index()  # create a long table with assinged CV_ntpr_prob
p_ntpr1 = p_ntpr1.fillna(-1)

p_ntpr1.sort_values(by = ['AnonymRegno'], inplace = True)
p_assigned.sort_values(by = ['AnonymRegno'], inplace= True)
p_assigned['ntpr_CV'] = p_ntpr1['ntpr_CV']
 











#for i in range(len(idx_lst)):
# i = 2
# j = idx_lst[i]
# p_CV_i = p_CV[p_CV['Kommun'] == j]
# p_AFV_i = p_AFV[p_AFV['Kommun'] == j]
# print (j)
    # if len(p_CV_i)>30: 
        # x = p_CV.delta_pr  
        # x.plot.kde(figsize = (8, 6), linewidth = 1, bw_method=0.3)
        # plt.xlim(-600,600)
        # plt.xlabel()
    
        # x1 = np.array(x).reshape(-1,1)
        # kde = KernelDensity(kernel = 'gaussian', bandwidth=0.3).fit(x1)
        # y = np.array(p_AFV_i.delta_pr).reshape(-1,1)
        # kde_score = kde.score_samples(y)
        # pr_CV = np.exp(kde_score)
        # p_AFV_i.pr_CV.loc[p_AFV['Kommun'] == j] = pr_CV
        # # p_AFV.pr_CV.loc[p_AFV['Kommun'] == j] = pr_CV
            
        # del x, x1, kde, df_lst, pr_CV, p_CV_i, kde_score
        
        # xxx = range(len(np.cumsum(p_CV['pr_CV'])))
        # plt.plot(xxx,np.cumsum(p_CV['pr_CV']))
        # # plt.xlim()
        # plt.xlabel('Cumulative Distribution Function for CV and AFV')
        # xxx = range(len(np.cumsum(p_AFV['pr_CV'])))
        # plt.plot(xxx,np.cumsum(p_AFV['pr_CV']))
        # # plt.xlim()
        
        # plt.show()
    

# {'cauchy': {'loc': -9.022352452470182, 'scale': 39.37919633573871}} For all points in CV
# {'cauchy': {'loc': -10.840516278685193, 'scale': 43.352452247121676}} For Stockholm in CV