####################################################################
# The purpose of this code is to take NetCDF files from the VERIFY
# THREDDS repository and create plots.
#
# NOTE: Uses Python3
#
# Useage: python PLOT_CO2_results.py GRAPHNAME
#    where GRAPHNAME can be inversions_full, or anything in the
#    possible_graphnames list below
# 
#   You can control the countries/regions which are plotted by
#   modifying the desired_plots list.
#
#   As of Feb 27, 2020, we use the following plots: rm -f *png *csv && python PLOT_CO2_results.py forestry_full && python PLOT_CO2_results.py grassland_full && python PLOT_CO2_results.py crops_full && python PLOT_CO2_results.py inversions_full && python PLOT_CO2_results.py inversions_combined && python PLOT_CO2_results.py inversions_combinedbar && python PLOT_CO2_results.py LULUCF_trendy
#
####################################################################
#!/usr/bin/env python

# These are downloadable or standard modules
import readline # optional, will allow Up/Down/History in the console
import code
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import copy
import os
import sys
import math
import pandas as pd
from netCDF4 import Dataset
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec
import re
from itertools import compress
# These are my own that I have created locally
from country_subroutines import get_countries_and_regions_from_cr_dict,get_country_region_data
from plotting_subroutines import get_simulation_parameters,find_date,get_cumulated_array,readfile,group_input,combine_simulations,calculate_country_areas,get_country_areas,read_fake_data


##########################################################################
# Here are some variables that are used throughout the code
##########################################################################

# This controls the alpha value (transparency) for real and invented data.
production_alpha=1.0
nonproduction_alpha=0.2
# If this is True, the symbols on the plots are made lighter if we 
# are using non-production data.  This demonstrates the work left to be
# done in terms of data processing, but sometimes we don't want to do this
# as then we can't see the final plot aesthetic.
lshow_productiondata=True

# Toggles between showing VERIFY inversions as a rectangle like the others, or
# a symbol with error bars
#lerrorbars=True

# Creates a horizontal line across the graph at zero.
lprintzero=True

# Make the Y-ranges on all the plots identical.
lharmonize_y=False

# Plot spatial fluxes or country totals? If the following variable is
# false, we will divide all fluxes by the area of the country/region before
# plotting, to give the flux per pixel.
lplot_countrytot=True

# This saves time by creating fake data, and helps debug the plots.  But, it is very specific and must
# be changed for the plot you are doing!
# If you want to create fake data, do a run with real data, and then copy all of the .csv files for
# the plot you want to "fake_data.csv","fake_data_min.csv","fake_data_max.csv","fake_data_err.csv"
luse_fake_data=False

# These are the year limits that are plotted.  The UNFCCC inventory data goes from 1990-2017.
# For next years of the project, we may have data up until 2021.
# so I generally do 1989.5-2021.5
xplot_min=1989.5
xplot_max=2021.5

# This is a flag that will set a lot of the parameters, include which simulations we plot.
# I do this here instead of in the subroutine that gets the simulation parameters
# since either way I want the full list of simulations to be displayed, and
# I see no way to do that without having both the list and the if statement in
# the simulation plot routine.  So may as well do it here before most things
# execute.
possible_graphnames=("test", "full_global", "full_verify", "luc_full", "sectorplot_full", "forestry_full", "grassland_full", "crops_full", "inversions_full", "inversions_test","biofuels","inversions_verify","lulucf","lulucf_full","inversions_combined","inversions_combinedbar","verifybu","fluxcom","lucf_full","lulucf_trendy","trendy","unfccc_lulucf_bar","all_orchidee","gcp_inversions","gcp_inversions_corrected","eurocom_inversions","eurocom_inversions_corrected","epic")
try:
   graphname=sys.argv[1]
   graphname=graphname.lower()
except:
   graphname=""
#endtry
if graphname not in possible_graphnames:
   print("I do not know what graph this is: " + graphname)
   print("Please choose from the following list")
   print(possible_graphnames)
   print("python PLOT_CO2_results.py inversions_full")
   sys.exit()
else:
   print("**************************************************************")
   print("Creating graph: " + graphname)
   print("**************************************************************")
#endif

# How many years do we extract from the data, or fill in with NaN if it's not found?
ndesiredyears=31
allyears=1990+np.arange(ndesiredyears)  ###1990-2017,ndesiredyears years

countries65=['ALA','ALB','AND', 'AUT',  'BEL',  'BGR',  'BIH',  'BLR',  'CHE',  'CYP',  'CZE', 'DEU', 'DNK','ESP','EST','FIN',  'FRA',  'FRO',  'GBR',  'GGY',  'GRC',  'HRV',  'HUN', 'IMN', 'IRL','ISL','ITA','JEY',  'LIE',  'LTU',  'LUX',  'LVA',  'MDA','MKD', 'MLT', 'MNE', 'NLD','NOR', 'POL',  'PRT',  'ROU',  'RUS',  'SJM',  'SMR',  'SRB',  'SVK', 'SVN', 'SWE', 'TUR','UKR','BNL', 'UKI',  'IBE',  'WEE',  'CEE',  'NOE',  'SOE',  'SEE', 'EAE', 'E15', 'E27','E28','EUR', 'EUT']

# This gives the full country name as a function of the ISO-3166 code
country_region_data=get_country_region_data()
countrynames=get_countries_and_regions_from_cr_dict(country_region_data)

# Only create plots for these countries/regions
if True:
   desired_plots=['E28','FRA','DEU','SWE','ESP']
   #desired_plots=['DEU','E28','KOS']
else:
   desired_plots=countries65.copy()
   #### Here are some new regions
   desired_plots.append('CSK')
   desired_plots.append('CHL')
   desired_plots.append('BLT')
   desired_plots.append('NAC')
   desired_plots.append('DSF')
   desired_plots.append('FMA')
   desired_plots.append('UMB')
   desired_plots.append('SEA')
#endif
#desired_plots.remove('KOS')


# What if I want a new region?  In theory, if I can build the dataseries
# before I get to the general plotting routines, they should treat
# it like just another region.  So, let's try to set everything
# up for a new region here.  The code now handles everything in 
# in group_input.
#desired_plots=['EAE2','WEE2']
# This is a test case that should produce indentical results
#desired_plots=['IBE','IBE2']



# This is something which controls the title printed on the plot, related
# to the country/group.  As a default, take the country/group name.
plot_titles_master={}
for cname in countrynames.keys():
   plot_titles_master[cname]=countrynames[cname]
#endfor
plot_titles_master["CSK"]="Former Czechoslovakia"
plot_titles_master["CHL"]="Switzerland + Liechtenstein"
plot_titles_master["BLT"]="Baltic countries"
plot_titles_master["NAC"]="North Adriatic Countries"
plot_titles_master["DSF"]="Denmark, Sweden, Finland"
plot_titles_master["FMA"]="France, Monaco, Andorra"
plot_titles_master["UMB"]="Ukraine, Rep. of Moldova, Belarus"
plot_titles_master["SEA"]="South-Eastern Europe alternate"
plot_titles_master["E28"]="EU27+UK"


##########################################################################


####################################################################
############################# This is the start of the program
####################################################################

nplots=len(desired_plots)

desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displayname_err_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,overwrite_coeffs,overwrite_operations,desired_legend,flipdatasign_master,lcorrect_inversion_master,lplot_errorbar_master,lwhiskerbars_master=get_simulation_parameters(graphname,lshow_productiondata)


# This is a generic code to read in all the simulations.  We may do different things based on the
# simulation name or type later on.


numsims=len(desired_simulations)

# Now that we have all the information above, populate the list of data that
# we will actually try to use.  This fields are described in more detail
# in the get_simulation_parameters subroutine.
variables=[]
files=[]
simtype=[]
plotmarker=[]
edgec= []
facec=[]
uncert_color=[]
markersize=[]
productiondata=[]
displayname=[]
displayname_err=[]
displaylegend=[]
flipdatasign=[]
lcorrect_inversion=[]
lplot_errorbar=[]
lwhiskerbars=[]
for simulationname in desired_simulations:
   variables.append(variables_master[simulationname])
   files.append(files_master[simulationname])
   simtype.append(simtype_master[simulationname])
   plotmarker.append(plotmarker_master[simulationname])
   edgec.append(edgec_master[simulationname])
   facec.append(facec_master[simulationname])
   uncert_color.append(uncert_color_master[simulationname])
   markersize.append(markersize_master[simulationname])
   productiondata.append(productiondata_master[simulationname])
   displayname.append(displayname_master[simulationname])
   displayname_err.append(displayname_err_master[simulationname])
   displaylegend.append(displaylegend_master[simulationname])
   flipdatasign.append(flipdatasign_master[simulationname])
   lcorrect_inversion.append(lcorrect_inversion_master[simulationname])
   lplot_errorbar.append(lplot_errorbar_master[simulationname])
   lwhiskerbars.append(lwhiskerbars_master[simulationname])
#endfor


# Now read in the data into one large array.  Based on the simulation
# type, we may have to modify how we process the data.
simulation_data=np.zeros((numsims,ndesiredyears,nplots))*np.nan
# Some of the files, like the inventories, have an error that we can read in
simulation_err=np.zeros((numsims,ndesiredyears,nplots))*np.nan
# and occasionally we want the min and the max values, in particular for
# combinations of other simulations.  I use this for uncertainty as well.
simulation_min=np.zeros((numsims,ndesiredyears,nplots))*np.nan
simulation_max=np.zeros((numsims,ndesiredyears,nplots))*np.nan


if luse_fake_data:
   print("WARNING: reading in fake data for graph: {}".format(graphname))
   print("All plots will have the same data.")
   for isim,simname in enumerate(desired_simulations):  
      for iplot in range(nplots):
         simulation_data[isim,:,iplot],simulation_err[isim,:,iplot],simulation_min[isim,:,iplot],simulation_max[isim,:,iplot]=read_fake_data(ndesiredyears,simname)
      #endfor
   #endfor

else:
   for isim,simname in enumerate(desired_simulations):  
      print("Reading in data for simulation: ",simname)
  
      fname=files[isim]
      try:
         f=open(fname)
         f.close()
      except:
         print("No file of name: " + fname)
         print("Please remove {0} from the list of desired simulations.".format(desired_simulations[isim]))
         sys.exit()
      #endtry

      if simtype[isim] == "INVENTORY":
         inv_fCO2=readfile(fname,variables[isim],ndesiredyears,True,1990,2018)  #monthly
         # This reads in the associated error.  It assumes that the file
         # has another variable of the same name, with _ERR added.
         inv_fCO2_err=readfile(fname,variables[isim] + "_ERR",ndesiredyears,True,1990,2018)  #monthly
         annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
         annfCO2_err=np.nanmean(inv_fCO2_err,axis=1)   #convert from monthly to yearly
         
         annfCO2_min=annfCO2.copy()*np.nan # these values are not used here
         annfCO2_max=annfCO2.copy()*np.nan
   
         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2_err,annfCO2_min,annfCO2_max,desired_plots,True,ndesiredyears,nplots,countries65,desired_simulations[isim])

         # I want to convert the percentage error values into min and max.  I do that below in 
         # a vector fashion.  The min and max values are what I will actually plot as the
         # error bars.


      elif simtype[isim] == ("MINMAX"):
         # This file has the variable value, as well as values of _MIN and _MAX which give error bars
         inv_fCO2=readfile(fname,variables[isim],ndesiredyears,True,1990,2018)  #monthly
         # This reads in the associated error.  It assumes that the file has two other variables with similar names..
         inv_fCO2_min=readfile(fname,variables[isim] + "_MIN",ndesiredyears,True,1990,2018)  #monthly
         inv_fCO2_max=readfile(fname,variables[isim] + "_MAX",ndesiredyears,True,1990,2018)  #monthly
         
         annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
         annfCO2_min=np.nanmean(inv_fCO2_min,axis=1)   #convert from monthly to yearly
         annfCO2_max=np.nanmean(inv_fCO2_max,axis=1)   #convert from monthly to yearly
         
         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2,annfCO2_min,annfCO2_max,desired_plots,False,ndesiredyears,nplots,countries65,desired_simulations[isim])

      elif simtype[isim] in ("TRENDY","VERIFY_BU","NONVERIFY_BU","INVENTORY_NOERR","VERIFY_TD","GLOBAL_TD","REGIONAL_TD","OTHER"):
         inv_fCO2=readfile(fname,variables[isim],ndesiredyears,True,1990,2018)  #monthly
         annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
         
         annfCO2_min=annfCO2.copy()*np.nan # these values are not used here
         annfCO2_max=annfCO2.copy()*np.nan
         
         # Some minor corrections have to be made to some of the files
         # The fluxes for ORCHIDEE seemed inverted with regards to the TRENDY
         # sign convention.  Flip that for the chart.  Same for CBM and the
         # two EFISCEN models.
         if flipdatasign[isim]:
            print("Flipping the sign of the {} fluxes.".format(desired_simulations[isim]))
            annfCO2=-annfCO2
         elif desired_simulations[isim] == "EUROCOM_Lumia":
            # One year in this inversion seems messed up.
            print("Correcting erroneously high values for Lumia fluxes.")
            annfCO2[annfCO2>1e30]=np.nan
         #endif
         if desired_simulations[isim] in ("EFISCEN","EFISCEN-unscaled"):
            # A couple years near the end of this inversion seem messed up.
            print("Correcting erroneously high values for EFISCEN fluxes.")
            annfCO2[abs(annfCO2)>1e35]=np.nan
         #endif

         if desired_simulations[isim] == "FAOSTAT_FL-FL":
            # The sum over the EU seems messed up
            print("Correcting erroneously high values for FAOSTAT_FL-FL fluxes.")
            annfCO2[abs(annfCO2)>1e35]=np.nan
         #endif

         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2,annfCO2_min,annfCO2_max,desired_plots,False,ndesiredyears,nplots,countries65,desired_simulations[isim])
      else:
         print("Do not know how to process data for simulation type: {0}".format(simtype[isim]))
         sys.exit()
      #endif

   #endfor
#endif

# If something is equal to zero, I don't plot it.
simulation_data[simulation_data == 0.0]=np.nan

# Use the values from the error array to fill out the min and the max array.  The min and the max array are
# best for plotting, and I want to use them to print out the data values, but errors can only be propogated
# above using the err array (which assumes symmetric errors).
# calculate the min and max values for each simulation from the error bars for all simulations that
# 1) Don't already have min/max values
# 2) Have error values

# Create a mask of the error values
have_err=np.asarray(simulation_err[:,:,:])
have_err= np.invert(np.isnan(have_err))
have_min=np.asarray(simulation_min[:,:,:])
have_min= np.invert(np.isnan(have_min))
have_max=np.asarray(simulation_max[:,:,:])
have_max= np.invert(np.isnan(have_max))
# Min and max should all have values at the same place.  If not, that is a problem.
# The logical_and value of numpy returns False when both elements are False, which
# is not what I want here.  So use xor.
test_min_max=np.invert(np.logical_xor(have_min,have_max))
if not test_min_max.all():
   print("Seem to have minimum values and not maximum values (or vice versa)!")
   for isim,simname in enumerate(desired_simulations):  
      print("Simulation: ",simname)
      for iyear in range(ndesiredyears):
         for iplot in range(nplots):
            print("iyear,iplot,min,max: {} {} {} {}".format(iyear,iplot,simulation_min[isim,iyear,iplot],simulation_max[isim,iyear,iplot]))
         #endfor
      #endfor
   #endfor
   sys.exit(1)
#endif

# Is there anywhere that we have a min/max value and we have an err value?  Because that seems wrong.
# We should have one or the other.
test_min_err=np.logical_and(have_min,have_err)
if test_min_err.any():
   print("Seem to have minimum values and error values at the same point!  Should only have one or the other right now.")
   print("Next we will convert the err into min/max and the min/max into err values.")
   for isim,simname in enumerate(desired_simulations):  
      print("Simulation: ",simname)
      for iyear in range(ndesiredyears):
         for iplot in range(nplots):
            print("iyear,iplot,min,max: {} {} {} {}".format(iyear,iplot,simulation_data[isim,iyear,iplot],simulation_err[isim,iyear,iplot],simulation_min[isim,iyear,iplot],simulation_max[isim,iyear,iplot]))
         #endfor
      #endfor
   #endfor
   sys.exit(1)
#endif


# Now create the mask.  have_min/have_max must be False and have_err must be True.
# I already checked above that have_min and have_max were identical.
err_mask=np.logical_and(np.invert(have_min),have_err)
# Be careful, since the data might be negative.  Taking the absolute value of the data
# makes sure that the min is lower than the data, and the max is higher.
# Remember, numbers are such that 100.0 is 100%!  Convert to a ratio when multiplying.
simulation_max=np.where( err_mask,simulation_data+abs(simulation_data)*simulation_err/100.0,simulation_max)
simulation_min=np.where( err_mask,simulation_data-abs(simulation_data)*simulation_err/100.0,simulation_min)

# Now where we have min/max but not error, calculate an error value.  This is an approximation, since
# the min/max may not be symmetric, but a % error is symmetric by defintion.
# I take the interval between the min and the max and divide it by two to estimate the error.  This can
# give crazy large values if the median happens to be near 0, so not sure it's useful for datasets with
# a min/max range as the error bars.
err_mask=np.logical_and(have_min,np.invert(have_err))
simulation_err=np.where( err_mask,0.5*(simulation_max-simulation_min)/abs(simulation_data),simulation_err)


# Check to see if we have inventory data.  If so, we do something different in plotting.
ninv=simtype.count("INVENTORY")
if ninv > 0:
   linventories=True
   print("We have some inventories in this dataset.")
else:
   linventories=False
   print("We do not have inventories in this dataset.")
#endif

#### This should be obsolete.  I calculate the averages and place them in a seperate file so I don't
# have to do it everytime I want to plot.
# We need to compute some properties of the TRENDY simulations for use later, since
# we don't plot each TRENDY run, just the range.
# Of course, none of it matters if we aren't actually using TRENDY runs,
# so check that as well.
#ntrendy=simtype.count("TRENDY")
#print("Number of TRENDY runs included: {0}".format(ntrendy))
#if ntrendy > 0:
#   trendy_data=np.zeros((ntrendy,ndesiredyears,nplots))*np.nan
#   ltrendy=True
#else:
#   ltrendy=False
#endif
#################

# We do the same thing with global inversions, if we have any
#nglobalinv=simtype.count("GLOBAL_TD")
#print("Number of global inversions included: {0}".format(nglobalinv))
#if nglobalinv > 0:
#   globalinv_data=np.zeros((nglobalinv,ndesiredyears,nplots))*np.nan
#   lglobalinv=True
#else:
#   lglobalinv=False
#endif

# And with regional (VERIFY) inversions, if we have any
#nverifyinv=simtype.count("VERIFY_TD")
#print("Number of VERIFY inversions included: {0}".format(nverifyinv))
#if nverifyinv > 0:
#   verifyinv_data=np.zeros((nverifyinv,ndesiredyears,nplots))*np.nan
#   lverifyinv=True
#else:
#   lverifyinv=False
#endif

# And with regional (REGIONAL) inversions, if we have any
#nregionalinv=simtype.count("REGIONAL_TD")
#print("Number of EUROCOM inversions included: {0}".format(nregionalinv))
#if nregionalinv > 0:
#   regionalinv_data=np.zeros((nregionalinv,ndesiredyears,nplots))*np.nan
#   lregionalinv=True
#else:
#   lregionalinv=False
#endif

# Now loop over all the simulations and pull the correct data out, so that
# we can find the median and the range

# Do this first with VERIFY, since if we have the CarboScopeReg inverisions,
# we want to add the mean to the EUROCOM inversions.
# This makes it a bit messy, since we repeat these same calculations
# below for the global and EUROCOM inversions, but I don't see any other way.
# Notice that I do not correct for other emissions here, but I do take 
# the mean.  I then have to take the mean again after the correction below.
# The reason is that I don't want to apply the correction for the verifymean
# twice.
#iverifyinv=0
#for isim,simname in enumerate(desired_simulations):  
#   if simtype[isim] == "VERIFY_TD":
#      verifyinv_data[iverifyinv,:,:]=simulation_data[isim,:,:]
#      iverifyinv=iverifyinv+1
   #endif
#endif
#if lverifyinv:
#   verifyinvmean=np.nanmean(verifyinv_data,axis=0)
#   verifyinvmax=np.nanmax(verifyinv_data,axis=0)
#   verifyinvmin=np.nanmin(verifyinv_data,axis=0)
#endif


#itrendy=0
#iglobalinv=0
#iregionalinv=0
#for isim,simname in enumerate(desired_simulations):  
#   if simtype[isim] == "TRENDY":
#      trendy_data[itrendy,:,:]=simulation_data[isim,:,:]
#      itrendy=itrendy+1
   #if simtype[isim] == "GLOBAL_TD":
   #   globalinv_data[iglobalinv,:,:]=simulation_data[isim,:,:]
   #   iglobalinv=iglobalinv+1
   #if simtype[isim] == "REGIONAL_TD":
      # In the case of EUROCOM CSR, we substitute the mean from the
      # VERIFY simulations, since Christoph has said he prefers the
      # VERIFY simulations.
   #   if simname == 'EUROCOM_Carboscope' and lverifyinv:
         # I don't want to add any points past the end of 2015, which is how far the 
         # EUROCOM results go.
   #      for iyear in range(ndesiredyears):
   #         if allyears[iyear] <= 2015:
   #            regionalinv_data[iregionalinv,iyear,:]=verifyinvmean[iyear,:]
   #         #endif
         #endfor
   #   else:
   #      regionalinv_data[iregionalinv,:,:]=simulation_data[isim,:,:]
      #endif
   #   iregionalinv=iregionalinv+1
   #endif
#endif

# For one plot type, we need to remove the biofuel emissions and the emissions
# from inland water bodies from the inversions.  Inversions see uptakes to both
# biomass stored in forests that to going to biofuels; our models don't consider biofuel uptake; 
# inventories report biofuels as a memo item, so not included in the LULUCF numbers).  It seems
# reasonable to assume that no inversion includes biofuel emissions with the FF priors, either.
# After much discussion, we found the biofuel corrections to be too complicated.  So we will
# NOT do that for 2020.
# I have to use a strange array declaration here because if I declare something
# like correction_simulations=("ULB_lakes_rivers"), Python thinks
# that it is a character array and loops over every letter.  Not what
# we want.

if any(lcorrect_inversion):
   correction_tag=" (removing ULB_lakes_rivers)"
   correction_simulations=np.array(["ULB_lakes_rivers"],dtype=object)
   correction_data=np.zeros((ndesiredyears,nplots))
   for isim,simname in enumerate(desired_simulations):  
      if simname in correction_simulations:
         correction_data[:,:]=correction_data[:,:]+simulation_data[isim,:,:]
      #endif
   #endfor
   for isim,simname in enumerate(desired_simulations):
      if lcorrect_inversion[isim]:
         simulation_data[isim,:,:]=simulation_data[isim,:,:]-correction_data[:,:]
         if desired_legend:
            if displayname[isim] in desired_legend:
               jsim=desired_legend.index(displayname[isim])
               desired_legend[jsim]=desired_legend[jsim]+correction_tag
            #endif
         #endif
         displayname[isim]=displayname[isim]+correction_tag
      #endif
   #endif
#   for iregionalinv in range(nregionalinv):
#      regionalinv_data[iregionalinv,:,:]=regionalinv_data[iregionalinv,:,:]-correction_data[:,:]
   #endfor
   #for iglobalinv in range(nglobalinv):
   #   globalinv_data[iglobalinv,:,:]=globalinv_data[iglobalinv,:,:]-correction_data[:,:]
   #endfor
   #for iverifyinv in range(nverifyinv):
   #   verifyinv_data[iverifyinv,:,:]=verifyinv_data[iverifyinv,:,:]-correction_data[:,:]
   #endfor
#endif

# note that I take the median for TRENDY but the mean for the rest.  The others
# only have 3-4 simulations, which is not really enough for a median.
#if ltrendy:
#   trendymedian=np.nanmedian(trendy_data,axis=0)
#   trendymax=np.nanmax(trendy_data,axis=0)
#   trendymin=np.nanmin(trendy_data,axis=0)
#endif

#if lglobalinv:
#   globalinvmean=np.nanmean(globalinv_data,axis=0)
#   globalinvmax=np.nanmax(globalinv_data,axis=0)
#   globalinvmin=np.nanmin(globalinv_data,axis=0)
#endif
#if lregionalinv:
#   regionalinvmean=np.nanmean(regionalinv_data,axis=0)
#   regionalinvmax=np.nanmax(regionalinv_data,axis=0)
#   regionalinvmin=np.nanmin(regionalinv_data,axis=0)
#endif
#if lverifyinv:
#   verifyinvmean=np.nanmean(verifyinv_data,axis=0)
#   verifyinvmax=np.nanmax(verifyinv_data,axis=0)
#   verifyinvmin=np.nanmin(verifyinv_data,axis=0)
#endif

# Sometimes I need to sum several variables into one timeseries.  This does that, assuming
# that there one simulation already in the dataset that will be overwritten.
simulation_data[:,:,:],simulation_min[:,:,:],simulation_max[:,:,:],simulation_err[:,:,:]=combine_simulations(overwrite_simulations,overwrite_coeffs,overwrite_operations,simulation_data,simulation_min,simulation_max,simulation_err,desired_simulations,graphname)

######### Here is where we get to the actual plotting
# set the titles
plot_titles=[]
for iplot,cplot in enumerate(desired_plots):
   try:
      plot_titles.append(plot_titles_master[cplot] + titleending)
   except:
      plot_titles.append("No title given.")
   #endtry
#endfor

# There may be some situations in which we want to make the range of the y-axis 
# identical in all plots
if lharmonize_y:
   ymin=np.nanmin(simulation_data[:,:,:])
   ymin=ymin-0.05*abs(ymin)
   ymax=np.nanmax(simulation_data[:,:,:])
   ymax=ymax+0.05*abs(ymax)
#endif

##
# For one of the graphs, I do a little data processing.
# I do this before the loop because I want to still print out
# good values to the .csv files.
if graphname == "unfccc_lulucf_bar":

   # A few tests
   naverages=3
   syear_average=[1990, 2000, 2010]
   eyear_average=[1999, 2009, 2017]
   ##
   #naverages=3
   #syear_average=[1990, 1998, 2008]
   #eyear_average=[1997, 2007, 2017]
   ##
   #naverages=3
   #syear_average=[1990, 1999, 2009]
   #eyear_average=[1998, 2008, 2017]
   ##
   #naverages=4
   #syear_average=[1990, 1997, 2004, 2012]
   #eyear_average=[1996, 2003, 2010, 2017]
   ##
   #naverages=2
   #syear_average=[1990, 2004]
   #eyear_average=[2003, 2017]
   ##
   #naverages=3
   #syear_average=[1990, 2006, 2016]
   #eyear_average=[2005, 2015, 2017]
   ##

   # I want to replace the values by averages defined above.
   for iaverage in range(naverages):
      # Find the indices for the years that cover the range that we want
      temp_index=np.where( allyears == syear_average[iaverage])
      sindex=int(temp_index[0])
      temp_index=np.where( allyears == eyear_average[iaverage])
      eindex=int(temp_index[0])
      if syear_average[iaverage] != allyears[sindex]:
         print("Something is going wrong in starting year averages!")
         print("iaverage: {}, syear_average: {}".format(iaverage,syear_average[iaverage]))
         print("sindex: {}, allyears: {}".format(sindex,allyears[sindex]))
         sys.exit(1)
      #endif
      if eyear_average[iaverage] != allyears[eindex]:
         print("Something is going wrong in ending year averages!")
         print("iaverage: {}, eyear_average: {}".format(iaverage,eyear_average[iaverage]))
         print("eindex: {}, allyears: {}".format(eindex,allyears[eindex]))
         sys.exit(1)
      #endif       
      if eindex < sindex:
         print("Something wrong with averages at XYW.")
         print("iaverage: {}, syear: {}, eyear: {}".format(iaverage,syear_average[iaverage],eyear_average[iaverage]))
         sys.exit(1)
      #endif
      temp_array=simulation_data[:,sindex:eindex+1,:].copy()
      for iindex in range(sindex,eindex+1,1):
         simulation_data[:,iindex,:]=np.nanmean(temp_array,axis=1)
      #endfor
   #endif

##


######## Sometimes people want raw data.  I will
# print all raw data for all the plots to this file.
datafile=open("plotting_data.txt","w")

# In case I want to scale by the area of the country, get the
# country areas
country_areas=get_country_areas()

for iplot,cplot in enumerate(desired_plots):

   print("**** On plot {0} ****".format(plot_titles_master[cplot]))
   datafile.write("**** On plot {0} ****\n".format(plot_titles_master[cplot]))

   # Create a dataframe for all of these simulations, and print it to a .csv file
   # In order to do this, I should process all the data outside this loop
   # and make sure it's stored in simulation_data.  I am working towards that goal,
   # though perhaps not quite there yet.
   df=pd.DataFrame(data=simulation_data[:,:,iplot],index=desired_simulations,columns=allyears)

   # Since we want to use only a single .csv, loop through the min and
   # the max files.  If there is a difference between the min and the max,
   # add lines to the dataframe append _MIN and _MAX to the name of the
   # simulation.
   for isim,csim in enumerate(desired_simulations):
      
      # Have we filled in any min values for this simulation?
      nancheckmin=np.invert(np.isnan(simulation_min[isim,:,iplot]))
      nancheckmax=np.invert(np.isnan(simulation_max[isim,:,iplot]))
      nancheck=np.invert(np.isnan(simulation_data[isim,:,iplot]))
      # First, do we have some non-NaN minimum values?
      if nancheckmin.any():
         
         # Now, do we have any indices where both the min and the data
         # are not NaN, and they are different?
         # First, pull out non-NaN values
         min_non_NaN=list(compress(simulation_min[isim,:,iplot],nancheckmin))
         non_NaN=list(compress(simulation_data[isim,:,iplot],nancheck))

         if len(min_non_NaN) != len(non_NaN):
            print("Why do data and minimumn values have different numbers of NaN?")
            print(csim,desired_plots[iplot])
            print("Data: ",simulation_data[isim,:,iplot])
            print("Min: ",simulation_min[isim,:,iplot])
            sys.exit(1)
         #endif
            
         test_comp=np.invert(min_non_NaN == non_NaN)
         if test_comp.any():
            # Not terribly efficient to do it this way, but our DataFrames
            # should be small
            print("Found minimum values for ",desired_simulations[isim])

            # This creates the dataframe transposed from what I want.  But
            # it crashes if I flip the indices and columns, so I do this and
            # then append the transposed dataframe.
            newdf=pd.DataFrame(simulation_min[isim,:,iplot],index=allyears,columns=[desired_simulations[isim] + "_MIN"])
                  
            df=df.append(newdf.T)
            df.sort_index(inplace=True)
         #endif
      #endif

      # Next, do we have some non-NaN maximum values?
      if nancheckmax.any():
         
         # Now, do we have any indices where both the max and the data
         # are not NaN, and they are different?
         # First, pull out non-NaN values
         max_non_NaN=list(compress(simulation_max[isim,:,iplot],nancheckmax))
         non_NaN=list(compress(simulation_data[isim,:,iplot],nancheck))

         if len(max_non_NaN) != len(non_NaN):
            print("Why do data and maximum values have different numbers of NaN?")
            print(csim,desired_plots[iplot])
            print("Data: ",simulation_data[isim,:,iplot])
            print("Max: ",simulation_max[isim,:,iplot])
            sys.exit(1)
         #endif
            
         test_comp=np.invert(max_non_NaN == non_NaN)
         if test_comp.any():
            # Not terribly efficient to do it this way, but our DataFrames
            # should be small
            print("Found maximum values for ",desired_simulations[isim])

            # This creates the dataframe transposed from what I want.  But
            # it crashes if I flip the indices and columns, so I do this and
            # then append the transposed dataframe.
            newdf=pd.DataFrame(simulation_max[isim,:,iplot],index=allyears,columns=[desired_simulations[isim] + "_MAX"])
                  
            df=df.append(newdf.T)
            df.sort_index(inplace=True)
         #endif
      #endif
   #endif

   # Finally, print it all to the file.
   data_file_end=re.sub(r".png",r".csv",output_file_end)
   # Some people think it's more classicial to have the years as
   # the rows.  So do a quick transpose.
   df=df.T
   df.to_csv(path_or_buf=output_file_start+desired_plots[iplot]+data_file_end,sep=",")
   
   
   #df=pd.DataFrame(data=simulation_min[:,:,iplot],index=desired_simulations,columns=allyears)
   #data_file_end=re.sub(r".png",r"_min.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+desired_plots[iplot]+data_file_end,sep=",")
   #df=pd.DataFrame(data=simulation_max[:,:,iplot],index=desired_simulations,columns=allyears)
   #data_file_end=re.sub(r".png",r"_max.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+desired_plots[iplot]+data_file_end,sep=",")
   # This is more for debugging purposes, not always necessary
   #df=pd.DataFrame(data=simulation_err[:,:,iplot],index=desired_simulations,columns=allyears)
   #data_file_end=re.sub(r".png",r"_err.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+desired_plots[iplot]+data_file_end,sep=",")
   ####

   # In an effort to harmonize the spacing a bit, I create a three-panel
   # grid, and then put only the legend in the bottom panel.

   fig=plt.figure(2,figsize=(13, 8))
   canvas = FigureCanvas(fig)
   gs = gridspec.GridSpec(3, 1, height_ratios=[2.7,1,1])
   ax1=plt.subplot(gs[0])
   ax2 =plt.subplot(gs[2])

   # Try to combine all my different legends in one
   legend_axes=[]
   legend_titles=[]

   # Use this to keep the symbols plotted above the bars
   zorder_value=30

   # Do we scale the fluxes by the total area of the countries?
   if not lplot_countrytot:
      # The units of simulation data were in Tg C/yr.  This gives
      # Tg C/yr/square meter of country.  We want g C/yr/square meter of
      # country.
      simulation_data[:,:,iplot]=simulation_data[:,:,iplot]/country_areas[countrynames[cplot]]*1e12
      
   #endif

   # First, I plot a series of bars, if they are present.  I want the symbols to fall on top of these
   # bars, so best to plot these first, and change the zorder to be low.
   for isim,simname in enumerate(desired_simulations):  
      if lplot_errorbar[isim]:
         upperrange=simulation_max[isim,:,iplot]
         lowerrange=simulation_min[isim,:,iplot]
         if not lwhiskerbars[isim]:
            # This prints rectangles
            for iyear in range(ndesiredyears):
               if np.isnan(simulation_data[isim,iyear,iplot]):
                  continue
               #endif
               p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=uncert_color[isim], alpha=0.2,zorder=1)
               p2=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color=facec[isim],linestyle='--',zorder=2)
               ax1.add_patch(p1)
            #endfor
         else:
            # This prints a symbol with whisker error bars
            whiskerbars=np.array((simulation_data[isim,:,iplot]-lowerrange[:],upperrange[:]-simulation_data[isim,:,iplot])).reshape(2,ndesiredyears)
            p2=ax1.errorbar(allyears,simulation_data[isim,:,iplot],yerr=whiskerbars,marker=plotmarker[isim],mfc=facec[isim],mec='black',ms=10,capsize=10,capthick=2,ecolor="black",linestyle='None',zorder=5)

         #endif

         
         legend_axes.append(p2)
         #if lcorrect_inversion[isim]:
         #   legend_titles.append(displayname[isim] + " (removing ULB_lakes_rivers)")
         #else:
         legend_titles.append(displayname[isim])
         ##endif
         if not lwhiskerbars[isim]:
            legend_axes.append(p1)
            legend_titles.append(displayname_err[isim])
         #endif
      #endif
   #endfor


   # This is to plot TRENDY, if present
   #if 'TrendyV7' in desired_simulations:
   #   itrendy=desired_simulations.index('TrendyV7')
   #   upperrange=simulation_max[itrendy,:,iplot]
   #   lowerrange=simulation_min[itrendy,:,iplot]
   #   for iyear in range(ndesiredyears):
   #      p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="lightgray", alpha=0.6,zorder=1)
   #      p2=ax1.hlines(y=simulation_data[itrendy,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color="gray",linestyle='--',zorder=2)
   #      ax1.add_patch(p1)
         #ax1.fill_between(np.array([allyears[iyear]-0.5,allyears[iyear]+0.5]),lowerrange[iyear],upperrange[iyear],color="lightgray",alpha=0.60)
      #endfor
   #   legend_axes.append(p2)
   #   legend_titles.append("Median of TRENDY v7 DGVMs")
   #   legend_axes.append(p1)
   #   legend_titles.append("Min/Max of TRENDY v7 DGVMs")

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,trendymedian[:,iplot],marker="_",label="TRENDY_v7",facecolors="None", edgecolors="lightgray",s=60)

   #endif

   # This is to plot global inversions together, if present
   #if 'GCP_ALL' in desired_simulations:
   #   iglobal=desired_simulations.index('GCP_ALL')
   #   upperrange=simulation_max[iglobal,:,iplot]
   #   lowerrange=simulation_min[iglobal,:,iplot]
   #   for iyear in range(ndesiredyears):
   #      p2=ax1.hlines(y=simulation_data[iglobal,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='red',linestyle='--')
   #      p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="red", alpha=0.20)
   #      ax1.add_patch(p1)
      #endfor
   #   legend_axes.append(p2)
   #   if lcorrect_inversion[iglobal]:
   #      legend_titles.append("Mean of GCP inversions (removing ULB_lakes_rivers)")
   #   else:
   #      legend_titles.append("Mean of GCP inversions")
      #endif
   #   legend_axes.append(p1)
   #   legend_titles.append("Min/Max of GCP inversions")
      
      # Write raw data to a file
   #   datafile.write("**** On dataset Mean of GCP ****\n")
   #   datafile.write("years {}\n".format(allyears[:]))
   #   datafile.write("data {}\n".format(simulation_data[iglobal,iyear,iplot]))
   #   datafile.write("upperbounds {}\n".format(upperrange[:]))
   #   datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,globalinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

   # and the regional (VERIFY) inversions, if they are present
   #if "JENA-COMBINED" in desired_simulations:
   #   iverifyinv=desired_simulations.index('JENA-COMBINED')

   #   upperrange=simulation_max[iverifyinv,:,iplot]
   #   lowerrange=simulation_min[iverifyinv,:,iplot]

   #   if not lerrorbars: # This is for rectangles, like the other inversions
   #      for iyear in range(ndesiredyears):
   #         p2=ax1.hlines(y=simulation_data[iverifyinv,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='red',linestyle='--')
   #         p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="red", alpha=0.20)
   #         ax1.add_patch(p1)
         #endfor
   #      legend_axes.append(p2)
   #      if lcorrect_inversions["JENA-COMBINED"]:
   #         legend_titles.append("Mean of CarboScopeReg (removing ULB_lakes_rivers)")
   #      else:
   #         legend_titles.append("Mean of CarboScopeReg")
         #endif
   #      legend_axes.append(p1)
   #      legend_titles.append("Min/Max of CarboScopeReg")
   #   else:
         # This is for a symbol with error bars
         # Notice error bars must always be positive
   #      errorbars=np.array((simulation_data[iverifyinv,:,iplot]-lowerrange[:],upperrange[:]-simulation_data[iverifyinv,:,iplot])).reshape(2,ndesiredyears)
   #      p2=ax1.errorbar(allyears,simulation_data[iverifyinv,:,iplot],yerr=errorbars,marker='s',mfc='mediumblue',mec='black',ms=10,capsize=10,capthick=2,ecolor="black",linestyle='None',zorder=5)
   #      legend_axes.append(p2)
   #      if lcorrect_inversion["JENA-COMBINED"]:
   #         legend_titles.append("Mean of CarboScopeReg (removing ULB_lakes_rivers)")
   #      else:
   #         legend_titles.append("Mean of CarboScopeReg")
         #endif

      #endif
      
      # Write raw data to a file
   #   datafile.write("**** On dataset Mean of CarboScopeReg (removing ULB_lakes_rivers) ****\n")
   #   datafile.write("years {}\n".format(allyears[:]))
   #   datafile.write("data {}\n".format(simulation_data[iverifyinv,:,iplot]))
   #   datafile.write("upperbounds {}\n".format(upperrange[:]))
   #   datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,verifyinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

   # and the regional (NON-VERIFY) inversions, if they are present
   #if lregionalinv:
   #   upperrange=regionalinvmax[:,iplot]
   #   lowerrange=regionalinvmin[:,iplot]
   #   for iyear in range(ndesiredyears):
   #      p2=ax1.hlines(y=regionalinvmean[iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='blue',linestyle='--')
   #      p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="blue", alpha=0.20)
   #      ax1.add_patch(p1)
      #endfor
   #   legend_axes.append(p2)
   #   if any(lcorrect_inversion):
   #      legend_titles.append("Mean of EUROCOM inversions (removing ULB_lakes_rivers)")
   #   else:
   #      legend_titles.append("Mean of EUROCOM inversions")
      #endif
   #   legend_axes.append(p1)
   #   legend_titles.append("Min/Max of EUROCOM inversions")
 
      # Write raw data to a file
   #   datafile.write("**** On dataset Mean of EUROCOM (removing ULB_lakes_rivers) ****\n")
   #   datafile.write("years {}\n".format(allyears[:]))
   #   datafile.write("data {}\n".format(regionalinvmean[:,iplot]))
   #   datafile.write("upperbounds {}\n".format(upperrange[:]))
   #   datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,regionalinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

   if "VERIFYBU" in desired_simulations:
      idata=desired_simulations.index("VERIFYBU")
      for iyear in range(ndesiredyears):
         p2=ax1.hlines(y=simulation_data[idata,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='yellow',linestyle='--')
         p1=mpl.patches.Rectangle((allyears[iyear]-0.5,simulation_min[idata,iyear,iplot]),1,simulation_max[idata,iyear,iplot]-simulation_min[idata,iyear,iplot], color="yellow", alpha=0.20)
         ax1.add_patch(p1)
      #endfor
      legend_axes.append(p2)
      legend_titles.append(displayname[idata])
      legend_axes.append(p1)
      legend_titles.append("Min/Max of VERIFY BU simulation")
 
      # Write raw data to a file
      datafile.write("**** On dataset Mean of VERIFY BU simulations ****\n")
      datafile.write("years {}\n".format(allyears[:]))
      datafile.write("data {}\n".format(simulation_data[idata,:,iplot]))
      datafile.write("upperbounds {}\n".format(simulation_max[idata,:,iplot]))
      datafile.write("lowerbounds {}\n".format(simulation_min[idata,:,iplot]))

   #endif


   # This is to plot the inventories
   if linventories and not (graphname == "unfccc_lulucf_bar"):

      if graphname == "sectorplot_full":

         temp_desired_sims=("UNFCCC_FL-FL","UNFCCC_GL-GL","UNFCCC_CL-CL")
         temp_data=np.zeros((len(temp_desired_sims),ndesiredyears))
         for isim,csim in enumerate(temp_desired_sims):
            temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
         #endfor

         # plot the whole sum of these three runs
         #p1=ax1.scatter(allyears,np.nansum(temp_data,axis=0),marker="X",facecolors="blue", edgecolors="blue",s=60,alpha=nonproduction_alpha)
         #legend_axes.append(p1)
         #legend_titles.append("UNFCCC_LU")

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
         
         barwidth=1.0
         for isim,csim in enumerate(temp_desired_sims):
            if productiondata[desired_simulations.index(csim)]:
               p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=production_alpha*0.5)
            else:
               p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=nonproduction_alpha*0.5)
            #endif
            legend_axes.append(p1)
            legend_titles.append(csim)
         #endfor
      #endif


      for isim,simname in enumerate(desired_simulations):  

         if any(lcorrect_inversion) and desired_simulations[isim] in correction_simulations:
            continue
         #endif 

         if not displaylegend[isim]:
            continue
         #endif

         if graphname == "forestry_full" and desired_simulations[isim] in ("LUH2v2_FOREST","UNFCCC_FOREST"):
            continue
         #endif 


         if simtype[isim] == "INVENTORY" and graphname != "sectorplot_full":
            print("Plotting inventories!")
            print(simulation_max[isim,:,iplot])
            datafile.write("**** On dataset {0} ****\n".format(desired_simulations[isim]))

#            upperrange=simulation_data[isim,:,iplot]+simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
#            lowerrange=simulation_data[isim,:,iplot]-simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
            upperrange=simulation_max[isim,:,iplot]
            lowerrange=simulation_min[isim,:,iplot]
            datafile.write("years {}\n".format(allyears[:]))
            datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))
            datafile.write("upperbounds {}\n".format(upperrange[:]))
            datafile.write("lowerbounds {}\n".format(lowerrange[:]))

            # Check to see if we have any data.  If not, then we can skip it.
            # This happens for UNFCCC sometimes, but not for map-based products.
            test_vals=simulation_data[isim,:,iplot]
            check_vals=np.where(np.isnan(test_vals),True,False)
            if check_vals.all():
               print("No data for {}.  Skipping.".format(desired_simulations[isim]))
               print(test_vals)
               print(check_vals)
               continue
            #endif

            lshow_uncert=False
            for iyear in range(ndesiredyears):

               # If we have no uncertainty, then I don't want to show it.
               if not np.isnan(lowerrange[iyear]) and not np.isnan(lowerrange[iyear]):
                  p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=uncert_color[isim], alpha=0.30,zorder=zorder_value-2)
                  ax1.add_patch(p1)
                  lshow_uncert=True
               #endif
               #ax1.fill_between(np.array([allyears[iyear]-0.5,allyears[iyear]+0.5]),lowerrange[iyear],upperrange[iyear],color=uncert_color[isim],alpha=0.30,zorder=zorder_value-1)
            #endfor

            if lshow_uncert:
               legend_axes.append(p1)
               legend_titles.append(displayname[isim] + " uncertainty")
            #endif

            # I want to make sure the symbol shows up on top of the error bars.
            # If this is not real data, make it lighter.
            for iyear in range(ndesiredyears):
               if productiondata[isim]:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=production_alpha,zorder=zorder_value-1)
               else:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=nonproduction_alpha,zorder=zorder_value-1)
               #endif
            #endif

            legend_axes.append(p1)
            legend_titles.append(displayname[isim])
            datafile.write("\n")

         #endif
      #endfor
   #endif

   # This is to plot all the other simulations not covered by the special cases above
   for isim,simname in enumerate(desired_simulations):  
      if simtype[isim] in ("NONVERIFY_BU","INVENTORY_NOERR","VERIFY_BU","TRENDY","GLOBAL_TD","REGIONAL_TD","MINMAX") or graphname == "inversions_verify":
         
         # We should have already plotted this above
         if lplot_errorbar[isim]:
            continue
         #endif

         # Check to see if we have any data.  If not, then we can skip it.
         test_vals=simulation_data[isim,:,iplot]
         check_vals=np.where(np.isnan(test_vals),True,False)
         if check_vals.all():
            print("No data for {}.  Skipping.".format(desired_simulations[isim]))
            print(test_vals)
            print(check_vals)
            continue
         #endif

         # I do something differently for one of the plots
         if graphname == "sectorplot_full" and desired_simulations[isim] in ("EPIC","ECOSSE_GL-GL","EFISCEN"):
            continue
         #endif
         if any(lcorrect_inversion) and desired_simulations[isim] in correction_simulations:
            continue
         #endif      

         if not displaylegend[isim]:
            continue
         #endif

         # I use lighter symbols if the data is not real, i.e. I created a false dataset just to have something to plot
         if productiondata[isim]:
            p1=ax1.scatter(allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=production_alpha,zorder=zorder_value)
         else:
            p1=ax1.scatter(allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=nonproduction_alpha,zorder=zorder_value)
         #endif
         legend_axes.append(p1)
         legend_titles.append(displayname[isim])

         datafile.write("**** On dataset {0} ****\n".format(displayname[isim]))
         datafile.write("years {}\n".format(allyears[:]))
         datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))

      #endif
   #endif

   # For this particular graph, I plot three of the VERIFY runs in a different way.
   if graphname == "sectorplot_full":

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

   #endif

   # I want to plot the forest area on this plot as bars at the bottom.
   if graphname == "forestry_full" and lplot_areas:

      axsub = ax1.twinx()
      
      forest_areas=("LUH2v2_FOREST","UNFCCC_FOREST")
      barwidth=0.3
      offset=-barwidth/2.0

      for forest_area in forest_areas:
         if forest_area in desired_simulations:
      
            # This plots the LUH2v2 ESA-CCI forest areas
            isim=desired_simulations.index(forest_area)

            # Check to see if we have any data.  If not, then we can skip it.
            # This happens for UNFCCC sometimes, but not for map-based products.
            test_vals=simulation_data[isim,:,iplot]
            check_vals=np.where(np.isnan(test_vals),True,False)
            if check_vals.all():
               print("No data for {}.  Skipping.".format(desired_simulations[isim]))
               print(test_vals)
               print(check_vals)
               continue
            #endif

            # convert from m**2 to kha
            p1=axsub.bar(allyears+offset, simulation_data[isim,:,iplot]/1000.0/10000.0, color=facec[desired_simulations.index(forest_area)],width=barwidth,alpha=production_alpha*0.3)
            legend_axes.append(p1)
            legend_titles.append(displayname_master[forest_area])

            offset=offset+barwidth
         #endif
      #endif

      axsub.set_ylabel('Forest area \n[kha]')
      

      datafile.write("**** On dataset {0} ****\n".format(displayname[isim]))
      datafile.write("years {}\n".format(allyears[:]))
      datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))

      # I want the bars to only take up the bottom third of the graph or so.
      ylimits=axsub.get_ylim()
      yaxisrange=ylimits[1]-ylimits[0]
      axsub.set_ylim(ylimits[0],ylimits[1]+3.0*yaxisrange)

   #endif

   # I want to try stacking some bars at the bottom and right-side axis of some of the inversion plots
   if any(lcorrect_inversion):

      temp_data=np.zeros((len(correction_simulations),ndesiredyears))
      for isim,csim in enumerate(correction_simulations):
         temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
      #endfor

      # Now I want to add a second axis to this plot.  But I am not going to label it at all.
      # I want the scale to be the same as the original, but I want 0 to align with the bottom.
      axsub = ax1.twinx()  

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
      for isim,csim in enumerate(correction_simulations):
         if productiondata[desired_simulations.index(csim)]:
            p1=axsub.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=production_alpha*0.3)
         else:
            p1=axsub.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=nonproduction_alpha*0.3)
         #endif
         legend_axes.append(p1)
         legend_titles.append(csim)
      #endfor


      if not lplot_countrytot:
         axsub.set_ylabel(r'Correction for inversions\n[g C/yr/(m$^2$ of country)]')
      else:
         axsub.set_ylabel(r'Correction for inversions\n[Tg C yr$^{-1}$]')
      #endif

      # I would like the limits of the secondary X axis to be the same as the first, only shifted down
      # so that the bottom is equal to zero.
      ylimits=ax1.get_ylim()
      # Be careful if we are harmonizing the main axis
      if lharmonize_y:
         yaxisrange=ymax-ymin
      else:
         yaxisrange=ylimits[1]-ylimits[0]
      #endif
      axsub.set_ylim(0,yaxisrange)
   #endif

   # This is a special bar plot that doesn't look like any
   # of the other timeseries.  I have already calculated
   # average values to use above.
   if graphname == "unfccc_lulucf_bar":

      # This stores some of the text objects, so I can use
      # them later to set the plot limits.  Note that I cannot
      # use the standard ax1.texts container, since I don't
      # want all of the objects taken into account, just some.
      text_objects=[]

      required_simulations=['UNFCCC_LULUCF', \
                            'UNFCCC_FL-FL', \
                            'UNFCCC_GL-GL', \
                            'UNFCCC_CL-CL', \
                            'UNFCCC_forest_convert', \
                            'UNFCCC_grassland_convert', \
                            'UNFCCC_cropland_convert', \
                            'UNFCCC_wetland_convert', \
                            'UNFCCC_settlement_convert', \
                            'UNFCCC_other_convert']
      for csim in required_simulations:
         if csim not in desired_simulations:
            print("Need to include {} in the simulation list!".format(csim))
         #endif
      #endif

      tot_index=desired_simulations.index("UNFCCC_LULUCF")

      # If we have no data, there is no reason to make this plot.
      test_vals=simulation_data[tot_index,:,iplot]
      check_vals=np.where(np.isnan(test_vals),True,False)
      if check_vals.all():
         print("No data for {}.  Skipping this country/region.".format(desired_simulations[isim]))
         #print(test_vals)
         #print(check_vals)
         continue
      #endif

      # Print out each of the bars for the average.  

      # I need to figure out where the total LULUCF value will be placed.  It depends on how many
      # average periods we have.  The first LULUCF value will be placed next to the first year,
      # and the last will be placed next to the last year.
      # I want the left side of the first bar to be one year away from left side of the plot, and
      # the right side of the last bar to be one year away from the right side of the plot.

      # Total bars: (len(barnames)+1)*(naverages-1)+1
      # Total years: xplot_max-xplot_min-2   # taking one year on either side
      # Bar width = (Total bars)/(Total years)
      

      # How wide the bars are between the LULUCF totals depends on how many bars we have
      # I know I will have five bars in addition to the total: FL-FL, GL-GL, CL-CL, net gain (LUC), net loss (LUC)
      # The net gain and net loss will be stacked from some of the other categories.
      barnames=["UNFCCC_FL-FL", "UNFCCC_GL-GL", "UNFCCC_CL-CL", 'UNFCCC_woodharvest',"LUC (+)", "LUC (+)"]
      nbars=len(barnames)

      nbars_tot=(len(barnames)+1)*(naverages-1)+1
      barwidth=(xplot_max-xplot_min-2)/nbars_tot

      nskip=(nbars+1)*barwidth

      # The first plotting position should therefore be the second year in our chart plus half
      # the bar width.
      plotting_positions=np.arange(xplot_min+1+0.5*barwidth,xplot_max-1,nskip)
      if len(plotting_positions) != naverages:
         print("Not sure why our plotting positions don't equal the number of averages!")
         print("Plotting positions: ",plotting_positions)
         print("naverages: ",naverages)
         print("xplot_min: ",xplot_min)
         print("xplot_max: ",xplot_max)
         print("nskip: ",nskip)
         print("nbars_tot: ",nbars_tot)
         print("nbars: ",nbars)
         print("barwidth: ",barwidth)
         sys.exit(1)
      #endif
      print("Plotting positions: ",plotting_positions)

      # The data positions are different from the plotting positions!
      lulucf_positions=np.array(syear_average.copy())
      data_mask=[False] * ndesiredyears
      for iyear in lulucf_positions:
         temp_index=np.where( allyears == iyear)
         sindex=int(temp_index[0])
         data_mask[sindex]=True
      #endfor
      temp_data=simulation_data[:,data_mask,iplot].copy()

      # The LULUCF values are the full values.  For the rest of the bars, though, I plot the difference
      # between the values.  So the other arrays are one shorter than this array.
      ndiffs=temp_data.shape[1]-1
      diff_array=np.zeros((temp_data.shape[0],ndiffs),dtype=float)
      percent_diff_array=np.zeros((temp_data.shape[0],ndiffs),dtype=float)
      for iyear in range(ndiffs):
         diff_array[:,iyear]=temp_data[:,iyear+1]-temp_data[:,iyear]
         percent_diff_array[:,iyear]=diff_array[:,iyear]/abs(temp_data[:,iyear])*100
      #endif

      # This gets tricky for the net gain and net loss.  I need to loop over all the possible data at every point
      # to see if it's positive or negative, and then add it to the correct one.

      netsims=['UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert']

      lulucf_bars=ax1.bar(plotting_positions, temp_data[tot_index,:], color=facec[desired_simulations.index("UNFCCC_LULUCF")],width=barwidth,alpha=production_alpha)
      legend_axes.append(lulucf_bars)
      legend_titles.append(displayname[tot_index])

      # These are routines to put text above and below the bars.
      # Notice that I pass the result of the ax1.bar here.  Even if
      # this is only a single bar, I need to loop over it, since 
      # all the bars are stored in a BarContainer object.
      #
      def top_label(rects,percent_label,text_objects):
         # This is somewhat confusing.  The ha and va (horizontal and vertical alignments)
         # in the text call below refer to the final object, after it has been rotated.
         for idx,rect in enumerate(rects):
            height = rect.get_height()
            bottom_point=rect.get_y()
            # Height can be less than zero.  I suppose for bars, the x,y is always
            # the origin, and negative values will be plotted downwards.
            if(height * percent_label < 0.0):
               print("Percent change has one sign and bar height has another!")
               print("height: ",height)
               print("percent_label: ",percent_label)
               sys.exit(1)
            #endif
            if(height > 0):
               text_obj=ax1.text(rect.get_x() + rect.get_width()/2., height+bottom_point,
                        " +{:.1f}%".format(percent_label),fontsize=12,color='k',fontweight='bold',
                                 ha='center', va='bottom', rotation=90) 
               text_objects.append(text_obj)

            else:
               text_obj=ax1.text(rect.get_x() + rect.get_width()/2., bottom_point,
                        " -{:.1f}%".format(abs(percent_label)),fontsize=12,color='k',fontweight='bold',
                        ha='center', va='bottom', rotation=90)
               text_objects.append(text_obj)
           #endif
         #endfor
      #enddef
      #
      def bottom_label(rects,cname,text_objects):
         for idx,rect in enumerate(rects):
            height = rect.get_height()
            bottom_point=rect.get_y()
            print("In bottom label! ",height,bottom_point,height+bottom_point)
            # I add some space for padding
            if height < 0.0:
               text_obj=ax1.text(rect.get_x() + rect.get_width()/2., height+bottom_point,
                                 cname + " ",fontsize=12,color='k',fontweight='bold',
                                 ha='center', va='top', rotation=90) 
            else:
               text_obj=ax1.text(rect.get_x() + rect.get_width()/2., bottom_point,
                                 cname + " ",fontsize=12,color='k',fontweight='bold',
                                 ha='center', va='top', rotation=90) 
            #endif
            text_objects.append(text_obj)

           #endif
         #endfor
      #enddef

      # I will do some odd manipulations and will have to rescale the plotting axes after.
      # So keep track of the min and max values.
      plotmin=temp_data[tot_index,:].min()
      plotmax=temp_data[tot_index,:].max()
      # Since we are doing bar plots, we need to make sure the bottom of the bar
      # is included in our viewing window.
      # If I remove this, I can zoom in on where things actually happen.
      #plotmax=max(plotmax,0.0)
      #plotmin=min(plotmin,0.0)

      # For every interval, we need to make a new bar plot, since the values in the loss/gain
      # may change.
      for iyear in range(ndiffs):

         # First, how much total change did we have between the last period and this period?
         tot_change=diff_array[tot_index,iyear]
         tot_percent_change=diff_array[tot_index,iyear]/abs(temp_data[tot_index,iyear+1])*100.0

         yval=temp_data[tot_index,iyear]
         
         barnames_normal=["UNFCCC_FL-FL", "UNFCCC_GL-GL", "UNFCCC_CL-CL","UNFCCC_woodharvest"]
         for ibar,cbar in enumerate(barnames_normal):
            xval=plotting_positions[iyear]+barwidth*(ibar+1)
            
            isim=desired_simulations.index(barnames[ibar])
            plot_value=diff_array[isim,iyear]
            color_value=facec[isim]
            
            p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=production_alpha)
            top_label(p1,diff_array[isim,iyear]/tot_change*tot_percent_change,text_objects)
            bottom_label(p1,displayname[isim],text_objects)
            if displayname[isim] not in legend_titles:
               legend_axes.append(p1)
               legend_titles.append(displayname[isim])
            #endif
            yval=yval+plot_value

            if yval > plotmax:
               plotmax=yval
            elif yval <= plotmin:
               plotmin=yval
            #endif
            

         #endfor

         barnames_net=["LUC (+)", "LUC (-)"]
         for ibar,cbar in enumerate(barnames_net):
            xval=plotting_positions[iyear]+barwidth*(ibar+1+len(barnames_normal))
            
            overall_bar_bottom=yval
            final_height=0.0

            if barnames_net[ibar] == "LUC (+)":
               # Plot all positive values
               for jsim in range(len(netsims)):
                  isim=desired_simulations.index(netsims[jsim])
                  plot_value=diff_array[isim,iyear]
                  color_value=facec[isim]
                  if plot_value > 0.0:
                     # Net gain
                     print("vcxv gain ",netsims[jsim],xval,yval,plot_value)
                     p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=production_alpha)
                     if displayname[isim] not in legend_titles:
                        legend_axes.append(p1)
                        legend_titles.append(displayname[isim])
                     #endif
                     yval=yval+plot_value
                     final_height=final_height+plot_value
                     if yval > plotmax:
                        plotmax=yval
                     elif yval <= plotmin:
                        plotmin=yval
                     #endif
                  #endif
               #endfor
            else:
               # Plot all negative values
               for jsim in range(len(netsims)):
                  isim=desired_simulations.index(netsims[jsim])
                  plot_value=diff_array[isim,iyear]
                  color_value=facec[isim]
                  if plot_value <= 0.0:
                     # Net loss
                     print("vcxv loss ",netsims[jsim],xval,yval,plot_value)
                     p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=production_alpha)
                     if displayname[isim] not in legend_titles:
                        legend_axes.append(p1)
                        legend_titles.append(displayname[isim])
                     #endif
                     yval=yval+plot_value
                     final_height=final_height+plot_value
                     if yval > plotmax:
                        plotmax=yval
                     elif yval <= plotmin:
                        plotmin=yval
                     #endif
                  #endif
               #endfor
            #endif

            # Create an outlined bar that we can also use to position the labels
            print("jfioezj ",final_height,overall_bar_bottom)
            p1=ax1.bar(xval, final_height, bottom=overall_bar_bottom,color="None",width=barwidth,edgecolor="black",linewidth=0.1,alpha=production_alpha)
            top_label(p1,final_height/abs(tot_change)*abs(tot_percent_change),text_objects)
            bottom_label(p1,barnames_net[ibar],text_objects)

        #endfor

      #endfor

      #
      #variables = globals().copy()
      #variables.update(locals())
      #shell = code.InteractiveConsole(variables)
      #shell.interact()
      #

      # This is a bit ugly, but the only way I see to find out what
      # the upper and lower extents are on our y-axis so that we can
      # adjust for the various text we have added and be sure that
      # it all falls inside the plot space.
      # It actually requires an iterative approach.  When I do the first pass,
      # I found out where the text is on the data coordinate system.  I then
      # rescale the y-axis.  However, the size of my text doesn't change,
      # which means it extends to a different y-value after scaling!
      #  I need to find the absolute coordinates of the bounding
      # box of the axis and then compare the text values to that,
      # adjusting until they converge.
      iloop=1
      loverlap=True
      while loverlap:
         if iloop > 20:
            break
         #endif
         #print("jifez ",iloop)
         for iobj in text_objects:
            # Bounding box seems to be in (x0,y0),(x1,y1) format, and not
            # in data coordinates.  How can I get it in data coordinates?
            im_ext = iobj.get_window_extent(renderer=canvas.get_renderer())
            # With this simple transform
            bbox = im_ext.transformed(ax1.transData.inverted())
            bbox_arr=np.array(bbox)
            # The y value of the bottom of the text box is therefore
            # bbox_arr[0,1]
            if plotmin > bbox_arr[0,1]:
               plotmin=bbox_arr[0,1]
            #endif
            if plotmax < bbox_arr[1,1]:
               plotmax=bbox_arr[1,1]
            #endif
            #print("jifoez ",iobj)
            #print("jifoez ",bbox_arr)
         #endfor

         # Rescale the axis after doing the manipulations above.
         # In theory, only a small buffer is needed because we have adjusted
         # our lowest value on the plot by the extents of the text.
         plotdiff=plotmax-plotmin
         ax1.set_ylim(plotmin,plotmax+0.05*abs(plotdiff))
         #print("nvvvvvvv ",iloop,plotdiff)
         iloop=iloop+1
         #loverlap=False
      #endwhile

      # This seems best done after all the scaling with the other text.
      # This is a short routine to put text inside of our bars
      def in_label(rects):
         for idx,rect in enumerate(rects):
            height = rect.get_height()
            if height < 0.0:
               ax1.text(rect.get_x() + rect.get_width()/2., 0.95*height,
                        "{:.2f}".format(height),fontsize=14,color='white',fontweight='bold',
                        ha='center', va='bottom', rotation=90)
            else:
               ax1.text(rect.get_x() + rect.get_width()/2., 0.5*height,
                        "{:.2f}".format(height),fontsize=14,color='white',fontweight='bold',
                     ha='center', va='center', rotation=90)
            #endif
         #endfor
      #enddef
      in_label(lulucf_bars)

      # Now I add a few things that I don't want rescaled
# Now add some text and arrows.
      text_place=ax1.get_ylim()
      text_place=text_place[0]-0.08*(text_place[1]-text_place[0])
      for iaverage in range(naverages):
         # This puts text for the large LULUCF bars to indicate which years they cover
         text_obj=ax1.text(plotting_positions[iaverage],text_place,'{}-{} mean'.format(syear_average[iaverage],eyear_average[iaverage]),horizontalalignment='center',fontsize=14)
         # I don't want to base scaling on this text
         #text_objects.append(text_obj)
      #endof

      # This adds a thick black arrow along the bottom axis which indicates a total change in the LULUCF bars from
      # one period to the next.  I have the arrow go from 25-75% of the distance between the two bars.
      ycoord=ax1.get_ylim()
      ycoord=ycoord[0]
      for iyear in range(ndiffs):
         yearrange=plotting_positions[iyear+1]-plotting_positions[iyear]
         midpoint=plotting_positions[iyear]+yearrange/2.0
         spoint=plotting_positions[iyear]+0.25*yearrange
         epoint=plotting_positions[iyear]+0.75*yearrange
         ax1.annotate('', xy=(epoint, ycoord),  xycoords='data',
                      xytext=(spoint,ycoord), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='right', verticalalignment='top',
            )
         deltaval=diff_array[tot_index,iyear]/abs(temp_data[tot_index,iyear+1])*100.0
         if deltaval>0.:
            ax1.text(midpoint, text_place, '+'+str(np.around(deltaval,decimals=1))+'%', ha="center", va="center", fontsize=13,fontweight='bold')
         else:
            ax1.text(midpoint, text_place, str(np.around(deltaval,decimals=1))+'%', ha="center", va="center", fontsize=13,fontweight='bold')
         #endif
      #endfor

   #endif
   ###

   # Sometimes we want the y-axis for every plot to be identical
   if lharmonize_y:
      ax1.set_ylim(ymin,ymax)
   #endif

   # Use a catch-all to redo the legend if need be. This will overwrite anything done
   # above if it's defined in the simulation set-up.
   if desired_legend:
      print("Reording legend.")

      # run a quick check
      remove_legends=[]
      for isim,csim in enumerate(desired_legend):
         if csim not in legend_titles:
            print("{0} does not appear to be present in the simulations we have treated.".format(csim))
            print("Please change desired_legend for graph {0}".format(graphname))
            print(desired_legend)
            print(legend_titles)
            #sys.exit(1)
            print("I am continuing, assuming that the legend was removed because no data exists.  CHECK YOUR PLOTS!")
            # It's bad to remove an element of the list inside the loop!  The next
            # element is missed.
            #desired_legend.remove(csim)
            remove_legends.append(csim)
         #endtry
      #endfor

      # Do NOT remove directly from desired_legend, since that will
      # mess up all the following plots.
      temp_desired_legend=desired_legend.copy()
      if remove_legends:
         for clegend in remove_legends:
            temp_desired_legend.remove(clegend)
         #endfor
      #endif

      # I cannot use a simple equals here, because the axes are references.  Using the equals copies the reference,
      # so when the one of the references is modified, we lose the original value.  Thankfully, "copy" copies the
      # actual object.
      legend_axes_backup=copy.copy(legend_axes)
      for isim,csim in enumerate(temp_desired_legend):
         legend_axes[isim]=copy.copy(legend_axes_backup[legend_titles.index(csim)])
      #endif
      legend_titles=temp_desired_legend

      print("After re-ordering: ",legend_titles)
   #endif

   

   # Now a bunch of things changing the general appearence of the plot
   if not lplot_countrytot:
      ax1.set_ylabel(r'g C yr$^{-1}$ m$^2$ of country)', fontsize=14)
   else:
      ax1.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)
   #endif
   # For the xaxis, there are some plots where we don't want ticks and tick labels
   if graphname != "unfccc_lulucf_bar":
      ax1.set_xlabel('Year', fontsize=14)
      ax1.xaxis.set_major_locator(MultipleLocator(5))
      ax1.xaxis.set_minor_locator(MultipleLocator(1))
      ax1.tick_params(axis='x', which='major', labelsize=14)
      ax1.tick_params(axis='x', which='minor', labelsize=14)
      # We have some special lines here, which indicate the start of IPCC accounting periods, I believe?
      ax1.axvline(x=2005,color='peru', linestyle=':')
      ax1.axvline(x=2015,color='k', linestyle=':')
   else:
      ax1.tick_params(
         axis='x',          # changes apply to the x-axis
         which='both',      # both major and minor ticks are affected
         bottom=False,      # ticks along the bottom edge are off
         top=False,         # ticks along the top edge are off
         labelbottom=False) # labels along the bottom edge are off
   #endif

   ax1.set_xlim(xplot_min,xplot_max)
   ax1.tick_params(axis='y', which='major', labelsize=14)
   ax1.tick_params(axis='y', which='minor', labelsize=14)

   if graphname == "forestry_full" and lplot_areas:
      # I want the bars to only take up the bottom third of the graph or so, so I want
      # the full data to only take up the top two-thirds
      ylimits=ax1.get_ylim()
      yaxisrange=ylimits[1]-ylimits[0]
      ax1.set_ylim(ylimits[0]-0.5*yaxisrange,ylimits[1])
   #endif

#   ax1.legend(legend_axes,legend_titles,bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",mode="expand", borderaxespad=0, ncol=3,fontsize='large')

   # Now copy the full ax1 legend to ax2, and turn off that from ax1, just
   # to make the spacing a little bit better.
   # Also change the number of columns in the legend in case we have a lot of text.
   if graphname in ("inversions_combined","inversions_full", "inversions_test","inversions_combined","inversions_combinedbar"):
      ax2.legend(legend_axes,legend_titles,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=2,fontsize='large')                     
   else:
      ax2.legend(legend_axes,legend_titles,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=3,fontsize='large')                     
   #endif
   ax2.axis('off')

   cc='/home/orchidee03/cqiu/2Drun/inventories/inventories3/cc_by_gray.png'
   img=plt.imread(cc)
   newax = fig.add_axes([0.1, 0.0, 0.05, 0.05], anchor='NE', zorder=-1)
   newax.imshow(img)
   newax.axis('off')
   # In January 2020, we decided to change the data source tagline
   #ax1.text(1.0,0.3, 'VERIFY Data: '+datasource, transform=newax.transAxes,fontsize=12,color='darkgray')
   ax1.text(1.0,0.3, 'VERIFY Project', transform=newax.transAxes,fontsize=12,color='darkgray')

   if printfakewarning:
      if lshow_productiondata:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data (shown in lighter symbols). Bars indicating range are always lighter.', transform=newax.transAxes,fontsize=12,color='red')
      else:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data.  For illustration purposes only.', transform=newax.transAxes,fontsize=12,color='red')
      #endif
   #endif

   ax1.set_title(plot_titles[iplot],fontsize=16)

   if lprintzero:
      ax1.hlines(y=0.0,xmin=allyears[0]-0.5,xmax=allyears[-1]+0.5,color="black",linestyle='--',linewidth=0.1)
   #endif

   #plt.tight_layout(rect=[0, 0.05,1 , 1])
   fig.savefig(output_file_start+desired_plots[iplot]+output_file_end,dpi=300)
   plt.close(fig)















