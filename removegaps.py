#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy import ndimage
from netCDF4 import Dataset
from math import pi
from scipy.ndimage.filters import convolve
from scipy.signal import fftconvolve,gaussian

#from skimage import filters



############################
############################

ncv = Dataset('topography2.nc').variables
lat = ncv['latitude'][:]
lon = ncv['longitude'][:]
ztopo= ncv['relief'][:,:]

############################
############################

#doplot = False
doplot = True

nl = 2
nc = 4

plt.figure(figsize=(12,8))

if doplot:
   lon0 = -48; lon1 = -20; lat0 = -50; lat1 = -40
   #lon0 = -48; lon1 = -10; lat0 = -70; lat1 = -40

   #lon0 = -40; lon1 = -30; lat0 = -5; lat1 = 5
   #lon0 = 100; lon1 = 110; lat0 = -3; lat1 = 3  # aphrodite
   #lon0 = 90; lon1 = 110; lat0 = -20; lat1 = 20  # aphrodite
   #lon0 = -150; lon1 = -130; lat0 = -3; lat1 = 3  # a location with (real?) sharp edges
   #lon0 = -60; lon1 = -30; lat0 = 15; lat1 = 25  # a location with a data gap
   #lon0 = -90; lon1 = -70; lat0 = 0; lat1 = 40  # beta regio

   indlon = (lon>lon0)*(lon<lon1)
   indlat = (lat>lat0)*(lat<lat1)
   
   lon = lon[indlon]
   lat = lat[indlat]
   
   ztopo = ztopo[indlat,:]
   ztopo = ztopo[:,indlon]

   levs = np.linspace(ztopo.min(),ztopo.max(),100)

   plt.subplot(nl,nc,1)
   plt.contourf(lon,lat,ztopo,levs)
   #plt.spectral()
   plt.colorbar()
   plt.title('Original Topography')

# zero is reserved for missing values in the filtering, so we shift the whole topography
shift = 1.e5

zemask = ztopo.mask + 0
zedata = ztopo.data + 0.


ztopo_prev = np.zeros((len(lat),len(lon))) 
ztopo_prev[zemask==0] = zedata[zemask==0] + shift 
#ztopo_prev[zemask!=0] = 0.

maxiter = 7
iii = 0
#ranks = [4,4,6,6,8,8,10,10,15,15,20]
ranks = [4,6,8,10,15,20,50]
for rank in ranks:

   jjj = 0
   iii = iii+1
   dontstop = True

   while dontstop:
      print('Rank: ',rank)
      jjj = jjj+1

      linvec = np.arange(1,2*rank+1.1,1)
      linvec = rank + 1 - np.abs(linvec-rank-1)
      weights = np.outer(linvec,linvec)
      weights = weights/np.sum(weights)

      #weights = np.outer(gaussian(2*rank+1,5),gaussian(2*rank+1,5))
      
      #ztopo_new = convolve(ztopo_prev,weights)
      ztopo_new = fftconvolve(ztopo_prev,weights,mode='same')
      
      denom = np.ones((len(lat),len(lon)))
      denom[ztopo_prev==0] = 0.
      #denom = convolve(denom,weights)
      denom = fftconvolve(denom,weights,mode='same')

      denom[denom<=0.1] = np.nan
      
      ztopo_new = ztopo_new/denom
   
      ztopo_new[ztopo_prev!=0.] = ztopo_prev[ztopo_prev!=0.] 
   
      ztopo_new[np.isnan(ztopo_new)] = 0.
   
      ztopo_prev = ztopo_new + 0.
   
      if rank==ranks[-1]:
        if (np.sum(ztopo_new==0.) == 0):
          dontstop=False
        elif (jjj>=maxiter):
          print('ABORT: After',jjj,'iterations, there are still blank values')
          exit()
      else:
        dontstop=False

      if doplot and dontstop==False:
        ztopo_new[ztopo_new==0.] = np.nan
        plt.subplot(nl,nc,1+iii)
        plt.contourf(lon,lat,ztopo_new-shift,100)
        #plt.spectral()
        plt.colorbar()
        plt.title('Rank '+str(rank))
        #if rank==ranks[-1]:
        # plt.subplot(339)
        # plt.contourf(lon,lat,denom,100)
        # plt.spectral()
        # plt.colorbar()
   
   

if doplot:
  
  plt.savefig('removegaps.png')
  plt.show()

else: 
  
  ### Create file
  nc = Dataset('topography3.nc', 'w', format='NETCDF3_64BIT')
  nc.createDimension('latitude',len(lat))
  nc.createDimension('longitude',len(lon))
  
  lat_ = nc.createVariable('latitude', 'f', ('latitude',))
  lat_[:] = lat
  
  lon_ = nc.createVariable('longitude', 'f', ('longitude',))
  lon_[:] = lon
  
  ztopo_ = nc.createVariable('relief', 'f', ('latitude','longitude',))
  ztopo_[:] = ztopo_new-shift

  
  nc.close()


