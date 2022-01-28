####################################################################
# The purpose of this code is to create a couple China plots from a
# .csv file with the data.
#
# NOTE: Uses Python3
#
# Useage: python create_china_plots.py
#    where GRAPHNAME can be inversions_full, or anything in the

####################################################################
#!/usr/bin/env python

# These are downloadable or standard modules
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
from matplotlib import collections as mc
import matplotlib.gridspec as gridspec
import re
from itertools import compress
from textwrap import fill # legend text can be too long
import argparse

# I use Python 3 constructs.
if sys.version_info[0] < 3:
    raise Exception("You must use Python 3")
#endif

################ Some subroutines
def plot_bars(ax1,data_values,lowerrange,upperrange,years,color,legend_axes,legend_titles,legend_name,legend_err_name):
    for iyear in range(len(years)):
        if np.isnan(data_values[iyear]):
            continue
        #endif
        p1=mpl.patches.Rectangle((years[iyear]-0.5,lowerrange[iyear]),1,upperrange[iyear]-lowerrange[iyear], color=color, alpha=0.3,zorder=1)
        p2=ax1.hlines(y=data_values[iyear],xmin=years[iyear]-0.5,xmax=years[iyear]+0.5,color=color,linestyle='--',zorder=2)
        ax1.add_patch(p1)
    #endfor
    
    legend_axes.append(p2)
    legend_titles.append(legend_name)
    legend_axes.append(p1)
    legend_titles.append(legend_err_name)

    return ax1,legend_axes,legend_titles

#enddef

##
def plot_lines(ax1,data_values,years,color,legend_axes,legend_titles,legend_name,linestyle):

    p2, =ax1.plot(years,data_values,ls=linestyle,color=color)

    legend_axes.append(p2)
    legend_titles.append(legend_name)

    return ax1,legend_axes,legend_titles

#enddef

# This is based on Philippe Ciais's AR4 report.  Using a solid horizontal line
# with caps at each end that give the uncertainty.
def plot_bu_dataset(ax1,data_values,years,color,legend_axes,legend_titles,legend_name,min_values=None,max_values=None):

    

    # Now create the caps.  If a datavalue is next to a NaN, put a cap there
    # This is perhaps a silly way to check if an array has been passed
    if hasattr(min_values, "__len__"):
        
        lines=[]
        colors=[]
        sindex=0
        eindex=-1
        syear=years[sindex]
        eyear=years[eindex]

        for iyear in range(1,len(years)-1):
            if np.isnan(data_values[iyear]):
                continue
            #endif
            if np.isnan(data_values[iyear-1]) or np.isnan(data_values[iyear+1]):
                print("Putting a cap at ",iyear,legend_name,max_values[iyear],data_values[iyear],min_values[iyear])
                lines.append([(years[iyear]-0.25,max_values[iyear]),(years[iyear]+0.25,max_values[iyear])])
                colors.append(color)
                lines.append([(years[iyear]-0.25,min_values[iyear]),(years[iyear]+0.25,min_values[iyear])])
                colors.append(color)
                lines.append([(years[iyear],min_values[iyear]),(years[iyear],max_values[iyear])])
                colors.append(color)

                if np.isnan(data_values[iyear-1]):
                    syear=years[iyear]
                    sindex=iyear
                #endif
                if np.isnan(data_values[iyear+1]):
                    eyear=years[iyear]
                    eindex=iyear
                #endif

            #endif
        #endfor
        lines.append([(syear,data_values[sindex]),(eyear,data_values[eindex])])
        colors.append(color)
        #lines=[[(1990,0),(2016,0)],[(2016,-500),(2016,500)]]
        #c=["red","blue"]
        print(lines,colors)
        lc = mc.LineCollection(lines,colors=colors,linestyle="dashdot")
        p2=ax1.add_collection(lc)

    else:
        # Only lines, no caps
        p2, =ax1.plot(years,data_values,ls='dashdot',color=color)

    #endif

    legend_axes.append(p2)
    legend_titles.append(legend_name)

    return ax1,legend_axes,legend_titles

#enddef

##
def plot_points(ax1,data_values,years,color,legend_axes,legend_titles,legend_name,markerstyle,ms=None):

    if ms:
        p2, =ax1.plot(years,data_values,ls='',marker=markerstyle,markerfacecolor=color,markeredgecolor="black",markersize=ms)
    else:
        p2, =ax1.plot(years,data_values,ls='',marker=markerstyle,markerfacecolor=color,markeredgecolor="black")
    #endif

    legend_axes.append(p2)
    legend_titles.append(legend_name)

    return ax1,legend_axes,legend_titles

#enddef

##

def plot_inversions(df,legend_names):

    fig=plt.figure(2,figsize=(13, 8))
    canvas = FigureCanvas(fig)
    gs = gridspec.GridSpec(3, 1, height_ratios=[2.7,1,1])
    ax1=plt.subplot(gs[0])
    ax2 =plt.subplot(gs[2])

    legend_axes=[]
    legend_titles=[]

    # We have some special lines here
    kp_string="Kyoto Protocol (entering into force)"
    pa_string="Paris Agreement"
    p1=ax1.axvline(x=2005,color='peru', linestyle=':')
    legend_axes.append(p1)
    legend_titles.append(kp_string)
    p1=ax1.axvline(x=2015,color='k', linestyle=':')
    legend_axes.append(p1)
    legend_titles.append(pa_string)

    # What are the years?
    years=df.index.to_numpy()
    print(years)
    column_names=list(df.columns)
    print(column_names)

    # Plot the UNFCCC data
    timeseries=df.loc[:,"UNFCCC LULUCF NGHGI (2019) [Gg CO2 yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"gold",legend_axes,legend_titles,"UNFCCC LULUCF NGHGI (2019)",'o',ms=10)

    # Plot the FOASTAT data
    timeseries=df.loc[:,"FAOSTAT [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"darkviolet",legend_axes,legend_titles,"FAOSTAT",'P')

    # Plot the BLUE data
    timeseries=df.loc[:,"BLUE [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"tan",legend_axes,legend_titles,"BLUE",'^')
    
    # Plot the Trendy ensemble
    timeseries=df.loc[:,"Median of TRENDY v7 DGVMs [Tg C yr-1]"]
    timeseries_min=df.loc[:,"Median of TRENDY v7 DGVMs MIN VALUES [Tg C yr-1]"]
    timeseries_max=df.loc[:,"Median of TRENDY v7 DGVMs MAX VALUES [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bars(ax1,timeseries.values[:],timeseries_min.values[:],timeseries_max.values[:],years,"gray",legend_axes,legend_titles,"Median of TRENDY v7 DGVMs","Min/Max of TRENDY v7 DGVMs")

    # Plot the GCP inversions
    timeseries=df.loc[:,"Mean of GCP inversions [Tg C yr-1]"]
    timeseries_min=df.loc[:,"Mean of GCP inversions MIN VALUES [Tg C yr-1]"]
    timeseries_max=df.loc[:,"Mean of GCP inversions MAX VALUES [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bars(ax1,timeseries.values[:],timeseries_min.values[:],timeseries_max.values[:],years,"r",legend_axes,legend_titles,"Mean of GCP inversions","Min/Max of GCP inversions")

    # Plot the SR-1 inversions.  Plotting them as lines and not as bars,
    # since the uncertainty is different than what we plot in the bars.
    timeseries=df.loc[:,"SR-1 [Pg C yr-1]"]
    timeseries_min=df.loc[:,"SR-1 MIN VALUES [Pg C yr-1]"]
    timeseries_max=df.loc[:,"SR-1 MAX VALUES [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_lines(ax1,timeseries.values[:],years,"red",legend_axes,legend_titles,"Wang et al. (2020) SR-1 inversion",'solid')

    # Plot the SR-2 inversions
    timeseries=df.loc[:,"SR-2 [Pg C yr-1]"]
    timeseries_min=df.loc[:,"SR-2 MIN VALUES [Pg C yr-1]"]
    timeseries_max=df.loc[:,"SR-2 MAX VALUES [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_lines(ax1,timeseries.values[:],years,"red",legend_axes,legend_titles,"Wang et al. (2020) SR-2 inversion",'dashed')


    # Now a bunch of things changing the general appearence of the plot
    ax1.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)

    ax1.set_xlabel('Year', fontsize=14)
    ax1.xaxis.set_major_locator(MultipleLocator(5))
    ax1.xaxis.set_minor_locator(MultipleLocator(1))
    ax1.tick_params(axis='x', which='major', labelsize=14)
    ax1.tick_params(axis='x', which='minor', labelsize=14)

    ax1.set_xlim(1990,2021.5)
    ax1.tick_params(axis='y', which='major', labelsize=14)
    ax1.tick_params(axis='y', which='minor', labelsize=14)
    
    # Now copy the full ax1 legend to ax2, and turn off that from ax1, just
    # to make the spacing a little bit better.
    # Also change the number of columns in the legend in case we have a lot of text.
    # Need to wrap legend labels to make sure they don't spill over
    # into other columns.
    labels = [fill(l, 40) for l in legend_titles]
    ax2.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=2,fontsize='large')                     
    ax2.axis('off')

    cc='/home/orchidee03/cqiu/2Drun/inventories/inventories3/cc_by_gray.png'
    img=plt.imread(cc)
    newax = fig.add_axes([0.1, 0.0, 0.05, 0.05], anchor='NE', zorder=-1)
    newax.imshow(img)
    newax.axis('off')
    ax1.text(1.0,0.3, 'VERIFY Project', transform=newax.transAxes,fontsize=12,color='darkgray')

    ax1.set_title(r"China : CO$_2$ emissions from land use, land use change, and forestry",fontsize=16)
    
    ax1.hlines(y=0.0,xmin=1990,xmax=2021.5,color="black",linestyle='--',linewidth=0.1)
    
    fig.savefig("D6.2_China_inversions_v1.png",dpi=300)
    plt.close(fig)

#enddef

##

def plot_bu(df,legend_names):

    fig=plt.figure(2,figsize=(13, 8))
    canvas = FigureCanvas(fig)
    gs = gridspec.GridSpec(3, 1, height_ratios=[2.7,1,1])
    ax1=plt.subplot(gs[0])
    ax2 =plt.subplot(gs[2])

    legend_axes=[]
    legend_titles=[]

    # We have some special lines here
    kp_string="Kyoto Protocol (entering into force)"
    pa_string="Paris Agreement"
    p1=ax1.axvline(x=2005,color='peru', linestyle=':')
    legend_axes.append(p1)
    legend_titles.append(kp_string)
    p1=ax1.axvline(x=2015,color='k', linestyle=':')
    legend_axes.append(p1)
    legend_titles.append(pa_string)

    # What are the years?
    years=df.index.to_numpy()
    print(years)
    column_names=list(df.columns)
    print(column_names)

    # Plot the UNFCCC data
    timeseries=df.loc[:,"UNFCCC LULUCF NGHGI (2019) [Gg CO2 yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"gold",legend_axes,legend_titles,"UNFCCC LULUCF NGHGI (2019)",'o',ms=10)

    # Plot the FOASTAT data
    timeseries=df.loc[:,"FAOSTAT [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"darkviolet",legend_axes,legend_titles,"FAOSTAT",'P')

    # Plot the BLUE data
    timeseries=df.loc[:,"BLUE [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_points(ax1,timeseries.values[:],years,"tan",legend_axes,legend_titles,"BLUE",'^')
    
    # Plot the Trendy ensemble
    timeseries=df.loc[:,"Median of TRENDY v7 DGVMs [Tg C yr-1]"]
    timeseries_min=df.loc[:,"Median of TRENDY v7 DGVMs MIN VALUES [Tg C yr-1]"]
    timeseries_max=df.loc[:,"Median of TRENDY v7 DGVMs MAX VALUES [Tg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bars(ax1,timeseries.values[:],timeseries_min.values[:],timeseries_max.values[:],years,"gray",legend_axes,legend_titles,"Median of TRENDY v7 DGVMs","Min/Max of TRENDY v7 DGVMs")
    
    # Plot the BU data from Wang et al
    timeseries=df.loc[:,"BU Ref 16 [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bu_dataset(ax1,timeseries.values[:],years,"blue",legend_axes,legend_titles,"Tian et al. (2011)")

    timeseries=df.loc[:,"BU Ref 15 [Pg C yr-1]"]
    timeseries_min=df.loc[:,"BU Ref 15 MIN VALUES [Pg C yr-1]"]
    timeseries_max=df.loc[:,"BU Ref 15 MAX VALUES [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bu_dataset(ax1,timeseries.values[:],years,"red",legend_axes,legend_titles,"Piao et al. (2009)",max_values=timeseries_max.values[:],min_values=timeseries_min.values[:])

    timeseries=df.loc[:,"BU Ref 14 [Pg C yr-1]"]
    timeseries_min=df.loc[:,"BU Ref 14 MIN VALUES [Pg C yr-1]"]
    timeseries_max=df.loc[:,"BU Ref 14 MAX VALUES [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bu_dataset(ax1,timeseries.values[:],years,"orange",legend_axes,legend_titles,"Piao et al. (2012)",max_values=timeseries_max.values[:],min_values=timeseries_min.values[:])

    timeseries=df.loc[:,"BU Ref 18 [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bu_dataset(ax1,timeseries.values[:],years,"springgreen",legend_axes,legend_titles,"Wang et al. (2015)")

    timeseries=df.loc[:,"BU Ref 4 [Pg C yr-1]"]
    ax1,legend_axes,legend_titles=plot_bu_dataset(ax1,timeseries.values[:],years,"seagreen",legend_axes,legend_titles,"Jiang et al. (2016)")

    # Now a bunch of things changing the general appearence of the plot
    ax1.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)

    ax1.set_xlabel('Year', fontsize=14)
    ax1.xaxis.set_major_locator(MultipleLocator(5))
    ax1.xaxis.set_minor_locator(MultipleLocator(1))
    ax1.tick_params(axis='x', which='major', labelsize=14)
    ax1.tick_params(axis='x', which='minor', labelsize=14)

    ax1.set_xlim(1990,2021.5)
    ax1.tick_params(axis='y', which='major', labelsize=14)
    ax1.tick_params(axis='y', which='minor', labelsize=14)
    
    # Now copy the full ax1 legend to ax2, and turn off that from ax1, just
    # to make the spacing a little bit better.
    # Also change the number of columns in the legend in case we have a lot of text.
    # Need to wrap legend labels to make sure they don't spill over
    # into other columns.
    labels = [fill(l, 40) for l in legend_titles]
    ax2.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=2,fontsize='large')                     
    ax2.axis('off')

    cc='/home/orchidee03/cqiu/2Drun/inventories/inventories3/cc_by_gray.png'
    img=plt.imread(cc)
    newax = fig.add_axes([0.1, 0.0, 0.05, 0.05], anchor='NE', zorder=-1)
    newax.imshow(img)
    newax.axis('off')
    ax1.text(1.0,0.3, 'VERIFY Project', transform=newax.transAxes,fontsize=12,color='darkgray')

    ax1.set_title(r"China : bottom-up CO$_2$ emissions from land use, land use change, and forestry",fontsize=16)
    
    ax1.hlines(y=0.0,xmin=1990,xmax=2021.5,color="black",linestyle='--',linewidth=0.1)
    
    fig.savefig("D6.2_China_bottomup_v1.png",dpi=300)
    plt.close(fig)

#enddef


#################################

# Read in the data from a .csv where the columns are datasets (with units
# in [] at the end of the names) and the rows are years.  Something very
# similar is printed out for every graph with the PLOT_CO2_results.py script.
chinadf = pd.read_csv("all_china_data.csv", sep=',',decimal='.',index_col=0,header=0)

# Now go through all the datasets and convert to the desired units.
desired_units="Tg C yr-1"
legend_name={}
for (simname, simdata) in chinadf.iteritems():
    #print(simname)
    match = re.search(r"^(.+) \[(.+)\]$", simname)
    if match:
           
        # These define the origin date for counting
        #print("Units: ",match[2])
        #print("Legend name : ",match[1])
        legend_name[simname]=match[1]
        if match[2] != desired_units:
            print("Converting units for {}.".format(match[1]))

            if match[2] == 'Pg C yr-1':
                chinadf[simname]=chinadf[simname]*1000.0
            elif match[2] == 'Gg CO2 yr-1':
                chinadf[simname]=chinadf[simname]/1000.0/44.01*12.01
            else:
                print("don't know how to convert units: {}".format(match[2]))
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif

        #endif
    else:
        print("Why can I not find units in parse_units?")
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
#endfor

# Now we should have a dataframe with all the good units and all our
# datasets.  So let's plot.
plot_inversions(chinadf,legend_name)

plot_bu(chinadf,legend_name)
