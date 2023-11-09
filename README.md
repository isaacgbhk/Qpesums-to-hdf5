# Qpesums-to-hdf5

# Usage

This project is specifically designed to convert 3D Qpesums data to HDF5 format. 3D Qpesums data will not be provided, and purchase is required.

# Steps
1. Unzip the raw files (Yearly -> Daily)
   * Python implementation
   ```
   import glob
   import os
   
   for file in glob("path-to-QPESUMS_3d_CWB/20xx/*.gz"):
       filename = file.split('/')[-1]
       cmd = f"tar -xvf {filename}"
       os.system(cmd)
   ```

2. Unzip and Move all day files (36x times) into one folder
   ```
    day_files = glob(f"path_to_daily_files/*.gz")
    day_files.sort()

    # Create folder
    try: os.mkdir(f"...All_day_unzip/{year}_all_day_unzip")
    except: print("Folder already exist")

    # unzip then move
    # 1. unzip
    for day_file in day_files:    
        cmd = f"gzip -dk {day_file}"
        os.system(cmd)
        
    # 2. move
        day_file_unzip = day_file.replace(".gz", "")
        cmd = f"mv {day_file_unzip} {day_file_unzip.replace(f'All_day_zip/{year}_all_day_zip', f'All_day_unzip/{year}_all_day_unzip')}"
        os.system(cmd)
   
    day_folders = glob("./*")
    day_folders.sort()
    
    for day_folder in day_folders:
        cmd = f"mv -v {day_folder}/mrefl_mosaic/* {year}_all_day_zip/"
        os.system(cmd)

   ```

3. Decode and Write hdf5

    3.1 Change the path in decode_and_write.py

        line 21: day_files = ...
        line 27: os.mkdir(...)
        line 47: filename = ...
        
    3.2 Run decode_and_write.py
    * In terminal
    ```
    python3 decode_and_write.py 
    ```
