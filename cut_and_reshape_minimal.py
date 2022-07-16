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

from mylib import count_steps, check_bms


BMS_MIN = 1e-2
PRECISION = 5
EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
NEW_FOLDER = "/test_cut_min/"
NEWNAME_APP = "_cut.h5"

def cut_reshape(in_file, out_fold):
    new_map = os.path.join( out_fold, in_file.split('.')[0] + NEWNAME_APP)
    
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
    
                


####################################################################

def run():
    print('-------------------------------------------------\n')
    print('---------           Welcome!         ------------\n')
    print("---        Let's cut your XRF maps!           ---\n")
    print('-------------------------------------------------\n')
    
    in_path = './'
    out_path = in_path + NEW_FOLDER
    # if out_path is read only, uncomment next line
    # out_path = str(input('Where do you want to save the reshaped maps?' ))
    
    # checks automatically all the h5 files in the in_path 
    file_list = glob.glob('{0}/*'.format(in_path)+EXT)
    print('I found '+str(len(file_list))+' files matching the extension '+EXT)
    print(file_list)
    print('\n')
    
    if len(file_list) == 0:
        print("--> Can't do much with 0 files! Sorry!")
        print("--> Move the maps in the same folder as the program and try again!")
    
    else: 
        print("--> All these files will be cut and reshaped. \n")
        print("--> Don't worry: overwriting is not an option. ;)")
        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            cut_reshape(filename, out_path)
            print('\n --> Map {0}/{1} successfully checked.\n'.format(i+1, len(file_list)))

    print('\n --> Have a nice day!')

if __name__ == "__main__":
    run()
