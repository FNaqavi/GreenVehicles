# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:33:19 2022

@author: naqavi
"""


## postnr inside Cordon:
# sodermalm					                    116 xx, 117 xx, 118 xx
# kungsholmen, Essingens				            112 xx
# Albano                                        113 xx
# djurgården				        	                115 xx
# östermalm, nörra djurgården, lidingöbro		114 xx, 115 xx
# gamla, norrmalm stan och skeppholmen		    111 xx


def home_cordon(pass1):
    pass1['in_cordon'] = 0
    pass1['in_cordon'][pass1['postnr']<11899] = 1
    pass1['in_cordon'][pass1['postnr']<11100] = 0
    return pass1