# h5_treatment
Scripts for data manipulation and format conversion of h5 files generated at the XRF beamline (Elettra Synchrotron, Trieste, Italy).
H5 files to be processed in the working path.

- **Linux environment**  
You can run the scripts from the terminal and follow the progress of the data handling: just type ```python name-of-the-script.py```  
Alternatively, you can double click on the icon and wait for it to run: new files will be saved in a subfolder.

- **Windows environment**  
Make sure you have **python 3** installed and that you have the python packages h5py and numpy installed, then double click on the icon.

## reshape_XRF-MAPS 
The XRF maps produced at the XRF beamline (h5 files) have to be manually reshaped when imported in PyMCA - ROI imaging tool.  
This means that you have to know how many columns/rows are there in your image, otherwise the map will look "bad" or will not make sense (in the best case) or artefacts may appear (worst case, because you don't realise what happened!).  

To solve this issue, you can use a python script to reshape the h5 map. The script will create a copy (you won't lose any data!) of your files into a subfolder named "reshaped".

The new files can be automatically opened by PyMCA in the right (row, column) format.

## cut_XRF-MAPS
To fix incomplete data collection (due to beam dumps or manual interruption) and makes a new file discarding the non-valid pixels

## cut_and_reshape_XRF-MAPS
To fix incomplete data collection (due to beam dumps or manual interruptions causing a non-rectangular shape of the map). This script creates a new file discarding the non-valid pixels (beam dump) or cutting the incomplete rows/columns to have rectangular shape.  
New files are reshaped so that you don't need to input rows and columns in ROI imaging tool (PyMCA software)

## convert_h5_to_orange
To fix compatibility issues with Orange software.  
Output: ```.csv``` files with X and Y coordinates, I0 (bms), and all the 2048 channels of the fluorescence detector.

## extract_new_roi_from_h5
To extract XAS spectra using new ROIs from the one(s) defined when data collection was started. The user is asked to input the new ROI using the following syntax to indicate the first and last channels to be used: [first, last]
Output: ```.txt``` file with _energy, I0, roi_new, alfafluo_new_ columns. _roi_new_ is the integral of the ICR within the channels selected, _alfafluo_new_ is the absorption coefficient calculated as ratio roi_new/I0.

## extract_doubleROI_fromh5
--> Work with Sirius3 detector
XSW on FeCo alloys - edition
To extract XAS spectra using two ROIs Co (or Fe) plus an alternative one to be used for self-absorption correction. 
At the moment, the script automatically checks the filename to choose between Co and Fe ROIs. The secondary ROI (for self absorption correction) is entered directly in the code.
The script also checks for the deadtime of each of the 3 elements of the SDD detector. If one value is above 10%, the filename of the txt files gets a "CHECK_DEADTIME" addition at the end.
Output: ```.txt``` file with _energy, theta/phi, I0, alfafluo_Fe_, _alfafluo-selfabsorption_ columns.

--> Further documentation writing in progress...

(Be patient...or ask directly to the author!)  
ilaria.carlomagno@elettra.eu
