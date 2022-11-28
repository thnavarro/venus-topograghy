# venus-topograghy
This is collection of processing tools for the 4km Venus Magellan topography.
They remove small-scale artifacts, fill missing gaps and turn it into a NetCDF file.
The initial goal was to create a topography usable by a GCM, but it can serve any general purpose, in particular for numerical modeling.


The initial file is the version 2 (1997 release) of the Global Topographic Data Record in a cub format, which can be found here (11/28/22):

https://astrogeology.usgs.gov/search/map/Venus/Magellan/RadarProperties/Venus_Magellan_Topography_Global_4641m_v02



cub2nc.py turns the .cub file into a NetCDF file.

removeartifacts.py identify and removes small-scale, unrealastic blips associetd with the orbit path.

removegaps.py infers the missing data by extrapolating the existing topography.

2GCM.py flips the topography in order to be used by the LMD/IPSL Venus GCM/PCM

Processing chain is:

 
    topography in .cub

     |
     |
     
    cub2nc.py  ___ topography1.nc (same as .cub, but in .nc format)

                         |
                         |

                  removeartifacts.py ____ topography2.nc (Topography without orbital artifacts)

                                              |
                                              |

                                        removegaps.py ____ topography3.nc (Topography without gaps)  

                                                                |
                                                                |

                                                             2GCM.py ____ Relief.nc
