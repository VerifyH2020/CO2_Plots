import numpy as np


# This is a plot which looks different from all the rest.  It's a series
# of stacked bar plots.
def create_unfccc_bar_plot(desired_simulations,simulation_data,iplot,naverages,syear_average,eyear_average,xplot_min,xplot_max,ndesiredyears,allyears,ax1,facec,production_alpha,legend_axes,legend_titles,displayname,canvas):

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
        return True
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


#enddef
