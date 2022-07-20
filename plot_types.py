import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sys,traceback
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.lines import Line2D
import re
import matplotlib.gridspec as gridspec
import matplotlib as mpl
from textwrap import fill # legend text can be too long
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from scikit_posthocs import outliers_grubbs as grubbs

# This is a plot which looks different from all the rest.  It's a series
# of stacked bar plots.
def create_unfccc_bar_plot(desired_simulations,simulation_data,iplot,naverages,syear_average,eyear_average,xplot_min,xplot_max,ndesiredyears,allyears,ax1,facec,production_alpha,legend_axes,legend_titles,displayname,canvas,output_file_end):

    # Need to make this more generalized to deal with 2021 as well
    # as 2019
    #### Total LULUCF
    possible_names=["UNFCCC2019_LULUCF","UNFCCC2020_LULUCF","UNFCCC2021_LULUCF"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding total LULUCF name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    total_lulucf_name=temp_names[0]
    #### forest remaining forests
    possible_names=["UNFCCC2019_FL-FL","UNFCCC2020_FL-FL","UNFCCC2021_FL-FL"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding forest remaining forest name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    fl_fl_name=temp_names[0]
    #### grassland remaining grassland
    possible_names=["UNFCCC2019_GL-GL","UNFCCC2020_GL-GL","UNFCCC2021_GL-GL"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding grassland remaining grassland name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    gl_gl_name=temp_names[0]
    #### cropland remaining cropland
    possible_names=["UNFCCC2019_CL-CL","UNFCCC2020_CL-CL","UNFCCC2021_CL-CL"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding cropland remaining cropland name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    cl_cl_name=temp_names[0]
    #### forest convert
    possible_names=["UNFCCC2019_forest_convert","UNFCCC2020_forest_convert","UNFCCC2021_forest_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding forest convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    fl_convert_name=temp_names[0]
    #### grassland convert
    possible_names=["UNFCCC2019_grassland_convert","UNFCCC2020_grassland_convert","UNFCCC2021_grassland_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding grassland convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    gl_convert_name=temp_names[0]
    #### cropland convert
    possible_names=["UNFCCC2019_cropland_convert","UNFCCC2020_cropland_convert","UNFCCC2021_cropland_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding cropland convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    cl_convert_name=temp_names[0]
    #### wetland convert
    possible_names=["UNFCCC2019_wetland_convert","UNFCCC2020_wetland_convert","UNFCCC2021_wetland_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding wetland convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    wl_convert_name=temp_names[0]
    #### settlement convert
    possible_names=["UNFCCC2019_settlement_convert","UNFCCC2020_settlement_convert","UNFCCC2021_settlement_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding settlement convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    sl_convert_name=temp_names[0]
    #### other convert
    possible_names=["UNFCCC2019_other_convert","UNFCCC2020_other_convert","UNFCCC2021_other_convert"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding other convert name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    ol_convert_name=temp_names[0]
    #### woodharvest
    possible_names=["UNFCCC2019_woodharvest","UNFCCC2020_woodharvest","UNFCCC2021_woodharvest"]
    temp_names=list(set(possible_names) & set(desired_simulations))
    if len(temp_names) != 1:
        print("Had problem finding woodharvest name!")
        print(desired_simulations)
        print(possible_names)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif
    hwp_name=temp_names[0]

    required_simulations=[ \
                           total_lulucf_name, \
                           fl_fl_name, \
                           gl_gl_name, \
                           cl_cl_name, \
                           fl_convert_name, \
                           gl_convert_name, \
                           cl_convert_name, \
                           wl_convert_name, \
                           sl_convert_name, \
                           ol_convert_name, \
                           hwp_name, \
    ]
    

    #####
    # A couple options for showing different versions.

    # If true, we will always have the value 0.0 in the plot.
    # If false, focus more on the transitions.
    # lshow_full_bars=False

    # A choice has to be made here: do I use the LULUCF totals, 
    # or the sum of the subsectors? 
    # luse_subsector_sums=True

    # If this is True, print out the LULUCF totals as a single gray bar. 
    # If false, print out all the subsector totals.
    #lplot_lulucf_tot_bars=True
    
    # Use a geometric color gradient.  This shows more color, less white/gray.
    #lgeom_gradient=True

    # Find out the version number of the plot.
    m=re.search(r'_[vV](\d+)\.png',output_file_end)
    if m:
        # The sector code we will extract from the .csv file
        version_number=m.group(1)
    else:
        print("Unable to find the version number of this plot!")
        print("Output file name: ",output_file_end)
        print("Looking for something like _v4.png")
        sys.exit(1)
    #endif

    # v2 = geometric gradient, focus on transitions, subsector sums, plot
    # subsector totals instead of gray LULUCF bar
    if version_number == "2":
        lshow_full_bars=False
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=False
        lgeom_gradient=True
    # v3 = linear gradient, focus on transitions, subsector sums, plot
    # subsector totals instead of gray LULUCF bar
    elif version_number == "3":
        lshow_full_bars=False
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=False
        lgeom_gradient=False
    # v4 = geometric gradient, show whole bar, subsector sums, plot
    # subsector totals instead of gray LULUCF bar
    elif version_number == "4":
        lshow_full_bars=True
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=False
        lgeom_gradient=True
    # v5 = linear gradient, show whole bar, subsector sums, plot
    # subsector totals instead of gray LULUCF bar
    elif version_number == "5":
        lshow_full_bars=False
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=False
        lgeom_gradient=False
    # v6 = geometric gradient, focus on transitions, subsector sums, plot
    # gray LULUCF bar
    elif version_number == "6":
        lshow_full_bars=False
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=True
        lgeom_gradient=True
    # v7 = linear gradient, focus on transitions, subsector sums, plot
    # gray LULUCF bar
    elif version_number == "7":
        lshow_full_bars=False
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=True
        lgeom_gradient=False
    # v8 = geometric gradient, show whole bar, subsector sums, plot
    # gray LULUCF bar
    elif version_number == "8":
        lshow_full_bars=True
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=True
        lgeom_gradient=True
    # v9 = linear gradient, show whole bar, subsector sums, plot
    # gray LULUCF bar
    elif version_number == "9":
        lshow_full_bars=True
        luse_subsector_sums=True
        lplot_lulucf_tot_bars=True
        lgeom_gradient=False
    else:
        print("Not sure how to handle this version number of this plot!")
        print("Output file name: ",output_file_end)
        print("Found version numbers: ",version_number)
        sys.exit(1)
    #endif

    # v6 = geometric gradient, focus on transtions, gray bar for LULUCF tot
    # v7 = linear gradient, focus on transtions, gray bar for LULUCF tot
    # v8 = geometric gradient, show whole bar, gray bar for LULUCF tot
    # v9 = linear gradient, show whole bar, gray bar for LULUCF tot

    #####

    # This stores some of the text objects, so I can use
    # them later to set the plot limits.  Note that I cannot
    # use the standard ax1.texts container, since I don't
    # want all of the objects taken into account, just some.
    text_objects=[]

    tot_index=desired_simulations.index(total_lulucf_name)

    # If we have no data, there is no reason to make this plot.
    test_vals=simulation_data[tot_index,:,iplot]
    check_vals=np.where(np.isnan(test_vals),True,False)
    if check_vals.all():
        print("No data for {}.  Skipping this country/region.".format(desired_simulations[tot_index]))
        #print(test_vals)
        #print(check_vals)
        return True,ax1
    #endif

    # It's not clear that UNFCCC_LULUCF will actually be the sum of all these
    # other categories.
    new_sum_vals=np.zeros((len(required_simulations),len(test_vals)))*np.nan
    for isim,csim in enumerate(required_simulations):
        if csim == total_lulucf_name:
            continue
        #endif

        
        temp_index=desired_simulations.index(csim)
        print("Subsectors: ",csim,temp_index,simulation_data[temp_index,:,iplot])
        new_sum_vals[isim,:]=simulation_data[temp_index,:,iplot]
    #endfor
    new_sum_vals=np.nansum(new_sum_vals,axis=0)
    # the above command leaves 0.0 where all elements were NaN.  That's not what I want.
    new_sum_vals=np.where(new_sum_vals == 0.0, np.nan, new_sum_vals)

    close_array=np.isclose(new_sum_vals,simulation_data[tot_index,:,iplot],rtol=0.0001)
    if not close_array.all():
        print("The LULUCF values are not close enough to the sum of all the subsectors!")
        print("LULUCF: ",simulation_data[tot_index,:,iplot])
        print("Subsectors: ",new_sum_vals)
        #for isim,csim in enumerate(desired_simulations):
        #    print("Diff: ",new_sum_vals-simulation_data[tot_index,:,iplot])
        #    print("{}: ".format(csim),simulation_data[isim,:,iplot])
        #endfor
    #endif

    # Do we have all NaNs in the new_sum_vals?  If so, cannot make this plot.
    testnans=np.isnan(new_sum_vals)
    if testnans.all():
        print("******************************")
        print("Have NaN values for subsectors!  Cannot make this plot.")
        for isim,csim in enumerate(required_simulations):
            temp_index=desired_simulations.index(csim)
            print("Subsectors: ",csim,temp_index,simulation_data[temp_index,:,iplot])
        #endfor
        print("******************************")
        return True,ax1
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
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
    barnames=[fl_fl_name, gl_gl_name, cl_cl_name, hwp_name,"LUC (+)", "LUC (+)"]
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

    if luse_subsector_sums:
        lulucf_total_values=new_sum_vals[data_mask].copy()
    else:
        lulucf_total_values=simulation_data[tot_index,data_mask,iplot].copy()
    #endif


    # The LULUCF values are the full values.  For the rest of the bars, though, I plot the difference
    # between the values.  So the other arrays are one shorter than this array.
    ndiffs=temp_data.shape[1]-1
    diff_array=np.zeros((temp_data.shape[0],ndiffs),dtype=float)
    lulucf_total_diffs=np.zeros((ndiffs),dtype=float)
    percent_diff_array=np.zeros((temp_data.shape[0],ndiffs),dtype=float)
    for iyear in range(ndiffs):
        diff_array[:,iyear]=temp_data[:,iyear+1]-temp_data[:,iyear]
        percent_diff_array[:,iyear]=diff_array[:,iyear]/abs(temp_data[:,iyear])*100
        lulucf_total_diffs[iyear]=lulucf_total_values[iyear+1]-lulucf_total_values[iyear]
    #endif

    # Check some information here:
    if True:
        for isim,csim in enumerate(required_simulations):
            print("Testing averages: ",isim,csim,temp_data[isim,:])
        #endfor
    #endif

    # This gets tricky for the net gain and net loss.  I need to loop over all the possible data at every point
    # to see if it's positive or negative, and then add it to the correct one.

    netsims=[fl_convert_name, \
                           gl_convert_name, \
                           cl_convert_name, \
                           wl_convert_name, \
                           sl_convert_name, \
                           ol_convert_name, \
             ]

    # I will do some odd manipulations and will have to rescale the plotting axes after.
    # So keep track of the min and max values.
    plotmin=np.nanmin(lulucf_total_values[:])
    plotmax=np.nanmax(lulucf_total_values[:])
    # Since we are doing bar plots, we need to make sure the bottom of the bar
    # is included in our viewing window.
    # If I remove this, I can zoom in on where things actually happen.
    #plotmax=max(plotmax,0.0)
    #plotmin=min(plotmin,0.0)

    #print("jiofez
    # I am going to try to create gradient bars to better show the direction of changes.
    # These are taking from https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/gradient_bar.html
    # I had to adapt it for my purposes.
    def gradient_image(ax, extent, cmap, direction=0.0, cmap_range=(0, 1)):
        #"""
        #Draw a gradient image based on a colormap.
        #
        #Parameters
        #----------
        #ax : Axes
        #    The axes to draw on.
        #extent
        #    The extent of the image as (xmin, xmax, ymin, ymax).
        #    By default, this is in Axes coordinates but may be
        #    changed using the *transform* kwarg.
        #direction : float
        #    The direction of the gradient. This is a number in
        #    range 0 (=vertical) to 1 (=horizontal).
        #cmap_range : float, float
        #    The fraction (cmin, cmax) of the colormap that should be
        #    used for the gradient, where the complete colormap is (0, 1).
        #**kwargs
        #    Other parameters are passed on to `.Axes.imshow()`.
        #    In particular useful is *cmap*.
        #"""

        #
        phi = direction * np.pi / 2
        v = np.array([np.cos(phi), np.sin(phi)])
        X = np.array([[v @ [1, 0], v @ [1, 1]],
                      [v @ [0, 0], v @ [0, 1]]])
        a, b = cmap_range
        X = a + (b - a) / X.max() * X
        im = ax.imshow(X, extent=extent, interpolation='bicubic',
                       vmin=0, vmax=1, cmap=cmap,aspect='auto')
        return im
    #enddef


    # notice I've changed this to just take a single value of x,y!
    def gradient_bar(ax, left, right, bottom, top, color_value, transition_color):

        # I want to create my own colormap that goes from the input color to white.
        N = 256
        vals = np.ones((N, 4))
        rgbvals=matplotlib.colors.to_rgba(color_value)
        grayvals=matplotlib.colors.to_rgba(transition_color)

        # I want the color to draw the eye in the direction the value is going.
        # For negative values, the color should be at the bottom.  For positive
        # values, the color should be at the top.
        # Notice that, since bottom and top are defined with the real value
        # of plot_value, there is nothing to do here!  The "top" value will be
        # below the "bottom" value in the case of a negative plot_value.

        # I want more color than gray/white, so use a geometric sequence.
        # Such a sequence cannot include 0.0, though.
        grayvals=np.where(np.asarray(grayvals) < 0.01,0.01,grayvals)
        rgbvals=np.where(np.asarray(rgbvals) < 0.01,0.01,rgbvals)

        if lgeom_gradient:
            vals[:, 0] = np.geomspace(grayvals[0], rgbvals[0], N)
            vals[:, 1] = np.geomspace(grayvals[1], rgbvals[1], N)
            vals[:, 2] = np.geomspace(grayvals[2], rgbvals[2], N)
        else:
            vals[:, 0] = np.linspace(grayvals[0], rgbvals[0], N)
            vals[:, 1] = np.linspace(grayvals[1], rgbvals[1], N)
            vals[:, 2] = np.linspace(grayvals[2], rgbvals[2], N)
        #endif

        newcmp = ListedColormap(vals)


        gradient_image(ax, (left, right, bottom, top), newcmp)

    #enddef

    if lplot_lulucf_tot_bars:
        lulucf_bars=ax1.bar(plotting_positions, lulucf_total_values[:], color=facec[desired_simulations.index(total_lulucf_name)],width=barwidth,alpha=production_alpha)
        #legend_axes.append(lulucf_bars)
        #legend_titles.append(displayname[tot_index])
    else:
        # The subsector totals can be either positive or negative.  So try something where I plot the negative values
        # on the left (taking up 1/2 of the column) and the positive values on the right (taking up the other 1/2).
        
        for iyear in range(len(plotting_positions)):

            xval=plotting_positions[iyear]

            # First, negative values
            yval=0.0
            for isim,simname in enumerate(required_simulations):
                if simname == total_lulucf_name:
                    continue
                #endif
                plot_value=temp_data[isim,iyear]

                color_value=facec[isim]
                if plot_value <= 0.0:
                    # Net loss
                    #print("vcxv loss ",netsims[jsim],xval,yval,plot_value)
                    #p1=ax1.bar(xval-barwidth/4.0, plot_value, bottom=yval,color=color_value,width=barwidth/2.0,alpha=production_alpha)
                    p1=gradient_bar(ax1,xval-barwidth/2.0, xval, yval, plot_value+yval, color_value, facec[desired_simulations.index(total_lulucf_name)])
                    #if displayname[isim] not in legend_titles:
                    #    legend_axes.append(p1)
                    #    legend_titles.append(displayname[isim])
                    #endif
                    yval=yval+plot_value
                    if yval > plotmax:
                        plotmax=yval
                    elif yval <= plotmin:
                        plotmin=yval
                    #endif
                #endif
            #endfor

            # now, positive values
            for isim,simname in enumerate(required_simulations):
                if simname == total_lulucf_name:
                    continue
                #endif
                plot_value=temp_data[isim,iyear]

                color_value=facec[isim]
                if plot_value > 0.0:
                    p1=gradient_bar(ax1,xval+barwidth/2.0, xval, yval, plot_value+yval, color_value, facec[desired_simulations.index(total_lulucf_name)])
                    #p1=ax1.bar(xval+barwidth/4.0, plot_value, bottom=yval,color=color_value,width=barwidth/2.0,alpha=production_alpha)
                    #if displayname[isim] not in legend_titles:
                    #    legend_axes.append(p1)
                    #    legend_titles.append(displayname[isim])
                    #endif
                    yval=yval+plot_value
                    if yval > plotmax:
                        plotmax=yval
                    elif yval <= plotmin:
                        plotmin=yval
                    #endif
                #endif
            #endfor

        #endfor

        print("Trying this!")
    #endif
    ###############

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
#            print("In bottom label! ",height,bottom_point,height+bottom_point)
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

        #endfor
    #enddef

    # For every interval, we need to make a new bar plot, since the values in the loss/gain
    # may change.
    for iyear in range(ndiffs):

        # First, how much total change did we have between the last period and this period?
        tot_change=lulucf_total_diffs[iyear]
        tot_percent_change=lulucf_total_diffs[iyear]/abs(lulucf_total_values[iyear+1])*100.0

        yval=lulucf_total_values[iyear]
        print("Starting value for ",iyear,yval)
        print(lulucf_total_diffs)
        print(lulucf_total_values)
         
        barnames_normal=[fl_fl_name, gl_gl_name, cl_cl_name,hwp_name]
        for ibar,cbar in enumerate(barnames_normal):
            xval=plotting_positions[iyear]+barwidth*(ibar+1)
            
            isim=desired_simulations.index(barnames[ibar])
            plot_value=diff_array[isim,iyear]
            color_value=facec[isim]

            # If the plot value is NaN for one of these bars, just give
            # it a value of 0.0 to show it doesn't contribute.
            #print("jifoez ",iyear,cbar,xval,barwidth,yval,plot_value)
            if np.isnan(plot_value):
                plot_value=0.0
            #endif
            p1=gradient_bar(ax1,xval-barwidth/2.0, xval+barwidth/2.0, yval, plot_value+yval, color_value, "white")
            p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=0.0)
            top_label(p1,diff_array[isim,iyear]/tot_change*tot_percent_change,text_objects)
            bottom_label(p1,displayname[isim],text_objects)
            #if displayname[isim] not in legend_titles:
            #    legend_axes.append(p1)
            #    legend_titles.append(displayname[isim])
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
                        #print("vcxv gain ",netsims[jsim],xval,yval,plot_value)
                        p1=gradient_bar(ax1,xval-barwidth/2.0, xval+barwidth/2.0, yval, plot_value+yval, color_value, "white")
                        #p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=production_alpha)
                        #if displayname[isim] not in legend_titles:
                        #    legend_axes.append(p1)
                        #    legend_titles.append(displayname[isim])
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
                        #print("vcxv loss ",netsims[jsim],xval,yval,plot_value)
                        p1=gradient_bar(ax1,xval-barwidth/2.0, xval+barwidth/2.0, yval, plot_value+yval, color_value, "white")
#                        p1=ax1.bar(xval, plot_value, bottom=yval,color=color_value,width=barwidth,alpha=production_alpha)
                        #if displayname[isim] not in legend_titles:
                        #    legend_axes.append(p1)
                        #    legend_titles.append(displayname[isim])
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
            #print("jfioezj ",final_height,overall_bar_bottom)
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

    # This is a short routine to put text inside of our bars
    # Note that we have to check to see if the bar is a source or a sink!
    # If it's a source (the value is positive), we attach the label close
    # to the top.  If a sink (the value is negative), we attach it to the
    # endif.
    def in_label(rects,text_objects):
        for idx,rect in enumerate(rects):
            height = rect.get_height()
            #print("Placing data at: ",rect.get_x() + rect.get_width()/2.,0.95*height,0.05*height)
            if height < 0.0:
                text_obj=ax1.text(rect.get_x() + rect.get_width()/2., 0.95*height,
                         "{:.2f}".format(height),fontsize=14,color='white',fontweight='bold',
                         ha='center', va='bottom', rotation=90)
            else:
                text_obj=ax1.text(rect.get_x() + rect.get_width()/2., 0.95*height,
                        "+{:.2f}".format(height),fontsize=14,color='white',fontweight='bold',
                         ha='center', va='top', rotation=90)
            #endif
            text_objects.append(text_obj)
        #endfor
        return text_objects
    #enddef

    # This prints the LULUCF total inside the gray bar.  Don't need
    # to do this if we are not printing those bars.
    if lplot_lulucf_tot_bars:
        text_objects=in_label(lulucf_bars,text_objects)
    #endif

    # Give us a little bit of space on the plot mins and maxes


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
#            print("jiofjez ",iobj)
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
#        print("jifoez ",plotmin,plotmax,plotdiff)

        if lshow_full_bars:
            if plotmax < 0.0:
                plotmax=0.0
            elif plotmin > 0.0:
                plotmin=0.0
            #endif
        #endif
        ax1.set_ylim(plotmin-0.05*abs(plotdiff),plotmax+0.05*abs(plotdiff))
        #print("nvvvvvvv ",iloop,plotdiff)
        iloop=iloop+1
        #loverlap=False
    #endwhile


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
        deltaval=lulucf_total_diffs[iyear]/abs(lulucf_total_values[iyear+1])*100.0
        if deltaval>0.:
            ax1.text(midpoint, text_place, '+'+str(np.around(deltaval,decimals=1))+'%', ha="center", va="center", fontsize=13,fontweight='bold')
        else:
            ax1.text(midpoint, text_place, str(np.around(deltaval,decimals=1))+'%', ha="center", va="center", fontsize=13,fontweight='bold')
        #endif
    #endfor

    # Create a custom legend.
    #custom_lines=[]
    for isim,csim in enumerate(required_simulations):
        color_value=facec[isim]
        legend_axes.append(matplotlib.patches.Patch(facecolor=color_value,fill=True))
        #legend_axes.append(Line2D([0], [0], color=color_value, lw=10))
        legend_titles.append(displayname[isim])
    #endif

    # This is for trying something really fancy.  I want to make a legend
    # rectangle where multiple colors appear, based on the LUC values
    # that are used above for + and -.  It doesn't work yet, so for the moment
    # I use a white box with a black outline for both LUC(+) and LUC(-).
    def legend_artist():
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch = mpatches.Rectangle([x0, y0], width, height, facecolor='red',
                                   edgecolor='black', hatch='xx', lw=3,
                                   transform=handlebox.get_transform())
        handlebox.add_artist(patch)
        return patch

    # Now add two special legends
    #legend_axes.append(legend_artist())
    legend_axes.append(matplotlib.patches.Patch(edgecolor="black",fill=False))
    legend_titles.append("LUC(-)")
    legend_axes.append(matplotlib.patches.Patch(edgecolor="black",fill=False))
    legend_titles.append("LUC(+)")

    return False,ax1
    

    # This is done at the end of the outside loop for all other files
#    fig.savefig(output_file_start+desired_plots[iplot]+output_file_end,dpi=300)
#    plt.close(fig)

#    return True

#enddef

############################################################
# This plot is a plot showing the mean values of each simulation
# It's done in addition to most plots
######### SHOULD NO LONGER BE USED.  I created a seperate script to work
######### from the .csv files.
def create_mean_plot(legend_titles,displayname,simulation_data,simulation_min,simulation_max,iplot,pa_string,kp_string,facec,zorder_value,uncert_color,simulation_mean,lplot_countrytot,plot_titles,output_file_start,desired_plots,output_file_end,uncert_alpha,overlapping_years,exclude_simulation_means,desired_simulations):

    figmean=plt.figure(2,figsize=(13, 8))
    gsmean = gridspec.GridSpec(2, 1, height_ratios=[9,1])
    ax1mean=plt.subplot(gsmean[0])
    #ax2mean =plt.subplot(gsmean[2])

    # Don't need these two items on our legend
    legend_titles_adjusted=[]
    for ilegend,clegend in enumerate(legend_titles):
        # Skip anything with area in it.
        m_area=re.search("area",clegend,re.IGNORECASE)
        m_uncert=re.search("uncertainty",clegend,re.IGNORECASE)
        m_minmax=re.search("Min/Max",clegend,re.IGNORECASE)
        if not m_area and not m_uncert and not m_minmax:
            if clegend not in [pa_string,kp_string]:
                legend_titles_adjusted.append(clegend)
                print("Adding legend: ",clegend)
            #endif
        #endif
    #endfor

    # We need this because we need to know where to make a division
    ##### Only way to do this seems to be to create a second run with the
    # order of plots that you want, instead of having a different order here
    # than is done in the main code
    #expected_simulations=[displayname.index['UNFCCC_LULUCF'],displayname.index['FAOSTAT_LULUCF'],displayname.index['EUROCOM_ALL'],displayname.index['GCP_ALL'],displayname.index['CSR-COMBINED'],displayname.index['TrendyV7'],displayname.index['ORCHIDEE-BU'],displayname.index['BLUE'],displayname.index['H&N']]
    



    # Need to figure out how many simulations we have, and then
    # spread them evenly across the x axis.  
    nsims=len(legend_titles_adjusted)
    xaxis_vector=np.asarray(range(nsims))
    barwidth=0.5
    #legend_axis=[]
    xlabels=[]
    iposition=0
    for ititle,ctitle in enumerate(legend_titles_adjusted): 

        isim=displayname.index(ctitle)

        # We exclude some simulations from the overlap period, like MS-NRT, which
        # only has a single year.
        if desired_simulations[isim] not in exclude_simulation_means:
            mean_years=overlapping_years[iplot]
        else:
            mean_years=np.asarray(simulation_data[isim,:,iplot])
            mean_years= np.invert(np.isnan(mean_years))
        #endif

        # Do we have an outlier?  Use Grubb's test
        loutliers=grubbs(simulation_data[isim,mean_years,iplot],hypo=True)
        if loutliers:
            print("Outliers!",ctitle,mean_years)
            print("Before outliers: ",simulation_data[isim,mean_years,iplot])
            print("After outliers: ",grubbs(simulation_data[isim,mean_years,iplot]))
            #loutliers=grubbs(simulation_data[isim,mean_years,iplot])
        #endif
            
        # Do we have error bars?
        if not np.isnan(simulation_min[isim,-1,iplot]) and not np.isnan(simulation_max[isim,-1,iplot]):
            #meanmin=np.nanmin(simulation_data[isim,mean_years,iplot])
            #meanmax=np.nanmax(simulation_data[isim,mean_years,iplot])
            #fullmin=np.nanmin(simulation_min[isim,mean_years,iplot])
            #fullmax=np.nanmax(simulation_max[isim,mean_years,iplot])
            meanmin=np.nanmean(simulation_min[isim,mean_years,iplot])
            meanmax=np.nanmean(simulation_max[isim,mean_years,iplot])
            #p1=mpl.patches.Rectangle((float(iposition)-barwidth/2.0,meanmin),barwidth,meanmax-meanmin, color=facec[isim], zorder=zorder_value)
            #ax1mean.add_patch(p1)
            p1=mpl.patches.Rectangle((float(iposition)-barwidth/2.0,meanmin),barwidth,meanmax-meanmin, color=uncert_color[isim], alpha=uncert_alpha,zorder=zorder_value-2)
            ax1mean.add_patch(p1)
            p2=ax1mean.hlines(y=simulation_mean[isim,iplot],xmin=float(iposition)-barwidth/2.0,xmax=float(iposition)+barwidth/2.0,color='black',linestyle='--',zorder=zorder_value+1)
            #            p1=ax1mean.bar(iposition, simulation_mean[isim,iplot], yerr=errordata, color=facec[isim],width=barwidth,label=displayname[isim],error_kw=dict(lw=2,capsize=15,capthick=1))

        else:
            #meanmin=np.nanmin(simulation_data[isim,mean_years,iplot])
            #meanmax=np.nanmax(simulation_data[isim,mean_years,iplot])
            dotted_mean_color="black"
            #if facec[isim] == "black":
            #    dotted_mean_color="white"
            #else:
            #    dotted_mean_color="black"
            #endif

            p2=ax1mean.hlines(y=simulation_mean[isim,iplot],xmin=float(iposition)-barwidth/2.0,xmax=float(iposition)+barwidth/2.0,color=dotted_mean_color,linestyle='--',zorder=zorder_value+1)
            #p1=mpl.patches.Rectangle((float(iposition)-barwidth/2.0,meanmin),barwidth,meanmax-meanmin, color=facec[isim], zorder=zorder_value)
            #ax1mean.add_patch(p1)
            #            p1=ax1mean.bar(iposition, simulation_mean[isim,iplot], color=facec[isim],width=barwidth,label=displayname[isim])
        #endif
        xlabels.append(displayname[isim])
        iposition=iposition+1
            
    #endfor

    #ax1mean.yaxis.grid(True)
    ax1mean.set_xticks(xaxis_vector)
    
    # Two label styles.  One horizontal, splitting the label across
    # mutiple lines
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
    if not lplot_countrytot:
        ax1mean.set_ylabel(r'g C yr$^{-1}$ m$^2$ of country)', fontsize=14)
    else:
        ax1mean.set_ylabel(r'Tg C yr$^{-1}$', fontsize=14)
    #endif

    #if graphname in ("inversions_combined","inversions_full", "inversions_test","inversions_combined","inversions_combinedbar"):
    # Need to wrap legend labels to make sure they don't spill over
    # into other columns.
    #   labels = [fill(l, 40) for l in legend_titles_adjusted]
    #   ax2mean.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=2,fontsize='large')                     
    #else:
    #   labels = [fill(l, 30) for l in legend_titles_adjusted]
    #   ax2mean.legend(legend_axes,labels,bbox_to_anchor=(0,0,1,1), loc="lower left",mode="expand", borderaxespad=0, ncol=3,fontsize='large')                     
    #endif
    #ax2mean.axis('off')
    ax1mean.set_title("Mean of overlapping timeseries (2006-2015)\n" + plot_titles[iplot],fontsize=16)
    ax1mean.set_xlim(-1,nsims)
    ax1mean.hlines(y=0.0,xmin=-1,xmax=nsims,color="black",linestyle='--',linewidth=0.1)
    
    ax1mean.text(0.02,0.05, 'sink', transform=ax1mean.transAxes,fontsize=14,color='darkgreen',weight='bold',alpha=0.6)
    ax1mean.text(0.02,0.85, 'source', transform=ax1mean.transAxes,fontsize=14,color='firebrick',weight='bold',alpha=0.6)

    #####
    # This won't work for every graph, but i'm trying to show different groups of results.
    # Give a little more space at the top
    ymin,ymax=ax1mean.get_ylim()
    ax1mean.set_ylim(ymin=ymin,ymax=ymax+0.1*(ymax-ymin))

    # This is for UNFCCC, FAO, GCP, EUROCOM, CSR, TRENDY, H&N, VERIFY_BU
    if False:
        ymin,ymax=ax1mean.get_ylim()
        p1=mpl.patches.Rectangle((1.5,ymin),3.0,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        p1=mpl.patches.Rectangle((6.5,ymin),2.5,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        ax1mean.text(0.5,0.98*(ymax-ymin)+ymin, 'Inventories', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(3.0,0.98*(ymax-ymin)+ymin, 'Top-down', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(5.5,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(DGVMs, bookkeeping)', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(7.3,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(combined)', va='top', ha="center",fontsize=12,color='black')

    # This is for UNFCCC, FAO, GCP, EUROCOM, CSR, TRENDY, ORCHIDEE, BLUE, H&N
    if True:
        ymin,ymax=ax1mean.get_ylim()
        p1=mpl.patches.Rectangle((1.5,ymin),3.0,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        p1=mpl.patches.Rectangle((6.5,ymin),2.5,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        ax1mean.text(0.5,0.98*(ymax-ymin)+ymin, 'Inventories', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(3.0,0.98*(ymax-ymin)+ymin, 'Top-down', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(5.5,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(DGVMs)', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(7.5,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(bookkeeping)', va='top', ha="center",fontsize=12,color='black')
        
    # This is for UNFCCC, FAO, GCP, EUROCOM, CSR, TRENDY, ORCHIDEE, EPIC, EFISCEN, BLUE, H&N
    if False:
        ymin,ymax=ax1mean.get_ylim()
        p1=mpl.patches.Rectangle((1.5,ymin),3.0,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        p1=mpl.patches.Rectangle((6.5,ymin),4.5,ymax-ymin, color="lightgray", zorder=-100,alpha=0.3)
        ax1mean.add_patch(p1)
        ax1mean.text(0.5,0.98*(ymax-ymin)+ymin, 'Inventories', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(3.0,0.98*(ymax-ymin)+ymin, 'Top-down', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(5.5,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(complete)', va='top', ha="center",fontsize=12,color='black')
        ax1mean.text(8.5,0.98*(ymax-ymin)+ymin, 'Bottom-up\n(partial)', va='top', ha="center",fontsize=12,color='black')

    #####

    cc='/home/orchidee03/cqiu/2Drun/inventories/inventories3/cc_by_gray.png'
    img=plt.imread(cc)
    newax = figmean.add_axes([0.1, 0.0, 0.05, 0.05], anchor='NE', zorder=-1)
    newax.imshow(img)
    newax.axis('off')
    
    ax1mean.text(1.0,0.3, 'VERIFY Project', transform=newax.transAxes,fontsize=12,color='darkgray')

    figmean.savefig("MeanBar" +output_file_start+desired_plots[iplot]+output_file_end,dpi=300)


    plt.close(figmean)
#enddef
