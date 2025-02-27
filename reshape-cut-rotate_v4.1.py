#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This script does 4 things:
# 1) It checks for beam dumps during MAP acquisition
#   In case BMS is < BMS_MIN, it reshapes the map discarding void pixels
# 2) It discards half-filled rows/columns in case of manual interruption of the map
# 3) rotates the maps when the acquisition was done "column-first"
# 4) reshapes the maps so that PyMCA already knows how many columns and rows there are in each file

from datetime import datetime
import glob
import h5py
import math
import numpy as np
import os

from h5_map_handling import check_bms, count_steps, orientation, warning

EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
POSITIONERS = "/Measurement/Positioners"
NEW_FOLDER = "/cut-reshaped/"
I0_MONITOR = "/BMS-T-Average"

# The motor positions copied to the output file are the following:
AcceptedList = ['BMS-3-Average','DIODE-Average','X','Y','Z']
# aggiungi LiveTime!

def cut_reshape(in_file, out_fold):
    
    f = h5py.File(in_file, 'r')
    move_ver = False
    comment_line = 'This file has been generated with the script reshape-cut-rotate_V4.1.\n'
    
    for run in f.keys():
        date_str = 'Run%Y%m%d %H%M%S'
        # the first part of the string contains date and time of acquisition
        date_acq = datetime.strptime(run[:18], date_str)     
        # the rest of the string is the sample_name
        sample_name = run[19:]
        new_map = './'+ NEW_FOLDER + sample_name + date_acq.strftime('_%Y-%m-%d_%H-%M-%S')
    
        print("Sample_name: %s." %sample_name)
        print(date_acq.strftime('\tAcquisition time: %d/%m/%Y - %H:%M:%S.'))
        
        try:                
            x = np.array(f[run+PATH_SCALAR+"/X"][...])
            y = np.array(f[run+PATH_SCALAR+"/Y"][...])
        except KeyError:
            warning('HOR/VER movement not found! Moving on!')
            break
        
    # when X moves first, in order to see the map on PyMCA, the number of 
    # columns to enter is the number of rows. The map will appear rotated.  
    # The following section fixes this issue. The output file will be shown 
    # in the correct orientation on PyMCA.
        if len(x)==1 or len(y)==1:        
            warning('This does not look like a map: is it a linear scan?')
            break
        if len(np.shape(x)) == 2:
            warning('This maps seems to be 2D...no need for reshaping. Moving on!')
            break
        elif len(np.shape(x)) > 2 or len(np.shape(y)) >2:
            warning('This maps seems to be have >2 dimensions. Moving on!')
            break        
        try:
            x, y, move_ver = orientation(x, y)            
        except ValueError:
            break

        shape_x, shape_y = count_steps(x), count_steps(y)
        tot_points_raw = shape_x * shape_y

        print("\tOriginal map shape: (%d, %d), points = %d." %(shape_x, shape_y, tot_points_raw) )

        # check for beam dump on the BMS signal (i0)
        bms = np.array(f[run+PATH_SCALAR+I0_MONITOR][...])
        beam_lost, valid_pixels, comment_line = check_bms(bms, comment_line)
        
        if valid_pixels == 0:
            warning('No valid pixels, moving on.')
            break

        if move_ver:
            row = shape_x
            col = math.floor(valid_pixels/shape_x)
            new_map += '_rot'
            comment_line += 'This map has been rotated.\n'
        else:
            col = shape_y
            row = math.floor(valid_pixels/shape_y)
                              
        if valid_pixels < shape_x*shape_y:
            print('    !\tValid pixels = %s out of %s' %(valid_pixels, shape_x*shape_y))
            if not beam_lost:
                print('\tIncomplete map collection found.')
                comment_line += 'Incomplete acquisition found. The original map was cut to have a rectangular shape.'
            print('\tNew map shape: (%d, %d)' %(row, col))
            new_map += '_cut'           

        if (row*col==shape_x*shape_y):
            print('\tNo cutting, just reshaping.\n')
            comment_line += 'This map was not cut. Only reshaping has been done.'
            print('\tNew map shape: (%d, %d)' %(row, col))
            
        new_map += '.h5'                              
        fout =  h5py.File(new_map, 'w')
        final_points = row * col
        
        fout.create_dataset("Comments", data=comment_line)
 
        # Reshaping TransientVectorData
        for vectorData in f[run+PATH_VECTOR].keys():
            v = f[run+PATH_VECTOR+"/"+vectorData][...]
            v = v[0:final_points]
            v = v.reshape(row,col,v.shape[-1])                   
            # the rotation of the map is done here:
            if move_ver:
               v = np.rot90(v, -1, axes=(1,0))
 
            fout.create_dataset(run+"/Detector_data/"+vectorData, data=v, compression = "gzip", shuffle=True)
 
        # Reshaping TransientScalarData:')
        for scalarData in f[run+PATH_SCALAR].keys():
            if scalarData in AcceptedList or scalarData.endswith('LiveTime'):                
                s = f[run+PATH_SCALAR+"/"+scalarData][...]
                s = s[0:final_points]
                if s.shape[0] == final_points:
                    s = s.reshape(row, col)
                
                if move_ver:
                    s = np.rot90(s, -1, axes=(1,0))
                
                fout.create_dataset(run+"/Motor_positions/"+scalarData, data=s)
 
        # Reshaping Positioners (i.e. motor position before map collection)
        for motor_position in f[run+POSITIONERS].keys():
            p = f[run+POSITIONERS+"/"+motor_position][...]                   
            fout.create_dataset(run+"/Starting_positions/"+motor_position, data=p)


####################################################################

def run():
    print('\n')
    print('\t-------------------------------------------------\n')
    print('\t---------           Welcome!         ------------\n')
    print("\t---        Let's cut your XRF maps!           ---\n")
    print('\t-------------------------------------------------\n')
    
    in_path = './'
    out_path = in_path + NEW_FOLDER
    # if out_path is read only, uncomment next line
    # out_path = str(input('Where do you want to save the reshaped maps?' ))
    
    # checks automatically all the h5 files in the in_path 
    file_list = glob.glob('{0}/*'.format(in_path)+EXT)
    print('I found '+str(len(file_list))+' files matching the extension '+EXT+':')
    print(file_list)
    print('\n')
    
    if len(file_list) == 0:
        print("\t-> Can't do much with 0 files! Sorry!")
        print("\t-> Move the maps in the same folder as the program and try again!")   
    else: 
        print("\t-> All the files mentioned above will be cut and reshaped.")
        print("\t-> Don't worry: overwriting raw data is not an option. ;) \n")        

        if not os.path.exists(out_path):
            os.makedirs(out_path)        

        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            cut_reshape(filename, out_path)
            print('\n- - - - Map {0}/{1} successfully processed.\n'.format(i+1, len(file_list)))

    print('\tHave a nice day.\n')

if __name__ == "__main__":
    run()
