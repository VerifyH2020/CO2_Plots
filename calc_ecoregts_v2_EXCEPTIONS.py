#!/usr/bin/env python
import numpy as np, netCDF4, os
from mpl_toolkits.basemap import maskoceans
from grid import Grid
import sys,traceback
from string import Template
import math
from operator import add

# Local
from country_subroutines import get_country_region_data,convert_country_to_code
from exception_lists import create_unfccc_exceptions,create_efiscenspace_exceptions
from netcdf_subroutines import create_time_axis_from_netcdf

###### Usage
# python calc_ecoregts_v2_EXCEPTIONS.py
######

# The purpose of this script is to look at all CountryTot files for a given
# 2D.nc filename created by the script calc_ecoregts_v2.py and make
# some modifications.


if __name__ == "__main__":

   ##########################################
   # These are some special cases, where the value is not equal to
   # some combination of the individual countries.  For the moment,
   # this primarily happens with the EU-27+UK, which reports emissions
   # to the UNFCCC as a group that are not included in any member state.
   # In order to deal with this, we look to see if this ISO code appears
   # in the countries/regions in the file and, if so, after the standard
   # processing is done, we change that line by some stored values.
   exceptions=[]
   
   # Real database?  Or test database?
   #database_dir="/home/surface8/mmcgrath/TEST_VERIFY_DATABASE/"

   database_dir="/home/dods/verify/"

   #exceptions=create_unfccc_exceptions(database_dir,exceptions)
   
   # Based on what the EFISCEN-Space team wants, and how all the machinary
   # that we have in place works, I need to do this in a different way.
   # Except for replacing the EU-27+UK
#   efiscen2021_filename=Template("/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EFISCEN/Dec2021/TEST/Tier3BUDD_CO2_ForestFluxes_EFISCENSpace-SX_WENR_FOR_EU_1M_V3_20211217_SCHELHAAS_WP3_$filetype.nc")  
   efiscen2021_filename=Template(database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_ForestFluxes_EFISCENSpace-SX_WENR_FOR_EU_1M_V3_20211217_SCHELHAAS_WP3_$filetype.nc")  
   exceptions=create_efiscenspace_exceptions(database_dir,exceptions,filename=efiscen2021_filename)


   ##########################################
   
   possible_file_types=["CountryTotWithEEZEU","CountryTotWithOutEEZEU","CountryTotWithEEZ","CountryTotWithOutEEZ","CountryTotWithEEZGlobal","CountryTotWithOutEEZGlobal","CountryTotWithEEZAllCountriesRegions","CountryTotWithOutEEZAllCountriesRegions","CountryTotWithEEZMaster","CountryTotWithOutEEZMaster"]

   for exception in exceptions:
      print("*****************************************")
      print("Checking exception: {},{}".format(exception.varname,exception.region_code))
      for filetype in possible_file_types:

         # Check to see if the file exists.  If so, open it and check to see
         # if the variable and the region that we want to change exist.  If not,
         # we can go to the next file.
         filename=exception.filename.substitute(filetype=filetype)
         try:
            srcnc = netCDF4.Dataset(filename,"r+")
            print("Checking file: ",filename)
            
         except:
            #print(filename + " does not exist.  Skipping.")
            continue
         #endtry

         if exception.varname not in srcnc.variables.keys():
            print("Cannot find variable {} in this file.  Skipping".format(exception.varname))
            print(srcnc.variables.keys())
            continue
         #endif

         regcode = srcnc.variables["country_code"][:]
         code_index=-1
         for idx in range(regcode.shape[0]):

            ccode="".join([letter.decode('UTF-8') for letter in regcode[idx] if letter is not np.ma.masked])
            if ccode == exception.region_code:
               code_index=idx
            #endif
         #endif

         if code_index == -1:
            print("Region {} not found.  Skipping.".format(exception.region_code))
            continue
         #endif

         # Check the units
         if srcnc.variables[exception.varname].units != exception.current_units:
            print("Converting units from {} to {}.".format(exception.current_units,srcnc.variables[exception.varname].units))
            exception.convert_units(srcnc.variables[exception.varname].units)
         #endif

         print("Replacing data.")
         # Replace the data
         if len(exception.data) == 1: # replace all values (this happens with uncertainties)
            for itime in range(srcnc.variables[exception.varname].shape[0]):
               srcnc.variables[exception.varname][itime,code_index]=exception.data[0]
            #endfor
         elif len(exception.data) == srcnc.variables[exception.varname].shape[0]:
            srcnc.variables[exception.varname][:,code_index]=exception.data[:]
         elif (srcnc.variables[exception.varname].shape[0] % len(exception.data)) == 0 and (srcnc.variables[exception.varname].shape[0]/len(exception.data)) == 12:
            # This is a shortcut.  It assumes that you gave it annual values and
            # it's copying them to a monthly timeseries using the same value
            # for all months in a year.
            for itime in range(srcnc.variables[exception.varname].shape[0]):
               jtime=math.floor(itime/12)
               srcnc.variables[exception.varname][itime,code_index]=exception.data[jtime]
            #endfor
         else:
            print("Data you want to replace is not the same length as what it's replacing!")
            print(exception.varname,exception.varname,exception.varname)
            print("Length of data requested: ",len(exception.data))
            print("Shape of data to overwrite: ",srcnc.variables[exception.varname].shape)
            print("Number of years (assuming monthly data): ",srcnc.variables[exception.varname].shape[0]/len(exception.data))
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
         #endif

         # Add a note
         srcnc.setncatts({'data_{}_{}'.format(exception.region_code,exception.varname) : 'The data for region {} and variable {} is not taken from the 2D file, but rather added afterwards by the script calc_ecoregts_v2_EXCEPTIONS.py'.format(exception.region_code,exception.varname)})

         srcnc.close()

      #endfor

   #endfor


   # Create a special routine for EFISCEN-Space.
   print("*****************************************")
   print("Creating exceptions for EFISCEN-Space.")
   for filetype in possible_file_types:
       # Check to see if the file exists.  If so, open it and check to see
       # if the variable and the region that we want to change exist.  If not,
       # we can go to the next file.
       filename=efiscen2021_filename.substitute(filetype=filetype)
       try:
           srcnc = netCDF4.Dataset(filename,"r+")
           print("Checking file: ",filename)
           
       except:
           print(filename + " does not exist.  Skipping.")
           continue
       #endtry

       # get the time axis
       timeaxis=create_time_axis_from_netcdf(filename)

       # EU-27+UK should already be replaced.  So what I need to do here
       # is set all countries outside of the 15 and EU-27+UK to NaN, and then
       # set all zero values in these timeseries to NaN, as per the team's
       # wishes.
       varnames=["FCO2_NBP_FOR","FCO2_NEP_FOR","HARVEST_FOR","BIOMASS_FOR"]
       keep_cnames=["Ireland","Norway","Sweden","Poland","Germany","Netherlands","Belgium","Luxembourg","France","Spain","Switzerland","Italy","Czech Republic","Slovak Republic","Romania","E28"]
       #  I need to be explicit about this here.  It seems there is some
       # leakage from other countries, even when I use only pixels with a 
       # fraction of 1.0.  Not sure what is going on.
       country_data_extents={}
       country_data_extents["Ireland"]=[2011,2016]
       country_data_extents["Norway"]=[2016,2021]
       country_data_extents["Sweden"]=[2016,2021]
       country_data_extents["Poland"]=[2012,2017]
       country_data_extents["Germany"]=[2012,2017]
       country_data_extents["Netherlands"]=[2013,2018]
       country_data_extents["Belgium"]=[2013,2018] # The table lists Beligum-Flanders
       country_data_extents["Luxembourg"]=[2010,2015]
       country_data_extents["France"]=[2009,2014]
       country_data_extents["Spain"]=[2002,2007]
       country_data_extents["Switzerland"]=[2005,2010]
       country_data_extents["Italy"]=[2005,2010]
       country_data_extents["Czech Republic"]=[2015,2020]
       country_data_extents["Slovak Republic"]=[2016,2021]
       country_data_extents["Romania"]=[2010,2015]
       country_data_extents["E28"]=[2005,2020]

       keep_ccodes=[]

       country_region_data=get_country_region_data()

       remove_ccodes=list(country_region_data.keys())
       for cname in keep_cnames:
           ccode=convert_country_to_code(cname,country_region_data)
           if ccode in remove_ccodes:
               remove_ccodes.remove(ccode)
           #endif
           keep_ccodes.append(ccode)
           if cname in country_data_extents.keys():
               country_data_extents[ccode]=country_data_extents[cname]
           #endif
       #endfor

       regcode = srcnc.variables["country_code"][:]
       for remove_ccode in remove_ccodes:
           print("Eliminating data for: ",remove_ccode)
           code_index=-1
           for idx in range(regcode.shape[0]):
           
               ccode="".join([letter.decode('UTF-8') for letter in regcode[idx] if letter is not np.ma.masked])
               if ccode == remove_ccode:
                   code_index=idx
               #endif
           #endfor
           if code_index == -1:
               print("Country/region {} not found in this EFISCEN-Space file.".format(remove_ccode))
               continue
           #endif

           # Set them equal to NaN
           for varname in varnames:
               srcnc.variables[varname][:,code_index]=np.nan
           #endfor

       #endfor

       # Now for the countries that exist, set any zero values equal
       # to NaN.
       for keep_ccode in keep_ccodes:
           code_index == -1
           for idx in range(regcode.shape[0]):
           
               ccode="".join([letter.decode('UTF-8') for letter in regcode[idx] if letter is not np.ma.masked])
               if ccode == keep_ccode:
                   code_index=idx
               #endif
           #endfor
           if code_index == -1:
               print("Keep country/region {} not found in this EFISCEN-Space file.".format(keep_ccode))
               continue
           #endif
           
           print("Found code: ",keep_ccode,code_index)
           year_list=country_data_extents[keep_ccode]
           # Set any values not in a specific years to NaN
           for varname in varnames:
               
               for itime,rtime in enumerate(timeaxis.values):
                   current_year=timeaxis.get_year(rtime)
                   if current_year < year_list[0] or current_year > year_list[1]: 
                       srcnc.variables[varname][itime,code_index]=np.nan
                   #endif
               #endfor

           #endfor

       #endfor

       srcnc.close()

   #endfor


#endif main
     





