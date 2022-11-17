#!/usr/bin/env python
# -*- coding: utf-8 -*-

import h5py
import numpy as np
import os
import sys
import time

separator = ' '
DECIMALS = 3

def process_hdf_file(file_name, include_motors = False):
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
            bruker_roi_integrals = f['bruker/roiintegrals']
            if len(bruker_roi_integrals.shape) > 1:
                num_rois = bruker_roi_integrals.shape[1]
            elif len(bruker_roi_integrals.shape) == 1:
                num_rois = 1
            else: 
                num_rois = 0
            # print 'num rois', num_rois
            if num_rois >= 1:
                roi_string = ', roi1, a_fluo1'
                roi1 = f['bruker/roi1']
                alfafluo1 = f['postprocessing/alphafluo1']
            if num_rois >= 2:
                roi_string += ', roi2, a_fluo2'
                roi2 = bruker_roi_integrals[:,1]
                alfafluo2 = f['postprocessing/alphafluo2']
            if num_rois >= 3:
                roi_string += ', roi3, a_fluo3'
                roi3 = bruker_roi_integrals[:,2]
                alfafluo3 = f['postprocessing/alphafluo3']
            if num_rois == 4:
                roi_string += ', roi4, a_fluo4'
                roi4 = bruker_roi_integrals[:,3]
                alfafluo4 = f['postprocessing/alphafluo4']
            title_string += roi_string
            title_string += ', deadtime (%)'
            got_bruker = True
            acq_time = f['bruker/acquisitiontime'][()]
            deadtime = []
            for i in range(len(triggers)):
                deadtime.append( (acq_time - f['bruker/livetime'][i]) / acq_time * 100)
            if np.amax(deadtime) > 10:
                print ('Max deadtime exceeded 10%! Inspect data with care!\n')
            else:
                print ('Deadtime <10% in the whole dataset.')
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
                data_line = separator.join([data_line, str(np.round(keithley[i], DECIMALS)), str(alphatrans[i])])
            if got_bruker:
                if num_rois >= 1:
                    data_line = separator.join([data_line, str(roi1[i]), str(alfafluo1[i])])
                if num_rois >= 2:
                    data_line = separator.join([data_line, str(roi2[i]), str(alfafluo2[i])])
                if num_rois >= 3:
                    data_line = separator.join([data_line, str(roi3[i]), str(alfafluo3[i])])
                if num_rois == 4:
                    data_line = separator.join([data_line, str(roi4[i]), str(alfafluo4[i])])
                data_line = separator.join([data_line, str(deadtime[i])])
            tf.write(data_line + '\n')
        print 'Saved file', target_file

        
if __name__ == "__main__":
    #usage: ./sys.argv[0] path_of_file
    try:
        include_motors = False
        name_file = sys.argv[1]
        if len(sys.argv) == 3:
            include_motors = eval(sys.argv[2])
        process_hdf_file(name_file, include_motors)
    except Exception as e:
        # print e.message
        print 'Which file?'
    
        