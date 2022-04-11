# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:04:47 2022

@author: naqavi
"""

import importPassages
from datetime import datetime
from datetime import time


def set_price():
    passages = importPassages.get_passages()
    passages['passagetime'] = [datetime.strptime(passages.Passagetid[i], '%H:%M:%S').time() for i in range(len(passages))]
    passages['passagedate'] = [datetime.strptime(passages.Passagedatum[i], '%Y-%m-%d').date() for i in range(len(passages))]
    
    # Compute nominal charges
    passages['price'] = 0
    def set_price(start, end, price_series, price):
        idx = [start <= passages.passagetime[i] < end for i in range(len(passages))]
        idx = [int(idx[i]) for i in range(len(passages))]
        price_series = [i * price for i in idx] + price_series 
        return price_series
    
    price1 = set_price(time(6, 30), time(7), passages['price'], 10)
    price2 = set_price(time(7), time(7,30), price1, 15)
    price3 = set_price(time(7, 30), time(8,30), price2, 20)
    price4 = set_price(time(8, 30), time(9), price3, 15)
    price5 = set_price(time(9), time(15,30), price4, 10)
    price6 = set_price(time(15, 30), time(16), price5, 15)
    price7 = set_price(time(16), time(17,30), price6, 20)
    price8 = set_price(time(17,30), time(18), price7, 15)
    price9 = set_price(time(18), time(18,30), price8, 10)
    passages['price'] = price9
    
    # Since 2013 observations only seem to exist during charging periods, filter out 
    # the same for 2012.
    passages = passages[passages['price'] > 0]
    # remove nan values in Kommun column
    passages['Kommun'] = passages['Kommun'].astype(str)
    passages = passages[passages['Kommun'] != 'nan']
    passages.reset_index()
    del price1, price2, price3, price4, price5, price6, price7, price8, price9
    return passages