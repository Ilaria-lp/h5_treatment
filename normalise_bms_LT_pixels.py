#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__      = "Ilaria Carlomagno"
__license__ = "MIT"
__version__ = "7.0"
__email__ = "ilaria.carlomagno@elettra.eu"

# This script does these things:
# 1) Finds the sample name in the hdf file
# 2) Reads the XRF spectra in each hdf5 file
# 3) Normalises each spectra by the LiveTime of the fluo detector, by the i0 and pixel number
# 4) Calculates the cumulative spectrum and writes it to a txt file

from datetime import datetime
import glob
import h5py
import numpy as np
import os

EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData"
PATH_VECTOR = "/Measurement/TransientVectorData"
NEW_FOLDER = "/normalised/"
I0_MONITOR = "/BMS-3-Average/"
LIVETIME = "/SDD#1-LiveTime/"
DATA_PATH = "/SDD#1-Spectra/"


def get_name_and_date(h5file):
    key = list(h5file.keys())[0]
    date_str = 'Run%Y%m%d %H%M%S'
    # the first part of the string contains date and time of acquisition
    date_acq = datetime.strptime(key[:18], date_str)     
    # the rest of the string is the sample_name
    sample_name = key[19:]
    return key, sample_name, date_acq

def normalise_to_livetime(h5file, run):
    livetime = np.array(h5file[run+PATH_SCALAR+LIVETIME][...])
    livetime = livetime.reshape(-1,1)
    
    norm_data = np.array(h5file[run+PATH_VECTOR+DATA_PATH][...])
    norm_data = np.divide(norm_data, livetime)
   
    return norm_data  
    

def norm_bms_and_sum(h5file, data, run):
    i0 = np.array(h5file[run+PATH_SCALAR+I0_MONITOR][...])
    i0 = i0.reshape(-1,1)
    norm_data = np.divide(data, i0)

    #now normalising to the pixels number
    pixels = np.shape(data)[0]
    norm_data = np.sum(norm_data, axis=0)
    norm_data /= pixels

    return norm_data


def warning(message, indent = 1, width = None, title = None):
    indent = 2
    lines = message.split('\n')
    space = ' ' * indent
    if not width:
        width = max(map(len, lines)) 
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)

############################################### main method

def normalise_h5(in_file, out_fold):
    
    f = h5py.File(in_file, 'r')
    move_ver = False
    comment_line = '#This file has been generated with the script to normalise by the i0, LiveTime and pixels number.\n'      
    today = datetime.today().date()
    comment_line += today.strftime('#The original file was processed on: %d/%m/%Y.\n')

    run, sample_name, date_acq = get_name_and_date(f)

    sum_norm_txt = './'+ NEW_FOLDER + sample_name
    sum_norm_txt += '_cumulative_norm.txt'                              
    fout =  open(sum_norm_txt, 'w')
    
    fout.write(comment_line)
    print('\tNormalising your data to the LiveTime of the fluo detector.')
    norm_spec = normalise_to_livetime(f, run)
    
    print('\tNormalising your data to the i0 and pixel number.')
    norm_spec = norm_bms_and_sum(f, norm_spec, run)
   
    fout.write('#Normalised fluo counts\n')
    for i in range(len(norm_spec)):
        fluo_i = "{:.3E}".format(norm_spec[i])
        fout.write(fluo_i+'\n')
    
    fout.close()
    f.close()
    
####################################################################

def run():
    print('\n')
    print('\t-------------------------------------------------\n')
    print('\t---------           Welcome!         ------------\n')
    print("\t---     Let's calculate the cumulative        ---\n")
    print("\t---      spectrum from your XRF maps!         ---\n")
    print('\t-------------------------------------------------\n')
    
    in_path = './'
    out_path = in_path + NEW_FOLDER
    # if out_path is read only, uncomment next line
    # out_path = str(input('Where do you want to save the reshaped maps?' ))
    
    # checks automatically all the h5 files in the in_path 
    file_list = glob.glob('{0}/*'.format(in_path)+EXT)
    print('\tI found '+str(len(file_list))+' files matching the extension '+EXT+':')
    print('\t'+str(file_list))
    print('\n')
    
    if len(file_list) == 0:
        print("\t⚠ Can't do much with 0 files! Sorry!")
        print("\tMove the maps in the same folder as the program and try again!")   
    else: 
        print("\tAll the files mentioned above will be reshaped (and cut, if needed).")
        print("\t☆ Don't worry: overwriting raw data is not an option. ☆ \n")        

        if not os.path.exists(out_path):
            os.makedirs(out_path)        

        for filename, i in zip(file_list, range(len(file_list))):
            print('\tOpening file:',filename)
            filename = filename[2:]
            normalise_h5(filename, out_path)
            print('\n- - - - Spectrum {0}/{1} successfully extracted.\n'.format(i+1, len(file_list)))

    print('\t ☆ Have a nice day ☆ \n')

if __name__ == "__main__":
    run()
