#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import h5py
import itertools
import numpy as np
import os
import sys

BMS_MIN = 1e-2
PRECISION = 5
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
NEWNAME_APP = "_cut.h5"


def check_bms(bms):
    beam_lost = False
            
    if bms.min() > BMS_MIN:
        print("No beam dumps detected.")
        return (beam_lost, len(bms))
        # if all the pixels are valid, it ends here.
        
    for last in range(len(bms)):
        if bms[::-1][0] < BMS_MIN:
            bms = bms[:len(bms)-1]
            beam_lost = True
        else:
            last-=1
            print('bms_out = ', bms[::-1][0])
            break                    
    print('No beam in '+ str(last+1) + ' pixels.')
    print('Length of bms after the cut: ', len(bms))
    return(beam_lost, len(bms))

    
def count_steps(x):
    # gives the shape of the array by counting the numbers of different values
    step_x = np.round(np.diff(np.unique(x*10**PRECISION)).min())/10**PRECISION 
    stx = np.round((x-x.min())/step_x).astype(int)  
    shape_x = stx.max()+1
    return(shape_x)


# flipping has to be implemented yet! An idea could be starting from the following
def descending(j):
    if (j[0]>j[-1]):
        to_be_flipped = True
    else:
        pass


def orientation(l,m):
    move_X_first = False
    
    # when l moves first, then columns and rows in the h5 are swapped
    # with respect to what PyMCA is expecting
    # This means the map needs to be rotated.
    
    if (l[1]!=l[0]) and (m[1]==m[0]):
        print('X moved first: swapped cols and rows')      
        move_X_first = True
        l, m = m, l        
        return l, m, move_X_first
    
    # when m moves first, rows and columns are in the correct order
    elif (m[1]!=m[0]) and (l[1]==l[0]):
        print('Y moved first: no swapping of rows and cols')
        return l, m, move_X_first
    # if both motors are moved or if none moves, then the map is not correct
    # when X moves first, in order to see the map on PyMCA, the number of 
    # columns to enter is the number of rows. The map will appear rotated.  
    else:
        raise ValueError('Something is wrong with this map. Please check the file!')




def read_positions(filename,PATH_SCALAR):
    with h5py.File(filename, 'r') as f:
                
           #ciclo sui run
        for run in f.keys():
            print ("Run: %s" %run)
            x=f[run+PATH_SCALAR+"/X"][...]
            y=f[run+PATH_SCALAR+"/Y"][...]                    
                
        return x,y
