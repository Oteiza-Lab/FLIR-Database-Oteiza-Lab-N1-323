# FLIR-Database-Oteiza-Lab-N1-323
Python script used to run FLIR Camera and store video data connected to the N1-323 / Actuator / Camera configuration.

## README
**CAREFULLY REVIEW THIS DOCUMENTATION BEFORE ACTUATOR USE TO ENSURE PROPER HANDLING OF THE EQUIPMENT**

Oteiza Lab FLIR Database
Last Updated 16/07/2024 - Daniel Durst

---------------------------------------------

## OVERVIEW

This README contains information on the Oteiza Lab FLIR Database, including proper use and issue fix information. If you are to improve the code, include additional functionality in this README, then update the date and name for documentation purposes.

The purpose of this database is to store video and user configuration data that pertains to footage of the fish in currents.
The python script is designed to connect to the camera and request, from the user, the specifications that the user wants for the videos being taken. The script can be run in two different ways, 1) Prompts given to the user sequentially and 2) command line with flags (both detailed below). The script will ensure that the valeus entered are within the capable range of the camera.

The camera (FLIR Blackfly S BFS-U3-16S2M) is connected to the computer via USB 3.0 (computer side) and USB 3.0 type Micro-B Male with Screws (camera side). Should you need further information on the camera (model may be improved by the time this is seen), visit https://www.flir.co.uk/products/blackfly-s-usb3/?model=BFS-U3-16S2M-CS.

The camera is operated in python through the Spinnaker SDK and PostGre SQL. For more information on both of these, visit https://www.flir.com/products/spinnaker-sdk/?vertical=machine+vision&segment=iis and https://www.postgresql.org/download/ respectively. The camera can be configured and viewed through the application SpinView.

Before running, you will have to configure your python interpreter to 3.10 and install all the imported features in the script.

---------------------------------------------

## STEPS TO RUN FLIR DATABASE PROPERLY

1 Open SpinView.
- Under System, the Blackfly S BFS-U3-16S2M FLIR Camera should be connected via one of the available Host Controllers.
- Double click on the Blackfly.
- Ensure that the camera is running (green play button is active, red stop button is available to click).
- **CLOSE THE SPINVIEW APPLICATION**

2 Open pgAdmin 4.
- Click on Servers
- Enter n1-323 as the password.
- Click on PostgreSQL 16 --> Databases --> FLIR_Database_OteizaLab --> Schemas --> public --> Tables --> videos
- Right click on videos --> View/Edit Data --> All Rows

3 Open VSCode.
- Open FLIR_Database_OteizaLab folder.
- If necessary, navigate to proper directory: PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> (your user in place of mine).

      PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> cd /
      PS C:\> cd Users
      PS C:\Users> cd daniel.durst
      PS C:\Users\daniel.durst> cd Downloads
      PS C:\Users\daniel.durst\Downloads> cd FLIR_Database_OteizaLab

4 Run Commands.
- Running the file alone:

      PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 dataabse.py
      ___ (follow prompts)
      ___ (output, connect to database, getimages)

- Running the file with parameters and flags [-ti DURATION] [-fps FPS] [-ex] [-et EXPOSURE_TIME] [-wi WIDTH] [-he HEIGHT] [-lens LENS]:

      PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 database.py -ti 30 -fps 30 -ex -wi 1440 -he 1080 -lens FixedFocal35mm
      ___ (output, connect to database, getimages)
      **IMPORTANT NOTE**
        - If you want auto exposure when running with flags, simply run -ex as a flag with no value.
        - If you want to set an exposure, run -et INSTEAD of -ex and add the exposure value.

5 Open Video.
- After running commands, a prompt will ask to open the video now. Type yes and click enter.
- The video is also saved in the FLIR_Database_OteizaLab folder in the Downloads.
- To view the video entry in the database, navigate to videos --> View/Edit Data --> All Rows.

6 **IF AT ANY TIME THE CAMERA MUST BE STOPPED**
- Hold down CTRL + C:
- You will still be able to open the video that was being taken with the prompt, however this file is NOT saved to the database.

---------------------------------------------

---------------------------------------------

## EDITING DATABASE
All attributes that are added must also have a variable in the script that is returned and sent to the database with the cursor SQL command.

1 Adding a stored attribute to the table:

  ALTER TABLE videos
  ADD COLUMN fish VARCHAR(255);

2 Deleting a stored attribute from the table (WILL DELETE ALL ENTRIES OF THAT COLUMN):

  ALTER TABLE videos
  DROP COLUMN fish;

3 Adding a new table to the database:

  CREATE TABLE fish (
	name VARCHAR(255) PRIMARY KEY,
	color VARCHAR(255) NOT NULL
);

4 Deleting a table from the database (WILL DELETE ALL DATA STORED IN THE TABLE):

  DROP TABLE fish;

5 Deleting a data instance (video with its data) from a table (target Primary Key):

  DELETE FROM videos
  WHERE id = 38;

6 Deleting all data instances in a table:

  DELETE FROM videos;

---------------------------------------------

---------------------------------------------

## ISSUE FIXES

### 1 Running Script, Camera Functioning Properly, Width Error

    PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 test.py -ti 30 -fps 30 -ex -wi 1440 -he 1080 -lens 30x
    Successfully connected to PostgreSQL server!
    -----------------------------------------------------
    CAMERA CAPABILITIES:
    Max Resolution Width: 1440, Min Resolution Width: 8
    Max Exposure Time: 29999999.0, Min Exposure Time: 4.0
    Max Frame Rate: 200.0, Min Frame Rate: 1.0
    -----------------------------------------------------
    
    -----------------------------------------------------
    USER SPECIFICATIONS:
    Duration: 30 seconds
    Frame Rate: 30 fps
    Automatic Exposure: Yes
    Resolution: 1440x1080 pixels
    Lens Type: 30x
    -----------------------------------------------------
    
    Error: Spinnaker: GenICam::AccessException= Node is not writable. : AccessException thrown in node 'Width' while calling 'Width.SetValue()' (file 'IntegerT.h', line 77) [-2006]

Steps to FIX:
- Close SpinView.
- Run reset.py

    PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 reset.py
    Initializing FLIR camera system...
    Resetting FLIR camera to factory defaults...
    FLIR camera reset completed successfully.

### 2 FPS Issue
- Currently, the hardware setup is incapable of performing at a high FPS.
- The FLIR camera promises up to 30 FPS, but the read/write speed of the computer/camera configuration only allows for up to ~2.5 FPS.
- This issue stems from either an SD Card not being used or other hardware components being out of date.
- Once the hardware is upgraded, follow these steps to ensure the FPS has been improved.

1 Run Commands:
- Run Configure.py, Run Transferratehigh.py, Run Configure.py, Run Transferratelow.py:

	PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 configure.py
	Camera configured for maximum frame rate.
	PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 transferratehigh.py
	Captured 23 frames in 10.46 seconds at higher resolution.
	Data transfer rate: 3.26 MB/s
	PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 configure.py       
	Camera configured for maximum frame rate.
	PS C:\Users\daniel.durst\Downloads\FLIR_Database_OteizaLab> python3.10 transferratelow.py
	Captured 31 frames in 10.66 seconds at lower resolution.
	Data transfer rate: 0.85 MB/s

- This way, you will be able to tell the current FPS and DTR at low and high resolutions.

### 3 PySpin cannot be Resolved by PyLance
- This will occur if you are using Python 11>. This is because Spinnaker SDK only has a 3.10 python version out right now.
- Hence, we have to downgrade our python interpreter as well as some other components.

How to FIX (This is what worked for n1-323):
1 Install Python 3.10 from https://www.python.org
2 CTRL + SHIFT + P --> Python: Select Interpreter --> Python 3.10.11
3 pip install numpy<2
4 pip uninstall PySpin
5 pip install PySpin
