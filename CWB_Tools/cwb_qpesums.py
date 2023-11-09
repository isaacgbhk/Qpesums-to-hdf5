import struct
import numpy as np
from typing import NamedTuple
import datetime

class qpesums_header(NamedTuple):
    dt:datetime.datetime
    dims:tuple
    xy_ll:tuple
    ds:tuple
    proj:str
    varname:str
    varunit:str
    varscale:int
    no_data_value:int
    radars:tuple

def get_qpesums_xy(hdr):
    nx = hdr.dims[0]
    ny = hdr.dims[1]
    dx = hdr.ds[0]
    dy = hdr.ds[1]
    x_l = hdr.xy_ll[0]
    y_l = hdr.xy_ll[1]
    x_t = x_l + (nx-1)*dx
    y_t = y_l + (ny-1)*dy
    
    #print((x_l, x_t, y_l, y_t))
    
    return np.linspace(x_l, x_t, nx), np.linspace(y_l, y_t, ny)    


def get_qpesums_header(fname):
    with open(fname,"rb") as f:
        data = f.read()
    
    # 1-9: integer yyyy,mm,dd,hh,mn,ss,nx,ny,nz
    num = 9
    pos_s = 0
    pos_e = pos_s + 4*num
    s = 'i'*num
    grp1_result = struct.unpack(s, data[pos_s:pos_e])
    yyyy,mm,dd,hh,mn,ss = grp1_result[0:6]
    nx, ny, nz = grp1_result[6:9]
    #dims = grp1_result[6:9]
    
    dt = datetime.datetime(year=yyyy, month=mm, day=dd, hour=hh, minute=mn, second=ss)
    dims = (nx,ny,nz)
    
    # 10: character proj*4
    num = 4
    pos_s = pos_e
    pos_e = pos_s + 1*num
    s = 'c'*num
    proj = struct.unpack(s, data[pos_s:pos_e])
    proj = b''.join(proj)
    
    # 11-20: integer map_scale,projlat1,projlat2,projlon,alon,alat,xy_scale,dx,dy,dxy_scale
    num = 10
    pos_s = pos_e
    pos_e = pos_s + 4*num
    s = 'i'*num
    grp2_result = struct.unpack(s, data[pos_s:pos_e])
    #print(grp2_result)
    x_tl, y_tl, xy_scale, dx, dy, dxy_scale = grp2_result[4:10]
    ds = (dx/dxy_scale, dy/dxy_scale)
    x_ll = x_tl/xy_scale
    y_ll = y_tl/xy_scale - (ny-1)*(dy/dxy_scale)
    xy_ll = (x_ll, y_ll)
    
    # 21-24: zht,z_scale,i_bb_mode,unkn01
    num = nz + 2 + 9
    pos_s = pos_e
    pos_e = pos_s + 4*num
    s = 'i'*num
    grp3_result = struct.unpack(s, data[pos_s:pos_e])
   # print(grp3_result)
    
    # 25-26: varname,varunit
    num = 20+6
    pos_s = pos_e
    pos_e = pos_s + 1*num
    s = 'c'*num 
    grp4_result = struct.unpack(s, data[pos_s:pos_e])
    #print(grp4_result)
    varname = b''.join(grp4_result[0:20])
    varunit = b''.join(grp4_result[20:26])
    
    # 27-29: var_scale,missing,nradar
    num = 3
    pos_s = pos_e
    pos_e = pos_s + 4*num
    s = 'i'*num 
    grp5_result = struct.unpack(s, data[pos_s:pos_e])
    #print(grp5_result)
    nradars = grp5_result[2]
    no_data_value = grp5_result[1]
    varscale = grp5_result[0]
    
    # 30: mosradar
    num = nradars*4
    pos_s = pos_e
    pos_e = pos_s + 1*num
    s = 'c'*num 
    grp6_result = struct.unpack(s, data[pos_s:pos_e])
    
    l_radars = []
    for i in range(nradars):
        l_radars.append(b''.join(grp6_result[i*4:(i+1)*4]))
    
    radars = tuple(l_radars)
    #print(radars)
    return qpesums_header(dt, dims, xy_ll, ds, proj, varname, varunit, varscale, no_data_value,radars)
    
def import_qpesums_bin(fname):
    
    with open(fname,"rb") as f:
        data = f.read()
    
    hdr = get_qpesums_header(fname)
    
     # 31: var
    num = hdr.dims[0]*hdr.dims[1]*hdr.dims[2]
    pos_s = 9*4+4+10*4+(hdr.dims[2]+2+9)*4+(20+6)+3*4+len(hdr.radars)*4;
    pos_e = pos_s + 2*num
    s = 'h'*num 
    var_result = struct.unpack(s, data[pos_s:pos_e])
    
    var_result = np.array(var_result, dtype=np.float32)
    var_result /= hdr.varscale
    
    return hdr, var_result