#!/usr/bin/env python

from planetaryimage import CubeFile
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy import ndimage
from netCDF4 import Dataset
from math import pi

topo = CubeFile.open('Venus_Magellan_Topography_Global_4641m_v02.cub')


ztopo = topo.apply_numpy_specials()
ztopo = ztopo[0,:,:]
ztopo = ztopo[::-1,:]

ztopo = ztopo - 880.


ztopo = np.ma.masked_invalid(ztopo)


nlat = ztopo.shape[0]
nlon = ztopo.shape[1]

lat = np.linspace(-90.,90.,num=nlat)
lon = np.linspace(-180.,180.,num=nlon)


miss = -9.e33

ztopo[np.isnan(ztopo)] = miss

### Create file
nc = Dataset('topography1.nc', 'w', format='NETCDF3_64BIT')
nc.createDimension('latitude',ztopo.shape[0])
nc.createDimension('longitude',ztopo.shape[1])

lat = nc.createVariable('latitude', 'f', ('latitude',))
lat[:] = np.linspace(-90.,90.,num=ztopo.shape[0])

lon = nc.createVariable('longitude', 'f', ('longitude',))
lon[:] = np.linspace(-180.,180.,num=ztopo.shape[1])

ztopo_ = nc.createVariable('relief', 'f', ('latitude','longitude',),fill_value=miss)
ztopo_[:] = ztopo


nc.close()



