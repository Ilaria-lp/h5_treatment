#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import h5py
import itertools
import numpy as np
import os
import sys

BMS_MIN = 1e-2
PRECISION = 10**5
PATH_SCALAR = "/Measurement/TransientScalarData"
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

# gives the shape of the array by counting the numbers of different values    
def count_steps(x):
    step_x = np.round(np.diff(np.unique(x*PRECISION)).min())/PRECISION 
    stx = np.round((x-x.min())/step_x).astype(int)  
    shape_x = stx.max()+1
    return(shape_x)


# flipping has to be implemented yet! An idea could be starting from the following
def _descending(j):
    if (j[0]>j[-1]):
        to_be_flipped = True
    else:
        pass

# When the vertical motor moves first, the map is collected filling column after column. 
# When PyMCA will try to resize the array of XRF data, the correct image will be shown only entering the cols and rows values swapped.
# The map will have the correct position of the pixel with respect to one another, but it will appear rotated by 90deg counterclockwise.
# The function takes the array of the x and y positions, and returns them swapped when the vertical motor is moved first. And it returns a flag used for the 90deg clockwise rotation needed to bring the map orientation back to normal. 
def orientation(ver,hor):
    move_ver_first = False
 
    if (ver[1]!=ver[0]) and (hor[1]==hor[0]):
        print('X (VER) moved first: swapped cols and rows')      
        move_ver_first = True
        ver, hor = hor, ver        
        return ver, hor, move_ver_first
    
    # when the horizontal motor moves first, no need to swap rows and columns
    elif (hor[1]!=hor[0]) and (ver[1]==ver[0]):
        print('Y (HOR) moved first: no swapping of rows and cols')
        return ver, hor, move_ver_first
    # if both motors are moved or if none moves, then the map is somewhat broken.
    else:
        raise ValueError('Something is wrong with this map. Please check the file!')


def _read_positions(filename,PATH_SCALAR):
    with h5py.File(filename, 'r') as f:
                
        for run in f.keys():
            print ("Run: %s" %run)
            x=f[run+PATH_SCALAR+"/X"][...]
            y=f[run+PATH_SCALAR+"/Y"][...]                    
        return x,y