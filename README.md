# h5_treatment
Scripts for data manipulation and format conversion of h5 files generated at the XRF beamline - Elettra Synchrotron  
Maps to be checked/cut and executable must be in the same folder.

- **Linux environment**  
You can run the scripts from the terminal and follow the progress of the data handling: just type ```python name-of-the-script.py```  
Alternatively, you can double click on the icon and wait for it to run: new files will be saved in a subfolder.

- **Windows environment**  
Make sure you have **python 3** installed and that you have the python packages h5py and numpy installed, then double click on the icon.

## reshape_XRF-MAPS 
The XRF maps produced at the XRF beamline (h5 files) have to be manually reshaped when imported in PyMCA - ROI imaging tool.  
This means that you have to know how many columns/rows are there in your image, otherwise the map will look "bad" or will not make sense (in the best case) or artefacts may appear (worst case, because you don't realise what happened!).  

To solve this issue, you can use a python script to reshape the h5 map. The script will create a copy (you won't lose any data!) of your files into a subfolder named "reshaped".

The new files can be automatically opened by PyMCA in the right (row,column) format.

## cut_XRF-MAPS
Fix incomplete data collection (due to beam dumps or manual interruption) and makes a new file discarding the non-valid pixels

## cut_and_reshape_XRF-MAPS
Fixes incomplete data collection (due to beam dumps or manual interruption) and makes a new file discarding the non-valid pixels.  
New files are reshaped so that you don't need to input rows and columns in ROI imaging tool (PyMCA software)

## convert_h5_to_orange
Fix compatibility issues with Orange software.  
Saves a ```.csv``` file with the X and Y coordinates, the I0 (bms), and the channels of the fluorescence detector.


--> Further documentation writing in progress...

(Be patient...or ask directly to the author!)  
ilaria.carlomagno@elettra.eu
