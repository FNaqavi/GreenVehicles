# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:36:49 2022

@author: naqavi
"""

# from GV_exepmtion_kommun_assignment import GV_share_assignment
# from create_veh_pass import create_veh_pass
# from sklearn.neighbors import KernelDensity
import pandas as pd
# import matplotlib.pyplot as plt
# from fitter import Fitter
# from fitter import get_common_distributions
from scipy.stats import cauchy


# p_assigned, passages = GV_share_assignment()
# veh_year, pass_veh = create_veh_pass()

def get_prices(passages,p_assigned):

    p = passages#[passages['Kommun'] != 'LIDINGÖ']
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
    
    
    # Assign weights to AFV based on PDF of difference in total nominal price in CV
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
    y = cauchy.pdf(x.sort_values(), loc, scale)
    sumy = sum(y)   # use to normalize weight
    
    # plt.plot(x.sort_values(),y)
    
    x1_AFV = p_AFV.delta_ntpr
    x2_AFV = x1_AFV.sort_values()
    y1_AFV = cauchy.pdf(x2_AFV, loc, scale)
    # plt.plot(x1_AFV.sort_values(),y1_AFV)
    # plt.show()
    y1_AFV = pd.Series(y1_AFV)
    # y_series = pd.Series(y1_AFV, index= x2_AFV.index)
    y1_AFV = y1_AFV.reindex(x2_AFV.index).sort_index()
    p_AFV.loc[:,'ntpr_CV'] = y1_AFV
    
    x1_CV = p_CV.delta_ntpr
    x2_CV = x1_CV.sort_values()
    y1_CV = cauchy.pdf(x2_CV, loc, scale)
    # plt.plot(x1.sort_values(),y1)
    # plt.show()
    y1_CV = pd.Series(y1_CV)
    # y_series = pd.Series(y1_CV, index= x2_CV.index)
    y1_CV = y1_CV.reindex(x2_CV.index).sort_index()
    p_CV.loc[:,'ntpr_CV'] = y1_CV
    
    p_ntpr1 = pd.concat([p_AFV, p_CV]).reset_index()  # create a long table with assinged CV_ntpr_prob
    p_ntpr1 = p_ntpr1.fillna(-1)
    
    p_ntpr1.sort_values(by = ['AnonymRegno'], inplace = True)
    p_assigned.sort_values(by = ['AnonymRegno'], inplace= True)
    p_assigned['ntpr_CV'] = p_ntpr1['ntpr_CV']
    p_assigned['norm_ntpr_CV'] = p_assigned['ntpr_CV'] / sumy
    p_assigned['1-exempt_assigned'] = 1-p_assigned['exempt_assigned']
    p_assigned['prb*ntpr'] = p_assigned['1-exempt_assigned']*p_assigned['norm_ntpr_CV']
    # del x1, x2, y1, y_series, scale, loc, p_ntpr, p_ntpr1, p_AFV, p_CV
    
    return p_assigned

# {'cauchy': {'loc': -9.022352452470182, 'scale': 39.37919633573871}} For all points in CV
# {'cauchy': {'loc': -10.840516278685193, 'scale': 43.352452247121676}} For Stockholm in CV