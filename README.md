# h5_treatment
Scripts for data manipulation and format conversion of h5 files generated at the XRF beamline - Elettra Synchrotron

Maps to be checked/cut and executable must be in the same folder.
Double click on the program and wait for it to run. New files will be saved in a subfolder.
If you prefer, you can launch them from the terminal and follow the progress of the analysis.

- - - - - - reshape_XRF-MAPS
  creates new files reshaping the maps so that you do not need to input rows and columns in ROI imaging
The XRF maps produced at XRF as h5 files have to be manually reshaped when imported in PyMCA - ROI imaging tool.
This means that you have to know how many columns/rows are there in your image, otherwise the map will look "bad" or will not make sense (in the best case) or artefacts may appear (worst case, because you don't realise what happened!).

To solve this issue, you can use a python script to convert the h5 map into a new format.
You can find it on the xrf-desktop-01 computer in the folder Documents/scripts as "Reshape_XRF-MAPS_auto.py".

Linux environment:

Run the terminal in the Documents/scripts folder --> type "python Reshape_XRF-MAPS_auto.py"

Windows environment:
If you own the txt file, change the extension to ".py" (this can happen if you received the script via email: Python files cannot be attached to emails because the antivirus prevents to send messages with this extension!);
make sure you have python 3 installed and that you have the python packages h5py and numpy installed;
double click on it.
In both cases, you will be asked for the path where the h5 files are stored.
Then, the script will create a copy (you won't lose any data!) of your files into a subfolder named "reshaped".

The new files are automatically opened by PyMCA in the right row x column format.

- - - - - - cut_XRF-MAPS
  fixes incomplete data collection (due to beam dumps or manual interruption) and makes a new file discarding the non-valid pixels

- - - - - - cut_and_reshape_XRF-maps
    fixes incomplete data collection (due to beam dumps or manual interruption) and makes a new file discarding the non-valid pixels.
    New files are reshaped so that you don't need to input rows and columns in ROI imaging tool (PyMCA software)





--> Documentation writing in progress...

(Be patient...or ask directly to the author!)
ilaria.carlomagno@elettra.eu
