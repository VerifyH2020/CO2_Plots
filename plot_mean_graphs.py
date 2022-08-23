####################################################################
# The purpose of this code is to take .csv files with data in them
# and create a bar plot showing the means of several simulations.
#
# Two possibilities exist:
#   1) V2019
#   2) V2021
#
# I have made it so that V2019 can be overlaid on V2021.
#
# NOTE: Uses Python3
#
####################################################################
#!/usr/bin/env python

# These are downloadable or standard modules
import sys,traceback
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib as mpl
from textwrap import fill # legend text can be too long
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import argparse

# These are my own that I have created locally
from mean_graphs_subroutines import get_simulation_parameters
from country_subroutines import get_country_region_data



# I use Python 3 constructs.
if sys.version_info[0] < 3:
    raise Exception("You must use Python 3")
#endif

###############################################
# Set up all the input parameters that control the simulation
parser = argparse.ArgumentParser(description='Create mean plots from .csv files made from data found on the VERIFY database.')

possible_versions=["V2019_orig","V2019_ext","V2021_orig",'V2021_ext']
parser.add_argument('--version', dest='version', action='store',required=True, choices=possible_versions, help='the type of graph that you wish to plot')
parser.add_argument('--overlay_version', dest='overlay_version', action='store',required=False, choices=possible_versions, help='if given, will overlay a simplied version of this plot on the other')
parser.add_argument('--lcolor', dest='lcolor', action='store', default='True',help='If False, then striping is used instead of color for the bars.')
possible_true_values=["true","t","yes","y"]
parser.add_argument('--country_code', dest='country_code', action='store',required=False, default='E28', help='the three letter ISO code of the country or region to create the graph for.  Looks for a file with this code in the name to pull the values from.')

args = parser.parse_args()
country_code=args.country_code
plot_version=args.version
if args.lcolor.lower() in possible_true_values:
    lcolor=True
else:
    lcolor=False
#endif
overlay_version=args.overlay_version
if overlay_version is None:
    loverlay=False
else:
    loverlay=True
#endtry
sim_params=get_simulation_parameters(plot_version,country_code)

# Here are some that we use frequently.
desired_simulation_names=sim_params.desired_simulations.keys()
###############################################


############################## Now do the plots
figmean=plt.figure(2,figsize=(13, 8))
gsmean = gridspec.GridSpec(2, 1, height_ratios=[9,1])
ax1mean=plt.subplot(gsmean[0])

# Need to figure out how many simulations we have, and then
# spread them evenly across the x axis.  
# This gets a little trickier if we are not plotting a simulation in
# every column.
nsims=len(desired_simulation_names)
xaxis_vector=np.asarray(range(max(sim_params.plotting_columns)+1))
barwidth=0.5
xlabels=[]
for ix in range(len(xaxis_vector)):
    xlabels.append("")
#endfor

for ititle,ctitle in enumerate(desired_simulation_names): 

    iposition=float(sim_params.desired_simulations[ctitle].plotting_column)

    # Shorten a few names
    yval=sim_params.desired_simulations[ctitle].value
    xval_min=iposition-barwidth/2.0
    xval_max=iposition+barwidth/2.0

    # Do we have error bars?
    if sim_params.desired_simulations[ctitle].lerror:
        meanmin=sim_params.desired_simulations[ctitle].min_value
        meanmax=sim_params.desired_simulations[ctitle].max_value
        if lcolor:
            p1=mpl.patches.Rectangle((xval_min,meanmin),barwidth,meanmax-meanmin, color=sim_params.desired_simulations[ctitle].color, alpha=0.5,zorder=1)
            p3=mpl.patches.Rectangle((xval_min,meanmin),barwidth,meanmax-meanmin, facecolor="none", edgecolor="black",alpha=1.0,lw=1.5,zorder=20)
            ax1mean.add_patch(p3)
        else:
            p1=mpl.patches.Rectangle((xval_min,meanmin),barwidth,meanmax-meanmin, facecolor="none",edgecolor="black",hatch=r"//", alpha=0.5,zorder=1)
        #endif
        ax1mean.add_patch(p1)
    #endif

    # Here is the mean value
    if lcolor:
        p2=ax1mean.hlines(y=yval,xmin=xval_min,xmax=xval_max,color="black",linestyle='--',zorder=2)
    else:
        p2=ax1mean.hlines(y=yval,xmin=xval_min,xmax=xval_max,color="black",linestyle=':',zorder=2)
    #endif

    xlabels[sim_params.desired_simulations[ctitle].plotting_column]=sim_params.desired_simulations[ctitle].displayname
         
    # If we are doing overlap, try removing all mentions of version numbers.
    if loverlay:
        xlabels[sim_params.desired_simulations[ctitle].plotting_column]=xlabels[sim_params.desired_simulations[ctitle].plotting_column].replace(" V2021","").replace("-V2021","").replace(" (2021)","").replace("EUROCOMv2","EUROCOM").replace(" v10","")
    #endif


#endfor

ax1mean.set_xticks(xaxis_vector)
    
# Two label styles.  One splitting the label across mutiple lines
if True:
    xlabels = [fill(l, 20) for l in xlabels]
    plt.xticks(rotation=45, ha='right')
else:
    # The other, a single line and rotated at 45 degrees
    plt.xticks(rotation=45, ha='right')
#endif
ax1mean.set_xticklabels(xlabels)
ax1mean.tick_params(axis='x', which='major', labelsize=10)
ax1mean.tick_params(axis='y', which='major', labelsize=14)

ax1mean.yaxis.set_minor_locator(AutoMinorLocator())
ax1mean.tick_params(which='minor', direction='in', length=3)
ax1mean.tick_params(which='major', direction='in', length=5)

# Now a bunch of things changing the general appearence of the plot
ax1mean.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)

if loverlay:
    cr_data=get_country_region_data()
    if plot_version in ["V2021_orig","V2021_ext"] and overlay_version in ["V2019_orig","V2019_ext"]:
        # With the use of six simulations in the GCP2021, this now only
        # goes from 2010 to 2018
        sim_params.title="Mean of overlapping timeseries - V2019 (2006-2015) and V2021 (2010-2018)\n{} : net land CO$_2$ fluxes".format(cr_data[country_code].long_name)
    else:
        print("*********************************")
        print("Not sure how to name this plot.")
        print(plot_version,overlay_version)
        print("*********************************")
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
#endif
ax1mean.set_title(sim_params.title,fontsize=16)

ax1mean.set_xlim(-1,len(xlabels))
ax1mean.hlines(y=0.0,xmin=-1,xmax=len(xlabels),color="black",linestyle='--',linewidth=0.1)

# Do we overlay?
if loverlay:
    sim_params_overlay=get_simulation_parameters(overlay_version,country_code)

    # Here are some that we use frequently.
    desired_simulation_names_overlay=sim_params_overlay.desired_simulations.keys()
    ###############################################


    # Need to figure out how many simulations we have, and then
    # spread them evenly across the x axis.  
    nsims_overlay=len(desired_simulation_names_overlay)
    xaxis_vector_overlay=np.asarray(range(nsims_overlay))
    xlabels_overlay=[]

    for ititle,ctitle in enumerate(desired_simulation_names_overlay): 
        
        iposition=float(sim_params_overlay.desired_simulations[ctitle].plotting_column)
        
        # Shorten a few names
        yval=sim_params_overlay.desired_simulations[ctitle].value
        xval_min=iposition-barwidth/2.0
        xval_max=iposition+barwidth/2.0

        # Do we have error bars?
        if sim_params_overlay.desired_simulations[ctitle].lerror:
            meanmin=sim_params_overlay.desired_simulations[ctitle].min_value
            meanmax=sim_params_overlay.desired_simulations[ctitle].max_value
            p1=mpl.patches.Rectangle((xval_min,meanmin),barwidth,meanmax-meanmin, facecolor="none",edgecolor="gray",lw=1.0,hatch=r"//", alpha=1.0,zorder=1)
            ax1mean.add_patch(p1)
        #endif

        # Here is the mean value
        p2=ax1mean.hlines(y=yval,xmin=xval_min,xmax=xval_max,color="gray",lw=1.0,linestyle='--',zorder=2,alpha=1.0)
    #endfor

#endif

ax1mean.text(0.02,0.05, 'sink', transform=ax1mean.transAxes,fontsize=14,color='darkgreen',weight='bold',alpha=0.6)
ax1mean.text(0.02,0.85, 'source', transform=ax1mean.transAxes,fontsize=14,color='firebrick',weight='bold',alpha=0.6)

#####
# Sometimes we need to fix the limits.
if sim_params.ymin is not None:
    ax1mean.set_ylim(sim_params.ymin,sim_params.ymax)
#endif
#####

#####
# This won't work for every graph, but i'm trying to show different groups of results.
# Give a little more space at the top
ymin,ymax=ax1mean.get_ylim()
ax1mean.set_ylim(ymin=ymin,ymax=ymax+0.1*(ymax-ymin))

# Put in a series of shaded gray bars to distinguish different groups.
ymin,ymax=ax1mean.get_ylim()
#bar_colors=["white","lightgray"]
for gray_bar in sim_params.gray_bars:
    xmin=gray_bar.xmin
    xmax=gray_bar.xmax
    if lcolor:
        bar_color=gray_bar.bar_color
    else:
        bar_color="white" # Will likely overlay this plot on another
    #endif
    bar_text=gray_bar.bar_text
    bar_text_xval=gray_bar.bar_text_xval
    p1=mpl.patches.Rectangle((xmin,ymin),xmax-xmin,ymax-ymin, color=bar_color, zorder=-100,alpha=0.3)
    ax1mean.add_patch(p1)
    ax1mean.text(bar_text_xval,0.98*(ymax-ymin)+ymin, bar_text, va='top', ha="center",fontsize=12,color='black')
#endfor

cc='/home/users/mmcgrath/CODE.OBELIX/PYTHON/VerifyH2020/cc_by_gray.png'
img=plt.imread(cc)
newax = figmean.add_axes([0.1, 0.0, 0.05, 0.05], anchor='NE', zorder=-1)
newax.imshow(img)
newax.axis('off')
    
ax1mean.text(1.0,0.3, 'VERIFY Project', transform=newax.transAxes,fontsize=12,color='darkgray')

if lcolor:
    ltransparent=False
else:
    ltransparent=True
#endif

# Change the output file if we overlay another graph
if loverlay:
    sim_params.output_file_name=sim_params.output_file_name.replace(".png","_overlay.png")
#endif
figmean.savefig(sim_params.output_file_name,dpi=300,transparent=ltransparent)


plt.close(figmean)

print("Finished script normally.")
