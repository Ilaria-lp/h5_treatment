#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This script does 4 things:
# 1) It checks for beam dumps during MAP acquisition. In case BMS is < BMS_MIN, it reshapes the map discarding void pixels.
# 2) It discards half-filled rows/columns in case of incomplete map acquisition.
# 3) It rotates the maps when the acquisition was done "column-first" (moving the vertical motor first).
# 4) It reshapes the maps so that PyMCA already knows how many rows and columns there are in each file.

import glob
import h5py
import itertools
import numpy as np
import os
import sys

from mylib import check_bms, count_steps, orientation

PRECISION = 5
EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
NEW_FOLDER = "/cut-reshaped/"
NEWNAME_APP = "_processed.h5"

def cut_reshape(in_file, out_fold):
    
    with h5py.File(in_file, 'r') as f:
        new_map = os.path.join( out_fold, in_file.split('.h5')[0] + NEWNAME_APP)   
        
        move_ver = False

        for run in f.keys():
            print ("Run: %s" %run)
            
            x = f[run+PATH_SCALAR+"/X"][...]  # at the XRF beamline this is the vertical motor
            y = f[run+PATH_SCALAR+"/Y"][...]  # and this is the horizontal motor
            
            # when X moves first, in order to see the map on PyMCA, the number of 
            # columns to enter is the number of rows. The map will appear rotated.  
            # The following section fixes this issue, inverting X and Y.
            try:
                x, y, move_ver = orientation(x, y)
            except ValueError:
                print('x x x Size not valid for map. Please check file. x x x \n\n\n')
                break

            shape_x, shape_y = count_steps(x), count_steps(y)
            total_points = shape_x * shape_y
            
            print("Original map size: (%d,%d), total point=%d" % (shape_x, shape_y, total_points) )


            # check for beam dump/drift on the BMS signal
            bms = f[run+PATH_SCALAR+"/BMS-T-Average"][...]
            beam_lost, valid_pixels = check_bms(bms)
            
            if valid_pixels == 0:
                print('x x x x x x x No valid pixels, moving on.\n\n\n')
                break

            if move_ver:
                print('VERTICAL MOTOR MOVED FIRST.')
                row = shape_x
                col = np.round(valid_pixels/shape_x)
                new_map = new_map[:-3] + '_rot.h5'
            else:
                print('HORIZONTAL MOTOR MOVED FIRST.')
                col = shape_y
                row = np.round(valid_pixels/shape_y)
                                  
            if valid_pixels < shape_x*shape_y:
                print('Valid pixels =', valid_pixels, 'out of', shape_x*shape_y)
                new_map = new_map[:-3] + '_cut.h5'
                    
            if beam_lost:
                print('Beam dump detected! This map will be cut.')                
                print('Original size:', shape_x, shape_y)
                print('New size:', row, col)
            
            if (row*col==shape_x*shape_y):
                print('This map is ok! No cutting, just reshaping!\n')
                print('Map size:', shape_x, shape_y)

            with h5py.File(new_map, 'w') as fout:
                total_point = row * col
                
                # --> Now reshaping TransientVectorData
                for vectorData in f[run+PATH_VECTOR].keys():

                    v = f[run+PATH_VECTOR+"/"+vectorData][...]
                    v = v[0:total_point]
                    v = v.reshape((row,col,v.shape[-1]))
                    
                    # the rotation of the map is done here:
                    if move_ver:
                       print('Now rotating map here to facilitate data viewing on PyMCA.')
                       v = np.rot90(v, -1, axes=(1,0))
                       print(v.shape)

                    fout.create_dataset(run+PATH_VECTOR+"/"+vectorData, data=v, compression = "gzip", shuffle=True)
                
                # --> Now reshaping TransientScalarData
                for scalarData in f[run+PATH_SCALAR].keys():
                    s = f[run+PATH_SCALAR+"/"+scalarData][...]
                    s = s[0:total_point]
                    if s.shape[0] == total_point:
                        s = s.reshape(row, col)
                    if move_ver:
                        s = np.rot90(s, -1, axes=(1,0))
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
        print("--> Don't worry: overwriting is not an option. ;) \n\n\n")
        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            cut_reshape(filename, out_path)
            print('\n - - - - Map {0}/{1} successfully checked.\n'.format(i+1, len(file_list)))

    print('\n --> Have a nice day!')

if __name__ == "__main__":
    run()