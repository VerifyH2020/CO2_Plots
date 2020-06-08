# CO2_Plots
Scripts to make CO2 plots, as well as scripts to process non-NetCDF files into NetCDF files in VERIFY format

Useage: python PLOT_CO2_results.py GRAPHNAME
    where GRAPHNAME can be inversions_full, or anything in the
    possible_graphnames list below
 
   You can control the countries/regions which are plotted by
   modifying the desired_plots list.
   
  possible_graphnames=("test", "luc_full", "sectorplot_full", "forestry_full", "grassland_full", "crops_full", "inversions_full", "inversions_test", "biofuels", "inversions_verify", "lulucf","lulucf_full", "inversions_combined", "inversions_combinedbar", "verifybu", "fluxcom", "lucf_full", "lulucf_trendy", "trendy", "unfccc_lulucf_bar", "all_orchidee", "gcp_inversions", "gcp_inversions_corrected", "eurocom_inversions", "eurocom_inversions_corrected", "epic", "lulucf_msnrt", "orc_trendy", "fao", "unfccc_fao", "unfccc_fao_trendy")
