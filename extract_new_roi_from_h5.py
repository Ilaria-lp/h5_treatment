#!/usr/bin/env python
# -*- coding: utf-8 -*-

import h5py
import numpy as np
import os
import sys
import time

separator = ' '
DECIMALS = 3

def process_hdf_file(file_name, roi, include_motors = False):
    src_file = file_name
    target_file_name = file_name.split('/')[-1].split('.')
    target_file_name[-1] = 'txt'
    target_file = '.'.join(target_file_name)

    with h5py.File(src_file, 'r') as f, open(target_file, 'w') as tf:
        triggers = f['triggers']
        energy = f['monomoto/energy']
        title_string = '# energy'
        if include_motors:
            angle = f['monomoto/incidenceangle']
            motorpos = f['monomoto/incidencemotor']
            separation = f['monomoto/crystalseparation']
            title_string += ', inc_motor, separation, inc_angle' 
        bms = f['bms/current']
        bms_bkg = f['bms/background']
        title_string += ', bms'
        try:
            if f['bms/bms_secondary_channel'] > 0 and\
                f['bms/bms_secondary_channel'] != f['bms/bms_channel']:
                bms_2nd = f['bms/2nd_current']
                got_2nd = True
                title_string += ', 2nd_ch'
            else:
                got_2nd = False
        except:
            got_2nd = False
        try:
            keithley = f['keithley/current']
            alphatrans = f['postprocessing/alphatrans']
            title_string += ', diode, a_trans'
            got_keithley = True
        except Exception as e:
            # print 'Keithley error:', e.message
            got_keithley = False
        # print 'got_keithley', got_keithley
        try:                      
            roi_string = ', roi_new, a_fluo_new'                    
            array_new = np.array(f['bruker/spectrum'])
            roi_new = []
            alfafluo_new = []            
            for point in range(len(triggers)):
                roi_new.append( np.sum(array_new[point][roi[0]:roi[1]+1]) )
                alfafluo_new.append( roi_new [point] / bms[point])
            
            title_string += roi_string
            got_bruker = True
        except Exception as e:
            got_bruker = False
            # print 'Bruker error:', e.message
        title_string += '\n'

        tf.write(title_string)
        for i in range(len(triggers)):
            data_line =  str(energy[i])
            if include_motors:        
                data_line = separator.join([data_line, str(motorpos[i]), 
                    str(separation[i]), str(angle[i])])
            data_line = separator.join([data_line, str(np.round(bms[i], DECIMALS))]) 
            if got_2nd:
                data_line = separator.join([data_line, str(np.round(bms_2nd[i], DECIMALS))]) 
            if got_keithley:
                data_line = separator.join([data_line, str(np.round(keithley[i], DECIMALS)), str(np.round(alphatrans[i], DECIMALS))])
            if got_bruker:
                data_line = separator.join([data_line, str(roi_new[i]), str(np.round(alfafluo_new[i],DECIMALS))])
            tf.write(data_line + '\n')
        print 'Saved file', target_file

        
if __name__ == "__main__":
    #usage: ./sys.argv[0] path_of_file
    new_roi = input('First and last channel of the new ROI? [min, max]\n' )   
    try:
        include_motors = False
        name_file = sys.argv[1]
        if len(sys.argv) == 3:
            include_motors = eval(sys.argv[2])
        process_hdf_file(name_file, new_roi, include_motors)
    except Exception as e:
        # print e.message
        print 'Which file?'
    
        