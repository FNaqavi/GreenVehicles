# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:31:22 2022

@author: naqavi
"""

import pandas as pd

def secs(df):
    hour = pd.Series([df['passagetime'][i].hour for i in range(len(df))])
    minute = pd.Series([df['passagetime'][i].minute for i in range(len(df))])
    second = pd.Series([df['passagetime'][i].second for i in range(len(df))])
    return (hour * 60 + minute) * 60 + second
