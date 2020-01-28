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
####################################################################
#!/usr/bin/env python
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
from plotting_subroutines import get_simulation_parameters,find_date,get_cumulated_array,readfile,group_input

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
lerrorbars=True

# Creates a horizontal line across the graph at zero.
lprintzero=False

# Make the Y-ranges on all the plots identical.
lharmonize_y=False

# This is a flag that will set a lot of the parameters, include which simulations we plot
possible_graphnames=("test", "full_global", "full_verify", "LUC_full", "sectorplot_full", "forestry_full", "grassland_full", "crops_full", "inversions_full", "inversions_test","biofuels","inversions_verify","lulucf")
try:
   graphname=sys.argv[1]
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

countries65=['ALA','ALB','AND', 'AUT',  'BEL',  'BGR',  'BIH',  'BLR',  'CHE',  'CYP',  'CZE', 'DEU', 'DNK','ESP','EST','FIN',  'FRA',  'FRO',  'GBR',  'GGY',  'GRC',  'HRV',  'HUN', 'IMN', 'IRL','ISL','ITA','JEY',  'LIE',  'LTU',  'LUX',  'LVA',  'MDA','MKD', 'MLT', 'MNE', 'NLD','NOR', 'POL',  'PRT',  'ROU',  'RUS',  'SJM',  'SMR',  'SRB',  'SVK', 'SVN', 'SWE', 'TUR','UKR','BNL', 'UKI',  'IBE',  'WEE',  'CEE',  'NOE',  'SOE',  'SEE', 'EAE', 'E15', 'E27','E28','EUR', 'EUT','KOS']

# This gives the full country name as a function of the ISO-3166 code
countrynames={ \
  "ALA": "Aaland Islands", \
  "ALB": "Albania", \
  "AND": "Andorra", \
  "AUT": "Austria", \
  "BEL": "Belgium", \
  "BGR": "Bulgaria", \
  "BIH": "Bosnia and Herzegovina", \
  "BLR": "Belarus", \
  "CHE": "Switzerland", \
  "CYP": "Cyprus", \
  "CZE": "Czech Republic", \
  "DEU": "Germany", \
  "DNK": "Denmark", \
  "ESP": "Spain", \
  "EST": "Estonia", \
  "FIN": "Finland", \
  "FRA": "France", \
  "FRO": "Faroe Islands", \
  "GBR": "United Kingdom", \
  "GGY": "Guernsey", \
  "GRC": "Greece", \
  "HRV": "Croatia", \
  "HUN": "Hungary", \
  "IMN": "Isle of Man", \
  "IRL" : "Ireland", \
  "ISL" : "Iceland", \
  "ITA" : "Italy", \
  "JEY" : "Jersey", \
  "LIE" : "Liechtenstein", \
  "LTU" : "Lithuania", \
  "LUX" : "Luxembourg", \
  "LVA" : "Latvia", \
  "MDA" : "Moldova, \ Republic of", \
  "MKD" : "Macedonia, \ the former Yugoslav", \
  "MLT" : "Malta", \
  "MNE" : "Montenegro", \
  "NLD" : "Netherlands", \
  "NOR" : "Norway", \
  "POL" : "Poland", \
  "PRT" : "Portugal", \
  "ROU" : "Romania", \
  "RUS" : "Russian Federation", \
  "SJM" : "Svalbard and Jan Mayen", \
  "SMR" : "San Marino", \
  "SRB" : "Serbia", \
  "SVK" : "Slovakia", \
  "SVN" : "Slovenia", \
  "SWE" : "Sweden", \
  "TUR" : "Turkey", \
  "UKR" : "Ukraine", \
  "BNL" : "BENELUX", \
  "UKI" : "United Kingdom + Ireland", \
  "IBE" : "Spain + Portugal", \
  "WEE" : "Western Europe", \
  "CEE" : "Central Europe", \
  "NOE" : "Northern Europe", \
  "SOE" : "Southern Europe", \
  "SEE" : "South-Eastern Europe", \
  "EAE" : "Eastern Europe", \
  "E15" : "EU-15", \
  "E27" : "EU-27", \
  "E28" : "EU-28", \
  "EUR" : "all Europe", \
  "EUT" : "Europe", \
  "EUT" : "Europe", \
  "EAE2" : "Eastern Europe (modified)", \
  "WEE2" : "Western Europe (modified)", \
  "IBE2" : "Testing Spain + Portugal", \
}

ALA=countries65.index('ALA');ALB=countries65.index('ALB');AND=countries65.index('AND'); AUT=countries65.index('AUT');BEL=countries65.index('BEL');BGR=countries65.index('BGR');BIH=countries65.index('BIH');BLR=countries65.index('BLR');CHE=countries65.index('CHE');CYP=countries65.index('CYP');CZE=countries65.index('CZE');DEU=countries65.index('DEU');DNK=countries65.index('DNK');ESP=countries65.index('ESP');EST=countries65.index('EST');FIN=countries65.index('FIN');FRA=countries65.index('FRA');FRO=countries65.index('FRO');GBR=countries65.index('GBR');GGY=countries65.index('GGY');GRC=countries65.index('GRC');HRV=countries65.index('HRV');HUN=countries65.index('HUN');IMN=countries65.index('IMN');IRL=countries65.index('IRL');ISL=countries65.index('ISL');ITA=countries65.index('ITA');JEY=countries65.index('JEY');LIE=countries65.index('LIE');LTU=countries65.index('LTU');LUX=countries65.index('LUX');LVA=countries65.index('LVA');MDA=countries65.index('MDA');MKD=countries65.index('MKD'); MLT=countries65.index('MLT'); MNE=countries65.index('MNE'); NLD=countries65.index('NLD');NOR=countries65.index('NOR'); POL=countries65.index('POL');PRT=countries65.index('PRT');ROU=countries65.index('ROU');RUS=countries65.index('RUS');SJM=countries65.index('SJM');SMR=countries65.index('SMR');SRB=countries65.index('SRB');SVK=countries65.index('SVK');SVN=countries65.index('SVN');SWE=countries65.index('SWE'); TUR=countries65.index('TUR');UKR=countries65.index('UKR');BNL=countries65.index('BNL'); UKI=countries65.index('UKI');IBE=countries65.index('IBE');WEE=countries65.index('WEE');CEE=countries65.index('CEE');NOE=countries65.index('NOE');SOE=countries65.index('SOE');SEE=countries65.index('SEE');EAE=countries65.index('EAE');E15=countries65.index('E15');E27=countries65.index('E27');E28=countries65.index('E28');EUR=countries65.index('EUR'); EUT=countries65.index('EUT');KOS=countries65.index('KOS')

# Only create plots for these countries/regions
desired_plots=['FRA','DEU','SWE','E28']
####
#desired_plots=countries65
#desired_plots.remove('KOS')
####

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


##########################################################################


####################################################################
############################# This is the start of the program
####################################################################

numplot=len(desired_plots)

desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,datasource,output_file_start,output_file_end,titleending,printfakewarning=get_simulation_parameters(graphname,lshow_productiondata)


# This is a generic code to read in all the simulations.  We may do different things based on the
# simulation name or type later on.


numsims=len(desired_simulations)

# Now that we have all the information above, populate the list of data that
# we will actually try to use.
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
#endfor


# Now read in the data into one large array.  Based on the simulation
# type, we may have to modify how we process the data.
simulation_data=np.zeros((numsims,ndesiredyears,numplot))*np.nan
# Some of the files, like the inventories, have an error that we can read in
simulation_err=np.zeros((numsims,ndesiredyears,numplot))*np.nan

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
      inv_fCO2=readfile(fname,variables[isim],ndesiredyears)  #monthly
      # This reads in the associated error.  It assumes that the file
      # has another variable of the same name, with _ERR added.
      inv_fCO2_err=readfile(fname,variables[isim] + "_ERR",ndesiredyears)  #monthly
      annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly
      annfCO2_err=np.nanmean(inv_fCO2_err,axis=1)   #convert from monthly to yearly
      
      simulation_data[isim,:,:],simulation_err[isim,:,:]=group_input(annfCO2,annfCO2_err,desired_plots,True,ndesiredyears,numplot,countries65)
      #simulation_err[isim,:,:]=group_input(annfCO2_err,desired_plots)
   elif simtype[isim] in ("TRENDY","VERIFY_BU","NONVERIFY_BU","INVENTORY_NOERR","VERIFY_TD","GLOBAL_TD","REGIONAL_TD"):
      inv_fCO2=readfile(fname,variables[isim],ndesiredyears)  #monthly
      annfCO2=np.nanmean(inv_fCO2,axis=1)   #convert from monthly to yearly

      # Some minor corrections have to be made to some of the files
      # The fluxes for ORCHIDEE seemed inverted with regards to the TRENDY
      # sign convention.  Flip that for the chart.
      if desired_simulations[isim] in ("ORCHIDEE","ORCHIDEE_for","ORCHIDEE_grass","ORCHIDEE_crops", "CBM"):
         print("Flipping the sign of the ORCHIDEE VERIFY and CBM fluxes.")
         annfCO2=-annfCO2
      elif desired_simulations[isim] == "EUROCOM_Lumia":
         # One year in this inversion seems messed up.
         print("Correcting erroneously high values for Lumia fluxes.")
         annfCO2[annfCO2>1e30]=np.nan
      #endif

      simulation_data[isim,:,:],simulation_err[isim,:,:]=group_input(annfCO2,annfCO2,desired_plots,False,ndesiredyears,numplot,countries65)
   else:
      print("Do not know how to process data for simulation type: {0}".format(simtype[isim]))
      sys.exit()
   #endif


#endfor

# If something is equal to zero, I don't plot it.
simulation_data[simulation_data == 0.0]=np.nan

# Check to see if we have inventory data.  If so, we do something different in plotting.
ninv=simtype.count("INVENTORY")
if ninv > 0:
   linventories=True
   print("We have some inventories in this dataset.")
else:
   linventories=False
   print("We do not have inventories in this dataset.")
#endif

# We need to compute some properties of the TRENDY simulations for use later, since
# we don't plot each TRENDY run, just the range.
# Of course, none of it matters if we aren't actually using TRENDY runs,
# so check that as well.
ntrendy=simtype.count("TRENDY")
print("Number of TRENDY runs included: {0}".format(ntrendy))
if ntrendy > 0:
   trendy_data=np.zeros((ntrendy,ndesiredyears,numplot))*np.nan
   ltrendy=True
else:
   ltrendy=False
#endif

# We do the same thing with global inversions, if we have any
nglobalinv=simtype.count("GLOBAL_TD")
print("Number of global inversions included: {0}".format(nglobalinv))
if nglobalinv > 0:
   globalinv_data=np.zeros((nglobalinv,ndesiredyears,numplot))*np.nan
   lglobalinv=True
else:
   lglobalinv=False
#endif

# And with regional (VERIFY) inversions, if we have any
nverifyinv=simtype.count("VERIFY_TD")
print("Number of VERIFY inversions included: {0}".format(nverifyinv))
if nverifyinv > 0:
   verifyinv_data=np.zeros((nverifyinv,ndesiredyears,numplot))*np.nan
   lverifyinv=True
else:
   lverifyinv=False
#endif

# And with regional (REGIONAL) inversions, if we have any
nregionalinv=simtype.count("REGIONAL_TD")
print("Number of EUROCOM inversions included: {0}".format(nregionalinv))
if nregionalinv > 0:
   regionalinv_data=np.zeros((nregionalinv,ndesiredyears,numplot))*np.nan
   lregionalinv=True
else:
   lregionalinv=False
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
iverifyinv=0
for isim,simname in enumerate(desired_simulations):  
   if simtype[isim] == "VERIFY_TD":
      verifyinv_data[iverifyinv,:,:]=simulation_data[isim,:,:]
      iverifyinv=iverifyinv+1
   #endif
#endif
if lverifyinv:
   verifyinvmean=np.nanmean(verifyinv_data,axis=0)
   verifyinvmax=np.nanmax(verifyinv_data,axis=0)
   verifyinvmin=np.nanmin(verifyinv_data,axis=0)
#endif


itrendy=0
iglobalinv=0
iregionalinv=0
for isim,simname in enumerate(desired_simulations):  
   if simtype[isim] == "TRENDY":
      trendy_data[itrendy,:,:]=simulation_data[isim,:,:]
      itrendy=itrendy+1
   elif simtype[isim] == "GLOBAL_TD":
      globalinv_data[iglobalinv,:,:]=simulation_data[isim,:,:]
      iglobalinv=iglobalinv+1
   elif simtype[isim] == "REGIONAL_TD":
      # In the case of EUROCOM CSR, we substitute the mean from the
      # VERIFY simulations, since Christoph has said he prefers the
      # VERIFY simulations.
      if simname == 'EUROCOM_Carboscope' and lverifyinv:
         # I don't want to add any points past the end of 2015, which is how far the 
         # EUROCOM results go.
         for iyear in range(ndesiredyears):
            if allyears[iyear] <= 2015:
               regionalinv_data[iregionalinv,iyear,:]=verifyinvmean[iyear,:]
            #endif
         #endfor
      else:
         regionalinv_data[iregionalinv,:,:]=simulation_data[isim,:,:]
      #endif
      iregionalinv=iregionalinv+1
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
# like correction_simulations=("ULB_Inland_waters"), Python thinks
# that it is a character array and loops over every letter.  Not what
# we want.

if graphname in ('inversions_full','inversions_test'):
   correction_simulations=np.array(["ULB_Inland_waters"],dtype=object)
   correction_data=np.zeros((ndesiredyears,numplot))
   for isim,simname in enumerate(desired_simulations):  
      if simname in correction_simulations:
         correction_data[:,:]=correction_data[:,:]+simulation_data[isim,:,:]
      #endif
   #endfor
   for iregionalinv in range(nregionalinv):
      regionalinv_data[iregionalinv,:,:]=regionalinv_data[iregionalinv,:,:]-correction_data[:,:]
   #endfor
   for iglobalinv in range(nglobalinv):
      globalinv_data[iglobalinv,:,:]=globalinv_data[iglobalinv,:,:]-correction_data[:,:]
   #endfor
   for iverifyinv in range(nverifyinv):
      verifyinv_data[iverifyinv,:,:]=verifyinv_data[iverifyinv,:,:]-correction_data[:,:]
   #endfor
#endif

# note that I take the median for TRENDY but the mean for the rest.  The others
# only have 3-4 simulations, which is not really enough for a median.
if ltrendy:
   trendymedian=np.nanmedian(trendy_data,axis=0)
   trendymax=np.nanmax(trendy_data,axis=0)
   trendymin=np.nanmin(trendy_data,axis=0)
#endif
if lglobalinv:
   globalinvmean=np.nanmean(globalinv_data,axis=0)
   globalinvmax=np.nanmax(globalinv_data,axis=0)
   globalinvmin=np.nanmin(globalinv_data,axis=0)
#endif
if lregionalinv:
   regionalinvmean=np.nanmean(regionalinv_data,axis=0)
   regionalinvmax=np.nanmax(regionalinv_data,axis=0)
   regionalinvmin=np.nanmin(regionalinv_data,axis=0)
#endif
if lverifyinv:
   verifyinvmean=np.nanmean(verifyinv_data,axis=0)
   verifyinvmax=np.nanmax(verifyinv_data,axis=0)
   verifyinvmin=np.nanmin(verifyinv_data,axis=0)
   printindices=np.where(allyears == 2006)
#endif

# In the case of the UNFCCC LUC, this is a sum of six different timeseries.
# Those are all in different files, so I combine them here, propogate the
# error, and then only print out this in the actual plot.
if graphname == 'LUC_full':
   temp_desired_sims=('UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert')
   iluc=desired_simulations.index("UNFCCC_LUC")
   if iluc < 0:
      print("******************************************************************")
      print("For the graph {0}, you need to be sure to include the simulation UNFCCC_LUC!".format(graphname))
      print("******************************************************************")
      sys.exit()
   #endif
   simulation_data[iluc,:,:]=0.0
   simulation_err[iluc,:,:]=0.0
   for isim,csim in enumerate(temp_desired_sims):
      simulation_data[iluc,:,:]=simulation_data[iluc,:,:]+simulation_data[desired_simulations.index(csim),:,:]
      # Do a simple propogation of error, as well
      simulation_err[iluc,:,:]=simulation_err[iluc,:,:]+(simulation_err[desired_simulations.index(csim),:,:]*simulation_data[desired_simulations.index(csim),:,:])**2
   #endfor

   # don't like doing this in a loop, but the sqrt function doesn't seem to work on arrays?
   for iplot in range(len(simulation_err[0,0,:])):
      for itime in range(len(simulation_err[0,:,0])):
         simulation_err[iluc,itime,iplot]=math.sqrt(simulation_err[iluc,itime,iplot])/simulation_data[iluc,itime,iplot]
         #endif
      #endfor
   #endfor
   
   # make any zero elements nan so they don't plot.  Hopefully this doesn't lead to undesired
   # results.
   for iplot in range(len(simulation_err[0,0,:])):
      for itime in range(len(simulation_err[0,:,0])):
         if simulation_data[iluc,itime,iplot] == 0.0:
            simulation_data[iluc,itime,iplot]= np.nan
         #endif
      #endfor
   #endfor
#endif

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


######## Sometimes people want raw data.  I will
# print all raw data for all the plots to this file.
datafile=open("plotting_data.txt","w")

for iplot,cplot in enumerate(desired_plots):

   print("**** On plot {0} ****".format(plot_titles_master[cplot]))
   datafile.write("**** On plot {0} ****\n".format(plot_titles_master[cplot]))

   # In an effort to harmonize the spacing a bit, I create a three-panel
   # grid, and then put only the legend in the bottom panel.

   fig=plt.figure(2,figsize=(13, 8))
   gs = gridspec.GridSpec(3, 1, height_ratios=[4,1,1])
   ax1=plt.subplot(gs[0])
   ax2 =plt.subplot(gs[2])

   # Try to combine all my different legends in one
   legend_axes=[]
   legend_titles=[]

   # This is to plot the inventories
   if linventories:

      if graphname == "sectorplot_full":

         temp_desired_sims=("UNFCCC_for","UNFCCC_grass","UNFCCC_crops")
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

         if graphname in ("inversions_full", "inversions_test") and desired_simulations[isim] in correction_simulations:
            continue
         #endif 

         if graphname == 'LUC_full' and desired_simulations[isim] in ('UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert'):
            continue
         #endif

         if simtype[isim] == "INVENTORY" and graphname != "sectorplot_full":
            datafile.write("**** On dataset {0} ****\n".format(desired_simulations[isim]))

            upperrange=simulation_data[isim,:,iplot]+simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
            lowerrange=simulation_data[isim,:,iplot]-simulation_data[isim,:,iplot]*simulation_err[isim,:,iplot]
            datafile.write("years {}\n".format(allyears[:]))
            datafile.write("data {}\n".format(simulation_data[isim,:,iplot]))
            datafile.write("upperbounds {}\n".format(upperrange[:]))
            datafile.write("lowerbounds {}\n".format(lowerrange[:]))
            for iyear in range(ndesiredyears):
               p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=uncert_color[isim], alpha=0.30)
               ax1.add_patch(p1)
               ax1.fill_between(np.array([allyears[iyear]-0.5,allyears[iyear]+0.5]),lowerrange[iyear],upperrange[iyear],color=uncert_color[isim],alpha=0.30)
            #endfor

            legend_axes.append(p1)
            legend_titles.append(displayname[isim] + " uncertainty")

            # I want to make sure the symbol shows up on top of the error bars.
            # If this is not real data, make it lighter.
            for iyear in range(ndesiredyears):
               if productiondata[isim]:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=production_alpha)
               else:
                  p1=ax1.hlines(y=simulation_data[isim,iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color=facec[isim],linestyle='-',alpha=nonproduction_alpha)
               #endif
            #endif

            legend_axes.append(p1)
            legend_titles.append(displayname[isim])
            datafile.write("\n")

         #endif
      #endfor
   #endif

   # This is to plot TRENDY, if present
   if ltrendy:
      upperrange=trendymax[:,iplot]
      lowerrange=trendymin[:,iplot]
      for iyear in range(ndesiredyears):
         p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="lightgray", alpha=0.30)
         ax1.add_patch(p1)
         ax1.fill_between(np.array([allyears[iyear]-0.5,allyears[iyear]+0.5]),lowerrange[iyear],upperrange[iyear],color="lightgray",alpha=0.60)
      #endfor
      legend_axes.append(p1)
      legend_titles.append("Spread of TRENDY_v7")
 
      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      p1=ax1.scatter(allyears,trendymedian[:,iplot],marker="_",label="TRENDY_v7",facecolors="None", edgecolors="lightgray",s=60)

   #endif

# This is to plot global inversions together, if present
   if lglobalinv:
      upperrange=globalinvmax[:,iplot]
      lowerrange=globalinvmin[:,iplot]
      for iyear in range(ndesiredyears):
         p2=ax1.hlines(y=globalinvmean[iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='gray',linestyle='--')
         p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="gray", alpha=0.20)
         ax1.add_patch(p1)
      #endfor
      legend_axes.append(p2)
      legend_titles.append("Mean of GCP (removing lakes/rivers)")
      legend_axes.append(p1)
      legend_titles.append("Min/Max of GCP")
      
      # Write raw data to a file
      datafile.write("**** On dataset Mean of GCP ****\n")
      datafile.write("years {}\n".format(allyears[:]))
      datafile.write("data {}\n".format(globalinvmean[:,iplot]))
      datafile.write("upperbounds {}\n".format(upperrange[:]))
      datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,globalinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

# and the regional (VERIFY) inversions, if they are present
   if lverifyinv and graphname != "inversions_verify":
      upperrange=verifyinvmax[:,iplot]
      lowerrange=verifyinvmin[:,iplot]
      if not lerrorbars: # This is for rectangles, like the other inversions
         for iyear in range(ndesiredyears):
            p2=ax1.hlines(y=verifyinvmean[iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='red',linestyle='--')
            p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="red", alpha=0.20)
            ax1.add_patch(p1)
         #endfor
         legend_axes.append(p2)
         legend_titles.append("Mean of CarboScopeReg (removing lakes/rivers)")
         legend_axes.append(p1)
         legend_titles.append("Min/Max of CarboScopeReg")
      else:
         # This is for a symbol with error bars
         # Notice error bars must always be positive
         errorbars=np.array((verifyinvmean[:,iplot]-lowerrange[:],upperrange[:]-verifyinvmean[:,iplot])).reshape(2,ndesiredyears)
         p2=ax1.errorbar(allyears,verifyinvmean[:,iplot],yerr=errorbars,marker='s',mfc='red',mec='black',ms=10,capsize=10,capthick=2,ecolor="black",linestyle='None')
         legend_axes.append(p2)
         legend_titles.append("Mean of CarboScopeReg (removing lakes/rivers)")

      #endif
      
      # Write raw data to a file
      datafile.write("**** On dataset Mean of CarboScopeReg (removing lakes/rivers) ****\n")
      datafile.write("years {}\n".format(allyears[:]))
      datafile.write("data {}\n".format(verifyinvmean[:,iplot]))
      datafile.write("upperbounds {}\n".format(upperrange[:]))
      datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,verifyinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

# and the regional (NON-VERIFY) inversions, if they are present
   if lregionalinv:
      upperrange=regionalinvmax[:,iplot]
      lowerrange=regionalinvmin[:,iplot]
      for iyear in range(ndesiredyears):
         p2=ax1.hlines(y=regionalinvmean[iyear,iplot],xmin=allyears[iyear]-0.5,xmax=allyears[iyear]+0.5,color='blue',linestyle='--')
         p1=mpl.patches.Rectangle((allyears[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color="blue", alpha=0.20)
         ax1.add_patch(p1)
      #endfor
      legend_axes.append(p2)
      legend_titles.append("Mean of EUROCOM (removing lakes/rivers)")
      legend_axes.append(p1)
      legend_titles.append("Min/Max of EUROCOM")
 
      # Write raw data to a file
      datafile.write("**** On dataset Mean of EUROCOM (removing lakes/rivers) ****\n")
      datafile.write("years {}\n".format(allyears[:]))
      datafile.write("data {}\n".format(regionalinvmean[:,iplot]))
      datafile.write("upperbounds {}\n".format(upperrange[:]))
      datafile.write("lowerbounds {}\n".format(lowerrange[:]))

      # I want to make sure the symbol shows up on top of the error bars.  Just used a simple thick horizontal bar in the same color as above.
      #p1=ax1.scatter(allyears,regionalinvmean[:,iplot],marker="_",label="EUROCOM",facecolors="None", edgecolors="red",s=60)

   #endif

   # This is to plot all the other simulations not covered by the special cases above
   for isim,simname in enumerate(desired_simulations):  
      if simtype[isim] in ("NONVERIFY_BU","INVENTORY_NOERR","VERIFY_BU") or desired_simulations[isim] == 'TrendyV7_ORCHIDEE' or graphname == "inversions_verify":

         # I do something differently for one of the plots
         if graphname == "sectorplot_full" and desired_simulations[isim] in ("EPIC","ECOSSE_grass","EFISCEN"):
            continue
         #endif
         if graphname in ("inversions_full", "inversions_test") and desired_simulations[isim] in correction_simulations:
            continue
         #endif      



         # I use lighter symbols if the data is not real, i.e. I created a false dataset just to have something to plot
         if productiondata[isim]:
            p1=ax1.scatter(allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=production_alpha)
         else:
            p1=ax1.scatter(allyears,simulation_data[isim,:,iplot],marker=plotmarker[isim],label=desired_simulations[isim],facecolors=facec[isim], edgecolors=edgec[isim],s=markersize[isim],alpha=nonproduction_alpha)
         #endif
         legend_axes.append(p1)
         legend_titles.append(displayname[isim])

      #endif
   #endif

   # For this particular graph, I plot three of the VERIFY runs in a different way.
   if graphname == "sectorplot_full":

      temp_desired_sims=("EPIC","ECOSSE_grass","EFISCEN")
      temp_data=np.zeros((len(temp_desired_sims),ndesiredyears))
      for isim,csim in enumerate(temp_desired_sims):
         temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
      #endfor

      # plot the whole sum of these three runs
      p1=ax1.scatter(allyears,np.nansum(temp_data,axis=0),marker="P",label="EPIC/ECOSSE/EFISCEN",facecolors="blue", edgecolors="blue",s=60,alpha=nonproduction_alpha)
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

      # I want to rearrange the order of the legends
      # This only works if I already have all of these
      desired_legend_order=(\
                           "UNFCCC_for","UNFCCC_grass","UNFCCC_crops",\
                           "Spread of TRENDY_v7",\
                            "EFISCEN","ECOSSE_grass","EPIC",\
                            "EPIC/ECOSSE/EFISCEN","ORCHIDEE","FLUXCOM-rsmeteo",\
                         )
      # run a quick check
      for isim,csim in enumerate(desired_legend_order):
         try:
            legend_titles.index(csim) 
         except:
            print("{0} does not appear to be present in the simulations we have treated.".format(csim))
            print("Please change desired_legend_order for graph {0}".format(graphname))
            print(desired_legend_order)
            print(legend_titles)       
            sys.exit()
         #endtry
      #endfor

      # I cannot use a simple equals here, because the axes are references.  Using the equals copies the reference,
      # so when the one of the references is modified, we lose the original value.  Thankfully, "copy" copies the
      # actual object.
      legend_axes_backup=copy.copy(legend_axes)
      for isim,csim in enumerate(desired_legend_order):
         legend_axes[isim]=copy.copy(legend_axes_backup[legend_titles.index(csim)])
      #endif
      legend_titles=desired_legend_order

   #endif

   # I want to try stacking some bars in the inversion plot
   if graphname in ("inversions_full", "inversions_test"):

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


   # I want to rearrange the order of the legends
      # This only works if I already have all of these
      if lerrorbars:
         desired_legend_order=(\
                               "Mean of EUROCOM (removing lakes/rivers)","Min/Max of EUROCOM",\
                               "Mean of CarboScopeReg (removing lakes/rivers)",\
                               "Mean of GCP (removing lakes/rivers)","Min/Max of GCP",\
                               "UNFCCC_LULUCF","UNFCCC_LULUCF uncertainty",\
                               "ULB_Inland_waters",\
                            )
      else:
         desired_legend_order=(\
                               "Mean of EUROCOM (removing lakes/rivers)","Min/Max of EUROCOM",\
                               "Mean of CarboScopeReg (removing lakes/rivers)","Min/Max of CarboScopeReg",\
                               "Mean of GCP (removing lakes/rivers)","Min/Max of GCP",\
                               "UNFCCC_LULUCF","UNFCCC_LULUCF uncertainty",\
                               "ULB_Inland_waters",\
                            )
      #endif

      # run a quick check
      for isim,csim in enumerate(desired_legend_order):
         try:
            legend_titles.index(csim) 
         except:
            print("{0} does not appear to be present in the simulations we have treated.".format(csim))
            print("Please change desired_legend_order for graph {0}".format(graphname))
            print(desired_legend_order)
            print(legend_titles)
            sys.exit()
         #endtry
      #endfor

      # I cannot use a simple equals here, because the axes are references.  Using the equals copies the reference,
      # so when the one of the references is modified, we lose the original value.  Thankfully, "copy" copies the
      # actual object.
      legend_axes_backup=copy.copy(legend_axes)
      for isim,csim in enumerate(desired_legend_order):
         legend_axes[isim]=copy.copy(legend_axes_backup[legend_titles.index(csim)])
      #endif
      legend_titles=desired_legend_order

      axsub.set_ylabel('Correction for inversions\n[Tg C/yr]')
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

   # Sometimes we want the y-axis for every plot to be identical
   if lharmonize_y:
      ax1.set_ylim(ymin,ymax)
   #endif

   # We have some special lines here, which indicate the start of IPCC accounting periods, I believe?
   ax1.axvline(x=2005,color='peru', linestyle=':')
   ax1.axvline(x=2015,color='k', linestyle=':')

   # Now a bunch of things changing the general appearence of the plot
   ax1.set_ylabel('Tg C/yr', fontsize=14)
   ax1.set_xlabel('Year', fontsize=14)
   ax1.set_xlim(1989.5,2023)
   ax1.xaxis.set_major_locator(MultipleLocator(5))
   ax1.xaxis.set_minor_locator(MultipleLocator(1))
   ax1.tick_params(axis='both', which='major', labelsize=14)
   ax1.tick_params(axis='both', which='minor', labelsize=14)

#   ax1.legend(legend_axes,legend_titles,bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",mode="expand", borderaxespad=0, ncol=3,fontsize='large')

   # Now copy the full ax1 legend to ax2, and turn off that from ax1, just
   # to make the spacing a little bit better.
   # Also change the number of columns in the legend in case we have a lot of text.
   if graphname in ("inversions_full", "inversions_test"):
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
   ax1.text(1.0,0.3, 'VERIFY Data: '+datasource, transform=newax.transAxes,fontsize=12,color='darkgray')

   if printfakewarning:
      if lshow_productiondata:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data (shown in lighter symbols). Bars indicating range are always lighter.', transform=newax.transAxes,fontsize=12,color='red')
      else:
         ax1.text(1.0,1.0, 'WARNING: Graph contains fake data.  For illustration purposes only.', transform=newax.transAxes,fontsize=12,color='red')
      #endif
   #endif

   ax1.set_title(plot_titles[iplot],fontsize=16)

   if lprintzero:
      ax1.hlines(y=0.0,xmin=allyears[0]-0.5,xmax=allyears[-1]+0.5,color="black",linestyle='-')
   #endif

   #plt.tight_layout(rect=[0, 0.05,1 , 1])
   fig.savefig(output_file_start+desired_plots[iplot]+output_file_end,dpi=300)
   plt.close(fig)















