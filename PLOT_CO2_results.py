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
#   modifying the sim_params.desired_plots list.
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
import sys,traceback
import math
import pandas as pd
from netCDF4 import Dataset
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec
import re
from itertools import compress
from textwrap import fill # legend text can be too long
import argparse

# These are my own that I have created locally
from country_subroutines import get_countries_and_regions_from_cr_dict,get_country_region_data,get_country_codes_for_netCDF_file
from plotting_subroutines import get_simulation_parameters,find_date,get_cumulated_array,readfile,group_input,combine_simulations,calculate_country_areas,get_country_areas,read_fake_data,create_sectorplot_full,print_test_data
from plot_types import create_unfccc_bar_plot,create_mean_plot
from plotting_inputs import simulation_parameters

# I use Python 3 constructs.
if sys.version_info[0] < 3:
    raise Exception("You must use Python 3")
#endif

###############################################
# Set up all the input parameters that control the simulation
parser = argparse.ArgumentParser(description='Create synthesis plots from data found on the VERIFY database.')

sim_params=simulation_parameters(parser)

###############################################


####################################################################
############################# This is the start of the program
####################################################################

nplots=len(sim_params.desired_plots)

desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displayname_err_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,overwrite_coeffs,overwrite_operations,desired_legend,flipdatasign_master,lcorrect_inversion_master,lplot_errorbar_master,lwhiskerbars_master,ldetrend=get_simulation_parameters(sim_params.graphname,sim_params.lshow_productiondata)

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
simulation_data=np.zeros((numsims,sim_params.ndesiredyears,nplots))*np.nan
# Some of the files, like the inventories, have an error that we can read in
simulation_err=np.zeros((numsims,sim_params.ndesiredyears,nplots))*np.nan
# and occasionally we want the min and the max values, in particular for
# combinations of other simulations.  I use this for uncertainty as well.
simulation_min=np.zeros((numsims,sim_params.ndesiredyears,nplots))*np.nan
simulation_max=np.zeros((numsims,sim_params.ndesiredyears,nplots))*np.nan


if sim_params.luse_fake_data:
   print("WARNING: reading in fake data for graph: {}".format(sim_params.graphname))
   print("All plots will have the same data.")
   for isim,simname in enumerate(desired_simulations):  
      for iplot in range(nplots):
         simulation_data[isim,:,iplot],simulation_err[isim,:,iplot],simulation_min[isim,:,iplot],simulation_max[isim,:,iplot]=read_fake_data(sim_params.ndesiredyears,simname)
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
         inv_fCO2=readfile(fname,variables[isim],sim_params.ndesiredyears,True,1990,2018)  #monthly
         # This reads in the associated error.  It assumes that the file
         # has another variable of the same name, with _ERR added.
         inv_fCO2_err=readfile(fname,variables[isim] + "_ERR",sim_params.ndesiredyears,True,1990,2018)  #monthly
         annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
         annfCO2_err=np.nanmean(inv_fCO2_err,axis=1)   #convert from monthly to yearly
         
         annfCO2_min=annfCO2.copy()*np.nan # these values are not used here
         annfCO2_max=annfCO2.copy()*np.nan
   
         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2_err,annfCO2_min,annfCO2_max,sim_params.desired_plots,True,sim_params.ndesiredyears,nplots,sim_params.all_regions_countries,desired_simulations[isim])
         

         # I want to convert the percentage error values into min and max.  I do that below in 
         # a vector fashion.  The min and max values are what I will actually plot as the
         # error bars.


      elif simtype[isim] == ("MINMAX"):
         # This file has the variable value, as well as values of _MIN and _MAX which give error bars
         inv_fCO2=readfile(fname,variables[isim],sim_params.ndesiredyears,True,1990,2018)  #monthly
         # This reads in the associated error.  It assumes that the file has two other variables with similar names..
         inv_fCO2_min=readfile(fname,variables[isim] + "_MIN",sim_params.ndesiredyears,True,1990,2018)  #monthly
         inv_fCO2_max=readfile(fname,variables[isim] + "_MAX",sim_params.ndesiredyears,True,1990,2018)  #monthly
         
         annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
         annfCO2_min=np.nanmean(inv_fCO2_min,axis=1)   #convert from monthly to yearly
         annfCO2_max=np.nanmean(inv_fCO2_max,axis=1)   #convert from monthly to yearly

         print("Values: ",desired_simulations[isim],annfCO2[:,11])
         print("Min: ",desired_simulations[isim],annfCO2[:,11])
         print("Max: ",desired_simulations[isim],annfCO2[:,11])
         
         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2,annfCO2_min,annfCO2_max,sim_params.desired_plots,False,sim_params.ndesiredyears,nplots,sim_params.all_regions_countries,desired_simulations[isim])

      elif simtype[isim] in ("TRENDY","VERIFY_BU","NONVERIFY_BU","INVENTORY_NOERR","VERIFY_TD","GLOBAL_TD","REGIONAL_TD","OTHER"):
         inv_fCO2=readfile(fname,variables[isim],sim_params.ndesiredyears,True,sim_params.allyears[0],sim_params.allyears[-1])  #monthly
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

         simulation_data[isim,:,:],simulation_err[isim,:,:],simulation_min[isim,:,:],simulation_max[isim,:,:]=group_input(annfCO2,annfCO2,annfCO2_min,annfCO2_max,sim_params.desired_plots,False,sim_params.ndesiredyears,nplots,sim_params.all_regions_countries,desired_simulations[isim])
      else:
         print("Do not know how to process data for simulation type: {0}".format(simtype[isim]))
         sys.exit()
      #endif

   #endfor
#endif
print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 1 (after reading in all)")

# If something is equal to zero, I don't plot it.
simulation_data[simulation_data == 0.0]=np.nan

print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 3 (after NaNing data)")

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
      for iyear in range(sim_params.ndesiredyears):
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
      for iyear in range(sim_params.ndesiredyears):
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
print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 3 (after calculating min/max)")


# Now where we have min/max but not error, calculate an error value.  This is an approximation, since
# the min/max may not be symmetric, but a % error is symmetric by defintion.
# I take the interval between the min and the max and divide it by two to estimate the error.  This can
# give crazy large values if the median happens to be near 0, so not sure it's useful for datasets with
# a min/max range as the error bars.
err_mask=np.logical_and(have_min,np.invert(have_err))
simulation_err=np.where( err_mask,0.5*(simulation_max-simulation_min)/abs(simulation_data),simulation_err)

print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 4 (after calculating error)")

# Check to see if we have inventory data.  If so, we do something different in plotting.
ninv=simtype.count("INVENTORY")
if ninv > 0:
   linventories=True
   print("We have some inventories in this dataset.")
else:
   linventories=False
   print("We do not have inventories in this dataset.")
#endif


# For one plot type, we need to remove the biofuel emissions and the emissions
# from inland water bodies from the inversions.  Inversions see uptakes to both
# biomass stored in forests that to going to biofuels; our models don't consider biofuel uptake; 
# inventories report biofuels as a memo item, so not included in the LULUCF numbers).  It seems
# reasonable to assume that no inversion includes biofuel emissions with the FF priors, either.
# After much discussion, we found the biofuel corrections to be too complicated.  So we will
# NOT do that for 2020.
# I have to use a strange array declaration here because if I declare something
# like correction_simulations=("rivers_lakes_reservoirs_ULB"), Python thinks
# that it is a character array and loops over every letter.  Not what
# we want.

if any(lcorrect_inversion):
   correction_tag=" (removing rivers_lakes_reservoirs_ULB)"
   correction_simulations=np.array(["rivers_lakes_reservoirs_ULB"],dtype=object)
   correction_data=np.zeros((sim_params.ndesiredyears,nplots))
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

#endif

print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 6 (after corrections)")

# Sometimes I need to sum several variables into one timeseries.  This does that, assuming
# that there one simulation already in the dataset that will be overwritten.
simulation_data[:,:,:],simulation_min[:,:,:],simulation_max[:,:,:],simulation_err[:,:,:]=combine_simulations(overwrite_simulations,overwrite_coeffs,overwrite_operations,simulation_data,simulation_min,simulation_max,simulation_err,desired_simulations,sim_params.graphname)

print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 7 (after combine_simulations)")

# Need to be careful with this.  This applies Normalization to Zero Mean and Unit of Energy (Z-normalization)
# to every timeseries.  Not sure how it'll work with timeseries that
# have error bars.  Want to do this before the means are calculated.
if ldetrend:
    print("Detrending all timeseries with Z-normalization.")
    for isim,csim in enumerate(desired_simulations):
        for iplot in range(nplots):
            have_min=np.asarray(simulation_min[isim,:,iplot])
            have_min= np.invert(np.isnan(have_min))
            have_max=np.asarray(simulation_max[isim,:,iplot])
            have_max= np.invert(np.isnan(have_max))
            if have_min.any():
                print("Not sure I can detrend with minimum values!")
                print(csim,iplot)
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif
            if have_max.any():
                print("Not sure I can detrend with maximum values!")
                print(csim,iplot)
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif

            # Calculate the mean of the timeseries
            ts_mean=np.nanmean(simulation_data[isim,:,iplot])
#            print("jifoez ",csim,iplot,ts_mean)
#            print(simulation_data[isim,:,iplot])
            ts_std=np.nanstd(simulation_data[isim,:,iplot])
            simulation_data[isim,:,iplot]=(simulation_data[isim,:,iplot]-ts_mean)/ts_std
        #endfor
    #endfor

#endif

print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 7b (after detrending)")

# For clarity on the plots, we can plot the mean values of our period of
# interest for each dataset somewhere.  Do that calculation here.
if sim_params.lplot_means:
   print("Calculating means across all simulations for only the overlapping years.")
   simulation_mean=np.zeros((numsims,nplots))*np.nan

   # Calculate the years of overlap that we have.  I need to not consider
   # some datasets, due to very short timeframes (MS-NRT is only a single year).
   # Only take the overlapping years.  For each plot this could be different.
   exclude_simulation_means=['MS-NRT']
   remove_indices=[]
   for isim,csim in enumerate(exclude_simulation_means):
      try:
         remove_index=desired_simulations.index(csim)
         remove_indices.append(remove_index)
         print("Remove {} from our calculation of overlap years for the means.".format(csim))
      except:
         print("{} does not appear in our simulations.  Not removing from our calculation of overlap years for the means.".format(csim))
      #endtry
   #endfor
   #print(",ivoez ",desired_simulations)
   #remove_indices=desired_simulations.index(exclude_simulation_means)
   #print("azeza ",remove_indices)
   #print("jfioez BEFORE ",simulation_data.shape)
   if remove_indices:
      test_data=np.delete(simulation_data, remove_indices ,axis=0)
   else:
      test_data=simulation_data
   #endif
   #print("jfioez ",test_data.shape,simulation_data.shape)
   overlapping_years=[]
   for iplot in range(nplots):
      overlapping_years_plot=[]
      for iyear in range(sim_params.ndesiredyears):
         nans=np.isnan(test_data[:,iyear,iplot])
         # want True if there are no NaNs for this year
         overlapping_years_plot.append(not any(nans))
      #endfor
      overlapping_years.append(overlapping_years_plot)
      #print("fjeioze ",iyear,simulation_data[:,iyear,iplot])
      #print("jfieoze ",nans)
      #print("jfieoze ",overlapping_years[iyear],iyear)
   #endfor
   #print("jifez 0 ",overlapping_years[0])
   #print("jifez 1 ",overlapping_years[1])
   #print("jifez 2 ",overlapping_years[2])

   for isim,csim in enumerate(desired_simulations):
      for iplot in range(nplots):

         # We exclude some simulations from the overlap period, like MS-NRT, which
         # only has a single year.
         if csim not in exclude_simulation_means:
            mean_years=overlapping_years[iplot]
         else:
            mean_years=np.asarray(simulation_data[isim,:,iplot])
            mean_years= np.invert(np.isnan(mean_years))
         #endif

         simulation_mean[isim,iplot]=np.nanmean(simulation_data[isim,mean_years,iplot])
         # What if we just store this in the last value of our data array?
         if not np.isnan(simulation_data[isim,-1,iplot]):
            print("Already have data in the last year of this timeseries!")
            print("This messes up where I want to put the timeseries average.")
            print("Simulation: ",csim,"  Plot: ",iplot)
            print(simulation_data[isim,:,iplot])
            sys.exit(1)
         #endif
         simulation_data[isim,-1,iplot]=simulation_mean[isim,iplot]
         # If we have min and max values, need to put something there, too.
         # Else a failsafe will be triggered later.
         have_min=np.asarray(simulation_min[isim,:,iplot])
         have_min= np.invert(np.isnan(have_min))
         have_max=np.asarray(simulation_max[isim,:,iplot])
         have_max= np.invert(np.isnan(have_max))
         #print("jifoez ",have_min.any(),have_max.any(),desired_simulations[isim],mean_years)
         if have_min.any():
            simulation_min[isim,-1,iplot]=np.nanmean(simulation_min[isim,mean_years,iplot])
         #endif
         if have_max.any():
            simulation_max[isim,-1,iplot]=np.nanmean(simulation_max[isim,mean_years,iplot])
         #endif
      #endfor
   #endfor
#endif



######### Here is where we get to the actual plotting
# set the titles
plot_titles=[]
for iplot,cplot in enumerate(sim_params.desired_plots):
   try:
      plot_titles.append("FCO2 land - " + sim_params.plot_titles_master[cplot] + titleending)
   except:
      plot_titles.append("No title given.")
   #endtry
#endfor

# There may be some situations in which we want to make the range of the y-axis 
# identical in all plots
if sim_params.lharmonize_y:
   if sim_params.lexternal_y:
      ymin=sim_params.ymin_external
      ymax=sim_params.ymax_external
   else:
      ymin=np.nanmin(simulation_data[:,:,:])
      ymin=ymin-0.05*abs(ymin)
      ymax=np.nanmax(simulation_data[:,:,:])
      ymax=ymax+0.05*abs(ymax)
   #endif
#endif

##
# For one of the graphs, I do a little data processing.
# I do this before the loop because I want to still print out
# good values to the .csv files.
if sim_params.graphname == "unfccc_lulucf_bar":

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
      temp_index=np.where( sim_params.allyears == syear_average[iaverage])
      sindex=int(temp_index[0])
      temp_index=np.where( sim_params.allyears == eyear_average[iaverage])
      eindex=int(temp_index[0])
      if syear_average[iaverage] != sim_params.allyears[sindex]:
         print("Something is going wrong in starting year averages!")
         print("iaverage: {}, syear_average: {}".format(iaverage,syear_average[iaverage]))
         print("sindex: {}, sim_params.allyears: {}".format(sindex,sim_params.allyears[sindex]))
         sys.exit(1)
      #endif
      if eyear_average[iaverage] != sim_params.allyears[eindex]:
         print("Something is going wrong in ending year averages!")
         print("iaverage: {}, eyear_average: {}".format(iaverage,eyear_average[iaverage]))
         print("eindex: {}, sim_params.allyears: {}".format(eindex,sim_params.allyears[eindex]))
         sys.exit(1)
      #endif       
      if eindex < sindex:
         print("Something wrong with averages at XYW.")
         print("iaverage: {}, syear: {}, eyear: {}".format(iaverage,syear_average[iaverage],eyear_average[iaverage]))
         sys.exit(1)
      #endif
      temp_array=simulation_data[:,sindex:eindex+1,:].copy()
      temp_array_err=simulation_err[:,sindex:eindex+1,:].copy()
      temp_array_min=simulation_min[:,sindex:eindex+1,:].copy()
      temp_array_max=simulation_max[:,sindex:eindex+1,:].copy()
      for iindex in range(sindex,eindex+1,1):
         simulation_data[:,iindex,:]=np.nanmean(temp_array,axis=1)
         simulation_err[:,iindex,:]=np.nanmean(temp_array_err,axis=1)
         simulation_min[:,iindex,:]=np.nanmean(temp_array_min,axis=1)
         simulation_max[:,iindex,:]=np.nanmean(temp_array_max,axis=1)
      #endfor
   #endif

##
print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 8")

######## Sometimes people want raw data.  I will
# print all raw data for all the plots to this file.
#datafile=open("plotting_data.txt","w")

# In case I want to scale by the area of the country, get the
# country areas
#calculate_country_areas()
country_areas=get_country_areas()

for iplot,cplot in enumerate(sim_params.desired_plots):

   print("**** On plot {0} ****".format(sim_params.plot_titles_master[cplot]))
   #datafile.write("**** On plot {0} ****\n".format(sim_params.plot_titles_master[cplot]))

   # Create a dataframe for all of these simulations, and print it to a .csv file
   # In order to do this, I should process all the data outside this loop
   # and make sure it's stored in simulation_data.  I am working towards that goal,
   # though perhaps not quite there yet.
   df=pd.DataFrame(data=simulation_data[:,:,iplot],index=displayname,columns=sim_params.allyears)
   print_test_data(sim_params.ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,sim_params.itest_sim,sim_params.itest_plot,desired_simulations,sim_params.desired_plots,"CHECKPOINT 9 (starting plots)")

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

         # Notice that I can ignore this if all my data is NaN
         if len(min_non_NaN) != len(non_NaN) and len(non_NaN) != 0:
            print("Why do data and minimum values have different numbers of NaN?")
            print(csim,sim_params.desired_plots[iplot])
            print("Data: ",simulation_data[isim,:,iplot])
            print("Min: ",simulation_min[isim,:,iplot])
            # For certain edge cases, this happens.  Greenland, for example.
            if sim_params.desired_plots[iplot] not in ("GRL","JEY"):
               sys.exit(1)
            else:
               temp_min=simulation_min[isim,:,iplot]
               temp_min[np.isnan(simulation_data[isim,:,iplot])]=np.nan
               print("Adjusted Min: ",simulation_min[isim,:,iplot])
            #endif
         #endif
            
         test_comp=np.invert(min_non_NaN == non_NaN)
         if test_comp.any():
            # Not terribly efficient to do it this way, but our DataFrames
            # should be small
            print("Found minimum values for ",desired_simulations[isim])

            # This creates the dataframe transposed from what I want.  But
            # it crashes if I flip the indices and columns, so I do this and
            # then append the transposed dataframe.
            newdf=pd.DataFrame(simulation_min[isim,:,iplot],index=sim_params.allyears,columns=[displayname[isim] + " MIN VALUES"])
                  
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

         # Notice that I can ignore this if all my data is NaN
         if len(max_non_NaN) != len(non_NaN) and not nancheck.all() and len(non_NaN) != 0:
            print("Why do data and maximum values have different numbers of NaN?")
            print(csim,sim_params.desired_plots[iplot])
            print("Data: ",simulation_data[isim,:,iplot])
            print("Max: ",simulation_max[isim,:,iplot])
            # For certain edge cases, this happens.  Greenland, for example.
            if sim_params.desired_plots[iplot] not in ("GRL","JEY"):
               sys.exit(1)
            else:
               temp_max=simulation_max[isim,:,iplot]
               temp_max[np.isnan(simulation_data[isim,:,iplot])]=np.nan
               print("Adjusted Max: ",simulation_max[isim,:,iplot])
            #endif
         #endif
            
         test_comp=np.invert(max_non_NaN == non_NaN)
         if test_comp.any():
            # Not terribly efficient to do it this way, but our DataFrames
            # should be small
            print("Found maximum values for ",desired_simulations[isim])

            # This creates the dataframe transposed from what I want.  But
            # it crashes if I flip the indices and columns, so I do this and
            # then append the transposed dataframe.
            newdf=pd.DataFrame(simulation_max[isim,:,iplot],index=sim_params.allyears,columns=[displayname[isim] + " MAX VALUES"])
                  
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
   df.to_csv(path_or_buf=output_file_start+sim_params.desired_plots[iplot]+data_file_end,sep=",")
   
   
   #df=pd.DataFrame(data=simulation_min[:,:,iplot],index=desired_simulations,columns=sim_params.allyears)
   #data_file_end=re.sub(r".png",r"_min.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+sim_params.desired_plots[iplot]+data_file_end,sep=",")
   #df=pd.DataFrame(data=simulation_max[:,:,iplot],index=desired_simulations,columns=sim_params.allyears)
   #data_file_end=re.sub(r".png",r"_max.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+sim_params.desired_plots[iplot]+data_file_end,sep=",")
   # This is more for debugging purposes, not always necessary
   #df=pd.DataFrame(data=simulation_err[:,:,iplot],index=desired_simulations,columns=sim_params.allyears)
   #data_file_end=re.sub(r".png",r"_err.csv",output_file_end)
   #df.to_csv(path_or_buf=output_file_start+sim_params.desired_plots[iplot]+data_file_end,sep=",")
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
   if not sim_params.lplot_countrytot:
      # The units of simulation data were in Tg C/yr.  This gives
      # Tg C/yr/square meter of country.  We want g C/yr/square meter of
      # country.
      simulation_data[:,:,iplot]=simulation_data[:,:,iplot]/country_areas[sim_params.countrynames[cplot]]*1e12
      
   #endif

   # First, I plot a series of bars, if they are present.  I want the symbols to fall on top of these
   # bars, so best to plot these first, and change the zorder to be low.
   for isim,simname in enumerate(desired_simulations):  
      if lplot_errorbar[isim]:

         # If we have no data, we have nothing to plot.
         ldata=False

         upperrange=simulation_max[isim,:,iplot]
         lowerrange=simulation_min[isim,:,iplot]
         if not lwhiskerbars[isim]:
            # This prints rectangles
            for iyear in range(sim_params.ndesiredyears):
               if np.isnan(simulation_data[isim,iyear,iplot]):
                  continue
               #endif
               ldata=True
               p1=mpl.patches.Rectangle((sim_params.allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=uncert_color[isim], alpha=sim_params.uncert_alpha,zorder=1)
               p2=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=sim_params.allyears[iyear]-0.5,xmax=sim_params.allyears[iyear]+0.5,color=facec[isim],linestyle='--',zorder=2)
               ax1.add_patch(p1)
            #endfor
         else:
            # This prints a symbol with whisker error bars
            whiskerbars=np.array((simulation_data[isim,:,iplot]-lowerrange[:],upperrange[:]-simulation_data[isim,:,iplot])).reshape(2,sim_params.ndesiredyears)
            p2=ax1.errorbar(sim_params.allyears,simulation_data[isim,:,iplot],yerr=whiskerbars,marker=plotmarker[isim],mfc=facec[isim],mec='black',ms=10,capsize=10,capthick=2,ecolor="black",linestyle='None',zorder=5)
            nandata=np.isnan(simulation_data[isim,:,iplot])
            if not nandata.all():
               ldata=True
            #endif

         #endif

         if not ldata:
            continue
         #endif

         legend_axes.append(p2)
         #if lcorrect_inversion[isim]:
         #   legend_titles.append(displayname[isim] + " (removing rivers_lakes_reservoirs_ULB)")
         #else:
         legend_titles.append(displayname[isim])
         ##endif
         if not lwhiskerbars[isim]:
            legend_axes.append(p1)
            legend_titles.append(displayname_err[isim])
         #endif
      #endif
   #endfor

   if "VERIFYBU" in desired_simulations:
      idata=desired_simulations.index("VERIFYBU")
      for iyear in range(sim_params.ndesiredyears):
         p2=ax1.hlines(y=simulation_data[idata,iyear,iplot],xmin=sim_params.allyears[iyear]-0.5,xmax=sim_params.allyears[iyear]+0.5,color=facec[idata],linestyle='--')
         p1=mpl.patches.Rectangle((sim_params.allyears[iyear]-0.5,simulation_min[idata,iyear,iplot]),1,simulation_max[idata,iyear,iplot]-simulation_min[idata,iyear,iplot], color=uncert_color[idata], alpha=sim_params.uncert_alpha)
         ax1.add_patch(p1)
      #endfor
      legend_axes.append(p2)
      legend_titles.append(displayname[idata])
      legend_axes.append(p1)
      legend_titles.append("Min/Max of VERIFY BU simulation")
 
      # Write raw data to a file
      #datafile.write("**** On dataset Mean of VERIFY BU simulations ****\n")
      #datafile.write("years {}\n".format(sim_params.allyears[:]))
      #datafile.write("data {}\n".format(simulation_data[idata,:,iplot]))
      #datafile.write("upperbounds {}\n".format(simulation_max[idata,:,iplot]))
      #datafile.write("lowerbounds {}\n".format(simulation_min[idata,:,iplot]))

   #endif


   # This is to plot the inventories
   if linventories and not (sim_params.graphname == "unfccc_lulucf_bar"):

      if sim_params.graphname == "sectorplot_full":

         temp_desired_sims=("UNFCCC_FL-FL","UNFCCC_GL-GL","UNFCCC_CL-CL")
         temp_data=np.zeros((len(temp_desired_sims),sim_params.ndesiredyears))
         for isim,csim in enumerate(temp_desired_sims):
            temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
         #endfor

         # plot the whole sum of these three runs
         #p1=ax1.scatter(sim_params.allyears,np.nansum(temp_data,axis=0),marker="X",facecolors="blue", edgecolors="blue",s=60,alpha=sim_params.nonproduction_alpha)
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
               p1=ax1.bar(sim_params.allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=sim_params.production_alpha*0.5)
            else:
               p1=ax1.bar(sim_params.allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=sim_params.nonproduction_alpha*0.5)
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

         # We do something different for land areas, which are plotted as
         # bars on an altnerative axis
         if sim_params.graphname == "forestry_full" and desired_simulations[isim] in ("LUH2v2_FOREST","UNFCCC_FOREST"):
            continue
         #endif 
         if sim_params.graphname == "grassland_full" and desired_simulations[isim] in ("LUH2v2_GRASS","UNFCCC_GRASS"):
            continue
         #endif 
         if sim_params.graphname == "crops_full" and desired_simulations[isim] in ("LUH2v2_CROP","UNFCCC_CROP"):
            continue
         #endif 


         if simtype[isim] == "INVENTORY" and sim_params.graphname != "sectorplot_full":
            print("Plotting inventories!")
            print(simulation_max[isim,:,iplot])
            #datafile.write("**** On dataset {0} ****\n".format(desired_simulations[isim]))

#            upperrange=simulation_data[isim,:,iplot]+simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
#            lowerrange=simulation_data[isim,:,iplot]-simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
            upperrange=simulation_max[isim,:,iplot]
            lowerrange=simulation_min[isim,:,iplot]
            #datafile.write("years {}\n".format(sim_params.allyears[:]))
            #datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))
            #datafile.write("upperbounds {}\n".format(upperrange[:]))
            #datafile.write("lowerbounds {}\n".format(lowerrange[:]))

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
            for iyear in range(sim_params.ndesiredyears):

               # If we have no uncertainty, then I don't want to show it.
               if not np.isnan(lowerrange[iyear]) and not np.isnan(lowerrange[iyear]):
                  p1=mpl.patches.Rectangle((sim_params.allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=uncert_color[isim], alpha=sim_params.uncert_alpha,zorder=zorder_value-2)
                  ax1.add_patch(p1)
                  lshow_uncert=True
               #endif
               #ax1.fill_between(np.array([sim_params.allyears[iyear]-0.5,sim_params.allyears[iyear]+0.5]),lowerrange[iyear],upperrange[iyear],color=uncert_color[isim],alpha=sim_params.uncert_alpha,zorder=zorder_value-1)
            #endfor

            if lshow_uncert:
               legend_axes.append(p1)
               legend_titles.append(displayname[isim] + " uncertainty")
            #endif

            # I want to make sure the symbol shows up on top of the error bars.
            # If this is not real data, make it lighter.
            for iyear in range(sim_params.ndesiredyears):
               if productiondata[isim]:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=sim_params.allyears[iyear]-0.5,xmax=sim_params.allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=sim_params.production_alpha,zorder=zorder_value-1)
               else:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=sim_params.allyears[iyear]-0.5,xmax=sim_params.allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=sim_params.nonproduction_alpha,zorder=zorder_value-1)
               #endif
            #endif

            legend_axes.append(p1)
            legend_titles.append(displayname[isim])
            #datafile.write("\n")

         #endif
      #endfor
   #endif

   # This is to plot all the other simulations not covered by the special cases above
   for isim,simname in enumerate(desired_simulations):  
      if simtype[isim] in ("NONVERIFY_BU","INVENTORY_NOERR","VERIFY_BU","TRENDY","GLOBAL_TD","REGIONAL_TD","MINMAX") or sim_params.graphname == "inversions_verify":
         
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
         if sim_params.graphname == "sectorplot_full" and desired_simulations[isim] in ("EPIC","ECOSSE_GL-GL","EFISCEN"):
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
            p1=ax1.scatter(sim_params.allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=sim_params.production_alpha,zorder=zorder_value)
         else:
            p1=ax1.scatter(sim_params.allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=sim_params.nonproduction_alpha,zorder=zorder_value)
         #endif
         legend_axes.append(p1)
         legend_titles.append(displayname[isim])

         #datafile.write("**** On dataset {0} ****\n".format(displayname[isim]))
         #datafile.write("years {}\n".format(sim_params.allyears[:]))
         #datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))

      #endif
   #endif

   # For this particular graph, I plot three of the VERIFY runs in a different way.
   if sim_params.graphname == "sectorplot_full":

      create_sectorplot_full()

   #endif

   # I want to plot the forest area on this plot as bars at the bottom.
   if sim_params.graphname in ("forestry_full","grassland_full","crops_full") and lplot_areas:
      print("Getting ready to plot land areas.")
      axsub = ax1.twinx()
      
      if sim_params.graphname == "forestry_full":
         land_areas=("LUH2v2_FOREST","UNFCCC_FOREST")
         labelname='Forest area \n[kha]'
      elif sim_params.graphname == "grassland_full":
         land_areas=("LUH2v2_GRASS","UNFCCC_GRASS")
         labelname='Grassland area \n[kha]'
      elif sim_params.graphname == "crops_full":
         land_areas=("LUH2v2_CROP","UNFCCC_CROP")
         labelname='Cropland area \n[kha]'
      #endif

      barwidth=0.3
      offset=-barwidth/2.0

      for land_area in land_areas:
         
         if land_area in desired_simulations:
      
            # This plots the LUH2v2 ESA-CCI land areas
            isim=desired_simulations.index(land_area)

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
            p1=axsub.bar(sim_params.allyears+offset, simulation_data[isim,:,iplot]/1000.0/10000.0, color=facec[desired_simulations.index(land_area)],width=barwidth,alpha=sim_params.production_alpha*0.3)
            legend_axes.append(p1)
            legend_titles.append(displayname_master[land_area])

            offset=offset+barwidth
         #endif
      #endif

      axsub.set_ylabel(labelname)
      

      #datafile.write("**** On dataset {0} ****\n".format(displayname[isim]))
      #datafile.write("years {}\n".format(sim_params.allyears[:]))
      #datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))

      # I want the bars to only take up the bottom third of the graph or so.
      ylimits=axsub.get_ylim()
      yaxisrange=ylimits[1]-ylimits[0]
      axsub.set_ylim(ylimits[0],ylimits[1]+3.0*yaxisrange)

   #endif

   # I want to try stacking some bars at the bottom and right-side axis of some of the inversion plots
   if any(lcorrect_inversion):

      temp_data=np.zeros((len(correction_simulations),sim_params.ndesiredyears))
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
            p1=axsub.bar(sim_params.allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=sim_params.production_alpha*0.3)
         else:
            p1=axsub.bar(sim_params.allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=sim_params.nonproduction_alpha*0.3)
         #endif
         legend_axes.append(p1)
         legend_titles.append(csim)
      #endfor


      if not sim_params.lplot_countrytot:
         axsub.set_ylabel(r'Correction for inversions\n[g C/yr/(m$^2$ of country)]')
      else:
         axsub.set_ylabel(r'Correction for inversions\n[Tg C yr$^{-1}$]')
      #endif

      # I would like the limits of the secondary X axis to be the same as the first, only shifted down
      # so that the bottom is equal to zero.
      ylimits=ax1.get_ylim()
      # Be careful if we are harmonizing the main axis
      if sim_params.lharmonize_y:
         yaxisrange=ymax-ymin
      else:
         yaxisrange=ylimits[1]-ylimits[0]
      #endif
      axsub.set_ylim(0,yaxisrange)
   #endif

   # This is a special bar plot that doesn't look like any
   # of the other timeseries.  I have already calculated
   # average values to use above.
   if sim_params.graphname == "unfccc_lulucf_bar":
      lskip,ax1=create_unfccc_bar_plot(desired_simulations,simulation_data,iplot,naverages,syear_average,eyear_average,sim_params.xplot_min,sim_params.xplot_max,sim_params.ndesiredyears,sim_params.allyears,ax1,facec,sim_params.production_alpha,legend_axes,legend_titles,displayname,canvas,output_file_end)
      if lskip:
         continue
      #endif
   #endif
   ###

   # Sometimes we want the y-axis for every plot to be identical
   if sim_params.lharmonize_y:
      ax1.set_ylim(ymin,ymax)
   #endif

   kp_string="Kyoto Protocol (entering into force)"
   pa_string="Paris Agreement"

   if sim_params.graphname != "unfccc_lulucf_bar":
      # We have some special lines here
      p1=ax1.axvline(x=2005,color='peru', linestyle=':')
      legend_axes.append(p1)
      legend_titles.append(kp_string)
      p1=ax1.axvline(x=2015,color='k', linestyle=':')
      legend_axes.append(p1)
      legend_titles.append(pa_string)
   #endif

   # Use a catch-all to redo the legend if need be. This will overwrite anything done
   # above if it's defined in the simulation set-up.
   if desired_legend:
      print("Reording legend.")

      # run a quick check
      remove_legends=[]
      for isim,csim in enumerate(desired_legend):
         if csim not in legend_titles:
            print("--- {0} does not appear to be present in the simulations we have treated.".format(csim))
            print("Please change desired_legend for graph {0}".format(sim_params.graphname))
            print("DESIRED: ",desired_legend)
            print("PLOTTED: ",legend_titles)
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

      # I need to add two at the beginning, since we always want them there.
      temp_desired_legend.insert(0,kp_string)
      temp_desired_legend.insert(1,pa_string)

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
   if not sim_params.lplot_countrytot:
      ax1.set_ylabel(r'g C yr$^{-1}$ m$^2$ of country)', fontsize=14)
   else:
      ax1.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)
   #endif

   if ldetrend:
       ax1.set_ylabel(r'[unitless]', fontsize=14)
   #endif

   # A special plot for emission factors
   if sim_params.graphname == "emission_factors":
       ax1.set_ylabel(r'Tg C yr$^{-1}$ m$^{-2}$ FL-FL', fontsize=14)
       print("jfieozje ",ax1.get_ylim())
       ymin_temp=np.nanmin(simulation_data[:,:,iplot])
       ymin_temp=ymin_temp-0.05*abs(ymin_temp)
       ymax_temp=np.nanmax(simulation_data[:,:,iplot])
       ymax_temp=ymax_temp+0.05*abs(ymax_temp)

       if np.isnan(ymin_temp) or np.isnan(ymax_temp):
           ymin_temp=-1.0
           ymax_temp=1.0
        #endif
       ax1.set_ylim(ymin_temp,ymax_temp)
       print("nvkdls ",ymin_temp,ymax_temp)
    #endif


   # For the xaxis, there are some plots where we don't want ticks and tick labels
   if sim_params.graphname != "unfccc_lulucf_bar":
      ax1.set_xlabel('Year', fontsize=14)
      ax1.xaxis.set_major_locator(MultipleLocator(5))
      ax1.xaxis.set_minor_locator(MultipleLocator(1))
      ax1.tick_params(axis='x', which='major', labelsize=14)
      ax1.tick_params(axis='x', which='minor', labelsize=14)
   else:
      ax1.tick_params(
         axis='x',          # changes apply to the x-axis
         which='both',      # both major and minor ticks are affected
         bottom=False,      # ticks along the bottom edge are off
         top=False,         # ticks along the top edge are off
         labelbottom=False) # labels along the bottom edge are off
   #endif

   ax1.set_xlim(sim_params.xplot_min,sim_params.xplot_max)
   ax1.tick_params(axis='y', which='major', labelsize=14)
   ax1.tick_params(axis='y', which='minor', labelsize=14)

   if sim_params.graphname in ("forestry_full","grassland_full","crops_full") and lplot_areas:
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
   if sim_params.graphname in ("inversions_combined","inversions_full", "inversions_test","inversions_combined","inversions_combinedbar"):
      # Need to wrap legend labels to make sure they don't spill over
      # into other columns.
      labels = [fill(l, 40) for l in legend_titles]
      ax2.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=2,fontsize='large')                     
   else:
      labels = [fill(l, 30) for l in legend_titles]
      ax2.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=3,fontsize='large')                     
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
      if sim_params.lshow_productiondata:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data (shown in lighter symbols). Bars indicating range are always lighter.', transform=newax.transAxes,fontsize=12,color='red')
      else:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data.  For illustration purposes only.', transform=newax.transAxes,fontsize=12,color='red')
      #endif
   #endif

   ax1.set_title(plot_titles[iplot],fontsize=16)

   if sim_params.lprintzero:
      ax1.hlines(y=0.0,xmin=sim_params.xplot_min,xmax=sim_params.xplot_max,color="black",linestyle='--',linewidth=0.1)
   #endif

   # in this case, we have average simulation data plotted at the last
   # year in the timeseries.  We want to make this stand out a bit, so
   # we add a little light shading and change the tick label.
   if sim_params.lplot_means and sim_params.graphname != "unfccc_lulucf_bar":
#      ymin_temp,ymax_temp=ax1.get_ylim()
      #p1=mpl.patches.Rectangle((sim_params.allyears[-1]-1.0,ymin_temp),2.0,ymax_temp-ymin_temp, color="linen",alpha=0.5,zorder=-1)
      #ax1.add_patch(p1)
      # Set the labels by hand, since they should always be the same
      locs=[1990.0, 1995.0, 2000.0, 2005.0, 2010.0, 2015.0, 2021.0]
#      labels=["1990", "1995", "2000", "2005", "2010", "2015", "Mean\n1990-last year\navailable"]
      labels=["1990", "1995", "2000", "2005", "2010", "2015", "Mean of\noverlapping\ntimeseries"]
      ax1.set_xticks(locs)
      ax1.set_xticklabels(labels)
      #ax1.xaxis.labelpad=-13 # Needed if we make the mean label multi-line, since
      ax1.xaxis.labelpad=-27 # Needed if we make the mean label multi-line, since
      # that pushes down the Year label too far from the axis

   #endif

   #plt.tight_layout(rect=[0, 0.05,1 , 1])
   fig.savefig(output_file_start+sim_params.desired_plots[iplot]+output_file_end,dpi=300)
   plt.close(fig)

   # What if we make a bar plot from these means?
   # Tried doing this above, but having two figures open caused issues.
   #if False:
   if sim_params.lplot_means and sim_params.graphname != "unfccc_lulucf_bar" and sim_params.lplot_meangraph:
      create_mean_plot(legend_titles,displayname,simulation_data,simulation_min,simulation_max,iplot,pa_string,kp_string,facec,zorder_value,uncert_color,simulation_mean,sim_params.lplot_countrytot,plot_titles,output_file_start,sim_params.desired_plots,output_file_end,sim_params.uncert_alpha,overlapping_years,exclude_simulation_means,desired_simulations)

   #endif

print("Finished script.")













