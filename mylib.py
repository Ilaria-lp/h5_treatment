#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This script does 2 things:
#1) It checks for beam dumps during MAP acquisition
#   In case BMS is < BMS_MIN, it reshapes the map discarding void pixels
# AND
#2) It discards half-filled rows/columns in case of manual interruption of the map

import glob
import h5py
import itertools
import numpy as np
import os
import sys

BMS_MIN = 1e-2
PRECISION = 5
EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
NEW_FOLDER = "/test_cut_min/"
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
                
        else:
            break                    
    print('No beam in '+ str(last) + ' pixels.')
    return(beam_lost, len(bms))
    
    
def count_steps(x,y):
    # extracts the map size from the unique positions of X e Y
    step_x = np.round(np.diff(np.unique(x*10**PRECISION)).min())/10**PRECISION
    step_y = np.round(np.diff(np.unique(y*10**PRECISION)).min())/10**PRECISION
    
    stx = np.round((x-x.min())/step_x).astype(int)
    sty = np.round((y-y.min())/step_y).astype(int)
    
    shape_x = stx.max()+1
    shape_y = sty.max()+1
    
    return(shape_x,shape_y)
     

def cut_reshape(in_file, out_fold):
    dest_path = out_fold
    new_map = os.path.join( dest_path, in_file.split('.')[0] + NEWNAME_APP)
    
    with h5py.File(in_file, 'r') as f:
    
        move_hor = False
        for run in f.keys():
            print ("Run: %s" %run)
            
            x = f[run+PATH_SCALAR+"/X"][...]
            y = f[run+PATH_SCALAR+"/Y"][...]
            
            # direction of the map: vertical or horizontal?
            if x[1] == x[0]:
                move_hor = True

            shape_x, shape_y = count_steps(x,y)    

            # each pixel has several bms value: checking the minimum only
            bms = f[run+PATH_VECTOR+"/BMS-T"][...]
            bms = bms.min(axis=1)
            beam_lost, valid_pixels = check_bms(bms)
 
            if move_hor:
                col = shape_y
                row = np.round(valid_pixels/shape_y)
                
            else:
                row = shape_x
                col = np.round(valid_pixels/shape_x)
                    
            if valid_pixels < shape_x*shape_y:
                print('Valid pixels =', valid_pixels)
                print('Original map =', shape_x*shape_y)
                
                if move_hor:
                    row = valid_pixels/shape_y
                else:
                    col = valid_pixels/shape_x
                    
            if beam_lost:
                print('Original size:', shape_x, shape_y)
                print('New size:', row, col)
            
            if (row*col==shape_x*shape_y):
                print('This map is ok! Moving on!\n')
                break
                
            with h5py.File(new_map, 'w') as fout:
                total_point = row * col
                # print("Map size: (%d,%d), total point=%d\n" % (row, col, total_point))
                
                print('\n--> Cutting and reshaping TransientVectorData:')
                for vectorData in f[run+PATH_VECTOR].keys():
                    print (vectorData)
                    v = f[run+PATH_VECTOR+"/"+vectorData][...]
                    v = v[0:total_point]
                    v = v.reshape((row,col,v.shape[-1]))
                    # print("New shape: ",v.shape)
                    fout.create_dataset(run+PATH_VECTOR+"/"+vectorData, data=v, compression = "gzip", shuffle=True)
                print('\n--> Done! Now cutting and reshaping TransientScalarData:')
                
                for scalarData in f[run+PATH_SCALAR].keys():
                    print(scalarData)
                    s = f[run+PATH_SCALAR+"/"+scalarData][...]
                    s = s[0:total_point]
                    #print("New shape: ",s.shape)
                    fout.create_dataset(run+PATH_SCALAR+"/"+scalarData, data=s)
  
