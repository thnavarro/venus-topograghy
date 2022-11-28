#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy import ndimage
from netCDF4 import Dataset
from math import pi
#from scipy.ndimage import filters


from skimage import filters



############################
############################

ncv = Dataset('topography1.nc').variables
lat = ncv['latitude'][:]
lon = ncv['longitude'][:]
ztopo= ncv['relief'][:,:]

############################
############################

#doplot = False
doplot = True

if doplot:
   #lon0 = -40; lon1 = -30; lat0 = -5; lat1 = 5  # a location with artifacts/aliasing
   lon0 = 100; lon1 = 110; lat0 = -3; lat1 = 3  # aphrodite, strong artifacts
   #lon0 = 90; lon1 = 110; lat0 = -20; lat1 = 20  # aphrodite, strong artifacts
   #lon0 = -150; lon1 = -130; lat0 = -3; lat1 = 3  # a location with (real?) sharp edges
   #lon0 = -60; lon1 = -30; lat0 = 15; lat1 = 25  # a location with a data gap
   #lon0 = -90; lon1 = -70; lat0 = 0; lat1 = 40  # beta regio, where there are rifts


   indlon = (lon>lon0)*(lon<lon1)
   indlat = (lat>lat0)*(lat<lat1)
   
   lon = lon[indlon]
   lat = lat[indlat]
   
   ztopo = ztopo[indlat,:]
   ztopo = ztopo[:,indlon]




### if you want a final result more (less) smooth, increase (decrease) sigma2, 
### but also increase (decrease) seuil to be less (more) strict on the removal of problematic values.
#sigma1 = 4.; sigma2 = 2.; seuil = 0.2
sigma1 = 4.; sigma2 = 1.; seuil = 0.1
#sigma1 = 4.; sigma2 = 2.; seuil = 0.2


#### Gaussian filter to smooth topography
ztopo_normed = 2*(ztopo-ztopo.min())/(ztopo.max()-ztopo.min()) - 1.
ztopo_smooth = filters.gaussian(ztopo_normed,sigma1)

#### Use threshold on sharp topography (sharp = topo - smooth) to point out artifacts
ztopo_blanks = ztopo.copy()
ztopo_blanks[np.abs(ztopo_normed-ztopo_smooth)>seuil] = np.nan
ztopo_blanks = np.ma.masked_invalid(ztopo_blanks)

#### Smooth topography without these artifacts.
#### Note that this 2nd smoothing is not as strong as the 1st one.
ztopo_final = ztopo_normed.copy() 
ztopo_final[np.abs(ztopo_normed-ztopo_smooth)>seuil] = 0.
ztopo_final[ztopo.mask] = 0.
ztopo_final = filters.gaussian(ztopo_final,sigma2)

#### trick to perform gaussian smoothing of ztopo_final in the presence of NaNs
denom = np.ones_like(ztopo)
denom[np.abs(ztopo_normed-ztopo_smooth)>seuil] = 0.
denom[ztopo.mask] = 0.
denom = filters.gaussian(denom,sigma2)
ztopo_final = ztopo_final/denom

#### Add the data gaps
ztopo_final[ztopo.mask] = np.nan
ztopo_final = np.ma.masked_invalid(ztopo_final)
#ztopo_final.mask = ztopo.mask

#### Put back values on their original scale
ztopo_final = (ztopo_final-ztopo_final.min()) / (ztopo_final.max()-ztopo_final.min())
ztopo_final = ztopo_final*(ztopo_blanks.max()-ztopo_blanks.min()) + ztopo_blanks.min()

#miss = -8.e33
#
#ztopo_final[np.isnan(ztopo_final)] = miss
#ztopo_final[ztopo_final.mask] = miss


#################

if doplot:

  levs = np.linspace(ztopo.min(),ztopo.max(),100)
  levs_normed = np.arange(-1.,1.1,0.2)

  plt.figure(figsize= (12,10))

  plt.subplot(231)
  plt.contourf(lon,lat,ztopo,levs)
  #plt.spectral()
  plt.colorbar()
  plt.title('Original Topography')
  
  plt.subplot(232)
  plt.contourf(lon,lat,ztopo_smooth,100)
  #plt.spectral()
  plt.colorbar()
  plt.title('Smooth Topography')
  
  plt.subplot(233)
  plt.contourf(lon,lat,ztopo_normed-ztopo_smooth,100)
  plt.hsv()
  plt.colorbar()
  plt.title('Sharp Topography')
  
  plt.subplot(234)
  plt.contourf(lon,lat,ztopo_blanks,levs)
  #plt.spectral()
  plt.colorbar()
  plt.title('Topography without sharp points')
  
  plt.subplot(235)
  plt.contourf(lon,lat,ztopo_final,levs)
  #plt.spectral()
  plt.colorbar()
  plt.title('Final Topography:\nwithout sharp points, then smoothed')
  
  plt.subplot(236)
  plt.contourf(lon,lat,np.abs(ztopo-ztopo_final),100)
  plt.bone()
  plt.colorbar()
  plt.title('Original minus Final Topography')
  
  plt.savefig('removeartifacts.png')
  plt.show()


else:

 
  miss = -9.e33

  #ztopo_final = ztopo_final.data
  ztopo_final[np.isnan(ztopo_final)] = miss
  ztopo_final[ztopo_final.mask] = miss
  #print(ztopo_final.__dtype__)
  #print(ztopo.__dtype__)
 
  
  ### Create file
  nc = Dataset('topography2.nc', 'w', format='NETCDF3_64BIT')
  nc.createDimension('latitude',len(lat))
  nc.createDimension('longitude',len(lon))
  
  lat_ = nc.createVariable('latitude', 'f', ('latitude',))
  lat_[:] = lat
  
  lon_ = nc.createVariable('longitude', 'f', ('longitude',))
  lon_[:] = lon
  
  #ztopo_ = nc.createVariable('relief', 'f', ('latitude','longitude',),fill_value=miss)
  #ztopo_[:] = ztopo
  ztopo_ = nc.createVariable('relief', 'f', ('latitude','longitude',),fill_value=miss)
  ztopo_[:] = ztopo_final

  ztopo2_ = nc.createVariable('diff', 'f', ('latitude','longitude',),fill_value=miss)
  ztopo2_[:] = ztopo[:] - ztopo_final[:]
  
  nc.close()


