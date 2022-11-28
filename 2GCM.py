#!/usr/bin/env python

from netCDF4 import Dataset


############################
############################

ncv = Dataset('topography3.nc').variables
lat = ncv['latitude'][:]
lon = ncv['longitude'][:]
ztopo= ncv['relief'][:,:]

############################
############################


ztopo = ztopo[::-1,:]
ztopo = ztopo[:,::-1]

  
### Create file
nc = Dataset('Relief.nc', 'w', format='NETCDF3_64BIT')
nc.createDimension('latitude',len(lat))
nc.createDimension('longitude',len(lon))

lat_ = nc.createVariable('latitude', 'f', ('latitude',))
lat_[:] = lat

lon_ = nc.createVariable('longitude', 'f', ('longitude',))
lon_[:] = lon

ztopo_ = nc.createVariable('RELIEF', 'f', ('latitude','longitude',))
ztopo_[:] = ztopo


nc.close()


