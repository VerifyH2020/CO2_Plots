####################################################################
# These routines set up the input structure of our code, reading in
# arguments from the command line, creating the input parameter structure
# to hold all the variables related to the graphs that we are making.
#
####################################################################

# These are downloadable or standard modules
import argparse
import numpy as np
import matplotlib as mpl

# These are my own that I have created locally
from country_subroutines import get_countries_and_regions_from_cr_dict,get_country_region_data,get_country_codes_for_netCDF_file

##################################################################
# This is the primary output of these routines: a class that holds
# all the information that we need.  This is roughly grouped into
# different categories: command-line arguments, plotting countries,
# datasets used, plotting parameters 
#
# Command-line arguments are processed with the initialization.
#
##################################################################

class dataset_parameters():
    def __init__(self, simname,full_filename,simtype,variable,plotmarker,facec,displayname=None,flipdatasign=None):
        self.full_filename=full_filename
        # find the directory and filename from this
        #self.filedirectory=filedirectory
        #self.filename=filename
        
        self.simname=simname
        self.simtype=simtype
        self.variable=variable
        self.plotmarker=plotmarker
        self.facec=facec

        # now a few that are set automatically
        
        # The color around the edge of the symbol.
        self.edgec="black"
        # Allows for different colors for the error bars.
        self.uncert_color=facec
        # Controls the size of the plotting symbol
        self.markersize=60
        # If False, the symbols will be shown lighter (indicating the data
        # has been made up).
        self.productiondata=True
        # This indicates the text displayed in the plot legend.
        if displayname:
            self.displayname=displayname
        else:
            self.displayname=simname
        #endif
        # This indicates if the dataset will be displayed on the plot.  Sometimes we read in datasets
        # that we combine in various ways and we don't want the individual datasets shown.
        self.displaylegend=True
        # If true, the dataset will be multiplied by -1 on loading.  This is used to
        # make sources and sinks always follow the same sign convention.
        if flipdatasign:
            self.flipdatasign=flipdatasign
        else:
            self.flipdatasign=False
        #endif

        # If true, this dataset will be adjusted by the "correction" datasets
        # defined elsewhere.
        self.lcorrect_inversion=False
        # If True, this dataset will be plotted with error bars
        self.lplot_errorbar=False
        # This is a flag which, if True, plots whisker error bars.  If False,
        # plots rectangles for the error bars.
        self.lwhiskerbars=False

    #enddef
#endclass

class simulation_parameters():
    def __init__(self, parser):

        self.possible_graphs=["test", "luc_full", "sectorplot_full", "forestry_full", "grassland_full", "crops_full", "inversions_full", "inversions_test","biofuels","inversions_verify","lulucf","lulucf_full","inversions_combined","inversions_combinedbar","verifybu","verifybu_detrend","fluxcom","lucf_full","lulucf_trendy","trendy","unfccc_lulucf_bar","all_orchidee","gcp_inversions","gcp_inversions_corrected","eurocom_inversions","eurocom_inversions_corrected","epic","lulucf_msnrt","orc_trendy","fao","unfccc_fao","unfccc_fao_trendy","emission_factors","unfccc_woodharvest"]
        self.possible_true_values=["true","t","yes","y"]

        parser.add_argument('--graphname', dest='graphname', action='store',required=True, choices=self.possible_graphs, help='the type of graph that you wish to plot')
        
        parser.add_argument('--plot_all_countries', dest='plot_all_countries', action='store',default="False",help='if TRUE, we will create plots for every country and region that we can.  Otherwise, we only plot for what is hard-coded.')

        parser.add_argument('--plot_meangraph', dest='lplot_meangraph', action='store',default=False,help='if TRUE, we will create additional plots of the timeseries means for every country and region that we can.  The filename is the same, except preceded by MeanBar.')


        args = parser.parse_args()

        print("######################### INPUT VALUES #########################")
        self.graphname=args.graphname
        print("**************************************************************")
        print("Creating graph: " + self.graphname)
        print("**************************************************************")
        
        self.plot_all_countries=args.plot_all_countries
        if self.plot_all_countries.lower() in self.possible_true_values:
            self.plot_all_countries=True
        else:
            self.plot_all_countries=False
        #endif
            
        if self.plot_all_countries:
            print("Creating plots for ALL countries and regions.")
        else:
            print("Only creating plots for a hard-coded set of countries and regions.")
        #endif

        self.lplot_meangraph=args.lplot_meangraph
        if self.lplot_meangraph:
            print("Creating additional plots for graph means.")
        else:
            print("Not creating additional plots for graph means.")
        #endif

        print("######################### END INPUT VALUES #####################")

        ##########################################################################
        # Here are some variables that are used throughout the code, not yet put into
        # command line arguments.
        ##########################################################################
        self.define_global_parameters()


        ##########################################################################
        # Here are some parameters related to the countries that we are plotting
        # for.
        ##########################################################################
        self.define_country_parameters()


    #enddef

    def define_global_parameters(self):

        # This controls the alpha value (transparency) for real and invented data.
        self.production_alpha=1.0
        self.nonproduction_alpha=0.2
        # If this is True, the symbols on the plots are made lighter if we 
        # are using non-production data.  This demonstrates the work left to be
        # done in terms of data processing, but sometimes we don't want to do this
        # as then we can't see the final plot aesthetic.
        self.lshow_productiondata=True

        # This controls the transparency of the uncertainty error bars on some plots
        self.uncert_alpha=0.3
        
        # This adds the timeseries means to the plot if True.  For the moment, it
        # calculates the means and stores them in the last place in the timeseries
        # array, crashing with an error if there is already a value here (we assume
        # that you plot, for example, up to the year 2020 but only have data until
        # year 2018, in order to have a nice whitespace on the right side of the
        # plot).
        self.lplot_means=True

        # Print some additional data about one of the timeseries.  For debugging
        # purposes.
        self.ltest_data=False
        self.itest_sim=0
        self.itest_plot=0
        
        # Creates a horizontal line across the graph at zero.
        self.lprintzero=True
        
        # Make the Y-ranges on all the plots identical, selecting the ranges based
        # on the data.
        self.lharmonize_y=False
        
        # Make the Y-ranges on all the plots identical, imposing a range.
        self.lexternal_y=False
        self.ymin_external=-500.0
        self.ymax_external=500.0
        if self.lexternal_y:
            self.lharmonize_y=True
        #endif
            
        # Plot spatial fluxes or country totals? If the following variable is
        # false, we will divide all fluxes by the area of the country/region before
        # plotting, to give the flux per pixel.
        self.lplot_countrytot=True

        # This saves time by creating fake data, and helps debug the plots.  But, it is very specific and must
        # be changed for the plot you are doing!
        # If you want to create fake data, do a run with real data, and then copy all of the .csv files for
        # the plot you want to "fake_data.csv","fake_data_min.csv","fake_data_max.csv","fake_data_err.csv"
        self.luse_fake_data=False

        # How many years do we extract from the data, or fill in with NaN if it's not found?
        if True:
            # Standard plot
            self.ndesiredyears=32 # use a couple extra years for padding on the right hand side
            self.allyears=1990+np.arange(self.ndesiredyears)  ###1990-2022,ndesiredyears years. 
        else:
            # Sometimes we want something a bit different.  This works fine for
            # plotting the Trendy models, but might crash elsewhere where dates are
            # still hardcoded.
            self.ndesiredyears=14 # use a couple extra years for padding on the right hand side
            self.allyears=2008+np.arange(self.ndesiredyears)  ###1990-2022,ndesiredyears years. 

        #endif

        print("Extracting data from {} to {}.".format(self.allyears[0],self.allyears[-1]))

        # These are the year limits that are plotted.  The UNFCCC inventory data goes from 1990-2017.
        if True:
            # For next years of the project, we may have data up until 2021.
            # so I generally do 1989.5-2021.5.  2022.5 to give extra space for
            # the timeseries averages.
            self.xplot_min=1989.5
            self.xplot_max=2022.5
        else:
            self.xplot_min=allyears[0]-0.5
            self.xplot_max=allyears[-1]+0.5
        #endif


    #enddef

    def define_country_parameters(self):

        self.all_regions_countries=get_country_codes_for_netCDF_file()
        
        # This gives the full country name as a function of the ISO-3166 code
        country_region_data=get_country_region_data()
        self.countrynames=get_countries_and_regions_from_cr_dict(country_region_data)
        
        # Only create plots for these countries/regions
        if not self.plot_all_countries:
            self.desired_plots=['E28','FRA','DEU']
            #self.desired_plots=['E28','GBR','DNK','NLD','DEU','IRL']
            #   self.desired_plots=['E28','NLD','DEU']
            #   self.desired_plots=['DEU','FRA','WEE', 'EAE', 'E28']
            #   self.desired_plots=['DEU', 'E28']
            #self.desired_plots=['BGR','DEU','FRA','WEE', 'EAE', 'E28']
            #self.desired_plots=['GGY','FRA','WEE', 'EAE', 'E28']
            #self.desired_plots=['GRL','FRA','WEE', 'EAE', 'E28']
            # These are the regions we use in the synthesis paper
            #self.desired_plots=['E28','CEE','EAE','NOE','SOZ','WEE']
            
        else:
            self.desired_plots=self.all_regions_countries
        #endif
        #self.desired_plots.remove('KOS')


        # What if I want a new region?  In theory, if I can build the dataseries
        # before I get to the general plotting routines, they should treat
        # it like just another region.  So, let's try to set everything
        # up for a new region here.  The code now handles everything in 
        # in group_input.
        #self.desired_plots=['EAE2','WEE2']
        # This is a test case that should produce indentical results
        #self.desired_plots=['IBE','IBE2']



        # This is something which controls the title printed on the plot, related
        # to the country/group.  As a default, take the country/group name.
        self.plot_titles_master={}
        for cname in self.countrynames.keys():
            self.plot_titles_master[cname]=self.countrynames[cname]
        #endfor
        self.plot_titles_master["CSK"]="Former Czechoslovakia"
        self.plot_titles_master["CHL"]="Switzerland + Liechtenstein"
        self.plot_titles_master["BLT"]="Baltic countries"
        self.plot_titles_master["NAC"]="North Adriatic Countries"
        self.plot_titles_master["DSF"]="Denmark, Sweden, Finland"
        self.plot_titles_master["FMA"]="France, Monaco, Andorra"
        self.plot_titles_master["UMB"]="Ukraine, Rep. of Moldova, Belarus"
        self.plot_titles_master["SEA"]="South-Eastern Europe alternate"
        self.plot_titles_master["E28"]="EU27+UK"


    #enddef

    ##########################################################################
    def refine_plot_parameters(self):

        # Here are some dictionaries the define parameters for each simulation.
        # These may be varied below for each individual plot, but this is a first try.

        self.titleending="NO TITLE ENDING CHOSEN"
   
        # Turn this to True if you want to print a disclaimer on the plots about fake data being used.
        # Should be used in combination with lines like the following:
        #if lshow_productiondata:
        #   productiondata_master['ORCHIDEE-MICT']=False
        #endif
        # which will make the data print lighter.
        self.printfakewarning=False
        # Roxana proposes using this for all plots
        self.datasource='VERIFY Project'
        
        # Standard plotting format: divide it into three panels with
        # a 2.7:1:1 ratio, put the figure in the top panel and the
        # legend in the bottom.
        self.npanels=3
        self.panel_ratios=[2.7,1,1]
        self.igrid_plot=0
        self.igrid_legend=2
        
        # Do not apply Normalization to Zero Mean and Unit of Energy (Z-normalization)
        # to every timeseries 
        self.ldetrend=False
        
        self.overwrite_simulations={}
        self.overwrite_coeffs={}
        self.overwrite_operations={}
        self.desired_legend=[]
        
        master_datasets={}

        master_datasets["UNFCCC_totincLULUCF"]=dataset_parameters( "UNFCCC_totincLULUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_TotEmisIncLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "black")
        master_datasets["UNFCCC_totexcLULUCF"]=dataset_parameters( "UNFCCC_totexcLULUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_TotEmisExcLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "red")
        master_datasets["UNFCCC_LULUCF"]=dataset_parameters( "UNFCCC_LULUCF", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "green",displayname="UNFCCC LULUCF NGHGI (2019)")
        master_datasets["TrendyV7"]=dataset_parameters( "TrendyV7", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_AllTrendyMedianMinMax-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTotWithOutEEZ.nc", "MINMAX", "FCO2_NBP", "D", "grey")
        master_datasets["TrendyV7_CABLE"]=dataset_parameters( "TrendyV7_CABLE", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "red")
        master_datasets["TrendyV7_CLASS"]=dataset_parameters( "TrendyV7_CLASS", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CLASS-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "green")
        master_datasets["TrendyV7_CLM5"]=dataset_parameters( "TrendyV7_CLM5", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "blue")
        master_datasets["TrendyV7_DLEM"]=dataset_parameters( "TrendyV7_DLEM", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "violet")
        master_datasets["TrendyV7_ISAM"]=dataset_parameters( "TrendyV7_ISAM", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "yellow")
        master_datasets["TrendyV7_JSBACH"]=dataset_parameters( "TrendyV7_JSBACH", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "orange")
        master_datasets["TrendyV7_JULES"]=dataset_parameters( "TrendyV7_JULES", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_JULES-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "brown")
        master_datasets["TrendyV7_LPJ"]=dataset_parameters( "TrendyV7_LPJ", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_LPJ-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "gold")
        master_datasets["TrendyV7_LPX"]=dataset_parameters( "TrendyV7_LPX", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_LPX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "gray")
        master_datasets["TrendyV7_OCN"]=dataset_parameters( "TrendyV7_OCN", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "limegreen")
        master_datasets["TrendyV7_ORCHIDEE-CNP"]=dataset_parameters( "TrendyV7_ORCHIDEE-CNP", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ORCHIDEE-CNP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "yellowgreen")
        master_datasets["TrendyV7_ORCHIDEE"]=dataset_parameters( "TrendyV7_ORCHIDEE", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "none")
        master_datasets["TrendyV7_SDGVM"]=dataset_parameters( "TrendyV7_SDGVM", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "magenta")
        master_datasets["TrendyV7_SURFEX"]=dataset_parameters( "TrendyV7_SURFEX", "/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_SURFEX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc", "TRENDY", "FCO2_NBP", "D", "pink")
        master_datasets["ORCHIDEE_S0"]=dataset_parameters( "ORCHIDEE_S0", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S0_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "magenta", flipdatasign=True)
        master_datasets["ORCHIDEE_S1"]=dataset_parameters( "ORCHIDEE_S1", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S1_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=True)
        master_datasets["ORCHIDEE_S2"]=dataset_parameters( "ORCHIDEE_S2", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S2_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "red", flipdatasign=True)
        master_datasets["ORCHIDEE"]=dataset_parameters( "ORCHIDEE", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "dodgerblue", flipdatasign=True)
        master_datasets["ORCHIDEE_RH"]=dataset_parameters( "ORCHIDEE_RH", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "rh", "D", "red")
        master_datasets["EPIC"]=dataset_parameters( "EPIC", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithEEZ.nc", "VERIFY_BU", "FCO2_NBP_CRO", "o", "lightcoral", flipdatasign=True)
        master_datasets["EPIC_RH"]=dataset_parameters( "EPIC_RH", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_RH_CRO", "o", "pink")
        master_datasets["EPIC_fHarvest"]=dataset_parameters( "EPIC_fHarvest", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_FHARVEST_CRO", "^", "red")
        master_datasets["EPIC_clch"]=dataset_parameters( "EPIC_clch", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_CLCH_CRO", "P", "blue")
        master_datasets["EPIC_npp"]=dataset_parameters( "EPIC_npp", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NPP_CRO", "s", "green")
        master_datasets["CSR-COMBINED"]=dataset_parameters( "CSR-COMBINED", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_AllJENA_bgc-jena_LAND_GL_1M_V1_20200304_McGrath_WP3_CountryTotWithEEZ.nc", "MINMAX", "FCO2_NBP", "s", "mediumblue")
        master_datasets["CSR-REG-100km"]=dataset_parameters( "CSR-REG-100km", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "khaki")
        master_datasets["CSR-REG-200km"]=dataset_parameters( "CSR-REG-200km", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-200km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "orange")
        master_datasets["CSR-REG-Core100km"]=dataset_parameters( "CSR-REG-Core100km", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-Core100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "darkorange")
        master_datasets["CSR-REG-Valid100km"]=dataset_parameters( "CSR-REG-Valid100km", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-Valid100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "gold")
        master_datasets["BLUE"]=dataset_parameters( "BLUE", "/home/dods/verify/OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "CD_A", "^", "tan")
        master_datasets["H&N"]=dataset_parameters( "H&N", "/home/dods/verify/OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NBP", "^", "orange")
        master_datasets["ORCHIDEE-MICT"]=dataset_parameters( "ORCHIDEE-MICT", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_LandUseChange_ORCHIDEEMICT-SX_LSCE_LAND_EU_1M_V1_20190925_YUE_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "lightsteelblue", flipdatasign=True)
        master_datasets["FAOSTAT_For"]=dataset_parameters( "FAOSTAT_For", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_LUTOT_FOR", "o", "darkviolet")
        master_datasets["FAOSTAT_Crp"]=dataset_parameters( "FAOSTAT_Crp", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_SOIL_CRO", "P", "darkviolet")
        master_datasets["FAOSTAT_Grs"]=dataset_parameters( "FAOSTAT_Grs", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_SOIL_GRA", "X", "darkviolet")
        master_datasets["EUROCOM_Carboscope"]=dataset_parameters( "EUROCOM_Carboscope", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CarboScopeRegional_bgc-jena_LAND_EU_1M_V1_20191020_Gerbig_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "khaki")
        master_datasets["EUROCOM_Flexinvert"]=dataset_parameters( "EUROCOM_Flexinvert", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_FLEXINVERT_nilu_LAND_EU_1M_V1_20191020_Thompson_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "orange")
        master_datasets["EUROCOM_Lumia"]=dataset_parameters( "EUROCOM_Lumia", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_LUMIA-ORC_nateko_LAND_EU_1M_V1_20191020_Monteil_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "darkorange")
        master_datasets["EUROCOM_Chimere"]=dataset_parameters( "EUROCOM_Chimere", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CHIMERE-ORC_lsce_LAND_EU_1M_V1_20191020_Broquet_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "gold")
        master_datasets["EUROCOM_CTE"]=dataset_parameters( "EUROCOM_CTE", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CTE_wur_LAND_EU_1M_V1_20191020_Ingrid_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "red")
        master_datasets["EUROCOM_EnKF"]=dataset_parameters( "EUROCOM_EnKF", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_EnKF-RAMS_vu_LAND_EU_1M_V1_20191020_Antoon_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "darkred")
        master_datasets["EUROCOM_NAME"]=dataset_parameters( "EUROCOM_NAME", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_NAME-HB_bristol_LAND_EU_1M_V1_20191020_White_Grid-eurocom_CountryTotWithEEZ.nc", "REGIONAL_TD", "FCO2_NBP", "P", "magenta")
        master_datasets["EUROCOM_ALL"]=dataset_parameters( "EUROCOM_ALL", "/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_AllEUROCOMInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZ.nc", "MINMAX", "FCO2_NBP", "P", "blue")
        master_datasets["ECOSSE_CL-CL"]=dataset_parameters( "ECOSSE_CL-CL", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200825_KUHNERT_WP3_CountryTotWithEEZ.nc", "VERIFY_BU", "FCO2_NBP_CRO", "o", "darkred")
        master_datasets["ECOSSE_CL-CL_RH"]=dataset_parameters( "ECOSSE_CL-CL_RH", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200825_KUHNERT_WP3_CountryTotWithEEZ.nc", "VERIFY_BU", "FCO2_RH_CRO", "o", "green")
        master_datasets["ECOSSE_CL-CL_NPP"]=dataset_parameters( "ECOSSE_CL-CL_NPP", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200825_KUHNERT_WP3_CountryTotWithEEZ.nc", "VERIFY_BU", "FCO2_NPP_CRO", "o", "red")
        master_datasets["ECOSSE_CL-CL_FHARVEST"]=dataset_parameters( "ECOSSE_CL-CL_FHARVEST", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200825_KUHNERT_WP3_CountryTotWithEEZ.nc", "VERIFY_BU", "FCO2_FHARVEST_CRO", "o", "blue")
        master_datasets["ECOSSE_GL-GL"]=dataset_parameters( "ECOSSE_GL-GL", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-SX_UAbdn_GRS_EU28_1M_V1_20200518_KUHNERT_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_GRA", "o", "darkred")
        master_datasets["ECOSSE_CL-CL_us"]=dataset_parameters( "ECOSSE_CL-CL_us", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_swheat_co2_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_SOIL_CRO", "o", "darkred")
        master_datasets["ECOSSE_GL-GL_us"]=dataset_parameters( "ECOSSE_GL-GL_us", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_gra_co2_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_SOIL_GRA", "o", "darkred")
        master_datasets["EFISCEN-Space"]=dataset_parameters( "EFISCEN-Space", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_treeNEP_EFISCEN-Space-SX_WENR_FOR_EU_1M_V1_20190716_SCHELHAAS_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR", "o", "green", flipdatasign=True)
        master_datasets["UNFCCC_FL-FL"]=dataset_parameters( "UNFCCC_FL-FL", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "green")
        master_datasets["UNFCCC_GL-GL"]=dataset_parameters( "UNFCCC_GL-GL", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "brown")
        master_datasets["UNFCCC_CL-CL"]=dataset_parameters( "UNFCCC_CL-CL", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "gold")
        master_datasets["ORCHIDEE_FL-FL"]=dataset_parameters( "ORCHIDEE_FL-FL", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR", "D", "dodgerblue", flipdatasign=True)
        master_datasets["EFISCEN"]=dataset_parameters( "EFISCEN", "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True)
        master_datasets["EFISCEN_NPP"]=dataset_parameters( "EFISCEN_NPP", "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NPP_FOR", "o", "orange", flipdatasign=True)
        master_datasets["EFISCEN_NEE"]=dataset_parameters( "EFISCEN_NEE", "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NEE_FOR", "o", "blue", flipdatasign=True)
        master_datasets["EFISCEN-unscaled"]=dataset_parameters( "EFISCEN-unscaled", "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True)
        master_datasets["CBM"]=dataset_parameters( "CBM", "/home/dods/verify/OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NBP", "o", "crimson", flipdatasign=True)
        master_datasets["FLUXCOM_rsonlyRF_os"]=dataset_parameters( "FLUXCOM_rsonlyRF_os", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "yellowgreen")
        master_datasets["FLUXCOM_rsonlyANN_os"]=dataset_parameters( "FLUXCOM_rsonlyANN_os", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "green")
        master_datasets["FLUXCOM_rsonlyRF_ns"]=dataset_parameters( "FLUXCOM_rsonlyRF_ns", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "yellowgreen")
        master_datasets["FLUXCOM_rsonlyANN_ns"]=dataset_parameters( "FLUXCOM_rsonlyANN_ns", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "green")
        master_datasets["FLUXCOM_FL-FL_RF"]=dataset_parameters( "FLUXCOM_FL-FL_RF", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_forest", "s", "yellowgreen")
        master_datasets["FLUXCOM_FL-FL_ANN"]=dataset_parameters( "FLUXCOM_FL-FL_ANN", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_forest", "s", "green")
        master_datasets["FLUXCOM_GL-GL_RF"]=dataset_parameters( "FLUXCOM_GL-GL_RF", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_grass", "s", "yellowgreen")
        master_datasets["FLUXCOM_GL-GL_ANN"]=dataset_parameters( "FLUXCOM_GL-GL_ANN", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_grass", "s", "green")
        master_datasets["FLUXCOM_CL-CL_RF"]=dataset_parameters( "FLUXCOM_CL-CL_RF", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_crops", "s", "yellowgreen")
        master_datasets["FLUXCOM_CL-CL_ANN"]=dataset_parameters( "FLUXCOM_CL-CL_ANN", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_crops", "s", "green")
        master_datasets["ORCHIDEE_GL-GL"]=dataset_parameters( "ORCHIDEE_GL-GL", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_GRS", "D", "dodgerblue",flipdatasign=True)
        master_datasets["ORCHIDEE_CL-CL"]=dataset_parameters( "ORCHIDEE_CL-CL", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_CRP", "D", "dodgerblue", flipdatasign=True)
        master_datasets["TNO_biofuels"]=dataset_parameters( "TNO_biofuels", "/home/dods/verify/OTHER_PROJECTS/FCO2/TNO/Tier3BUDD_CO2_BiofuelEmissions_XXX-SX_TNO_XXX_EU_1M_V1_20191110_DERNIER_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP_TOT", "X", "saddlebrown")
        master_datasets["UNFCCC_biofuels"]=dataset_parameters( "UNFCCC_biofuels", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_Biofuels_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP", "o", "saddlebrown")
        master_datasets["rivers_lakes_reservoirs_ULB"]=dataset_parameters( "rivers_lakes_reservoirs_ULB", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_RiverLakeEmissions_XXXX-SX_ULB_INLWAT_EU_1M_V1_20190911_LAUERWALD_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_INLWAT", "o", "sandybrown")
        master_datasets["UNFCCC_forest_convert"]=dataset_parameters( "UNFCCC_forest_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_grassland_convert"]=dataset_parameters( "UNFCCC_grassland_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_cropland_convert"]=dataset_parameters( "UNFCCC_cropland_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_wetland_convert"]=dataset_parameters( "UNFCCC_wetland_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_settlement_convert"]=dataset_parameters( "UNFCCC_settlement_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_other_convert"]=dataset_parameters( "UNFCCC_other_convert", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC_woodharvest"]=dataset_parameters( "UNFCCC_woodharvest", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_HWP_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["GCP_JENA"]=dataset_parameters( "GCP_JENA", "/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_JENA-s76-4-3-2019_bgc-jena_LAND_GL_1M_V1_20191020_Christian_WPX_CountryTotWithEEZ.nc", "GLOBAL_TD", "FCO2_NBP", "o", "brown")
        master_datasets["GCP_CTRACKER"]=dataset_parameters( "GCP_CTRACKER", "/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2019_wur_LAND_GL_1M_V1_20191020_Wouter_WPX_CountryTotWithEEZ.nc", "GLOBAL_TD", "FCO2_NBP", "o", "gold")
        master_datasets["GCP_CAMS"]=dataset_parameters( "GCP_CAMS", "/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CAMS-V18-2-2019_lsce_LAND_GL_1M_V1_20191020_Chevallier_WPX_CountryTotWithEEZ.nc", "GLOBAL_TD", "FCO2_NBP", "o", "orange")
        master_datasets["GCP_ALL"]=dataset_parameters( "GCP_ALL", "/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_AllGCPInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZ.nc", "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["LUH2v2_FOREST"]=dataset_parameters( "LUH2v2_FOREST", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc", "OTHER", "FOREST_AREA", "o", "orange")
        master_datasets["UNFCCC_FOREST"]=dataset_parameters( "UNFCCC_FOREST", "/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_ForestArea_CRF2019-SX_UNFCCC_FOR_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc", "OTHER", "AREA", "o", "blue")
        master_datasets["LUH2v2_GRASS"]=dataset_parameters( "LUH2v2_GRASS", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc", "OTHER", "GRASSLAND_AREA", "o", "orange")
        master_datasets["UNFCCC_GRASS"]=dataset_parameters( "UNFCCC_GRASS", "/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_GrasslandArea_CRF2019-SX_UNFCCC_GRS_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc", "OTHER", "AREA", "o", "blue")
        master_datasets["LUH2v2_CROP"]=dataset_parameters( "LUH2v2_CROP", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc", "OTHER", "CROPLAND_AREA", "o", "orange")
        master_datasets["UNFCCC_CROP"]=dataset_parameters( "UNFCCC_CROP", "/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_CroplandArea_CRF2019-SX_UNFCCC_CRP_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc", "OTHER", "AREA", "o", "blue")
        master_datasets["MS-NRT"]=dataset_parameters( "MS-NRT", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP", "o", "red")
        master_datasets["UNFCCC_LUC"]=dataset_parameters( "UNFCCC_LUC", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "green")
        master_datasets["UNFCCC_LUCF"]=dataset_parameters( "UNFCCC_LUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", "INVENTORY", "FCO2_NBP", "_", "green")
        master_datasets["FAOSTAT_LULUCF"]=dataset_parameters( "FAOSTAT_LULUCF", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet")
        master_datasets["FAOSTAT_FL-FL"]=dataset_parameters( "FAOSTAT_FL-FL", "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet")
        master_datasets["VERIFYBU"]=dataset_parameters( "VERIFYBU", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "yellow")
        master_datasets["ORCHIDEE_LUC"]=dataset_parameters( "ORCHIDEE_LUC", "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "sandybrown")
        master_datasets["ORCHIDEE_Tier2_Forest"]=dataset_parameters( "ORCHIDEE_Tier2_Forest", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR", "D", "red")
        master_datasets["ORCHIDEE_Tier2_Forest_EF1"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF1", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF1", "D", "red")
        master_datasets["ORCHIDEE_Tier2_Forest_EF2"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF2", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF2", "D", "darkgreen")
        master_datasets["ORCHIDEE_Tier2_Forest_EF3"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF3", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF3", "D", "blue")
        master_datasets["ORCHIDEE_Tier2_Forest_EF4"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF4", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF4", "D", "gray")



        # Change the color of the error bars for some
        master_datasets['UNFCCC_LUC'].uncert_color='darkseagreen'
        master_datasets['GCP_ALL'].uncert_color='red'
        master_datasets['TrendyV7'].uncert_color='gray'
        master_datasets['CSR-COMBINED'].uncert_color='blue'
        master_datasets['UNFCCC_GL-GL'].uncert_color='brown'
        master_datasets['UNFCCC_CL-CL'].uncert_color='gold'
        
        # We always want these to be the same
        master_datasets['MS-NRT'].edgec=master_datasets['MS-NRT'].facec
        
        # Some we want to be just outlines
        master_datasets["ORCHIDEE_Tier2_Forest"].edgec=master_datasets["ORCHIDEE_FL-FL"].facec
        master_datasets["ORCHIDEE_Tier2_Forest"].facec="none"
        
        # And better names for these
        master_datasets['UNFCCC_LULUCF'].displayname='UNFCCC LULUCF NGHGI (2019)'
        master_datasets['UNFCCC_LULUCF'].displayname_err='UNFCCC LULUCF NGHGI (2019) uncertainty'
        master_datasets['FAOSTAT_LULUCF'].displayname='FAOSTAT'
        master_datasets['GCP_ALL'].displayname='Mean of GCP inversions'
        master_datasets['GCP_ALL'].displayname_err='Min/Max of GCP inversions'
        master_datasets['CSR-COMBINED'].displayname='Mean of CarboScopeReg'
        master_datasets['CSR-COMBINED'].displayname_err='Min/Max of CarboScopeReg'
        master_datasets['EUROCOM_ALL'].displayname='Mean of EUROCOM inversions'
        master_datasets['EUROCOM_ALL'].displayname_err='Min/Max of EUROCOM inversions'
        master_datasets['TrendyV7'].displayname='Median of TRENDY v7 DGVMs'
        master_datasets['TrendyV7'].displayname_err='Min/Max of TRENDY v7 DGVMs'
        
        master_datasets['ORCHIDEE_Tier2_Forest_EF1'].displayname='UNFCCC emissions / FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF2'].displayname='ORCHIDEE FL-FL emissions / LUH2v2-ESACCI FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF3'].displayname='ORCHIDEE FL-FL emissions / UNFCCC FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF4'].displayname='Created from Eq. 2.5 and ORCHIDEE'
        
        self.lplot_areas=False
        
        # Now define the actual simulation configs
        if self.graphname == "test":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'BLUE', \
                                  'TrendyV7', \
                              ]   
            self.output_file_start="TEST_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use change"
            self.output_file_start="test_"
            self.output_file_end="_2019_v1.png" 
        elif self.graphname == "luc_full":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LUC', \
                                  'UNFCCC_forest_convert', \
                                  'UNFCCC_grassland_convert', \
                                  'UNFCCC_cropland_convert', \
                                  'UNFCCC_wetland_convert', \
                                  'UNFCCC_settlement_convert', \
                                  'UNFCCC_other_convert', \
                                  'BLUE', \
                                  'H&N', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  'ORCHIDEE_LUC', \
                                  'ORCHIDEE', \
                                  'ORCHIDEE_S2', \
                              ]   
            self.output_file_start="LUC_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use change"
            
            # Change some colors and symbols here
            facec_master['BLUE']='blue'
            facec_master['H&N']='green'
            facec_master['ORCHIDEE-MICT']='red'
            facec_master['ORCHIDEE']='blue'
            
            plotmarker_master['BLUE']='^'
            plotmarker_master['H&N']='^'
            plotmarker_master['ORCHIDEE-MICT']='X'
            plotmarker_master['ORCHIDEE']='X'
            
            # These simulations will be combined together.
            self.overwrite_simulations["UNFCCC_LUC"]=['UNFCCC_forest_convert', \
                                                 'UNFCCC_grassland_convert', \
                                                 'UNFCCC_cropland_convert', \
                                                 'UNFCCC_wetland_convert', \
                                                 'UNFCCC_settlement_convert', \
                                                 'UNFCCC_other_convert', \
                                             ]
            self.overwrite_operations["UNFCCC_LUC"]="sum"
            self.overwrite_coeffs["UNFCCC_LUC"]=[1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                        ]
            self.overwrite_simulations["ORCHIDEE_LUC"]=['ORCHIDEE', \
                                                   'ORCHIDEE_S2', \
                                               ]
            self.overwrite_operations["ORCHIDEE_LUC"]="sum"
            self.overwrite_coeffs["ORCHIDEE_LUC"]=[1.0, \
                                              -1.0, \
                                          ]
            
            
            # So I don't want to generally plot the components
            displaylegend_master['UNFCCC_forest_convert']=False
            displaylegend_master['UNFCCC_grassland_convert']=False
            displaylegend_master['UNFCCC_cropland_convert']=False
            displaylegend_master['UNFCCC_wetland_convert']=False
            displaylegend_master['UNFCCC_settlement_convert']=False
            displaylegend_master['UNFCCC_other_convert']=False
            displaylegend_master['ORCHIDEE']=False
            displaylegend_master['ORCHIDEE_S2']=False
            
            
            #if lshow_productiondata:
            #   productiondata_master['ORCHIDEE-MICT']=False
            #endif
            
        elif self.graphname == "all_orchidee":
            self.desired_simulations=[ \
                                  'ORCHIDEE-MICT', \
                                  'ORCHIDEE_LUC', \
                                  'ORCHIDEE', \
                                  'ORCHIDEE_S2', \
                                  'ORCHIDEE_S1', \
                                  'ORCHIDEE_S0', \
                                  "TrendyV7_ORCHIDEE",\
                              ]   
            self.output_file_start="ORCHIDEE_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all ORCHIDEE simulations"
            
            # Change some colors and symbols here
            facec_master['ORCHIDEE-MICT']='red'
            facec_master['ORCHIDEE']='blue'
            
            plotmarker_master['ORCHIDEE-MICT']='^'
            plotmarker_master['TrendyV7_ORCHIDEE']='X'
            plotmarker_master['ORCHIDEE']='D'
            plotmarker_master['ORCHIDEE_S2']='D'
            plotmarker_master['ORCHIDEE_S1']='D'
            plotmarker_master['ORCHIDEE_S0']='D'
            plotmarker_master['ORCHIDEE_LUC']='P'
            
            # These simulations will be combined together.
            self.overwrite_simulations["ORCHIDEE_LUC"]=['ORCHIDEE', \
                                                   'ORCHIDEE_S2', \
                                               ]
            self.overwrite_operations["ORCHIDEE_LUC"]="sum"
            self.overwrite_coeffs["ORCHIDEE_LUC"]=[1.0, \
                                              -1.0, \
                                          ]
            
            
            
        elif self.graphname == "lucf_full":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LUCF', \
                                  'UNFCCC_forest_convert', \
                                  'UNFCCC_grassland_convert', \
                                  'UNFCCC_cropland_convert', \
                                  'UNFCCC_wetland_convert', \
                                  'UNFCCC_settlement_convert', \
                                  'UNFCCC_other_convert', \
                                  'UNFCCC_FL-FL', \
                                  'BLUE', \
                                  'H&N', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  'ORCHIDEE', \
                              ]   
            self.output_file_start="LUCF_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use change and forestry"
            
            # Change some colors and symbols here
            facec_master['BLUE']='blue'
            facec_master['H&N']='green'
            facec_master['ORCHIDEE-MICT']='red'
            facec_master['ORCHIDEE']='blue'
            
            plotmarker_master['BLUE']='^'
            plotmarker_master['H&N']='^'
            plotmarker_master['ORCHIDEE-MICT']='X'
            plotmarker_master['ORCHIDEE']='X'
            
            # These simulations will be combined together.
            self.overwrite_simulations["UNFCCC_LUCF"]=['UNFCCC_forest_convert', \
                                                  'UNFCCC_grassland_convert', \
                                                  'UNFCCC_cropland_convert', \
                                                  'UNFCCC_wetland_convert', \
                                                  'UNFCCC_settlement_convert', \
                                                  'UNFCCC_other_convert', \
                                                  'UNFCCC_FL-FL',\
                                              ]
            self.overwrite_operations["UNFCCC_LUCF"]="sum"
            self.overwrite_coeffs["UNFCCC_LUCF"]=[1.0, \
                                             1.0, \
                                             1.0, \
                                             1.0, \
                                             1.0, \
                                             1.0, \
                                             1.0, \
                                         ]
            # So I don't want to generally plot the components
            displaylegend_master['UNFCCC_forest_convert']=False
            displaylegend_master['UNFCCC_grassland_convert']=False
            displaylegend_master['UNFCCC_cropland_convert']=False
            displaylegend_master['UNFCCC_wetland_convert']=False
            displaylegend_master['UNFCCC_settlement_convert']=False
            displaylegend_master['UNFCCC_other_convert']=False
            displaylegend_master['UNFCCC_FL-FL']=False
            
            
            #if lshow_productiondata:
            #   productiondata_master['ORCHIDEE-MICT']=False
            #endif
            
            # This is simply meant to compare UNFCCC LULUCF with the MS-NRT data
        elif self.graphname == "lulucf_msnrt":
            self.desired_simulations=[ \
                                  'UNFCCC_LULUCF', \
                                  'MS-NRT', \
                              ]   
            self.output_file_start="UNFCCC-LULUCF-MSNRT_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"
            
            # These simulations will be combined together.
            #self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            #self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            #self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            # So I don't want to generally plot the components
            #displaylegend_master['FAOSTAT_Crp']=False
            #displaylegend_master['FAOSTAT_Grs']=False
            #displaylegend_master['FAOSTAT_For']=False
            
        elif self.graphname == "lulucf_full":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'BLUE', \
                                  'H&N', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  'ORCHIDEE', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                              ]   
            self.output_file_start="LULUCF_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            
        elif self.graphname == "lulucf_trendy":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'BLUE', \
                                  'H&N', \
                                  'MS-NRT', \
                                  #'ORCHIDEE-MICT', \
                                  'ORCHIDEE', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                                  'TrendyV7', \
                                  #"TrendyV7_ORCHIDEE",\
                              ]  
            
            self.desired_legend=[\
                            displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                            displayname_master["MS-NRT"],\
                            
                            displayname_master["FAOSTAT_LULUCF"],\
                            displayname_master["BLUE"],\
                            displayname_master["H&N"],\
                            displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                            displayname_master["ORCHIDEE"],\
                            #displayname_master["ORCHIDEE-MICT"],\
                            #displayname_master["TrendyV7_ORCHIDEE"],\
                        ]
            self.output_file_start="LULUCFTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # Plot these as bars
            lplot_errorbar_master["TrendyV7"]=True
            
        elif self.graphname == "orc_trendy":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'MS-NRT', \
                                  'ORCHIDEE', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                                  'TrendyV7', \
                                  "TrendyV7_ORCHIDEE",\
                              ]  
            
            displayname_master["ORCHIDEE"]="ORCHIDEE-VERIFY"
            self.desired_legend=[\
                            displayname_master["FAOSTAT_LULUCF"],\
                            displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                            displayname_master["MS-NRT"],\
                            
                            displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                            displayname_master["TrendyV7_ORCHIDEE"],\
                            displayname_master["ORCHIDEE"],\
                        ]
            self.output_file_start="LULUCFOrcTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # Plot these as bars
            lplot_errorbar_master["TrendyV7"]=True
            
        elif self.graphname == "unfccc_fao_trendy":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'MS-NRT', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                                  'TrendyV7', \
                                  "TrendyV7_ORCHIDEE",\
                              ]  
            
            self.desired_legend=[\
                            displayname_master["FAOSTAT_LULUCF"],\
                            displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                            displayname_master["MS-NRT"],\
                            
                            displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                            displayname_master["TrendyV7_ORCHIDEE"],\
                        ]
            self.output_file_start="UNFCCCFAOTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # Plot these as bars
            lplot_errorbar_master["TrendyV7"]=True
            
        elif self.graphname == "unfccc_fao":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LULUCF', \
                                  'MS-NRT', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                              ]  
            
            self.desired_legend=[\
                            displayname_master["FAOSTAT_LULUCF"],\
                            displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                            displayname_master["MS-NRT"],\
                            
                        ]
            self.output_file_start="UNFCCCFAO_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # Plot these as bars
            lplot_errorbar_master["TrendyV7"]=True
            
        elif self.graphname == "fao":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                              ]  
            
            self.desired_legend=[\
                            #                      "blah",\
                            displayname_master["FAOSTAT_LULUCF"],\
                        ]
            self.output_file_start="FAO_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # Plot these as bars
            lplot_errorbar_master["TrendyV7"]=True
            
        elif self.graphname == "sectorplot_full":
            self.desired_simulations=[ \
                                  'ORCHIDEE', \
                                  'ECOSSE_GL-GL', \
                                  'EFISCEN', \
                                  'UNFCCC_FL-FL', \
                                  'UNFCCC_GL-GL', \
                                  'UNFCCC_CL-CL', \
                                  'FLUXCOM_rsonlyANN_os', \
                                  'FLUXCOM_rsonlyRF_os', \
                                  'EPIC', \
                                  'TrendyV7', \
                              ]  
            self.desired_legend=[\
                            "UNFCCC_FL-FL","UNFCCC_GL-GL","UNFCCC_CL-CL",\
                            'Median of TRENDY v7 DGVMs', "Min/Max of TRENDY v7 DGVMs", \
                            "EFISCEN","ECOSSE_GL-GL","EPIC",\
                            "EPIC/ECOSSE/EFISCEN","ORCHIDEE","FLUXCOM_rsonlyANN_os","FLUXCOM_rsonlyRF_os", \
                        ]
            
            
            self.output_file_start="AllSectorBU_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use (land remaining land)"
            
            plotmarker_master['EPIC']="P"
            
            facec_master['EPIC']="brown"
            
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE_CL-CL']=False
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            
        elif self.graphname == "unfccc_lulucf_bar":
            self.desired_simulations=[ \
                                  'UNFCCC_LULUCF', \
                                  'UNFCCC_FL-FL', \
                                  'UNFCCC_GL-GL', \
                                  'UNFCCC_CL-CL', \
                                  'UNFCCC_forest_convert', \
                                  'UNFCCC_grassland_convert', \
                                  'UNFCCC_cropland_convert', \
                                  'UNFCCC_wetland_convert', \
                                  'UNFCCC_settlement_convert', \
                                  'UNFCCC_other_convert', \
                                  'UNFCCC_woodharvest', \
                              ]  
            # I cannot do this until all my simulations have been plotted
            #self.desired_legend=[\
                #                 displayname_master["UNFCCC_LULUCF"],\
                #                'UNFCCC_FL-FL','UNFCCC_GL-GL','UNFCCC_CL-CL',\
                #                'UNFCCC_forest_convert', \
                #                      'UNFCCC_grassland_convert', \
                #                      'UNFCCC_cropland_convert', \
                #                      'UNFCCC_wetland_convert', \
                #                      'UNFCCC_settlement_convert', \
                #                      'UNFCCC_other_convert', \
                #                 ]
            
            
            self.output_file_start="UNFCCCLULUCFbar_"
            # v3 has colored bars, v7 has gray bars
            self.output_file_end="_FCO2land_2019_v7.png" 
            self.titleending=r" : CO$_2$ emission trends from land use, land use change, and forestry"
            
            plotmarker_master['EPIC']="P"
            
            facec_master['UNFCCC_LULUCF']="darkgray"
            facec_master['UNFCCC_forest_convert']="darkgreen"
            facec_master['UNFCCC_grassland_convert']="magenta"
            facec_master['UNFCCC_cropland_convert']="violet"
            facec_master['UNFCCC_wetland_convert']="blue"
            facec_master['UNFCCC_settlement_convert']="dodgerblue"
            facec_master['UNFCCC_other_convert']="brown"
            facec_master['UNFCCC_woodharvest']="aqua"
            
            displayname_master['UNFCCC_FL-FL']='FL-FL'
            displayname_master['UNFCCC_GL-GL']='GL-GL'
            displayname_master['UNFCCC_CL-CL']='CL-CL'
            displayname_master['UNFCCC_woodharvest']='HWP'
            
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE_CL-CL']=False
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            
        elif self.graphname == "unfccc_woodharvest":
            self.desired_simulations=[ \
                                  #    'UNFCCC_LULUCF', \
                                  'UNFCCC_FL-FL', \
                                  'UNFCCC_woodharvest', \
                              ]  
            
            self.output_file_start="UNFCCCHWP_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emission trends from land use, land use change, and forestry"
            
            facec_master['UNFCCC_LULUCF']="darkgray"
            facec_master['UNFCCC_woodharvest']="aqua"
            
            displayname_master['UNFCCC_FL-FL']='FL-FL'
            displayname_master['UNFCCC_woodharvest']='HWP'
            
        elif self.graphname in ("verifybu","verifybu_detrend"):
            self.desired_simulations=[ \
                                  'ORCHIDEE', \
                                  'ORCHIDEE-MICT', \
                                  'EFISCEN', \
                                  #                            'EFISCEN-unscaled', \
                                  #'EFISCEN-Space', \
                                  'FLUXCOM_rsonlyANN_os', \
                                  'FLUXCOM_rsonlyRF_os', \
                                  #'ECOSSE_GL-GL', \
                                  'ECOSSE_CL-CL', \
                                  #'ECOSSE_GL-GL_us', \
                                  #'ECOSSE_CL-CL_us', \
                                  'EPIC', \
                                  'BLUE', \
                                  #                            'VERIFYBU', \
                              ]   
            self.output_file_start="VerifyBU_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all VERIFY bottom-up models"
            lplot_areas=True
            
            if self.graphname == "verifybu_detrend":
                self.output_file_start="VerifyBUdetrend_"
                self.ldetrend=True
                self.titleending=r" : detrended CO$_2$ emissions from all VERIFY bottom-up models"
            #endif
                
            # These simulations will be combined together.
            #self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE']
            #self.overwrite_operations["VERIFYBU"]="mean"
            #displaylegend_master["VERIFYBU"]=False
            
            plotmarker_master['EFISCEN']="P"
            plotmarker_master['CBM']="X"
            plotmarker_master['FLUXCOM_rsonlyRF_os']="s"
            plotmarker_master['FLUXCOM_rsonlyANN_os']="s"
            plotmarker_master['FAOSTAT_FL-FL']="d"
            
            edgec_master["ORCHIDEE_FL-FL"]="black"
            edgec_master["EFISCEN"]="black"
            edgec_master["CBM"]="black"
            edgec_master["FLUXCOM_FL-FL_RF"]="black"
            edgec_master["FLUXCOM_FL-FL_ANN"]="black"
            edgec_master["FAOSTAT_FL-FL"]="black"
            
            facec_master["ORCHIDEE_FL-FL"]="black"
            facec_master["EFISCEN-Space"]="blue"
            facec_master["EFISCEN"]="skyblue"
            facec_master["CBM"]="red"
            facec_master["FLUXCOM_FL-FL_RF"]="orange"
            facec_master["FLUXCOM_FL-FL_ANN"]="orangered"
            facec_master["FAOSTAT_FL-FL"]="yellow"
            
            
            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif
            
        elif self.graphname == "trendy":
            self.desired_simulations=[ \
                                  #'TrendyV7', \
                                  'TrendyV7_CABLE', \
                                  'TrendyV7_CLASS', \
                                  'TrendyV7_CLM5', \
                                  'TrendyV7_DLEM', \
                                  'TrendyV7_ISAM', \
                                  'TrendyV7_JSBACH', \
                                  'TrendyV7_JULES', \
                                  'TrendyV7_LPJ', \
                                  'TrendyV7_LPX', \
                                  'TrendyV7_OCN', \
                                  'TrendyV7_ORCHIDEE-CNP', \
                                  'TrendyV7_ORCHIDEE', \
                                  'TrendyV7_SDGVM', \
                                  'TrendyV7_SURFEX', \
            ]   
            self.output_file_start="TRENDY_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all TRENDY v7 bottom-up models"
            lplot_areas=True
            
            plotmarker_master['EFISCEN']="P"
            
            edgec_master["ORCHIDEE_FL-FL"]="black"
            
            facec_master["TrendyV7_ORCHIDEE"]="lightgray"
            
        elif self.graphname == "fluxcom":
            self.desired_simulations=[ \
                                  'FLUXCOM_rsonlyANN_os', \
                                  'FLUXCOM_rsonlyANN_ns', \
                                  'FLUXCOM_rsonlyRF_os', \
                                  'FLUXCOM_rsonlyRF_ns', \
                                  'FLUXCOM_FL-FL_RF', \
                                  'FLUXCOM_CL-CL_RF', \
                                  'FLUXCOM_GL-GL_RF', \
                                  'FLUXCOM_FL-FL_ANN', \
                                  'FLUXCOM_CL-CL_ANN', \
                                  'FLUXCOM_GL-GL_ANN', \
            ]   
            self.output_file_start="FLUXCOM_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from FLUXCOM with both the original and new LUH2v2-ESACCI land cover fractions"
            
            plotmarker_master['FLUXCOM_rsonlyRF_os']="s"
            plotmarker_master['FLUXCOM_rsonlyANN_os']="s"
            plotmarker_master['FLUXCOM_rsonlyRF_ns']="o"
            plotmarker_master['FLUXCOM_rsonlyANN_ns']="o"
            plotmarker_master["FLUXCOM_CL-CL_RF"]="P"
            plotmarker_master["FLUXCOM_FL-FL_RF"]="X"
            plotmarker_master["FLUXCOM_GL-GL_RF"]="^"
            plotmarker_master["FLUXCOM_CL-CL_ANN"]="P"
            plotmarker_master["FLUXCOM_FL-FL_ANN"]="X"
            plotmarker_master["FLUXCOM_GL-GL_ANN"]="^"
            
            facec_master["FLUXCOM_rsonlyRF_os"]="blue"
            facec_master["FLUXCOM_rsonlyANN_os"]="red"
            facec_master["FLUXCOM_rsonlyRF_ns"]="blue"
            facec_master["FLUXCOM_CL-CL_RF"]="blue"
            facec_master["FLUXCOM_FL-FL_RF"]="blue"
            facec_master["FLUXCOM_GL-GL_RF"]="blue"
            facec_master["FLUXCOM_rsonlyANN_ns"]="red"
            facec_master["FLUXCOM_CL-CL_ANN"]="red"
            facec_master["FLUXCOM_GL-GL_ANN"]="red"
            facec_master["FLUXCOM_FL-FL_ANN"]="red"
            
            
            # These simulations will be combined together.
            self.overwrite_simulations["FLUXCOM_rsonlyANN_ns"]=['FLUXCOM_FL-FL_ANN','FLUXCOM_GL-GL_ANN','FLUXCOM_CL-CL_ANN']
            # So I don't want to generally plot the components
            displaylegend_master['FLUXCOM_FL-FL_ANN']=True
            displaylegend_master['FLUXCOM_GL-GL_ANN']=True
            displaylegend_master['FLUXCOM_CL-CL_ANN']=True
            
            self.overwrite_simulations["FLUXCOM_rsonlyRF_ns"]=['FLUXCOM_FL-FL_RF','FLUXCOM_GL-GL_RF','FLUXCOM_CL-CL_RF']
            # So I don't want to generally plot the components
            displaylegend_master['FLUXCOM_FL-FL_RF']=True
            displaylegend_master['FLUXCOM_GL-GL_RF']=True
            displaylegend_master['FLUXCOM_CL-CL_RF']=True
            
        elif self.graphname == "forestry_full":
            self.desired_simulations=[ \
                                  'ORCHIDEE_FL-FL', \
                                  'ORCHIDEE_Tier2_Forest', \
                                  'EFISCEN', \
                                  #  'EFISCEN_NPP', \
                                  #  'EFISCEN_NEE', \
                                  #   'EFISCEN-unscaled', \
                                  #                            'EFISCEN-Space', \
                                  'CBM', \
                                  'UNFCCC_FL-FL', \
                                  #'FLUXCOM_FL-FL_ANN', \
                                  #'FLUXCOM_FL-FL_RF', \
                                  'FAOSTAT_FL-FL', \
                                  'LUH2v2_FOREST', \
                                  'UNFCCC_FOREST', \
            ]   
            
            displayname_master['UNFCCC_FOREST']='UNFCCC_FL-FL area'
            displayname_master['LUH2v2_FOREST']='LUH2v2-ESACCI_FL-FL area (used in ORCHIDEE)'
            
            self.desired_legend=[\
                            displayname_master['UNFCCC_FL-FL'],"UNFCCC_FL-FL uncertainty",\
                            displayname_master['FAOSTAT_FL-FL'], \
                            displayname_master['ORCHIDEE_FL-FL'], \
                            displayname_master['EFISCEN'], \
                            # displayname_master['EFISCEN_NPP'], \
                            # displayname_master['EFISCEN_NEE'], \
                            #                       'EFISCEN-Space', \
                            displayname_master['CBM'], \
                            displayname_master['ORCHIDEE_Tier2_Forest'], \
                            #displayname_master['FLUXCOM_FL-FL_ANN'], \
                            #displayname_master['FLUXCOM_FL-FL_RF'], \
                            displayname_master['LUH2v2_FOREST'], \
                            displayname_master['UNFCCC_FOREST'], \
            ]
            
            self.output_file_start="ForestRemain_"
            # v1 has EFISCEN data from a spreadsheet sent by Mart-Jan in April 2020
            #      self.output_file_end="_FCO2land_2019_v1.png" 
            # v2 has EFISCEn data from June 2020
            self.output_file_end="_FCO2land_2019_v2.png" 
            self.titleending=r" : FL-FL bottom-up net CO$_2$ emissions"
            lplot_areas=True
            
            
            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif
            
        elif self.graphname == "grassland_full":
            self.desired_simulations=[ \
                                  'ORCHIDEE_GL-GL', \
                                  #'ORCHIDEE_RH', \
                                  'ECOSSE_GL-GL', \
                                  #  'ECOSSE_GL-GL_us', \
                                  'UNFCCC_GL-GL', \
                                  # 'FLUXCOM_GL-GL_ANN', \
                                  # 'FLUXCOM_GL-GL_RF', \
                                  'LUH2v2_GRASS', \
                                  'UNFCCC_GRASS', \
            ]   
            self.output_file_start="GrasslandRemain_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : GL-GL bottom-up net CO$_2$ emissions"
            
            # Change some things from the above
            displayname_master['UNFCCC_GRASS']='UNFCCC_GL-GL area'
            displayname_master['LUH2v2_GRASS']='LUH2v2-ESACCI_GL-GL area (used in ORCHIDEE)'
            lplot_areas=True
            
            displayname_master['ECOSSE_GL-GL']='ECOSSE GL-GL'
            
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            self.desired_legend=[\
                            "UNFCCC_GL-GL","UNFCCC_GL-GL uncertainty",\
                            displayname_master['ORCHIDEE_GL-GL'], \
                            #displayname_master['ORCHIDEE_RH'], \
                            displayname_master['ECOSSE_GL-GL'], \
                            # 'FLUXCOM_GL-GL_ANN', \
                            # 'FLUXCOM_GL-GL_RF', \
                            displayname_master['LUH2v2_GRASS'], \
                            displayname_master['UNFCCC_GRASS'], \
                        ]
            
            
        elif self.graphname == "epic":
            self.desired_simulations=[ \
                                  'ORCHIDEE_CL-CL', \
                                  'ECOSSE_CL-CL', \
                                  'EPIC', \
                                  'EPIC_RH', \
                                  'EPIC_clch', \
                                  'EPIC_fHarvest', \
                                  'EPIC_npp', \
                              ]   
            
            
            self.output_file_start="EPICComparison_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CL-CL CO$_2$ emissions"
            
        elif self.graphname == "crops_full":
            self.desired_simulations=[ \
                                  'ORCHIDEE_CL-CL', \
                                  # 'ORCHIDEE_RH', \
                                  'ECOSSE_CL-CL', \
                                  #       'ECOSSE_CL-CL_NPP', \
                                  #       'ECOSSE_CL-CL_FHARVEST', \
                                  #       'ECOSSE_CL-CL_RH', \
                                  #     'ECOSSE_CL-CL_us', \
                                  'UNFCCC_CL-CL', \
                                  #    'FLUXCOM_CL-CL_ANN', \
                                  #    'FLUXCOM_CL-CL_RF', \
                                  'EPIC', \
                                  # 'EPIC_RH', \
                                  'LUH2v2_CROP', \
                                  'UNFCCC_CROP', \
                              ]   
            
            master_datasets['UNFCCC_CROP'].displayname='UNFCCC_CL-CL area'
            master_datasets['LUH2v2_CROP'].displayname='LUH2v2-ESACCI_CL-CL area (used in ORCHIDEE)'
            master_datasets['ECOSSE_CL-CL'].displayname='ECOSSE_CL-CL_NBP'
            
            self.desired_legend=[\
                            "UNFCCC_CL-CL","UNFCCC_CL-CL uncertainty",\
                            'ORCHIDEE_CL-CL', \
                            master_datasets['ECOSSE_CL-CL'].displayname, \
                            #    master_datasets['ECOSSE_CL-CL_RH'], \
                            #     master_datasets['ECOSSE_CL-CL_NPP'], \
                            #       master_datasets['ECOSSE_CL-CL_FHARVEST'], \
                            'EPIC_CL-CL', \
                            #  'FLUXCOM_CL-CL_ANN', \
                            #  'FLUXCOM_CL-CL_RF', \
                            # 'ORCHIDEE_RH', \
                            # 'EPIC_RH', \
                            master_datasets['LUH2v2_CROP'].displayname, \
                            master_datasets['UNFCCC_CROP'].displayname, \
                        ]
            
            self.output_file_start="CroplandRemain_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CL-CL bottom-up net CO$_2$ emissions"
            
            # Change some things from the above
            self.lplot_areas=True
            
            master_datasets['EPIC'].displayname='EPIC_CL-CL'
            ####            

        elif self.graphname == "biofuels":

            self.desired_simulations=[ \
                                  'UNFCCC_biofuels', \
                                  'TNO_biofuels', \
                              ]   
            self.output_file_start="biofuels_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from biofuel combustion"
            facec_master['UNFCCC_biofuels']='red'
            facec_master['TNO_biofuels']='blue'
            
        elif self.graphname == "emission_factors":
            self.desired_simulations=[ \
                                  'ORCHIDEE_Tier2_Forest_EF1', \
                                  'ORCHIDEE_Tier2_Forest_EF2', \
                                  'ORCHIDEE_Tier2_Forest_EF3', \
                                  'ORCHIDEE_Tier2_Forest_EF4', \
                              ]   
            
            self.output_file_start="FL-FLEmissionFactors_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : FL-FL bottom-up emission factors"
            lplot_areas=False
            
            
        elif self.graphname == "eurocom_inversions":
            self.desired_simulations=[ \
                                  'EUROCOM_ALL', \
                                  'EUROCOM_Carboscope', \
                                  'CSR-COMBINED', \
                                  'EUROCOM_Flexinvert', \
                                  'EUROCOM_Lumia', \
                                  'EUROCOM_Chimere', \
                                  'EUROCOM_CTE', \
                                  'EUROCOM_EnKF', \
                                  'EUROCOM_NAME', \
                              ]   
            self.output_file_start="EUROCOMInversions_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from EUROCOM inversions"
            
            lplot_errorbar_master['EUROCOM_ALL']=True
            
        elif self.graphname == "gcp_inversions":
            self.desired_simulations=[ \
                                  'GCP_ALL', \
                                  'GCP_JENA', \
                                  'GCP_CTRACKER', \
                                  'GCP_CAMS', \
                              ]   
            self.output_file_start="GCPInversions_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP inversions"
            
            displayname_master['GCP_ALL']="Mean of GCP inversions"
            displayname_err_master['GCP_ALL']="Min/Max of GCP inversions"
            
            lplot_errorbar_master['GCP_ALL']=True
            
        elif self.graphname == "gcp_inversions_corrected":
            self.desired_simulations=[ \
                                  'GCP_ALL', \
                                  'GCP_JENA', \
                                  'GCP_CTRACKER', \
                                  'GCP_CAMS', \
                                  'rivers_lakes_reservoirs_ULB', \
                              ]   
            self.output_file_start="GCPInversionsCorrected_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP inversions"
            
            master_datasets["GCP_ALL"].lcorrect_inversion=True
            master_datasets["GCP_JENA"].lcorrect_inversion=True
            master_datasets["GCP_CTRACKER"].lcorrect_inversion=True
            master_datasets["GCP_CAMS"].lcorrect_inversion=True
            
            lplot_errorbar_master['GCP_ALL']=True
            
        elif self.graphname in ("inversions_combined","inversions_combinedbar"):
            
            self.desired_simulations=[ \
                                  'UNFCCC_LULUCF', \
                                  'MS-NRT', \
                                  #                      'rivers_lakes_reservoirs_ULB', \
                                  'CSR-COMBINED', \
                                  'EUROCOM_ALL', \
                                  'GCP_ALL', \
                                  'BLUE', \
                                  #    'EPIC', \
                                  #    'EFISCEN', \
                                  'H&N', \
                                  #   'FLUXCOM_rsonlyANN_os', \
                                  #   'FLUXCOM_rsonlyRF_os', \
                                  #   'ORCHIDEE-MICT', \
                                  'ORCHIDEE', \
                                  'FAOSTAT_LULUCF', \
                                  'FAOSTAT_Crp', \
                                  'FAOSTAT_Grs', \
                                  'FAOSTAT_For', \
                                  'TrendyV7', \
                                  # 'TrendyV7_ORCHIDEE', \
                              ]        
            
            self.output_file_end="_FCO2land_2019_v1.png" 
            
            if self.graphname == "inversions_combined":
                self.titleending=r" : Comparison of top-down vs. bottom-up net land CO$_2$ fluxes"
                self.output_file_start="TopDownLULUCF_"
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 displayname_master['UNFCCC_LULUCF'], \
                                 displayname_err_master['UNFCCC_LULUCF'], \
                                 displayname_master['FAOSTAT_LULUCF'], \
                                 displayname_master['MS-NRT'], \
                                 displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                                 displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
                                 displayname_master['CSR-COMBINED'], \
                                 displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                                 displayname_master['ORCHIDEE'], \
                                 #    displayname_master['EPIC'], \
                                 #    displayname_master['EFISCEN'], \
                                 displayname_master['BLUE'], \
                                 displayname_master['H&N'], \
                                 #displayname_master['TrendyV7_ORCHIDEE'], \
                                 #displayname_master['ORCHIDEE-MICT'], \
                                 #      'FLUXCOM_rsonlyANN_os', \
                                 #      'FLUXCOM_rsonlyRF_os',
                             ]
                
                displaylegend_master['ORCHIDEE-MICT']=True
                displaylegend_master['ORCHIDEE']=True      
                displaylegend_master['TrendyV7_ORCHIDEE']=True
                
            else:
                self.output_file_start="TopDownLULUCFbar_"
                self.titleending=r" : Comparison of top-down vs. bottom-up (aggregated) net land CO$_2$ fluxes"
                
                self.desired_simulations.append("VERIFYBU")
                
                # These simulations will be combined together.
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE']
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE']
                self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE','BLUE']
                self.overwrite_operations["VERIFYBU"]="mean"
                displaylegend_master["VERIFYBU"]=False
                
                displayname_master["VERIFYBU"]="Mean of BU estimates (VERIFY)"
                displayname_err_master["VERIFYBU"]="Min/Max of BU estimates (VERIFY)"
                
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 displayname_master['UNFCCC_LULUCF'], \
                                 displayname_err_master['UNFCCC_LULUCF'], \
                                 displayname_master['MS-NRT'], \
                                 displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                                 displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
                                 displayname_master['CSR-COMBINED'], \
                                 displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                                 displayname_master['FAOSTAT_LULUCF'], \
                                 displayname_master['H&N'], \
                                 displayname_master['VERIFYBU'], \
                                 displayname_err_master['VERIFYBU'], \
                                 #        displayname_master['ORCHIDEE'], \
                                 #        displayname_master['TrendyV7_ORCHIDEE'], \
                                 #        displayname_master['ORCHIDEE-MICT'], \
                             ]
                
                # These simulations will be combined together.
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os']
                #self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE']
                #self.overwrite_operations["VERIFYBU"]="mean"
                
                # So I don't want to generally plot the components
                displaylegend_master['ORCHIDEE-MICT']=False
                displaylegend_master['ORCHIDEE']=False
                displaylegend_master['BLUE']=False
                displaylegend_master['FLUXCOM_rsonlyANN_os']=False
                displaylegend_master['FLUXCOM_rsonlyRF_os']=False
                
                displaylegend_master['TrendyV7_ORCHIDEE']=False
                
            #endif

            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
            self.overwrite_operations["FAOSTAT_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
            
            # So I don't want to generally plot the components
            displaylegend_master['FAOSTAT_Crp']=False
            displaylegend_master['FAOSTAT_Grs']=False
            displaylegend_master['FAOSTAT_For']=False
            
            # Change some colors and symbols here
            facec_master["FAOSTAT_LULUCF"]="yellow"
            plotmarker_master['FAOSTAT_LULUCF']='^'
            facec_master["ORCHIDEE"]="black"
            facec_master["ORCHIDEE-MICT"]="none"
            facec_master["TrendyV7_ORCHIDEE"]="none"
            edgec_master["TrendyV7_ORCHIDEE"]="dimgrey"
            edgec_master["ORCHIDEE-MICT"]="black"
            #displaylegend_master['ORCHIDEE-MICT']=False
            #displaylegend_master['TrendyV7_ORCHIDEE']=False
            
            # A couple of these plots will be displayed as bars instead of symbols
            lplot_errorbar_master["EUROCOM_ALL"]=True
            lplot_errorbar_master["GCP_ALL"]=True
            lplot_errorbar_master["TrendyV7"]=True
            lplot_errorbar_master["CSR-COMBINED"]=True
            lwhiskerbars_master["CSR-COMBINED"]=True
            
        elif self.graphname == "inversions_verify":
            self.desired_simulations=[ \
                                  'CSR-COMBINED', \
                                  'CSR-REG-100km', \
                                  'CSR-REG-200km', \
                                  'CSR-REG-Core100km', \
                                  'CSR-REG-Valid100km', \
                              ]   
            self.output_file_start="inversions_verify_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : CO$_2$ inversion from CarboScopeReg simulations in VERIFY"
            
        elif self.graphname in ( "inversions_test", "inversions_full"):
            
            if self.graphname == "inversions_test":
                self.titleending=r" : UNFCCC vs. net land CO$_2$ fluxes - TEST (not complete dataset)"
                self.desired_simulations=[ \
                                      'UNFCCC_LULUCF', \
                                      'MS-NRT', \
                                      'rivers_lakes_reservoirs_ULB', \
                                      'CSR-REG-100km', \
                                      'CSR-REG-200km', \
                                      'EUROCOM_Carboscope', \
                                      'EUROCOM_Flexinvert', \
                                      'GCP_JENA', \
                                      'GCP_CAMS', \
                                  ]   
                self.output_file_start="inversions_test_"
            else:
                self.titleending=r" : UNFCCC vs. top-down estimates of net land CO$_2$ fluxes"
                self.desired_simulations=[ \
                                      'UNFCCC_LULUCF', \
                                      'MS-NRT', \
                                      'rivers_lakes_reservoirs_ULB', \
                                      'CSR-COMBINED', \
                                      'EUROCOM_ALL', \
                                      'GCP_ALL', \
                                  ]   
                self.output_file_start="TopDownAndInventories_"
            #endif
            
            self.desired_legend=[ \
                             displayname_master['UNFCCC_LULUCF'], \
                             displayname_err_master['UNFCCC_LULUCF'], \
                             'MS-NRT', \
                             'rivers_lakes_reservoirs_ULB', \
                             displayname_master['CSR-COMBINED'], \
                             displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                             displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
                         ]
            
            self.output_file_end="_FCO2land_2019_v2.png" 
            edgec_master['MS-NRT']=facec_master['MS-NRT']
            
            # A couple of these plots will be displayed as bars instead of symbols
            lplot_errorbar_master["EUROCOM_ALL"]=True
            lplot_errorbar_master["GCP_ALL"]=True
            lplot_errorbar_master["CSR-COMBINED"]=True
            lwhiskerbars_master["CSR-COMBINED"]=True
            
            # And to correct some of the plots.
            master_datasets["GCP_ALL"].lcorrect_inversion=True
            master_datasets["CSR-COMBINED"].lcorrect_inversion=True
            master_datasets["EUROCOM_ALL"].lcorrect_inversion=True
            
        else:
            print("I do not understand which simulation this is:")
            print(self.graphname)
            sys.exit(1)
        #endif

        


        # Given the datsets we have selected, we are going to create a list of their parameters
        self.dataset_parameters=[]
        for simname in self.desired_simulations:
            self.dataset_parameters.append(master_datasets[simname])
        #endfor


        # Run some simple checks to make sure we don't crash later.
        for simname in self.desired_simulations:
            if not mpl.colors.is_color_like(master_datasets[simname].edgec):
                print("Do not recognize edge color {} for simulation {}.".format(master_datasets[simname].edgec,simname))
                sys.exit(1)
            #endif
            if not mpl.colors.is_color_like(master_datasets[simname].facec):
                print("Do not recognize face color {} for simulation {}.".format(master_datasets[simname].facec,simname))
                sys.exit(1)
            #endif
            if not mpl.colors.is_color_like(master_datasets[simname].uncert_color):
                print("Do not recognize uncert color {} for simulation {}.".format(master_datasets[simname].uncert_color,simname))
                sys.exit(1)
            #endif
        #endif


        #   return linclude_inventories,desired_inventories,desired_others,desired_verify,datasource,output_file_start,output_file_end
        #return desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displayname_err_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,overwrite_coeffs,overwrite_operations,desired_legend,flipdatasign_master,lcorrect_inversion_master,lplot_errorbar_master,lwhiskerbars_master,ldetrend,npanels,panel_ratios,igrid_plot,igrid_legend

    #enddef

    # Check to see if any of the datasets are inversions in need of correction
    def need_inversion_correction(self):

        lcorrect=False
        for isim,simname in enumerate(self.desired_simulations):
            if self.dataset_parameters[isim].lcorrect_inversion:
                lcorrect=True
            #endif
        #endfor

        return lcorrect

    #endif

    # We need these values fairly often
    def create_displayname_list(self):
        displayname=[]
        for isim,simname in enumerate(self.desired_simulations):
            displayname.append(self.dataset_parameters[isim].displayname)
        #endfor
        return displayname
    #enddef
    
    # Need to know how many inventory datasets we have
    def count_inventories(self):
        ninvs=0
        for isim,simname in enumerate(self.desired_simulations):
            if self.dataset_parameters[isim].simtype == "INVENTORY":
                ninvs=ninvs+1
        #endfor
        return ninvs
    #enddef

#endclass

