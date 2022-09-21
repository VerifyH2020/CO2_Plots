 #!/usr/bin/env python
import numpy as np, netCDF4, os
from mpl_toolkits.basemap import maskoceans
import sys,traceback
import re

# Local modules
from grid import Grid
from country_subroutines import get_country_region_data,calculate_country_areas,get_country_areas
from netcdf_subroutines import create_time_axis_from_netcdf

######
# python calc_ecoregts_v2.py PATH PATH_OUT
#
# PATH can be either a directory or a NetCDF file.  If a directory,
# the script will try to run on every .nc file in the directory for
# which an existing CountryTot file is not found.
######

# The purpose of this script is to take a spatially explicit NetCDF file
# and calculate country totals, putting them into a new .nc file that
# just has timeseries for every country.  The countries (and regions) are
# found in the path_mask file, which is a NetCDF file with a list of
# country (and region) names along with a mask showing which pixels belong
# to which country (0 means no part of the country is in that pixel, 1 means
# the pixel is fully contained in the country, and a number between 0 and 1
# means that part of the pixel is found in that country/region).

# The country masks are regridded to the resolution of the input file/files.
# In order to save time, these masks are stored in the path_regs directory
# with the grid, latitudinal, and longitudinal extent in the name.  For any
# given input file, the regridding is only done if a file matching the
# grid, latitudinal extent, and longitudinal extent is not found.

# All of the global attributes from the 2D.nc file are copied to the
# new file, and a line explaining the processing is added.
#
# Standard time/lat/lon variables are in files which end with _2D.nc.
# The script also now processes _2Dmod.nc files, which are similar
# to CountryTot files.  These were renamed to TempCT.
#
# NOTE: Some 2D.nc files are known to be incorrect.  If this script
#       is applied, the results are bad.  Therefore, we keep a list of
#       those files and skip them.  These are generally 2D.nc files that
#       were created from country totals listed in spreadsheets in 2019
#       and 2020.  Ideally, those would be replaced with 2Dmod/TempCT files,
#       but that would require redoing all those scripts and testing them.
#
#############################################################
# A subroutine to print missing information from regions to the
# NetCDF file.  Only used for the2Dmod TempCT file.
# Takes as input a dictionary of lists of the same length as
# the timeseries.  If the value is False, data is missing
# for that timestep and that country in that region.
# Also takes a timeaxis.  We only want to print out years
# that are missing, but sometimes we have monthly data.
############################################################
def print_missing_region_information(timeaxis,country_region_data,data_present,dstnc,output_varname):
   # I want to format it nicely, like
   # variable_name_REGION = "The following countries and years are missing for this region: Belarus (1990-1991), Russian Federation (1990-1991), Ukraine (1990-1991)"
   
   formatted_region_missing={}
   for ccode in country_region_data.keys():
      # What if a country has missing years?
      formatted_region_missing[ccode]=""
   #endfor

   for region_code in data_present.keys():

      print("data present ",region_code,data_present[region_code].shape,len(timeaxis.values))
      if data_present[region_code].shape[0] != len(timeaxis.values):
         print("I seem to have the wrong timeaxis here!")
         print("Length of timeaxis: ",len(timeaxis.values))
         print("Shape of data_present: ",data_present[region_code].shape,region_code)
         traceback.print_stack(file=sys.stdout)
         sys.exit(1)
      #endif

      # data_present a nyears,ncoutries array with True and False.  False means that data is missing for that year and
      # that composant country.
   
      print("Analyzing missing data for {}.".format(country_region_data[region_code].long_name))
      #print("Composant countries: ",country_region_data[region_code].composant_countries)
      
      info_string="The following countries and years are missing for this region:"

      # This dictionary will hold all the years each country is missing.
      country_missing={}
      for ccode in country_region_data[region_code].composant_countries:
         country_missing[ccode]=[]
      #endfor
   
      for icode,ccode in enumerate(country_region_data[region_code].composant_countries):
         # Do we have any missing data?
         temp_array=data_present[region_code]
         if not temp_array[:,icode].all():
            
            years_string="("
            #print("missing data for ",ccode)
            #print(temp_array[:,icode])
            lstart=True
            years_missing=[]
            for itime in range(len(timeaxis.values[:])):
               if not temp_array[itime,icode]:
                  # Year is missing.
                  years_missing.append(timeaxis.year_values[itime])
               #endif
            #endfor
            # Remove duplicates
            years_missing=set(years_missing)
            for year in years_missing:
               if lstart:
                  years_string=years_string + "{}".format(year)
                  previous_year=year
                  previous_start_year=year
                  lstart=False
               else:
                  if year-previous_year != 1:
                     if previous_year == previous_start_year:
                        years_string=years_string + ",".format(previous_year)
                     else:
                        years_string=years_string + "-{},".format(previous_year)
                     #endif
                     lstart=True
                  #endif
                  previous_year=year
               #endif
            #endfor
            if previous_year == previous_start_year:
               years_string=years_string + ",".format(previous_year)
            else:
               years_string=years_string + "-{})".format(previous_year)
            #endif
            ### Do I need this to clean up?
            #if len(country_missing[ccode]) == 1:
            #    p=re.compile(',$')
            #    years_string=re.sub(p,')',years_string)
            ##endif
            ###
            info_string=info_string + " {} {},".format(country_region_data[ccode].long_name,years_string) 
            #print(years_string)

         #endif
      #endfor
      #print(info_string)

      # If there is no trailing comma, no countries are missing and
      # we don't have to write anything.
      p=re.compile(',$')
      m=p.search(info_string)
      if m:
         # Strip off the trailing comma
         info_string=re.sub(p,'',info_string)
         attname=output_varname+"_{}".format(region_code.replace(" ","_"))

         dstnc.setncatts({attname: info_string})
         
         print(country_region_data[region_code].long_name)
         print(attname," : ",info_string)
      #endif

   #endfor

#enddef

#############################################################

#############################################################
### The start of the main program                        ###
#############################################################

try:
   path=sys.argv[1]
   path_out=sys.argv[2]
except:
   path=""
#endtry
if path == "":
   print("Need to specify both an input path/file and a place to put the new files.")
   print("python calc_ecoregts.py PATH PATH_OUT")
   sys.exit()
else:
   print("**************************************************************")
   print("Input path: " + path)
   print("Output path: " + path_out)
   print("**************************************************************")
#endif

# If there is no third argument, assume we are just using
# the country masks from the EU.  If there is a third argument (with
# any value), look for the map of 256 countries across the world.
try:
   region_flag=sys.argv[3]
except:
   region_flag="eu"
#endif

if region_flag.lower() in ["eu","eu27+uk"]:
   print("Using the mask file for the EU.")

   # Notice the filename now includes the extents of the grid so that
   # the script can process the same size grid if they are different lat/lons
   # path to OLD country mask files regridded to different input resolutions
   #path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/eurocomCountryMask%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   # For the NEW, extended masks.  
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/extended_eurocomCountryMask%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"

   # path to OLD country mask file to be regridded to each input resolution
   #path_mask = "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/eurocomCountryMaskEEZ_0.1x0.1.nc"
   # This is for the NEW mask
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/extended_country_region_masks_0.1x0.1.nc"

   print("Country mask file: ",path_mask)

   region_tag="EU"

elif region_flag.lower() in ["glob","global"]:
   print("Using the mask file for countries outside the EU.")

   # Notice the filename now includes the extents of the grid so that
   # the script can process the same size grid if they are different lat/lons
   #path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/gadm36_0.1deg_16countries_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   #path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/gadm36_0.1deg_16countries.nc"

   # This is for the mask with EU and non-EU together on the same grid
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/EU_16othercountries_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/EU_16othercountries.nc"
   region_tag="Global"
elif region_flag.lower() in ["afr","africa"]:
   print("Using the mask file for Africa.")
   #TRYING A NEW MASK FILE FOR AFRICA
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/african_global_country_region_masks_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/african_global_country_region_masks_0.1x0.1.nc"
   region_tag="Africa"
   
elif region_flag.lower() in ["all_countries_regions","allcountriesregions"]:
   print("Using the mask file for all countries and regions.")

   #TRYING A NEW MASK FILE FOR ALL REGION
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/all_countries_and_regions_masks_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/all_countries_and_regions_masks_0.1x0.1.nc"
   region_tag="AllCountriesRegions"
   
elif region_flag.lower() in ["test"]:

   # a file with just a single country for testing
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/test_masks_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/test_country_region_masks_0.1x0.1.nc"
   region_tag="Test"
  
else:
   print("Do not know which mask file to use!")
   sys.exit(1)
#endif
print("Country mask file: ",path_mask)

# variable names to be processed as country means : CountryTot = sum(data * area * fraction) / sum(area * fraction)
means = ["tas", "pr", "rsds", "mrso", "mrro", "evapotrans", "transpft", "landCoverFrac", "lai","FCO2_FL_REMAIN_ERR","FCO2_LULUCF_TOT_ERR","FCO2_FL_CONVERT_ERR","FCO2_CL_REMAIN_ERR","FCO2_CL_CONVERT_ERR","FCO2_GL_REMAIN_ERR","FCO2_GL_CONVERT_ERR","FCO2_WL_REMAIN_ERR","FCO2_WL_CONVERT_ERR","FCO2_SL_REMAIN_ERR","FCO2_SL_CONVERT_ERR","FCO2_OL_REMAIN_ERR","FCO2_OL_CONVERT_ERR","FCO2_HWP_ERR","FCH4_EMIS_CRP_RELERR","FN2O_EMIS_CRP_RELERR"]
# variable names to be processed as country sums : CountryTot = sum(data)
sums = ["CO2", "FOREST_AREA", "GRASSLAND_AREA", "CROPLAND_AREA", "AREA", "FCH4_EMIS_CRP","FCH4_EMIS_CRP_ABSERR","FN2O_EMIS_CRP","FN2O_EMIS_CRP_ABSERR"]
# all other variables are proccessed as country totals : CountryTot = sum(data * area * fraction)

#code_size=3

# possible netcdf variable names for time/lat/lon
timenames = set(["time", "year"])
latnames = set(["lat", "latitude", "south_north"])
lonnames = set(["lon", "longitude", "west_east"])

ncmask = netCDF4.Dataset(path_mask)
clat = ncmask.variables["latitude"][:]
clon = ncmask.variables["longitude"][:]
cmask = ncmask.variables["country_mask"][:]
cname = ncmask.variables["country_name"][:]
ccode = ncmask.variables["country_code"][:]
#print("nvkds ",nc.dimensions)
#print("nvkds ",nc.dimensions.keys())
#mask_file_dimensions=list(nc.dimensions.keys())
#nc.close()
cgrid = Grid(lat = clat, lon = clon)

###################################
# It seems to be very important that the mask file does not have nan values,
# only values between 0 and 1.  Check for that.
if np.isnan(cmask.min()) or np.isnan(cmask.max()):
   print("Mask file must not have NaN values!  Please redo it so that")
   print("all values are between 0 and 1.")
   print("Min value: ",cmask.min())
   print("Max value: ",cmask.max())
   for icountry in range(cmask.shape[0]):
      if np.isnan(cmask.min()):
         print(icountry,cname[icountry],cmask[icountry,:,:].min(),cmask[icountry,:,:].max())
      #endif
   #endfor
   sys.exit(1)
#endif
###################################

##################################
# Calculate the area of every country in the mask file.
print("Calculating mask file area.")
country_region_areas=[]
cname_mask=[]
ccode_mask=[]
## Run this if you change the mask file
#calculate_country_areas()
#####
country_region_areas=get_country_areas()
for icount in range(cmask.shape[0]):
   #area=np.ma.where(cmask[icount].mask == False, cmask[icount] * cgrid.area, 0).sum(axis=(-1,-2))
   #country_region_areas.append(area)
   cname_mask.append("".join([letter.decode('utf-8') for letter in cname[icount] if letter is not np.ma.masked]))
   ccode_mask.append("".join([letter.decode('utf-8') for letter in ccode[icount] if letter is not np.ma.masked]))
   # Convert the bytes into strings

   if ccode_mask[-1] in country_region_areas.keys():
      print(" Area for {} ({}): {} m**2".format(cname_mask[-1],ccode_mask[-1],country_region_areas[ccode_mask[-1]]))
   else:
      print("--> Could not find {} in country_region_areas.".format(ccode_mask[-1]))
      print("--> Likely a country/region that no longer exists.")
   #endif
#endfor

# Information about all our countries and regions
country_region_data=get_country_region_data()
##################################

#### 2D files to skip (see above note):
skip_files=["Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_2D.nc","Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_2D.nc","Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V2_20201221_PETRASCU_WPX_2D.nc","Tier1_CO2_HWP_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_OtherRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_WetlandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_SettlementRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_2D.nc","Tier3BUPB_CO2_LandFlux_BLUE-2019-HILDA_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithEEZ.nc","Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_2D.nc","Tier3BUPB_CO2_LandFlux_BLUE-2019-HILDA_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_2D.nc","Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20201026_PETRESCU_WPX_2D.nc","Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_2D.nc","Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20201103_SCHELHAAS_WPX_2D.nc","Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_2D.nc","Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20200601_SCHELHAAS_WPX_2D.nc","Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_2D.nc"]


for item in [path] if path.endswith(".nc") else [os.path.join(path, filename) for filename in os.listdir(path)]:

    possible_endings=["2D.nc","2Dmod.nc","TempCT.nc"]
    current_ending=None
    for ending in possible_endings:
       if item.endswith(ending):
          current_ending=ending
       #endif
    #endfor
    if not current_ending:
       continue
    #endif

    # The filename may be preceded by a directory.
    itemlist=item.split("/")
    if itemlist[-1] in skip_files:
       print("******************")
       print("Known problem creating a CountryTot from this file: ",item)
       print("Skipping.")
       print("******************")
       continue
    #endif

    ######################
    # This is a special case.  These files are created directly from
    # Excel spreadsheets or .csv file.  It wasn't possible to create
    # a normal 2D.nc file from these with reasonable size and accuracy,
    # so we came up with this compromise.  The 2Dmod/TempCT file is essentially
    # a CountryTot file, but only with countries.  This scripts just
    # puts the countries in the same order as we want for the CountryTot,
    # and also combines the countries into the regions we want.
    if item.endswith("2Dmod.nc") or item.endswith("TempCT.nc"):
       print("On intermediate country total file file: ",item)

       # I still want to create an EEZ and non-EEZ file, but they
       # will be identical.
       pathEEZ = os.path.join(path_out, os.path.split(item)[-1].replace(current_ending, "CountryTotWithEEZ"+region_tag+".nc"))
       pathNoEEZ = os.path.join(path_out, os.path.split(item)[-1].replace(current_ending, "CountryTotWithOutEEZ"+region_tag+".nc"))

       if os.path.exists(pathEEZ) or os.path.exists(pathNoEEZ):
          print(pathEEZ, pathNoEEZ)
          print("File exists!  Not overwriting.")
          continue
       #endif

       # Create a time axis that we will use with missing data to know
       # the years.
       timeaxis=create_time_axis_from_netcdf(item)

       srcnc = netCDF4.Dataset(item)

       for newpath in [pathEEZ, pathNoEEZ]:

          # For this file, there really should only be a few dimensions.
          # time, country, strlength, something for the time_bounds
          print("Create", newpath)
          strlength_names=set(["strlength","len_name"])
          strlength_name=list(strlength_names.intersection(ncmask.dimensions.keys()))[0]
          strlength_size=ncmask.dimensions[strlength_name].size
          nb2_names=set(["nb2"])
          nb2_name=list(nb2_names.intersection(srcnc.dimensions.keys()))[0]
          nb2_size=srcnc.dimensions[nb2_name].size
          ncout = netCDF4.Dataset(newpath, "w")
          ncout.createDimension(strlength_name, strlength_size)
          ncout.createDimension(nb2_name, nb2_size)
          ncout.createDimension("country", ccode.shape[0])
          countryvar="country"
          # Time dimension comes from the 2Dmod.nc file, not the mask file
          if len(timenames.intersection(srcnc.dimensions.keys())) == 0:
             timedim = timevar = ""
          else:
             timedim = list(timenames.intersection(srcnc.dimensions.keys()))[0]
             timevar = list(timenames.intersection(srcnc.variables.keys()))[0]
             timebounds_names=set(["time_bounds"])
             timeboundsvar=list(timebounds_names.intersection(srcnc.variables.keys()))[0]
          #endif
          if timedim != "": ncout.createDimension(timedim, None)
          # We should only have three dimensions in this file, I believe.
          #for dim in set(ncmask.dimensions.keys()).intersection(["strlength","country"]):
          #   ncout.createDimension(dim, ncmask.dimensions[dim].size)
          #endfor

          # These two character arrays are a little special.  They may not
          # always be the same size for the strings.
          varnames=["country_name","country_code"]
          for var in varnames:
             ncout.createVariable(var, "S1", (countryvar, strlength_name))
             ncout.variables[var].setncatts(ncmask.variables[var].__dict__)
             if ncout.variables[var].shape == ncmask.variables[var].shape:
                ncout.variables[var][:] = ncmask.variables[var][:]
             else:
                print("Different shapes ",var,ncout.variables[var].shape,ncmask.variables[var].shape)
                # Sometimes the string length is 3, sometimes 50
                # The first dimension should always be the same.
                for idx in range(ncmask.variables[var].shape[0]):
                   for jdx in range(min([ncout.variables[var].shape[1],ncmask.variables[var].shape[1]])):
                      if ncmask.variables[var][idx, jdx] is not np.ma.masked:
                         ncout.variables[var][idx, jdx]=ncmask.variables[var][idx, jdx]
                      #endif
                   #endfor
                #endfor
             #endif
          #endfor

          if timevar != "":
             ncout.createVariable(timevar, srcnc.variables[timevar].dtype, (timedim,))
             ncout.variables[timevar].setncatts(srcnc.variables[timevar].__dict__)
             ncout.variables[timevar][:] = srcnc.variables[timevar][:]
             ncout.createVariable(timeboundsvar, srcnc.variables[timeboundsvar].dtype, (timedim,nb2_name))
             ncout.variables[timeboundsvar].setncatts(srcnc.variables[timeboundsvar].__dict__)
             ncout.variables[timeboundsvar][:] = srcnc.variables[timeboundsvar][:]
          #endif

          # Now we take variables from the current 2Dmod.nc file
          # But only those with a time,country dimensions
#          for var in set(srcnc.variables.keys()).difference(["country","longitude","latitude","component_countries","country_code","country_name",timevar,timeboundsvar]):
          for var in srcnc.variables.keys():
             if srcnc[var].dimensions != (timevar,countryvar):
                continue
             #endif
             print("Copying over countries and regions for: ",var)

             # We need to propagate uncertainties properly across
             # regions, which means first converting to absolute
             # uncertainties from relative uncertainties.
             # Check to see:
             #    1) Is this a relative uncertainty?
             #    2) Do we have the variable needed to convert to aboslute?
             
             lpropagate=False
             m=re.search(r"(.+)_ERR",var)
             emission_variable_name=None
             if m:

                print("Found uncertainty: ",m[0])
                if m[1] in srcnc.variables.keys():
                   print("Found emission variable: ",m[1])
                   emission_variable_name=m[1]
                else:
                   print("****************************************")
                   print("Cannot find emission variable for this uncertainty.")
                   print(srcnc.variables.keys())
                   print("Stopping.")
                   print("****************************************")
                   traceback.print_stack(file=sys.stdout)
                   sys.exit(1)
                #endif

                # Is it a relative uncertainty?
                lfound=False
                lrelative=False
                try:
                   srcnc.variables[var].units
                   lfound=True
                except:
                   print("Did not find units for this variable.")
                   print("Assuming relative uncertainty.")
                   lfound=False
                   lrelative=True
                #endtry
                
                if lfound:
                   if srcnc.variables[var].units in ["%"]:
                      print("Found relative uncertainties.")
                   else:
                      print("Not sure about this uncertainty.")
                      print("Please check this script.")
                      print("Stopping early.")
                      print("****************************************")
                      traceback.print_stack(file=sys.stdout)
                      sys.exit(1)
                   #endif
                #endif

                # So now we know that we have a relative uncertainty and
                # all the tools we need to propagate it.
                lpropagate=True

             #endif

             # Create the variable
             ncout.createVariable(var, srcnc.variables[var].dtype, srcnc.variables[var].dimensions)
             ncout.variables[var].setncatts(srcnc.variables[var].__dict__)

             # Initialize an array that we will use to tell us what
             # is missing for every region.  This is a little more difficult
             # to process since we have monthly timesteps here, but
             # I'll deal with that later.
             data_present={}
             ntimesteps=srcnc[var][:,:].shape[0]
             for mcode in ccode_mask:
                # What if we have a country which is missing a few years?
                # That is also good to know.
                #if country_region_data[mcode].is_country:
                #   continue
                #endif
                data_present[mcode]=np.zeros((ntimesteps,len(country_region_data[mcode].composant_countries)))
             #endif

             # For every line in the mask file, loop through all
             # the codes for the component countries.  If I find something,
             # add it.  The component_countries in the mask file gives
             # the index of the countries in the mask file, but I need
             # to find the index of the countries in the src file.
             # Note that I don't need to avoid regions that already have
             # data, such as the EU27+UK, since I will overwrite those
             # with a different script.
             for ireg,mcode in enumerate(ccode_mask):
##### TESTING
#             for ireg,mcode in zip([62],['CEE']):
                print("Creating region: ",mcode)
                timeseries_total=np.zeros((len(srcnc.variables[timevar][:])))
                total_surface_area=0.0
                total_emissions=np.zeros((len(srcnc.variables[timevar][:])))

                # Loop over all the component countries in this region.
                for icomp,ccomp in enumerate(country_region_data[mcode].composant_countries):
                   print('feklj ',ireg,mcode,ccomp,icomp)
                   if ncmask["component_countries"][ireg,icomp] is not np.ma.masked:
                      iindex=ncmask["component_countries"][ireg,icomp]
                      #comp_code=b"".join([letter for letter in ccode[iindex] if letter is not np.ma.masked])
                      # Find this code in the source file that we are
                      # working on
                      for jreg in range(srcnc["country_code"][:].shape[0]):
                         test_code="".join([letter.decode('utf-8') for letter in srcnc["country_code"][jreg] if letter is not np.ma.masked])
#                         print("jfioew ",jreg,test_code,ccomp,test_code == ccomp)
                         if test_code == ccomp:

                            data_present[mcode][:,icomp]=~np.isnan(srcnc[var][:,jreg])
                            
                            # If values are NaN, set them equal to zero before
                            # adding.
                            # Will this mess up our weighting by
                            # country area for the region?
                            timeseries_temp=np.isnan(srcnc[var][:,jreg])
                            #if mcode == "E28":
                            #   print("DEBUG BEFORE: {}, {} - ".format(mcode,ccomp),timeseries_temp)
                            #   print(timeseries_total)
                            #endif
                            timeseries_temp=np.where(timeseries_temp,0.0,srcnc[var][:,jreg])

                            #if mcode == "E28":
                            #   print("DEBUG: {}, {} - ".format(mcode,ccomp),timeseries_temp)
                            #   print(timeseries_total)
                            #endif

                            # We need to do something special in the case
                            # of error variables: we need to propogate
                            # them to the regions.  In other words, we
                            # need to first convert them into aboslute
                            # errors by multiplying by the non-error
                            # variable of the same name.  In theory, I've
                            # designed all of this so that VAR and VAR_ERR
                            # should match up, and VAR_ERR should be a
                            # percentage (e.g., 15.0 for 15%).
                            if lpropagate:
                               print("nkdsd ",emission_variable_name,jreg)
                               emissions_timeseries_temp=np.isnan(srcnc[emission_variable_name][:,jreg])
                               emissions_timeseries_temp=np.where(emissions_timeseries_temp,0.0,srcnc[emission_variable_name][:,jreg])

                               lvalues=~np.isnan(emissions_timeseries_temp)
                               timeseries_total=np.where(lvalues,timeseries_total+(timeseries_temp/100.0*emissions_timeseries_temp)**2,np.nan)
                               total_emissions=np.where(lvalues,total_emissions+emissions_timeseries_temp,np.nan)
                               print("Propogating uncertainty: ",test_code,var)
#                               print('nvioewe COUNTRY ',jreg,srcnc["country_code"][jreg])
#                               print("UNCERTAINTY ",timeseries_temp[-1])
#                               print('EMISSIONS ',emissions_timeseries_temp[-1])


                            elif var in means:
                               print("Adding component mean: ",test_code,var)
                               # Need to find the area of this country.  

                               # Weight by the surface area of the region
                               timeseries_total=timeseries_total+timeseries_temp*country_region_areas[test_code]
                               total_surface_area=total_surface_area+country_region_areas[test_code]
                            else:
                               print("Adding component not mean: ",test_code,var)
                               timeseries_total=timeseries_total+timeseries_temp
                            #endif
                         #endif
                      #endfor
                   #endif
                #endfor

                # For a variable that is a mean for a region, I weight
                # it by the area of each country (i.e., temperature).  For
                # other variables, I just sum up the totals from each country
                if lpropagate:
                   ncout[var][:,ireg]=np.sqrt(timeseries_total/total_emissions**2)*100.0
                   #print("nvioew REGION ",ireg,ncout[var][:,ireg])
                   #print("nvioew TIMESERIES ",timeseries_total[-1])
                   #print("nvioew EMISSIONS ",total_emissions[-1])

                   # I want all uncertainties to be a single value.
                   # Taking the final value.
                   lfound=False
                   for iyear in range(len(ncout[var][:,ireg])-1,-1,-1):
                      if lfound:
                         continue
                      else:
                         if lvalues[iyear]:
                            lfound=True
                            ncout[var][:,ireg]=ncout[var][iyear,ireg]
                         #endif
                      #endif
#                   if mcode == "WEE":
#                      sys.exit(1)
#                   #endif
                elif var in means:
                   ncout[var][:,ireg]=timeseries_total/total_surface_area
                else:
                   ncout[var][:,ireg]=timeseries_total
                #endif
             
             #endfor

             print_missing_region_information(timeaxis,country_region_data,data_present,ncout,var)
#             print("fioew STPPING")
#             sys.exit(1)
          #endfor

          # And copy over the metadata
          ncout.setncatts(srcnc.__dict__)
          ncout.setncatts({'CountryTot_file_processing' : 'Created from the corresponding _2D.nc file using the script calc_ecoregts_v2.py.\nThe following variables are averaged (mean): {}   The following variables are summed across all pixels without modification: {}  Every other variable is multiplyied by the area of the pixel and the fraction of the pixel occupied by that country and then summed.'.format(means,sums)})
          ##
          ncout.close()
       #endfor

       srcnc.close()

       continue

    #endif
       

    #################################
    # Now back to the normal 2D files.
    #################################
    print("On file: ",item)
    pathEEZ = os.path.join(path_out, os.path.split(item)[-1].replace("_2D", "_CountryTotWithEEZ"+region_tag))
    pathNoEEZ = os.path.join(path_out, os.path.split(item)[-1].replace("_2D", "_CountryTotWithOutEEZ"+region_tag))
    if os.path.exists(pathEEZ) or os.path.exists(pathNoEEZ):
        print(pathEEZ, pathNoEEZ)
        #try:
        #   if input("Files exist! Overwrite (y/n)? ").upper() != "Y": continue
        #except:
        print("File exists!  Not overwriting.")
        continue
        #endtry
    #endif

    nc = netCDF4.Dataset(item)
    if len(timenames.intersection(nc.dimensions.keys())) == 0:
        timedim = timevar = ""
    else:
        timedim = list(timenames.intersection(nc.dimensions.keys()))[0]
        timevar = list(timenames.intersection(nc.variables.keys()))[0]
    #endif
    latdim = list(latnames.intersection(nc.dimensions.keys()))[0]
    latvar = list(latnames.intersection(nc.variables.keys()))[0]
    londim = list(lonnames.intersection(nc.dimensions.keys()))[0]
    lonvar = list(lonnames.intersection(nc.variables.keys()))[0]
    lat = nc.variables[latvar][:]
    lon = nc.variables[lonvar][:]
    nlat = len(lat)
    nlon = len(lon)
    print("%sx%s" % (nlat, nlon))
    slat=lat[0]
    elat=lat[-1]
    slon=lon[0]
    elon=lon[-1]
    if slat < 0.0:
       slat="{:.2f}S".format(abs(slat))
    else:
       slat="{:.2f}N".format(slat)
    #endif
    if elat < 0.0:
       elat="{:.2f}S".format(abs(elat))
    else:
       elat="{:.2f}N".format(elat)
    #endif
    if slon < 0.0:
       slon="{:.2f}W".format(abs(slon))
    else:
       slon="{:.2f}E".format(slon)
    #endif
    if elon < 0.0:
       elon="{:.2f}W".format(abs(elon))
    else:
       elon="{:.2f}E".format(elon)
    #endif

    print("Spatial extent: ",slat,elat,slon,elon)

    if not os.path.exists(path_regs % dict(nlat=nlat, nlon=nlon,slat=slat,elat=elat,slon=slon,elon=elon,EEZ='EEZ')):
        print("Building regridded file: ",path_regs % dict(nlat=nlat, nlon=nlon,slat=slat,elat=elat,slon=slon,elon=elon,EEZ='EEZ'))

        grid = Grid(lat = lat, lon = lon)
        cgrid.setRegrid(grid)
        newmask = cgrid.regrid(cmask)

        ncreg = netCDF4.Dataset(path_regs % dict(nlat=nlat, nlon=nlon,slat=slat,elat=elat,slon=slon,elon=elon,EEZ='EEZ'), "w")
        print("ncreg :: {} :: {} :: {}".format(nlon,nlat,len(cmask)))
        ncreg.createDimension("lon", nlon)
        ncreg.createDimension("lat", nlat)
        ncreg.createDimension("country", len(cmask))
        strlength_size=50
        ncreg.createDimension("strlength", strlength_size)
        ncreg.createVariable("country_code", "S1", ("country", "strlength"))
        ncreg.createVariable("country_name", "S1", ("country", "strlength"))
        ncreg.createVariable("lon", "f4", ("lon",))
        ncreg.createVariable("lat", "f4", ("lat",))
        ncreg.createVariable("area", "f4", ("lat", "lon"))
        ncreg.createVariable("country_mask", "f4", ("country", "lat", "lon"))
        ncreg.variables["lon"][:] = lon
        ncreg.variables["lat"][:] = lat
        ncreg.variables["area"][:] = grid.area
        ncreg.variables["country_mask"][:] = newmask.filled(0)

        for idx in range(cmask.shape[0]): 
            for jdx in range(len(ccode[idx])):
                if ccode[idx, jdx] is not np.ma.masked:
                    ncreg.variables["country_code"][idx, jdx] = ccode[idx, jdx]
                #endif
            #endfor
               
            for jdx in range(len(cname[idx])):
                if cname[idx, jdx] is not np.ma.masked:
                    ncreg.variables["country_name"][idx, jdx] = cname[idx, jdx]
                #endif
            #endfor
        #endfor

        ncreg.close()
    else:
        print("Using regridded file: ",path_regs % dict(nlat=nlat, nlon=nlon,slat=slat,elat=elat,slon=slon,elon=elon,EEZ='EEZ'))
    #endif

    ncreg = netCDF4.Dataset(path_regs % dict(nlat=nlat, nlon=nlon,slat=slat,elat=elat,slon=slon,elon=elon,EEZ='EEZ'))
    reglat = ncreg.variables["lat"][:]
    reglon = ncreg.variables["lon"][:]
    regmaskEEZ = ncreg.variables["country_mask"][:].filled(0)
    regcode = ncreg.variables["country_code"][:]
    regname = ncreg.variables["country_name"][:]
    regarea = ncreg.variables["area"][:]


    ncreg.close()

    # create regmask copy with filtered ocean pixels
    reglons, reglats = np.meshgrid(reglon, reglat)
    regmaskNoEEZ = np.zeros_like(regmaskEEZ)
    for idx in range(len(regmaskEEZ)):
        countryname=b"".join([letter for letter in regname[idx] if letter is not np.ma.masked])
        print("Making mask without EEZ for {}".format(countryname))
        regmaskNoEEZ[idx] = maskoceans(reglons, reglats, regmaskEEZ[idx], inlands = False, resolution = "f", grid = 1.25).filled(0)

    if not np.allclose(lat, reglat) or not np.allclose(lon, reglon): raise Exception

    for newpath, regmask in zip([pathEEZ, pathNoEEZ], [regmaskEEZ, regmaskNoEEZ]):
        print("Create", newpath)
        strlength_size=50
        ncout = netCDF4.Dataset(newpath, "w")
        ncout.createDimension("country", len(regmask))
        if timedim != "": ncout.createDimension(timedim, None)
        ncout.createDimension("strlength", strlength_size)
        for dim in set(nc.dimensions.keys()).difference([latdim, londim, timedim]):
            ncout.createDimension(dim, nc.dimensions[dim].size)

        ncout.createVariable("country_code", "S1", ("country", "strlength"))
        ncout.createVariable("country_name", "S1", ("country", "strlength"))
        if timevar != "":
            ncout.createVariable(timevar, nc.variables[timevar].dtype, (timedim,))
            ncout.variables[timevar].setncatts(nc.variables[timevar].__dict__)
            ncout.variables[timevar][:] = nc.variables[timevar][:]

        for var in set(nc.variables.keys()).difference([latvar, lonvar, timevar]):
            if var.startswith(lonvar) or var.startswith(latvar): continue
            print("var",var)
            if not nc.variables[var].dimensions[-2:] == tuple([latdim, londim]):
                ncout.createVariable(var, nc.variables[var].dtype, nc.variables[var].dimensions)
                ncout.variables[var].setncatts(nc.variables[var].__dict__)
                ncout.variables[var][:] = nc.variables[var][:]
            else:
                ncout.createVariable(var, "f4", tuple(list(nc.variables[var].dimensions[:-2]) + ["country"]))
                for key,value in nc.variables[var].__dict__.items():
                    if key in ["_FillValue", "missing_value"]: continue
                    if key == "units" and var not in means: wvalue = value.replace("m-2", "").replace("m2", "").replace("m^2", "").replace("m^-2", "").replace("  "," ").replace("//","/").strip()
                    elif key == "longname" or key == "long_name":
                        if var in means: wvalue = value + " (country mean)"
                        elif var in sums: wvalue = value + " (country sum)"
                        else: wvalue = value + " (country total)"
                        print("wvalue: ",wvalue)
                    else: wvalue = value
                    ncout.variables[var].setncattr(key, wvalue)

                data = np.ma.masked_invalid(nc.variables[var][:])
                print("data shape: ",data.shape, data.min(), data.max())

                for idx in range(len(regmask)):
                    
                    ncout.variables["country_code"][idx] = regcode[idx]
                    ncout.variables["country_name"][idx] = regname[idx]
                    if var in sums:
                        ncout.variables[var][:,idx] = (data * regmask[idx]).sum(axis=(-1,-2))
                    else:
                        if len(data.shape) < 4:
                            if var in means: 
                               ncout.variables[var][...,idx] = (data * regmask[idx] * regarea).sum(axis=(-1,-2)) / np.ma.where(data.mask == False, regmask[idx] * regarea, 0).sum(axis=(-1,-2))
                            else: 
                               ncout.variables[var][...,idx] = (data * regmask[idx] * regarea).sum(axis=(-1,-2))

                               # Only good to print this for small numbers
                               # of pixels (used for testing in specific cases)
                               #if ccode == "LIE":
                               if False:
                                  print('ON LICHTENSTEIN: ',data.shape)
                                  for ilat in range(data.shape[-2]):
                                     print("iure ",ilat,data.shape[-2])
                                     for ilon in range(data.shape[-1]):
                                        imonth=0
                                        #for imonth in range(data.shape[0]):
                                        if data[imonth,ilat,ilon] is not np.ma.masked and not np.isnan(data[imonth,ilat,ilon]):
                                           print("jiefo ",imonth,ilat,ilon,data[imonth,ilat,ilon],regmask[idx][ilat,ilon],regarea[ilat,ilon])
                                        #endif
                                        if regmask[idx][ilat,ilon] is not np.ma.masked and not np.isnan(regmask[idx][ilat,ilon]) and regmask[idx][ilat,ilon] != 0.0:
                                           print("mask jiefo ",ilat,ilon,reglat[ilat],reglon[ilon],regmask[idx][ilat,ilon])
                                           print("mask jiefo2 ",imonth,data[imonth,ilat,ilon],regarea[ilat,ilon])
                                        #endif
                                     #endfor
                                  #endfor
                                  #print("finishing early")
                                  #sys.exit(1)
                               #endif

                        else:
                            for jdx in range(data.shape[1]):
                                print(jdx)
                                if var in means: ncout.variables[var][:,jdx,idx] = (data[:,jdx,:,:] * regmask[idx] * regarea).sum(axis=(-1,-2)) / np.ma.where(data[:,jdx,:,:].mask == False, regmask[idx] * regarea, 0).sum(axis=(-1,-2))
                                else: ncout.variables[var][:,jdx,idx] = (data[:,jdx,:,:] * regmask[idx] * regarea).sum(axis=(-1,-2))
        # Copy all the global attributes, and add a new one
        ncout.setncatts(nc.__dict__)
        ncout.setncatts({'CountryTot_file_processing' : 'Created from the corresponding _2D.nc file using the script calc_ecoregts_v2.py.\nThe following variables are averaged (mean): {}   The following variables are summed across all pixels without modification: {}  Every other variable is multiplyied by the area of the pixel and the fraction of the pixel occupied by that country and then summed.'.format(means,sums)})
        ##
        ncout.close()

    nc.close()
print("Finished normally.  ",path_mask)

