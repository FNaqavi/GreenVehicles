# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 08:58:18 2022

@author: naqavi
"""

def get_passages():
    import pandas as pd
    
    
    #Import data
    pass_gv_12 = pd.read_csv("KTH_KontrollGruppPassager_2012.txt",',', index_col = False, encoding = 'latin1')
    pass_gv_13 = pd.read_csv("KTH_KontrollGruppPassager_2013.txt", ',', index_col = False, encoding = 'latin1')
    pass_cv_12 = pd.read_csv("KTH_BehandlingsGruppPassager_2012.txt", ',', index_col = False, encoding = 'latin1')
    pass_cv_13 = pd.read_csv("KTH_BehandlingsGruppPassager_2013.txt", ',', index_col = False, encoding = 'latin1')
    
    localities = pd.read_csv("Localities.csv",',', index_col = False, encoding = 'latin1')
    
    # Add columns for data-collection year and vehicle type
    pass_gv_12['year'] = 2012
    pass_gv_13['year'] = 2013
    pass_cv_12['year'] = 2012
    pass_cv_13['year'] = 2013
    pass_gv_12['expgrp'] = 'gv'
    pass_gv_13['expgrp'] = 'gv'
    pass_cv_12['expgrp'] = 'cv'
    pass_cv_13['expgrp'] = 'cv'
    
    # Merge and unite data
    df = [pass_gv_12, pass_gv_13, pass_cv_12, pass_cv_13]
    passages = pd.concat(df)
    passages.reset_index(drop = True, inplace = True)
    
    # Create unified fuel variable
    passages['expgrp'] = passages['expgrp'].astype('category')
    passages['Drivmedel'] = passages['Drivmedel 1']
    passages['Drivmedel'] = passages['Drivmedel 1'] + '.' + passages['Drivmedel 2']
    passages['Drivmedel'] = passages['Drivmedel']
    passages['Drivmedel'] = passages['Drivmedel'].astype(str)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Okänd', 'Petrol', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Diesel.Okänd', 'Petrol', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('El.Okänd', 'Electric', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.El', 'Electric_Hybrid', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Etanol.Okänd', 'Ethanol', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Etanol', 'Ethanol', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Bensin.Metangas', 'Natural_Gas', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Metangas.Metangas', 'Natural_Gas', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Metangas.Okänd', 'Natural_Gas', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('Motorgas.Okänd', 'Other', regex = True)
    passages['Drivmedel'] = passages['Drivmedel'].str.replace('nan', 'Other', regex = True)
    passages['FuelCat'] = passages['Drivmedel']
    passages['FuelCat'].loc[passages['Drivmedel'].isin(["Electric","Electric_Hybrid","Ethanol","Natural_Gas","Other"])] = 'gv'
    passages['FuelCat'].loc[passages['Drivmedel'].isin(["Petrol","Diesel"])] = 'cv'
    
    # Add municipalities to Passages based on localities
    passages['Ort'] = passages['Ägare ort'].copy()
    passages['Ort'] = [x.strip() for x in passages['Ort']]
    localities['Ort'] = [x.upper() for x in localities['Ort']]
    localities['Kommun'] = [x.upper() for x in localities['Kommun']]
    
    passages = pd.merge(passages, localities, how='left', on='Ort')


    return passages

