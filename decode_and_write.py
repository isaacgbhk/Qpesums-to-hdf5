import struct
import datetime
from typing import NamedTuple

import datetime
from glob import glob
from tqdm import tqdm
import datetime
import os


import h5py
import numpy as np
import matplotlib.pyplot as plt

# import CWB_Tools.cwb_qpesums as cwb
import CWB_Tools.cwb_qpesums_3D as cwb_3D


year = 2023
day_files = glob(f"...All_day_unzip/{year}_all_day_unzip/*")
day_files.sort()


# Create folder
try:
    os.mkdir(f"...All_day_h5/{year}_all_day_h5")
except:
    print("Folder already exist")
    
print(f"Start: {datetime.datetime.now()}, {len(day_files)}")
    
def decode_and_write(day_file):

# A. Decode QPESUMS 3D data

    hdr_dbz, dbzh = cwb_3D.import_qpesums_bin(day_file)
    nx_dbz = hdr_dbz.dims[0] ; ny_dbz = hdr_dbz.dims[1] ; nz_dbz = hdr_dbz.dims[2]

    # Reshape to 3D array
    dbzh = dbzh.reshape(nz_dbz, ny_dbz, nx_dbz)
    # Replace no_data_value with np.nan
    # dbzh[dbzh == hdr_dbz.no_data_value] = np.nan

# B. Write to HDF5 file
    prefix = day_file.split("/")[-1]
    filename = f".../All_day_h5/{year}_all_day_h5/{prefix}.hdf5"

    # initial
    with h5py.File(filename, "w") as f:
        # MAXDBZ
        dset1  = f.create_dataset(f"dataset1/data1/data", data = np.nanmax(dbzh, axis = 0), dtype="float32", maxshape = (ny_dbz, nx_dbz), chunks = True, compression="gzip")
        # DBZH
        dset2  = f.create_dataset(f"dataset2/data1/data", data = dbzh, dtype="float32", maxshape=(nz_dbz, ny_dbz, nx_dbz), chunks = True, compression="gzip")
        
        # TOPVIEW
        dset3  = f.create_dataset(f"dataset3/data1/data", data = np.zeros((ny_dbz, nx_dbz)), dtype="float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        # SIDEVIEW
        dset4  = f.create_dataset(f"dataset4/data1/data", data = np.zeros((ny_dbz, nx_dbz)), dtype="float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        
        # UK Orginal VIL
        # mFac = 3.44e-6
        # vil = ( 0.5e3 * mFac * np.sum(np.power(np.power(10.0, 0.1 * dbzh), 4.0 / 7.0), axis=0))
        
        # TW VIL (http://mopl.as.ntu.edu.tw/web/ASJ/30/30-1-2.pdf?fbclid=IwAR2-_kSOP57H6qiall8_pPG43kvlsuDeGrLt2IgwKytf-AEc23OyG80V4FE, p.27)
        mFac = 3.44e-3
        vil = (mFac * np.sum(np.power(np.power(10.0, 0.1 * dbzh), 4.0 / 7.0), axis=0)) * 0.5 # 0.5 km = 500m
        
        # VIL == vertical intergral liquid
        # VIL
        dset5  = f.create_dataset(f"dataset5/data1/data", data = vil, dtype = "float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        # TOP45
        dset6  = f.create_dataset(f"dataset6/data1/data", data = np.zeros((ny_dbz, nx_dbz)), dtype="float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        # TOP18
        dset7  = f.create_dataset(f"dataset7/data1/data", data = np.zeros((ny_dbz, nx_dbz)), dtype="float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        # VILD
        dset8  = f.create_dataset(f"dataset8/data1/data", data = np.zeros((ny_dbz, nx_dbz)), dtype="float32", maxshape=(ny_dbz, nx_dbz), chunks = True, compression="gzip")
        
        quantities = ["MAXDBZ","DBZH","TOPVIEW","SIDEVIEW","VIL","TOP45","TOP18","VILD",]
        
        for i in range(8):
            f.create_group(f"dataset{i + 1}/what")
            
            f[f"dataset{i + 1}/what"].attrs["product"]       = "COMP"
            f[f"dataset{i + 1}/what"].attrs["quantity"]      = quantities[i]
            f[f"dataset{i + 1}/what"].attrs["startdate"]     = prefix.split(".")[1]
            f[f"dataset{i + 1}/what"].attrs["starttime"]     = prefix.split(".")[2] + "00"
            f[f"dataset{i + 1}/what"].attrs["enddate"]       = prefix.split(".")[1]
            f[f"dataset{i + 1}/what"].attrs["endtime"]       = str(f"{(int(prefix.split('.')[2]) + 9):04}") + "00"
            f[f"dataset{i + 1}/what"].attrs["gain"]          = 1.0
            f[f"dataset{i + 1}/what"].attrs["offset"]        = 0.0
            f[f"dataset{i + 1}/what"].attrs["nodata"]        = np.nan
            f[f"dataset{i + 1}/what"].attrs["undetect"]      = -999.9
            f[f"dataset{i + 1}/what"].attrs["no_data_value"] = hdr_dbz.no_data_value

        f.create_group(f"what")
        f[f"what"].attrs["object"] = "COMP"
        f[f"what"].attrs["date"]  = prefix.split(".")[1]
        f[f"what"].attrs["time"]  = prefix.split(".")[2] + "00"
        f[f"what"].attrs["source"]  = "Qpesums"
        f[f"what"].attrs["no_data_value"] = hdr_dbz.no_data_value
        
        
        f.create_group(f"where")
        # EPSG web 1997
        f[f"where"].attrs["projdef"] = "None" #"UK orginal: +proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012718 +x_0=400000 +y_0=-100000 +ellps=airy +datum=OSGB36 +units=m +no_defs"
        
        f[f"where"].attrs["xsize"]   = nx_dbz
        f[f"where"].attrs["ysize"]   = ny_dbz
        f[f"where"].attrs["zsize"]   = nz_dbz
        
        f[f"where"].attrs["xscale"]  = hdr_dbz.varscale
        f[f"where"].attrs["yscale"]  = hdr_dbz.varscale
        f[f"where"].attrs["zscale"]  = hdr_dbz.zs[1] - hdr_dbz.zs[0]
        f[f"where"].attrs["zlevels"]  = hdr_dbz.zs
        
        total_lat = hdr_dbz.ds[0] * (ny_dbz - 1)
        total_lon = hdr_dbz.ds[1] * (nx_dbz - 1)
        
        # Bottom left corner
        f[f"where"].attrs["LL_lat"] = hdr_dbz.xy_ll[1]
        f[f"where"].attrs["LL_lon"] = hdr_dbz.xy_ll[0]
        
        # Bottom right corner
        f[f"where"].attrs["LR_lat"] = hdr_dbz.xy_ll[1]
        f[f"where"].attrs["LR_lon"] = hdr_dbz.xy_ll[0] + total_lon
        
        # Top left corner
        f[f"where"].attrs["UL_lat"] = hdr_dbz.xy_ll[1] + total_lat
        f[f"where"].attrs["UL_lon"] = hdr_dbz.xy_ll[0]
        
        # Top right corner
        f[f"where"].attrs["UR_lat"] = hdr_dbz.xy_ll[1] + total_lat
        f[f"where"].attrs["UR_lon"] = hdr_dbz.xy_ll[0] + total_lon

from concurrent.futures import ThreadPoolExecutor

strat = datetime.datetime.now()

with ThreadPoolExecutor(max_workers = 32) as executor: 
    executor.map(decode_and_write, day_files)

print(f"Time taken: {datetime.datetime.now() - strat}")
        
"""
nohup python3 decode_and_write.py > out_decode_2023.txt 2> err_decode_2023.txt &
"""
