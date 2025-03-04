#!/usr/bin/env python

# -*- coding: utf-8 -*-
__author__      = "Ilaria Carlomagno"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "ilaria.carlomagno@elettra.eu"

#This script:
# 1) Creates a txt file containing the total XRF emission over the whole energy range of the energy scan (XAS spectrum) NORMALISED TO THE I0
# 2) Saves the output files in a dedicated directory

import glob
import h5py
import numpy as np
import os

EXT = "h5"
PATH_I0 = "/Measurement/TransientScalarData/BMS-3-Average"
PATH_FLUO = "/Measurement/TransientVectorData/SIRIUS3-SUM-Spectrum"
NEW_FOLDER = "/cumulative_spectra/"
NEWNAME_APP = "_cumulative.txt"

def extract_xrf_spectrum(in_file, out_fold):
    
    with h5py.File(in_file, 'r') as f:
        for key in f.keys():
            # read XRF spectra of each point
            fluo_sum = f[key+PATH_FLUO][...]
            i0 = f[key+PATH_I0][...]
            cumulative_spectrum = np.sum(fluo_sum, axis = 0)   
            print(np.shape(cumulative_spectrum)
        
    xrf_file = os.path.join( out_fold, in_file.split('.h5')[0] + NEWNAME_APP)  
        
    with open(xrf_file, "w") as f_w:
        for i in range(len(cumulative_spectrum)):
            f_w.write(str(i) + "\t" + str(cumulative_spectrum[i]/i0[i]) + "\n") 


####################################################################

def run():
    print('---------------------------------------------------\n')
    print('---------             Welcome!         ------------\n')
    print("---  Let's extract your XRF cumulative spectra! ---\n")
    print('---------------------------------------------------\n')
    
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
        print("--> All these files will be analysed. \n")
        print("--> XRF spectra will be saved in a new folder. \n\n\n")
        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            extract_xrf_spectrum(filename, out_path)
            print('\n - - - - Map {0}/{1} successfully checked.\n'.format(i+1, len(file_list)))

    print('\n --> Have a nice day!')

if __name__ == "__main__":
    run()
