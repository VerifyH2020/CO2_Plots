import numpy as np
from datetime import date, timedelta
from calendar import isleap
import math
import netCDF4 as nc
import sys,traceback
from mpl_toolkits.basemap import maskoceans
import matplotlib as mpl
import pandas as pd


########################################################Define functions
def find_date(since19000101):
   start = date(1900,1,1)
   delta = timedelta(since19000101)
   offset = start + delta
   year=offset.year
   month=offset.month
   return year,month

def get_cumulated_array(data, **kwargs):
         cum = data.clip(**kwargs)
         cum = np.cumsum(cum, axis=0)
         d = np.zeros(np.shape(data))
         d[1:] = cum[:-1]
         return d  

def readfile(filename,variablename,ndesiredyears,lconvert_units,starting_year,ending_year,ncountries,output_units):
   # The goal of this routine is to read in a slice from starting_year
   # until ending_ear.
   # The time axes for all these files starts as days from 1900-01-01,
   # the axis itself might start at a different year (1901, 1970).
   # We need to find the indices corresponding to the year starting_year.
   # The 79 here is the number of countries and regions we have in the
   # CountryTot.nc files, so if that changes, this must change.  By hardcoding
   # it here, this serves as a check that we are using the files we think
   # we are using.
   FCO2=np.zeros((ndesiredyears,12,ncountries))*np.nan
   print("************************************************************")
   print("Reading in file: ",filename)
   print("************************************************************")
   ncfile=nc.Dataset(filename)
   FCO2_file=ncfile.variables[variablename][:].filled(fill_value=np.nan)  #kg C yr-1

   # Grab the units
   current_units=ncfile.variables[variablename].units
   print("Current units are: {}, and we want: {}".format(current_units,output_units))

   # we only need to convert units if we are not dealing with uncertainties,
   # since uncertainties are given as a fraction
   if lconvert_units:
      if current_units != output_units:
         print("Converting units from {} to {}".format(current_units,output_units))
         if output_units == "Tg C yr-1":
            if current_units in ["kg C yr-1","kg C yr-1 [country]"]:
               FCO2_TOT=FCO2_file/1e+9   #kg C/yr -->  Tg C/ year
               
            elif current_units in ["kg C"]:
               FCO2_TOT=FCO2_file/1e+9   #kg C -->  Tg C

            
            elif current_units in ["KgC h-1"]:
               FCO2_TOT=FCO2_file/1e+9*24.0*365.0   #KgC h-1 -->  Tg C yr-1
            else:
               print('***************************************')
               print("DO NOT KNOW HOW TO CONVERT THESE UNITS")
               print(current_units)
               print(output_units)
               print('***************************************')
               traceback.print_stack(file=sys.stdout)
               sys.exit(1)
            #endif
         elif output_units == "Tg N yr-1":
            if current_units in ["kg N yr-1"]:
               FCO2_TOT=FCO2_file/1e+9   #kg N/yr -->  Tg N/ year
            else:
               print('***************************************')
               print("DO NOT KNOW HOW TO CONVERT THESE UNITS")
               print(current_units)
               print(output_units)
               print('***************************************')
               traceback.print_stack(file=sys.stdout)
               sys.exit(1)
            #endif
         elif output_units == "%":
            if current_units in ["%/100","%"]:
               print("Nothing to convert here: ",output_units)
               FCO2_TOT=FCO2_file*1.0
            else:
               print('***************************************')
               print("DO NOT KNOW HOW TO CONVERT THESE UNITS")
               print(current_units)
               print(output_units)
               print('***************************************')
               traceback.print_stack(file=sys.stdout)
               sys.exit(1)
            #endif  


         else:
            print('***************************************')
            print("DO NOT KNOW HOW TO CONVERT THESE UNITS")
            print(current_units)
            print(output_units)
            print('***************************************')
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
         #endif
      else:
         print("Not changing units from file: ",ncfile.variables[variablename].units)
         FCO2_TOT=FCO2_file*1.0
         print("Shape of input array: ",FCO2_TOT.shape)
#         print("Shape of input array: ",FCO2_TOT.mask)
      #endif
   else:
      print("Not changing units from file: ",ncfile.variables[variablename].units)
      FCO2_TOT=FCO2_file*1.0
   #endif
   timeperiod=ncfile.variables['time'][:]  ##days since 1900-01-01, middle of each month
   startday=np.float(timeperiod[0]);endday=np.float(timeperiod[-1])
   startyear,startmonth=find_date(startday)  ## to convert to date 
   endyear,endmonth=find_date(endday)
   print("Timeseries starts at: {0}/{1}".format(startmonth,startyear))
   print("Timeseries starts at: {0}/{1}".format(endmonth,endyear))
   
   # This is something I added to distinguish more clearly between the two sets of dates we have.
   # If we have monthly data, our starting and ending year in the plot
   # are not integers.  But if we floor them, they will be.
   syear=math.floor(starting_year)
   eyear=math.floor(ending_year)
   desired_startdate=date(syear,1,15)-date(1900,1,1)
   desired_enddate=date(eyear,12,15)-date(1900,1,1)
   data_startdate=date(startyear,startmonth,15)-date(1900,1,1)
   data_enddate=date(endyear,endmonth,15)-date(1900,1,1)

   # this is a slow way to do it, but it works.
   mm=1
   yy=syear
   for iyear in range(ndesiredyears):
      for imonth in range(12):
         # does a member of our data exist in this month?
         firstdaymonth=date(yy,mm,1)-date(1900,1,1)
         if mm in (1,3,5,7,8,10,12):
            lastdaymonth=date(yy,mm,31)-date(1900,1,1)
         elif mm in (4,6,9,11):
            lastdaymonth=date(yy,mm,30)-date(1900,1,1)
         else:
            if isleap(yy):
               lastdaymonth=date(yy,mm,29)-date(1900,1,1)
            else:
               lastdaymonth=date(yy,mm,28)-date(1900,1,1)
            #endif
         #endif

         for jtime,jval in enumerate(ncfile.variables['time'][:]):
            if jval >= firstdaymonth.days and jval <= lastdaymonth.days:
               FCO2[iyear,imonth,:]=FCO2_TOT[jtime,:]
            #endif
         mm=mm+1
         if mm > 12:
            mm=1
            yy=yy+1
         #endif
      #endfor
   #endfor

   return FCO2,current_units


   #################################

   # Create an axis that covers both of them completely.  Copy all of the data onto that axis.  Then take the chunk I want.
   lowerbound=min(desired_startdate.days,data_startdate.days)
   upperbound=max(desired_enddate.days,data_enddate.days)


   # There are four possible cases for the data we are looking at vs. the time period we want.
   # 1) The period that we want is completely covered by the data.  
   # 2) The starting point of the data falls in the period we want. 
   # 3) The ending point of the data falls in the period we want.  
   # 4) Both fall in the period we want.  

  
   # The period we want is completely covered by the data we have
   if desired_startdate.days > data_startdate.days and desired_enddate.days < data_enddate.days:
      istart=0
      iend=ndesiredyears*12-1

      # Loop over our data to find indend and indstart
      for itime,ival in enumerate(ncfile.variables['time'][:]):
         if abs(ival-desired_startdate.days) < 5:
            # Here is the index we start from
            print("Found starting index! ",itime,ival,desired_startdate.days)
            indstart=itime
         #endif
         if abs(ival-desired_enddate.days) < 5:
            # Here is the index we start from
            print("Found ending index! ",itime,ival,desired_enddate.days)
            indend=itime
         #endif

      #endfor

      # the data is completely inside the data that we want
   elif data_startdate.days > desired_startdate.days and data_enddate.days < desired_enddate.days:
      # here, indstart and indend cover our full data range, but we need to adapt istart and iend
      indstart=0
      iendend=len(ncfile.variables['time'][:])

      # loop over the desired timelength to find istart and iend
      loopdate = desired_startdate.days
      yy=desired_startdate.year
      mm=desired_startdate.month
      iindex=0
      while yy <= desired_enddate.year and mm <= desired_enddate.year:
         if yy == data_enddate.year and mm == data_enddate.month:
            iend=iindex
         if yy == data_startdate.year and mm == data_startdate.month:
            istart=iindex
         iindex=iindex+1
         mm=mm+1
         if mm > 12:
            yy=yy+1
            mm=1
         #endif
      #endwhile

   else:
      print("Need to write!")
      print(desired_startdate.year,desired_startdate.month)
      print(desired_enddate.year,desired_enddate.month)
      print(data_startdate.year,data_startdate.month)
      print(data_enddate.year,data_enddate.month)
      sys.exit(1)
   #endif


   FCO2[istart:iend,:]=FCO2_TOT[indstart:indend,:]  # extract the slice we are interested in
   return FCO2
#enddef
#####################################################################


#####################################################################
# This subroutine aims to select the countries/regions that you wish to plot
# from the whole list of data available after reading in from the files
# I read in the uncertainties and the real data at the same time.
# If there is no min/max or error values, no worries.
# This is a bit tricky.  We can only propogate error if we have a symmetric distribution, which
# we may not have for min/max values.  So I calculate min/max values after this routine.
def group_input(inputvar,inputerr,inputmin,inputmax,desired_plots,luncert,ndesiredyears,nplots,all_regions_countries,desired_simulation,ntimesteps):
   
   # Notice that the inputvar will be the size of the number of regions
   # in the .nc file, while outputvar will be the size of a number
   # of plots.  Our job here is to make the two correspond.
   outputvar=np.zeros((ntimesteps,nplots))*np.nan
   outputerr=np.zeros((ntimesteps,nplots))*np.nan
   outputmin=np.zeros((ntimesteps,nplots))*np.nan
   outputmax=np.zeros((ntimesteps,nplots))*np.nan

   for igroup in range(nplots):
      indices=[]
      if desired_plots[igroup] in all_regions_countries:
         #outputvar[:,igroup]=inputvar[:,all_regions_countries.index(desired_plots[igroup])]
         indices.append(all_regions_countries.index(desired_plots[igroup]))
      elif desired_plots[igroup] == "EU-28":
         #outputvar[:,igroup]=inputvar[:,E28]
         indices.append(all_regions_countries.index('E28'))
      elif desired_plots[igroup] == "EAE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # European Russia, Estonia, Latvia, Lithuania, Belarus, Poland, Ukraine
         # Ignore European Russia, since we just have the totals for Russia
         indices.append(all_regions_countries.index('EST'))
         indices.append(all_regions_countries.index('LVA'))
         indices.append(all_regions_countries.index('LTU'))
         indices.append(all_regions_countries.index('BLR'))
         indices.append(all_regions_countries.index('POL'))
         indices.append(all_regions_countries.index('UKR'))
      elif desired_plots[igroup] == "WEE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # Belgium, France, Netherlands, Germany, Switzerland, UK, Spain, Portugal
         indices.append(all_regions_countries.index('BEL'))
         indices.append(all_regions_countries.index('FRA'))
         indices.append(all_regions_countries.index('NLD'))
         indices.append(all_regions_countries.index('DEU'))
         indices.append(all_regions_countries.index('CHE'))
         indices.append(all_regions_countries.index('GBR'))
         indices.append(all_regions_countries.index('ESP'))
         indices.append(all_regions_countries.index('PRT'))
         #################################################
         # note that most of the 3-letter codes below should be obsolete, now in the 
         # NetCDF file
         #################################################
      elif desired_plots[igroup] == "CSK":
         # This is from Roxana
         # Former Czechoslovakia (CSK)
         # Czechia (CZE), Slovakia (SVK)
         indices.append(all_regions_countries.index('CZE'))
         indices.append(all_regions_countries.index('SVK'))
      elif desired_plots[igroup] == "CHL":
         # This is from Roxana
         # Switzerland + Liechtenstein (CHL)
         # Switzerland (CHE), Liechtenstein (LIE)
         indices.append(all_regions_countries.index('CHE'))
         indices.append(all_regions_countries.index('LIE'))
      elif desired_plots[igroup] == "BLT":
         # This is from Roxana
         # Baltic countries (BLT)
         # Estonia (EST), Lithuania (LTU), Latvia (LVA)
         indices.append(all_regions_countries.index('EST'))
         indices.append(all_regions_countries.index('LTU'))
         indices.append(all_regions_countries.index('LVA'))
      elif desired_plots[igroup] == "NAC":
         # This is from Roxana
         # North Adriatic Countries (NAC)
         # Slovenia (SVN), Croatia (HRV)
         indices.append(all_regions_countries.index('SVN'))
         indices.append(all_regions_countries.index('HRV'))
      elif desired_plots[igroup] == "DSF":
         # This is from Roxana
         # Denmark, Sweden, Finland (DSF)
         # Sweden (SWE), Denmark (DNK), Finland (FIN)
         indices.append(all_regions_countries.index('SWE'))
         indices.append(all_regions_countries.index('DNK'))
         indices.append(all_regions_countries.index('FIN'))
      elif desired_plots[igroup] == "FMA":
         # This is from Roxana
         # France, Monaco, Andorra (FMA)
         # France (FRA), Monaco (MCO), Andorra (AND)
         # Note that Monaco is already combined with France in our
         # mask.
         indices.append(all_regions_countries.index('FRA'))
         indices.append(all_regions_countries.index('AND'))
      elif desired_plots[igroup] == "UMB":
         # This is from Roxana
         # Ukraine, Rep. of Moldova, Belarus (UMB)
         # Ukraine (UKR), Moldova, Republic of (MDA), Belarus (BLR)
         indices.append(all_regions_countries.index('UKR'))
         indices.append(all_regions_countries.index('MDA'))
         indices.append(all_regions_countries.index('BLR'))
      elif desired_plots[igroup] == "SEA":
         # This is from Roxana
         # South-Eastern Europe alternate (SEA)
         # Serbia (SRB), Montenegro (MNE),Kosovo (RKS), Bosnia and Herzegovina (BIH), Albania (ALB), Macedonia, the former Yugoslav (MKD)
         # Notice that Kosovo is included in Serbia and Montenegro in our mask.
         indices.append(all_regions_countries.index('SRB'))
         indices.append(all_regions_countries.index('MNE'))
         indices.append(all_regions_countries.index('BIH'))
         indices.append(all_regions_countries.index('ALB'))
         indices.append(all_regions_countries.index('MKD'))
      elif desired_plots[igroup] == "IBE2":
         # This is a test to compare against the IBE from the file, just to
         # see if the results are the same.
         indices.append(all_regions_countries.index('ESP'))
         indices.append(all_regions_countries.index('PRT'))
      else:
         print("Do not know what this country group is!")
         print(desired_plots[igroup])
         sys.exit(1)
      #endif
      for iindex in range(len(indices)):
         value=indices[iindex]
         # This is necessary because I initialize the arrays with nan
         if iindex == 0:
            outputvar[:,igroup]=inputvar[:,value]
            outputmin[:,igroup]=inputmin[:,value]
            outputmax[:,igroup]=inputmax[:,value]
            if luncert:
               outputerr[:,igroup]=(inputerr[:,value]*inputvar[:,value])**2
            #endif
         else:
            outputvar[:,igroup]=outputvar[:,igroup]+inputvar[:,value]
            outputmin[:,igroup]=outputmin[:,igroup]+inputmin[:,value]
            outputmax[:,igroup]=outputmax[:,igroup]+inputmax[:,value]
            if luncert:
               outputerr[:,igroup]=outputerr[:,igroup]+(inputerr[:,value]*inputvar[:,value])**2
            #endif
         #endif
      #endfor

      if luncert:
         # now convert uncertainty back to a percentage
         for iyear,rval in enumerate(outputerr[:,igroup]):
            if outputvar[iyear,igroup] != 0.0 and not np.isnan(outputvar[iyear,igroup]):
               outputerr[iyear,igroup]=math.sqrt(outputerr[iyear,igroup])/abs(outputvar[iyear,igroup])
            #endif
         #endfor
      #endif

      # I am concerned about leakage with some plots.  For example, EFISCEN-Space only has data
      # for three countries.  If our maps are not perfectly in line, a couple pixels make leak
      # over to other countries.  This should be enforced in the CountryTot graphs, not here.
      if desired_simulation == "EFISCEN-Space" and desired_plots[igroup] not in ("FRA","IRL","NLD"):
         outputvar[:,igroup]=np.nan
         outputerr[:,igroup]=np.nan
         outputmin[:,igroup]=np.nan
         outputmax[:,igroup]=np.nan
      #endif

   #endfor

   return outputvar,outputerr,outputmin,outputmax
#enddef
####################################################################




#####################################################################
# This subroutine combines a specificed list of existing simulations
# and puts the results into a specific simulation.
# I use this because sometimes I need to combine variables from
# a NetCDF file into a single simulation result.
# It overwrites the existing simulation_data and returns it.
def combine_simulations(overwrite_simulations,overwrite_coeffs,overwrite_operations,simulation_data,simulation_min,simulation_max,simulation_err,desired_simulations,graphname):

   if not overwrite_simulations:
      print("No simulations need to be combined.")
      return simulation_data,simulation_min,simulation_max,simulation_err
   #endif

# In the case of the UNFCCC LUC, this is a sum of six different timeseries.
# Those are all in different files, so I combine them here, propogate the
# error, and then only print out this in the actual plot.
   #temp_desired_sims=('UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert')

   for osim,temp_sims in overwrite_simulations.items():

      ntempsims=len(temp_sims)
      ndesiredyears=simulation_data.shape[1]
      nplots=simulation_data.shape[2]

      ioverwrite=desired_simulations.index(osim)
      if ioverwrite < 0:
         print("******************************************************************")
         print("For the graph {0}, you need to be sure to include the simulation {1}!".format(graphname,osim))
         print("******************************************************************")
         sys.exit(1)
      #endif
      print("Combining simulations: ",temp_sims)
      print("with operation {0}.".format(overwrite_operations[osim]))

      simulation_data[ioverwrite,:,:]=0.0
      simulation_err[ioverwrite,:,:]=0.0

      temp_data=np.zeros((ntempsims,ndesiredyears,nplots))*np.nan

      if overwrite_operations[osim] == "sum":
         coeffs=overwrite_coeffs[osim]

         for isim,csim in enumerate(temp_sims):
            simulation_data[ioverwrite,:,:]=simulation_data[ioverwrite,:,:]+coeffs[isim]*simulation_data[desired_simulations.index(csim),:,:]
            # Do a simple propogation of error, as well
            simulation_err[ioverwrite,:,:]=simulation_err[ioverwrite,:,:]+(simulation_err[desired_simulations.index(csim),:,:]*coeffs[isim]*simulation_data[desired_simulations.index(csim),:,:])**2
         #endfor
            
         # don't like doing this in a loop, but the sqrt function doesn't seem to work on arrays?
         for iplot in range(len(simulation_err[0,0,:])):
            for itime in range(len(simulation_err[0,:,0])):
               simulation_err[ioverwrite,itime,iplot]=math.sqrt(simulation_err[ioverwrite,itime,iplot])/simulation_data[ioverwrite,itime,iplot]
            #endfor
         #endfor
   
      elif overwrite_operations[osim] == "mean":
         for isim,csim in enumerate(temp_sims):
            temp_data[isim,:,:]=simulation_data[desired_simulations.index(csim),:,:]
         #endfor

         # If I ignore nan here, then I get a value where not all simulations are present.
         # I only want values when all simulations are present.
         simulation_data[ioverwrite,:,:]=temp_data.mean(axis=0)
         simulation_min[ioverwrite,:,:]=np.min(temp_data,axis=0)
         simulation_max[ioverwrite,:,:]=np.max(temp_data,axis=0)

      else:
         print("Do not recognize operation for {}!".format(osim))
         print(overwrite_operations[ioverwrite])
         sys.exit(1)
      #endif

            

         
      # make any zero elements nan so they don't plot.  Hopefully this doesn't lead to undesired
      # results.
      for iplot in range(len(simulation_err[0,0,:])):
         for itime in range(len(simulation_err[0,:,0])):
            if simulation_data[ioverwrite,itime,iplot] == 0.0:
               simulation_data[ioverwrite,itime,iplot]= np.nan
            #endif
         #endfor
      #endfor

   #endfor
   
   return simulation_data,simulation_min,simulation_max,simulation_err
#enddef
####################################################################

#####################################################################
# Create a dictionary of areas of countries/regions in square meters,
# based on our country masks.  The first routine calculates them,
# and prints out the values in a nice Python list so that I can
# copy them to the second routine, which just returns the list.
# Calculating the values is too expensive to do every time.
#
# The areas that it gives are close to what Google gives (within 1% for Estonia, larger difference for
# France but France in Google likely has overseas territories).
def calculate_country_areas():

#   src = nc.Dataset("/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/eurocomCountryMaskEEZ_304x560.nc","r")
   src = nc.Dataset("/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/extended_eurocomCountryMaskEEZ_304x560_35.06N72.94N_24.94W44.94E.nc","r")
   latcoord="lat"
   loncoord="lon"
   names = src.variables["country_name"][:]
   names = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in names]
   lat = src.variables[latcoord][:]
   lon = src.variables[loncoord][:]
   lons, lats = np.meshgrid(lon, lat)

   for iname,cname in enumerate(names):

      # find the area of this country/region

      # The mask we have is for the extended economic zones, which includes territory in the oceans.
      # Filter that out here.
      filtered_mask = maskoceans(lons, lats, src.variables["country_mask"][iname,:,:], inlands = False, resolution = "f", grid = 1.25)
      #filtered_mask = src.variables["country_mask"][iname,:,:]
   
      area_2D=filtered_mask*src.variables["area"][:,:]
      area=np.nansum(area_2D)
      filtered_mask=filtered_mask[:,:].filled(fill_value=0.0)
      #filtered_mask[ filtered_mask > 0.0 ]=1.0
      #print(np.nansum(filtered_mask[:,:]))

      print("   country_areas[\"{0}\"]={1}".format(cname,area))
   #endfor

   src.close()

   return
#enddef
   

def get_country_areas():

   # This is taken from our map with 79 regions.


   country_areas={}
   country_areas["Aaland Islands"]=1578897664.0
   country_areas["Albania"]=28352174080.0
   country_areas["Andorra"]=447315584.0
   country_areas["Austria"]=83591815168.0
   country_areas["Belgium"]=30669848576.0
   country_areas["Bulgaria"]=112254164992.0
   country_areas["Bosnia and Herzegovina"]=50907799552.0
   country_areas["Belarus"]=206009483264.0
   country_areas["Switzerland"]=41593430016.0
   country_areas["Cyprus"]=5524352512.0
   country_areas["Czech Republic"]=78416461824.0
   country_areas["Germany"]=356221026304.0
   country_areas["Denmark"]=44500295680.0
   country_areas["Spain"]=498337873920.0
   country_areas["Estonia"]=45490667520.0
   country_areas["Finland"]=334269054976.0
   country_areas["France"]=547293986816.0
   country_areas["Faroe Islands"]=1354416512.0
   country_areas["United Kingdom"]=245327314944.0
   country_areas["Guernsey"]=125637592.0
   country_areas["Georgia"]=56721285120.0
   country_areas["Greece"]=131507568640.0
   country_areas["Greenland"]=28462256128.0
   country_areas["Croatia"]=56145813504.0
   country_areas["Hungary"]=92676333568.0
   country_areas["Isle of Man"]=718484352.0
   country_areas["Ireland"]=69942263808.0
   country_areas["Iceland"]=101657755648.0
   country_areas["Italy"]=299969642496.0
   country_areas["Jersey"]=126276816.0
   country_areas["Liechtenstein"]=164011744.0
   country_areas["Lithuania"]=64425762816.0
   country_areas["Luxembourg"]=2557641728.0
   country_areas["Latvia"]=64558092288.0
   country_areas["Moldova, Republic of"]=33723500544.0
   country_areas["Macedonia, the former Yugoslav"]=24797104128.0
   country_areas["Malta"]=312614048.0
   country_areas["Montenegro"]=12890724352.0
   country_areas["Netherlands"]=35655667712.0
   country_areas["Norway"]=325791744000.0
   country_areas["Poland"]=311556964352.0
   country_areas["Portugal"]=87435624448.0
   country_areas["Romania"]=236436160512.0
   country_areas["Russian Federation"]=1995897176064.0
   country_areas["Svalbard and Jan Mayen"]=251208448.0
   country_areas["San Marino"]=59646068.0
   country_areas["Serbia"]=88679014400.0
   country_areas["Slovakia"]=48968114176.0
   country_areas["Slovenia"]=19864659968.0
   country_areas["Sweden"]=447214321664.0
   country_areas["Turkey"]=791915069440.0
   country_areas["Ukraine"]=596645642240.0
   country_areas["BENELUX"]=68883161088.0
   country_areas["Former Czechoslovakia"]=127384567808.0
   country_areas["Switzerland + Liechtenstein"]=41757442048.0
   country_areas["Baltic countries"]=174474510336.0
   country_areas["North Adriatic Countries"]=76010471424.0
   country_areas["Denmark, Sweden, Finland"]=825983631360.0
   country_areas["United Kingdom + Ireland"]=315269578752.0
   country_areas["Iberia"]=585773481984.0
   country_areas["Western Europe"]=931446718464.0
   country_areas["Western Europe (alternative)"]=1842534678528.0
   country_areas["Central Europe"]=1013024096256.0
   country_areas["Northern Europe"]=1326249934848.0
   country_areas["Southern Europe (all)"]=2502051495936.0
   country_areas["Southern Europe (non-EU)"]=1054263214080.0
   country_areas["Southern Europe (EU)"]=1447788412928.0
   country_areas["South-Western Europe"]=886055698432.0
   country_areas["South-Eastern Europe (all)"]=1615995863040.0
   country_areas["South-Eastern Europe (non-EU)"]=1054263214080.0
   country_areas["South-Eastern Europe (EU)"]=561732714496.0
   country_areas["Eastern Europe"]=2832275603456.0
   country_areas["Eastern Europe (alternative)"]=1288686665728.0
   country_areas["Eastern Europe (including Russia)"]=3284583317504.0
   country_areas["EU-11+CHE"]=2273153908736.0
   country_areas["EU-15"]=3214493614080.0
   country_areas["EU-27"]=4105796583424.0
   country_areas["EU-27+UK"]=4351123783680.0
   country_areas["all Europe"]=8654811561984.0

   return country_areas
#enddef
####################################################################

#######################################
# This loads some fake data so that we can work more quickly on 
# the graphs.  I took this from results for EU-27+UK.
def read_fake_data(ndesiredyears,simname):
   outputvar=np.zeros((ndesiredyears))*np.nan
   outputerr=np.zeros((ndesiredyears))*np.nan
   outputmin=np.zeros((ndesiredyears))*np.nan
   outputmax=np.zeros((ndesiredyears))*np.nan

   base_name="fake_data"
   dfdata=pd.read_csv(filepath_or_buffer=base_name+".csv",index_col=0,header=0)

   #print("column names ",dfdata.columns)

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,simname]
      outputvar=values.tolist()
   except:
      print("Could not find data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_MIN".format(simname)]
      outputmin=values.tolist()
   except:
      print("Could not find minimum data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_MAX".format(simname)]
      outputmax=values.tolist()
   except:
      print("Could not find maximum data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_ERR".format(simname)]
      outputerr=values.tolist()
   except:
      print("Could not find error data for {}.".format(simname))
   #endif

   return outputvar,outputerr,outputmin,outputmax
#enddef

#####
def print_test_data(ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,itest_sim,itest_plot,desired_simulations,desired_plots,checkpoint_string):

   if ltest_data:
      print("**************************************************")
      print(checkpoint_string)
      print("Simulation: ",desired_simulations[itest_sim])
      print("Plot: ",desired_plots[itest_plot])
      print("simulation data  ",simulation_data[itest_sim,:,itest_plot])
      print("simulation err ",simulation_err[itest_sim,:,itest_plot])
      print("simulation min ",simulation_min[itest_sim,:,itest_plot])
      print("simulation max ",simulation_max[itest_sim,:,itest_plot])
      print("**************************************************")
   #endif

   #traceback.print_stack(file=sys.stdout)
   #sys.exit(1)

#####


#### Not sure this is currently working
def create_sectorplot_full():
   temp_desired_sims=("EPIC","ECOSSE_GL-GL","EFISCEN")
   temp_data=np.zeros((len(temp_desired_sims),ndesiredyears))
   for isim,csim in enumerate(temp_desired_sims):
      temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
   #endfor
      
   # plot the whole sum of these three runs
   p1=ax1.scatter(allyears,np.nansum(temp_data,axis=0),marker="P",label="EPIC/ECOSSE/EFISCEN",facecolors="blue", edgecolors="blue",s=60,alpha=production_alpha)
   legend_axes.append(p1)
   legend_titles.append("EPIC/ECOSSE/EFISCEN")

   # This is where things get really clever.  I want to show stacked bars of the three component fluxes.  However, there
   # are sometimes positive, and sometimes negative values, which means I cannot always use the same base of the bars.
   # I am adapting code I found on stackexchange

   # Take negative and positive data apart and cumulate
   cumulated_data = get_cumulated_array(temp_data, min=0)
   cumulated_data_neg = get_cumulated_array(temp_data, max=0)
         
   # Re-merge negative and positive data.
   row_mask = (temp_data<0)
   cumulated_data[row_mask] = cumulated_data_neg[row_mask]
   data_stack = cumulated_data

   temp_data[temp_data == 0.0]=np.nan

   barwidth=0.3
   for isim,csim in enumerate(temp_desired_sims):
      if productiondata[desired_simulations.index(csim)]:
         p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=production_alpha)
      else:
         p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=nonproduction_alpha)
      #endif
      legend_axes.append(p1)
      legend_titles.append(csim)
   #endfor
