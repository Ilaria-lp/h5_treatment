#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import h5py
import math
import numpy as np


BMS_MIN = 1e-4
PRECISION = 10**5
PATH_SCALAR = "/Measurement/TransientScalarData"


def _calculate_new_shape(shape_x, shape_y, valid_pixels, move_ver, new_name, comment):
    if move_ver:
        row = shape_x
        col = math.floor(valid_pixels/shape_x)
        new_name += '_rot'
        comment += 'This map has been rotated.\n'
    else:
        col = shape_y
        row = math.floor(valid_pixels/shape_y)
                          
    if valid_pixels < shape_x*shape_y:
        print('    !\tValid pixels = %s out of %s' %(valid_pixels, shape_x*shape_y))
        if not beam_lost:
            print('\tIncomplete map collection found.')
            comment += 'Incomplete acquisition found. The original map was cut to have a rectangular shape.'
        print('\tNew map shape: (%d, %d)' %(row, col))
        new_name += '_cut'           

    if (row*col==shape_x*shape_y):
        print('\tNo cutting, just reshaping.')
        comment += 'This map was not cut. Only reshaping has been done.'
        print('\tNew map shape: (%d, %d)' %(row, col))
    
    return row, col, new_name, comment

def check_bms(bms, comment_line):
    beam_lost = False
            
    if bms.min() > BMS_MIN:
        print("\tNo beam dumps detected.")
        return (beam_lost, len(bms), comment_line)
        # if all the pixels are valid, it ends here.
        
    for last in range(len(bms)):
        if bms[::-1][0] < BMS_MIN:
            bms = bms[:len(bms)-1]
            beam_lost = True
        else:
            print('\tLast useful I0 value = %f' %(bms[::-1][0]))
            print('\tI0 at start = %f' %(bms[::1][0]))
            break                    
    print('  > > > Beam dump/drift: no beam in %d pixels.' %(last+1))
    
    if len(bms) == 0:
        warning('No valid pixels, moving on.')
        raise ValueError
    
    comment_line += 'The original map was cut until the last completed row/column.\n'
    return(beam_lost, len(bms), comment_line)

# gives the shape of the array by counting the numbers of different values    
def count_steps(x):
    step_x = np.round(np.diff(np.unique(x*PRECISION)).min())/PRECISION 
    stx = np.round((x-x.min())/step_x).astype(int)  
    shape_x = stx.max()+1
    return(shape_x)

def get_data(h5file, path):
    info = np.array(h5file[path][...])
    return info

# flipping has to be implemented yet! An idea could be starting from the following
def _descending(j):
    if (j[0]>j[-1]):
        to_be_flipped = True
    else:
        pass

def get_name_and_date(h5file):
    key = list(h5file.keys())[0]
    date_str = 'Run%Y%m%d %H%M%S'
    # the first part of the string contains date and time of acquisition
    date_acq = datetime.strptime(key[:18], date_str)     
    # the rest of the string is the sample_name
    sample_name = key[19:]
    return key, sample_name, date_acq

# When the vertical motor moves first, the map is collected filling column after column. 
# When PyMCA will try to resize the array of XRF data, the correct image will be shown only entering the cols and rows values swapped.
# The map will have the correct position of the pixel with respect to one another, but it will appear rotated by 90deg counterclockwise.
# The function takes the array of the x and y positions, and returns them swapped when the vertical motor is moved first. And it returns a flag used for the 90deg clockwise rotation needed to bring the map orientation back to normal. 
def orientation(ver,hor):
    move_ver_first = False
 
    if (ver[1]!=ver[0]) and (hor[1]==hor[0]):
        print('\tX (VER) moved first: the map will be rotated to fix data visualization on PyMCA.')      
        move_ver_first = True
        ver, hor = hor, ver        
        return ver, hor, move_ver_first
     
    # when the horizontal motor moves first, no need to swap rows and columns.
    # this is the most common situation, where no further action is needed.
    elif (hor[1]!=hor[0]) and (ver[1]==ver[0]):
        return ver, hor, move_ver_first
    # if both motors are moved or if none moves, then the map is somewhat broken.
    else:
        warning('\tThe two axes moved together!\nIs this a diagonal linear scan?')
        raise ValueError


def read_positions(h5file, path):
    x = np.array(h5file[path+"/X"][...])
    y = np.array(h5file[path+"/Y"][...])
    if len(x)==1 or len(y)==1:        
        warning('This does not look like a map:\nis it a linear scan?')
        raise TypeError
    elif len(np.shape(x)) == 2:
        warning('This maps seems to be 2D...no need for reshaping.\nMoving on!')
        raise TypeError
    elif len(np.shape(x)) > 2 or len(np.shape(y)) >2:
        warning('This maps seems to be have >2 dimensions.\nMoving on!')
        raise TypeError
    return x,y


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




def _write_vector_to_h5(v, row, col, rotate, fout):
    v = v[0:len]
    v = v.reshape(row,col,v.shape[-1])                   
    # the rotation of the map is done here:
    if rotate:
       v = np.rot90(v, -1, axes=(1,0))

    fout.create_dataset(key+"/Detector_data/"+vectorData, data=v, compression = "gzip", shuffle=True)
