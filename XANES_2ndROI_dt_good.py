#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import h5py
import itertools
import numpy as np
import os
import sys
import time

NEW_FOLDER = '/2nd_Roi/'
EXT = 'h5'

# first couple = Fe or Co ROI, second couple = ROI for self abs correction
Fe_roi = [600,644,263,286]
Co_roi = [660,700,600,644]

separator = ' '

def process_hdf_file(file_name, out_path, include_motors = False):
    src_file = file_name
    deadtime_high = False

    with h5py.File(src_file, 'r') as f:
        points = len(f['triggers'])
        energy = np.array(f['monomoto/energy'])
        title_string = '# energy'

#    post-processing for xsw in phi
        try:
            phi = np.array(f['xsw/phi'])
            got_phi = True
            title_string += ', phi'
            print('Moving phi: in-plane XSW detected.')
        except (KeyError):
            got_phi = False  

#    post-processing for xsw in theta
        try:
            theta = np.array(f['xsw/theta'])
            got_theta = True
            title_string += ', theta'
            print('Moving theta: out-of-plane XSW detected.')
        except KeyError:
            got_theta = False  

        if include_motors:
            angle = np.array(f['monomoto/incidenceangle'])
            motorpos = np.array(f['monomoto/incidencemotor'])
            separation = np.array(f['monomoto/crystalseparation'])
            title_string += ', inc_motor, separation, inc_angle' 
        
        try: 
            bms = np.array(f['bms/current'])
            title_string += ', i0'
        except KeyError:
            print('\n\n\n >>>> Could not find BMS data!!<<<< \n\n\n')
            return None
            
        try:
            if f['bms/bms_secondary_channel'] > 0 and\
                f['bms/bms_secondary_channel'] != f['bms/bms_channel']:
                bms_2nd = np.array(f['bms/2nd_current'])
                got_2nd = True
                title_string += ', 2nd_ch'
            else:
                got_2nd = False
        except:
            got_2nd = False

        try:
            keithley = np.array(f['keithley/current'])
            alphatrans = np.array(f['postprocessing/alphatrans'])
            title_string += ', a_trans'
            got_keithley = True
        except Exception as e:
            got_keithley = False
            
        try:                                
            array_new = np.array(f['sirius3/sum_spectrum'])
            got_fluo = True

            counts_roi1 = []
            counts_selfabs = []
            alfafluo_roi1 = []            
            alfafluo_selfabs = []

            if 'Co' in src_file:
                Roi = Co_roi
                roi_string = ', a_fluo_Co, a_fluo_Fe(SelfAbsCorr)'         
            elif 'Fe' in src_file:
                Roi = Fe_roi
                roi_string = ', a_fluo_Fe, a_fluo_(SelfAbsCorr)'         
            else:
                print('- - - - Co or Fe edge not detected from filename!!! - - -')

            for i in range(points):
                counts_roi1.append( np.sum(array_new[i][Roi[0]:Roi[1]+1]) )
                counts_selfabs.append( np.sum(array_new[i][Roi[2]:Roi[3]+1]) )

                alfafluo_roi1.append( counts_roi1[i] / bms[i])
                alfafluo_selfabs.append( counts_selfabs [i] / bms[i])
            
            title_string += roi_string

        ########  DEADTIME CHECK ########################

            deadtime_u = np.array(f['sirius3/up_deadtimepct'])
            deadtime_u = np.round(deadtime_u,1)
            deadtime_m = np.array(f['sirius3/mid_deadtimepct'])
            deadtime_m = np.round(deadtime_m,1)
            deadtime_d = np.array(f['sirius3/down_deadtimepct'])
            deadtime_d = np.round(deadtime_d,1)

            deadtime_max = np.amax([deadtime_u, deadtime_m, deadtime_d])
                      
            if deadtime_max > 10:
                deadtime_high = True
                title_string += ', dt_u (%), dt_m (%), dt_d (%)\n'
                title_string += '# watch out for the deadtime (dt)!!'

                print('! ! ! ! ! ! ! ! ! ! ! ! ! !')
                print('! !  deadtime alarm ! ! ! !')
                print('! ! ! ! ! ! ! ! ! ! ! ! ! !')              

        ################################################

        except Exception as e:
            got_fluo = False
            print 'Bruker/Sirius error:', e.message

        title_string += '\n'

    # adding a warning string to the filename
        target_file_name = file_name.split('/')[-1].split('.')
        if deadtime_high:
            target_file_name[0] += '_CHECK_DEADTIME'
        target_file_name[-1] = 'txt'
        target_file = '.'.join(target_file_name)
        target_file = out_path + target_file

    # opening target file
        with open(target_file, 'w') as tf:

            tf.write(title_string)
            for i in range(points):
                data_line =  str(energy[i])
                if got_phi:
                        data_line = separator.join([data_line, str(np.round(phi[i], 4))]) 
                if got_theta:
                        data_line = separator.join([data_line, str(np.round(theta[i],   4))]) 
                if include_motors:        
                    data_line = separator.join([data_line, str(motorpos[i]), 
                        str(separation[i]), str(angle[i])])
                data_line = separator.join([data_line, str(np.round(bms[i], 4))]) 
                if got_2nd:
                    data_line = separator.join([data_line, str(np.round(bms_2nd[i], 2))]) 
                if got_keithley:
                    data_line = separator.join([data_line, str(np.round(alphatrans[i], 4))])
                if got_fluo:
                    data_line = separator.join([data_line, str(np.round(alfafluo_roi1[i],0))])
                    data_line = separator.join([data_line, str(np.round(alfafluo_selfabs[i],0))])
                if deadtime_high:
                   data_line = separator.join([data_line, str(deadtime_u[i]), str(deadtime_m[i]), str(deadtime_d[i])])

                tf.write(data_line + '\n')
            print ('Saved file', target_file)

        
if __name__ == "__main__":

    print('-------------------------------------------------\n')
    print('---------           Welcome!         ------------\n')
    print("---     Let's post-process your data!         ---\n")
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
        print("--> Move the h5files in the same folder as the program and try again!")
    
    else: 
        print("--> All these files will be post-processed. \n")
        print("--> Don't worry: overwriting is not an option. ;)")

        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            print(filename)
            include_motors = False
            process_hdf_file(filename, out_path, include_motors)

            print('\n --> Data {0}/{1} successfully processed.\n'.format(i+1, len(file_list)))

    print('\n --> Have a nice day!')