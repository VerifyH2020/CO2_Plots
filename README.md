# CO2_Plots
Scripts to make CO2 plots, as well as scripts to process non-NetCDF files into NetCDF files in VERIFY format

Useage: python PLOT_CO2_results.py GRAPHNAME
    where GRAPHNAME can be inversions_full, or anything in the
    possible_graphnames list below
 
   You can control the countries/regions which are plotted by
   modifying the desired_plots list.
   
   possible_graphnames=("test", "full_global", "full_verify", "LUC_full", "sectorplot_full", "forestry_full", "grassland_full", "crops_full", "inversions_full", "inversions_test","biofuels","inversions_verify","lulucf")
