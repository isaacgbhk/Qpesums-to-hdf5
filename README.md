# Qpesums-to-hdf5

# Steps


1. Unzip the raw files

   * Linux command
   ```
   tar -xvf {filename}
   ```
   * Python implementation
   ```
   import glob
   import os
   
   for file in glob("path-to-QPESUMS_3d_CWB/20xx/*.gz"):
       filename = file.split('/')[-1]
       cmd = f"tar -xvf {filename}"
       os.system(cmd)
   ```
2. Move all day files (36x times) into one folder
   ```
    import glob
    import os
   
    day_folders = glob("./*")
    day_folders.sort()
    # day_folders = day_folders[0:-1]
    
    print(len(day_folders))

    for day_folder in day_folders:
        cmd = f"mv -v {day_folder}/mrefl_mosaic/* 2020_all_day_zip/"
        os.system(cmd)

   ```
