 #!/usr/bin/env python
import numpy as np, netCDF4, os
from mpl_toolkits.basemap import maskoceans
from grid import Grid
import sys

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
# to CountryTot files.

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

   #TRYING A NEW MASK FILE FOR AFRICA
   path_regs = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/african_global_country_region_masks_%(EEZ)s_%(nlat)sx%(nlon)s_%(slat)s%(elat)s_%(slon)s%(elon)s.nc"
   path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/african_global_country_region_masks_0.1x0.1.nc"
   region_tag="Africa"
   
elif region_flag.lower() in ["all_countries_regions"]:

   #TRYING A NEW MASK FILE FOR AFRICA
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
means = ["tas", "pr", "rsds", "mrso", "mrro", "evapotrans", "transpft", "landCoverFrac", "lai","FCO2_FL_REMAIN_ERR","FCO2_LULUCF_TOT_ERR","FCO2_FL_CONVERT_ERR","FCO2_CL_REMAIN_ERR","FCO2_CL_CONVERT_ERR","FCO2_GL_REMAIN_ERR","FCO2_GL_CONVERT_ERR","FCO2_WL_REMAIN_ERR","FCO2_WL_CONVERT_ERR","FCO2_SL_REMAIN_ERR","FCO2_SL_CONVERT_ERR","FCO2_OL_REMAIN_ERR","FCO2_OL_CONVERT_ERR","FCO2_HWP_ERR"]
# variable names to be processed as country sums : CountryTot = sum(data)
sums = ["CO2", "FOREST_AREA", "GRASSLAND_AREA", "CROPLAND_AREA", "AREA"]
# all other variables are proccessed as country totals : CountryTot = sum(data * area * fraction)

#strlength_size=50
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
for icount in range(cmask.shape[0]):
   area=np.ma.where(cmask[icount].mask == False, cmask[icount] * cgrid.area, 0).sum(axis=(-1,-2))
   country_region_areas.append(area)
   cname_mask.append(b"".join([letter for letter in cname[icount] if letter is not np.ma.masked]))
   ccode_mask.append(b"".join([letter for letter in ccode[icount] if letter is not np.ma.masked]))
   print(" Area for {} ({}): {} m**2".format(cname_mask[-1],ccode_mask[-1],country_region_areas[-1]))
#endfor
##################################

for item in [path] if path.endswith(".nc") else [os.path.join(path, filename) for filename in os.listdir(path)]:
    if not item.endswith("2D.nc") and not item.endswith("2Dmod.nc"): 
       continue
    #endif

    ######################
    # This is a special case.  These files are created directly from
    # Excel spreadsheets or .csv file.  It wasn't possible to create
    # a normal 2D.nc file from these with reasonable size and accuracy,
    # so we came up with this compromise.  The 2Dmod file is essentially
    # a CountryTot file, but only with countries.  This scripts just
    # puts the countries in the same order as we want for the CountryTot,
    # and also combines the countries into the regions we want.
    if item.endswith("2Dmod.nc"):
       print("On modified 2D file: ",item)

       # I still want to create an EEZ and non-EEZ file, but they
       # will be identical.
       pathEEZ = os.path.join(path_out, os.path.split(item)[-1].replace("_2Dmod", "_CountryTotWithEEZ"+region_tag))
       pathNoEEZ = os.path.join(path_out, os.path.split(item)[-1].replace("_2Dmod", "_CountryTotWithOutEEZ"+region_tag))
       if os.path.exists(pathEEZ) or os.path.exists(pathNoEEZ):
          print(pathEEZ, pathNoEEZ)
          print("File exists!  Not overwriting.")
          continue
       #endif

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

             ncout.createVariable(var, srcnc.variables[var].dtype, srcnc.variables[var].dimensions)
             ncout.variables[var].setncatts(srcnc.variables[var].__dict__)

             # For every line in the mask file, loop through all
             # the codes for the component countries.  If I find something,
             # add it.  The component_countries in the mask file gives
             # the index of the countries in the mask file, but I need
             # to find the index of the countries in the src file.
             for ireg in range(ccode.shape[0]):
                ccode_mask=b"".join([letter for letter in ccode[ireg] if letter is not np.ma.masked])
                timeseries_total=np.zeros((len(srcnc.variables[timevar][:])))
                for icomp in range(ncmask["component_countries"].shape[1]):
                   if ncmask["component_countries"][ireg,icomp] is not np.ma.masked:
                      iindex=ncmask["component_countries"][ireg,icomp]
                      comp_code=b"".join([letter for letter in ccode[iindex] if letter is not np.ma.masked])
                      # Find this code in the source file that we are
                      # working on
                      for jreg in range(srcnc["country_code"][:].shape[0]):
                         test_code=b"".join([letter for letter in srcnc["country_code"][jreg] if letter is not np.ma.masked])
                         if test_code == comp_code:
                            if var in means:
                               # Need to find the area of this country.  This
                               # information comes from the mask file, so I need
                               # to find the index of this country in the mask
                               # file.
                               kreg=-1
                               for icount,code in enumerate(ccode_mask):
                                  if code == comp_code:
                                     kreg=icount
                                  #endif
                               #endfor
                               if kreg == -1:
                                  print("Was not able to find kreg code!")
                                  sys.exit(1)
                               #endif

                               # Weight by the surface area of the region
                               timeseries_total=timeseries_total+srcnc[var][:,jreg]*country_region_areas[kreg]
                               total_surface_area=total_surface_area+country_region_areas[kreg]
                            else:
                               timeseries_total=timeseries_total+srcnc[var][:,jreg]
                            #endif
                         #endif
                      #endfor
                   #endif
                #endfor

                # For a variable that is a mean for a region, I weight
                # it by the area of each country (i.e., temperature).  For
                # other variables, I just sum up the totals from each country
                if var in means:
                   ncout[var][:,ireg]=timeseries_total/total_surface_area
                else:
                   ncout[var][:,ireg]=timeseries_total
                #endif

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

