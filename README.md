# Getting Started
-Install dependencies via [Acconeer's Exploration Tool](https://github.com/acconeer/acconeer-python-exploration). 
-Connect the sensor to a COM port, and identify which COM port it is in. On Windows, you can use Device Manager to determine this.
- Specify the port, a csv file to write to, and an H5 file to write to as indicated in breathing_v2.py. *You cannot write over H5 files, so create a new H5 file every time.*
- All determined tunings are included in breathing_v2.py, and be commented/uncommented as desired. 

# Running Tests
The Vernier GoDirect Belt can collect data on the [web app](https://graphicalanalysis.app/). Go to Sensor Data Collection, then turn on the Respiration Belt. Connect via Bluetooth as prompted by Graphical Analysis, or via cord. 
The settings can be changed in the bottom left hand corner of the app. Click 'Collect' to begin collecting the data. 
To export, click on the top left and navigate to "Export."

# Bugs
-'Cannot close recorder' when ending the program. This bug does not affect data collection or function of the program. 
