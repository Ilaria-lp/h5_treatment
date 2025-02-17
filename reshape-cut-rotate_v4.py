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
import numpy as np
import os

from h5_map_handling import check_bms, count_steps, orientation

EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
POSITIONERS = "/Measurement/Positioners"
NEW_FOLDER = "/cut-reshaped/"
NEWNAME_APP = "_reshaped.h5"
I0_MONITOR = "/BMS-T-Average" 

def cut_reshape(in_file, out_fold):
    
    with h5py.File(in_file, 'r') as f:
        move_ver = False

        for run in f.keys():
            sample_name = run[19:]
            print(run)
            date_acq = datetime.strptime(run[3:17], '%Y%m%d %H%M%S')           
            new_map = './'+ NEW_FOLDER + sample_name + date_acq.strftime('_%Y-%m-%d_%H-%M-%S')
    
            print ("Sample_name: %s." %sample_name)
            print date_acq.strftime('\tAcquisition time: %d/%m/%Y - %H:%M.')
            
            try:                
                x = f[run+PATH_SCALAR+"/X"][...]
                y = f[run+PATH_SCALAR+"/Y"][...]
            except KeyError:
                print('\tx x x x x x x x x WARNING x x x x x x x x x')
                print('\tx  HOR/VER movement not found! Moving on! x')
                print('\tx x x x x x x x x x x x x x x x x x x x x x\n')
                break
            
        # when X moves first, in order to see the map on PyMCA, the number of 
        # columns to enter is the number of rows. The map will appear rotated.  
        # The following section fixes this issue. The output file will be shown 
        # in the correct orientation on PyMCA.
            try:
                x, y, move_ver = orientation(x, y)
            except ValueError:
                print('\tx x x x x x x x x x x x x x x x x x x x x x x x')
                print('\tx  Size not valid for map. Please check file. x ')
                print('\tx x x x x x x x x x x x x x x x x x x x x x x x\n')
                break

            shape_x, shape_y = count_steps(x), count_steps(y)
            total_points = shape_x * shape_y
            
            print("\tOriginal map shape: (%d, %d), points = %d." %(shape_x, shape_y, total_points) )

            # check for beam dump on the BMS signal
            bms = f[run+PATH_SCALAR+I0_MONITOR][...]
            beam_lost, valid_pixels = check_bms(bms)
            
            if valid_pixels == 0:
                print('\tx x x x x x x x x x x x x x x x')
                print('\tx No valid pixels, moving on. x')
                print('\tx x x x x x x x x x x x x x x x\n')
                break

            if move_ver:
                row = shape_x
                col = np.round(valid_pixels/shape_x)
                new_map += '_rot.h5'
            else:
                col = shape_y
                row = np.round(valid_pixels/shape_y)
                                  
            if valid_pixels < shape_x*shape_y:
                print('    !\tValid pixels = %s out of %s' %(valid_pixels, shape_x*shape_y))
                if not beam_lost:
                    print('\tIncomplete map collection found.')
                print('\tNew map shape: (%d, %d)' %(row, col))
                new_map += '_cut.h5'           

            if (row*col==shape_x*shape_y):
                print('\tNo cutting, just reshaping.\n')
                print('\tNew map shape: (%d, %d)' %(row, col))
                new_map += '.h5'                              

            with h5py.File(new_map, 'w') as fout:
                total_point = row * col
                
                # Reshaping TransientVectorData
                for vectorData in f[run+PATH_VECTOR].keys():

                    v = f[run+PATH_VECTOR+"/"+vectorData][...]
                    v = v[0:total_point]
                    v = v.reshape((row,col,v.shape[-1]))
                    
                    # the rotation of the map is done here:
                    if move_ver:
                       v = np.rot90(v, -1, axes=(1,0))

                    fout.create_dataset(run+PATH_VECTOR+"/"+vectorData, data=v, compression = "gzip", shuffle=True)

                # Reshaping TransientScalarData:')
                for scalarData in f[run+PATH_SCALAR].keys():
                    s = f[run+PATH_SCALAR+"/"+scalarData][...]
                    s = s[0:total_point]
                    if s.shape[0] == total_point:
                        s = s.reshape(row, col)
                    if move_ver:
                        s = np.rot90(s, -1, axes=(1,0))

                    fout.create_dataset(run+PATH_SCALAR+"/"+scalarData, data=s)

                # Reshaping Positioners (i.e. motor position before map collection)
                for motor_position in f[run+POSITIONERS].keys():
                    p = f[run+POSITIONERS+"/"+motor_position][...]
                    p = p[0:total_point]
                    if p.shape[0] == total_point:
                        p = p.reshape(row, col)
                    if move_ver:
                        s = np.rot90(s, -1, axes=(1,0))

                    fout.create_dataset(run+POSITIONERS+"/"+motor_position, data=p)


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

    print('Have a nice day.\n')

if __name__ == "__main__":
    run()
