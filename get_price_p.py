# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:36:49 2022

@author: naqavi
"""

import numpy as np
from GV_exepmtion_kommun_assignment import GV_share_assignment
from create_veh_pass import create_veh_pass
from sklearn.neighbors import KernelDensity


p_assigned, passages = GV_share_assignment()
veh_year, pass_veh = create_veh_pass()

p = passages[passages['Kommun'] != 'LIDINGÖ']
p_pr = p.groupby(by = ['AnonymRegno', 'year','Kommun', 'FuelCat']).price.sum().reset_index()
p_CV = p_pr[p_pr['FuelCat'] == 'CV']
p_CV_2012 = p_CV[p_CV['year'] == 2012]
p_CV_2013 = p_CV[p_CV['year'] == 2013]
idx_lst = p_CV_2012.Kommun.unique()
p_AFV = p_pr[p_pr['FuelCat'] == 'AFV']
p_AFV['pr_CV'] = 0
df_lst = []
for i in range(len(idx_lst)):
    j = idx_lst[i]
    p_CV_i = p_CV[p_CV['Kommun'] == j]
    p_AFV_i = p_AFV[p_AFV['Kommun'] == j]
    if len(p_CV_i)>30:  
        x = p_CV_i.price
        x1 = np.array(x).reshape(-1,1)
        kde = KernelDensity(kernel = 'gaussian', bandwidth=1).fit(x1)
        y = np.array(p_AFV_i.price).reshape(-1,1)
        kde_score = kde.score_samples(y)
        pr_CV = np.exp(kde_score)
        p_AFV.pr_CV.loc[p_AFV['Kommun'] == j] = pr_CV

del x, x1, kde, df_lst, pr_CV, p_CV_i, kde_score
