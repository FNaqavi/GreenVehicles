# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:04:47 2022

@author: naqavi
"""

import importPassages
from datetime import datetime
from datetime import time
import numpy as np

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
    # passages['Kommun'] = passages['Kommun'].astype(str)
    passages[['Kommun']] = passages[['Kommun']].fillna('nan')
    passages = passages[passages['Kommun'] != 'nan']
    passages = passages[passages['Kommun'] != 'LIDINGÖ']   
    passages['Riktning'] = passages['Riktning'].str.replace('Ut', 'UT', regex = True)
    passages['Riktning'] = passages['Riktning'].str.replace('In', 'IN', regex = True)
    
    # we need to define days from start of the data collection in each year for comparison
    # because the data collection days have a partial overlap in the two years
    passages['dayFromStart'] = 0
    def Fill_daysFromStart(passages,date, day):
        passages['dayFromStart'] = np.where(passages['Passagedatum'] == date, day, passages['dayFromStart'])
        return passages
    
    passages = Fill_daysFromStart(passages,'2012-05-23',1)
    passages = Fill_daysFromStart(passages,'2012-05-24',2)
    passages = Fill_daysFromStart(passages,'2012-05-25',3)
    passages = Fill_daysFromStart(passages,'2012-05-28',4)
    passages = Fill_daysFromStart(passages,'2012-05-29',5)
    passages = Fill_daysFromStart(passages,'2012-05-30',6)
    passages = Fill_daysFromStart(passages,'2012-05-31',7)
    passages = Fill_daysFromStart(passages,'2012-05-01',8)
    passages = Fill_daysFromStart(passages,'2012-05-04',9)

    passages = Fill_daysFromStart(passages,'2013-05-23',1)
    passages = Fill_daysFromStart(passages,'2013-05-24',2)
    passages = Fill_daysFromStart(passages,'2013-05-27',3)
    passages = Fill_daysFromStart(passages,'2013-05-28',4)
    passages = Fill_daysFromStart(passages,'2013-05-29',5)
    passages = Fill_daysFromStart(passages,'2013-05-30',6)
    passages = Fill_daysFromStart(passages,'2013-05-31',7)
    passages = Fill_daysFromStart(passages,'2013-05-03',8)
    passages = Fill_daysFromStart(passages,'2013-05-04',9) 
    
    passages.reset_index(inplace = True,drop = True)
    # this line gets the first word in the paying stations 
    passages['stations'] = [passages.Betalstation[i].split(' ')[0] for i in range(len(passages))]
    

    del price1, price2, price3, price4, price5, price6, price7, price8, price9
    return passages