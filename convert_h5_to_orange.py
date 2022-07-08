#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import h5py
import numpy as np
import os
import sys
import time

separator = ' '
DECIMALS = 6
EXT = "h5"
PATH_SCALAR = "/Measurement/TransientScalarData/"
PATH_VECTOR = "/Measurement/TransientVectorData/"
NEW_FOLDER = "/convert/"
BMS_channel = "BMS-3"


def convert(map_name, out_path):
    
    txt_file_name = map_name.split('/')[-1].split('.')
    txt_file_name[-1] = 'txt'
    txt_file = os.path.join( out_path, map_name.split('.')[0] + '.csv')
    

    with h5py.File(map_name, 'r') as f, open(txt_file, 'w') as txt:
        run = f.keys()[0]
        x = f[run+PATH_SCALAR+"X"][...]
        y = f[run+PATH_SCALAR+"Y"][...]
        
        bms = f[run+PATH_VECTOR+BMS_channel][...]
        bms = bms.mean(axis=1)
        
        spectra = f[run+PATH_VECTOR+"SDD#1-Spectra"][...]            
        
        map = zip(x,y,bms)
        
        title_string = '# x, y, bms, spectrum'
        txt.write(title_string)
        
        for i in range(len(x)):
            txt.write('\n{},{},{}'.format(map[i][0],map[i][1],map[i][2]))
            for ch in range(2048):
                txt.write(',{}'.format(spectra[i][ch]))
            

def run():
    print('-------------------------------------------------\n')
    print('---------           Welcome!         ------------\n')
    print("---        Converting maps to csv !           ---\n")
    print('---------    (Orange compatible)    -------------\n')
    
    in_path = './'
    out_path = in_path + NEW_FOLDER
    
    # checks automatically all the h5 files in the in_path 
    file_list = glob.glob('{0}/*'.format(in_path)+EXT)
    print('I found '+str(len(file_list))+' files matching the extension '+EXT)
    print(file_list)
    print('\n')
    
    if len(file_list) == 0:
        print("--> Can't do much with 0 files! Sorry!")
        print("--> Move the maps in the same folder as the program and try again!")
    
    else: 
        print("--> All these files will be converted. \n")
        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            convert(filename, out_path)
            print('\n --> Map {0}/{1} successfully converted.\n'.format(i+1, len(file_list)))


        print('\n --> Have a nice day!')

if __name__ == "__main__":
    run()            