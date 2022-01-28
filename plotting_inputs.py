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
import sys,traceback

# These are my own that I have created locally
from country_subroutines import get_countries_and_regions_from_cr_dict,get_country_region_data,get_country_codes_for_netCDF_file,convert_names_and_codes

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
    def __init__(self, simname,full_filename,simtype,variable,plotmarker,facec,displayname=None,flipdatasign=None,lignore_for_range=None,lcheck_for_mean_overlap=None):
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

        self.displayname_err=self.displayname

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

        # If true, the dataset will be ignored when calculating the
        # simulation data range for mean plotting offsets.  Typically
        # areas, and emissions that are not included on the main chart
        # should be True.
        if lignore_for_range:
            self.lignore_for_range=lignore_for_range
        else:
            self.lignore_for_range=False
        #endif

        # If true, when plotting the mean values on a chart, we will check
        # to see if this symbol overlaps with any others.  If so, we will
        # offset the value on the x-axis by a little so that the symbol
        # will still be seen.  This only makes sense for those datasets
        # with a symbol, not those datasets with a horizontal line depicting
        # the mean.
        if lcheck_for_mean_overlap:
            self.lcheck_for_mean_overlap=lcheck_for_mean_overlap
        else:
            self.lcheck_for_mean_overlap=False
        #endif

        # For some types of plots, having lines makes it easier to see.
        # But in general we don't want them
        self.plot_lines=False
        self.linestyle="solid"

    #enddef
#endclass

class simulation_parameters():
    def __init__(self, parser):

        self.possible_graphs=["test", "luc_full", "sectorplot_full", "forestremain_2019", "forestremain_2021", "grasslandremain_2019", "grasslandremain_2021", "croplandremain_2019", "croplandremain_2021", "topdownandinventories_2019","topdownandinventories_2021","biofuels","inversions_verify","lulucf","lulucf_full","topdownlulucf_2019","topdownlulucfbar_2019","topdownlulucf_2021","topdownlulucfbar_2021","verifybu","verifybu_detrend","fluxcom","lucf_full","lulucftrendy_2019","lulucftrendy_2021","unfccclulucfbar_2019","unfccclulucfbar_2021","all_orchidee","gcp_inversions_corrected","eurocominversions","eurocominversionsv2","eurocomcomparison","epic_comparison","lulucf_msnrt","orc_trendy","faostat2021","faolulucfcomparison","fao_crp_grs","fao_for","unfccc_fao","unfccc_fao_trendy","emission_factors","unfccc_woodharvest","d6.2","unfccc_forest_test","unfccclulucfcomparison","unfcccflcomparison","unfcccclcomparison","unfcccglcomparison","orchidees3comparison","trendyv9_all","trendyv9_removed","csr_inversions_comparison","trendyv9_gcp","trendy_gcp","trendyv7_all","trendyv7_removed","trendyv10_all","trendyv10_removed","trendycomparison","gcp2019_all","gcp2020_all","gcpinversion2021","gcpcomparison","gcp_trendy","trendyv10_gcp2021_all","trendyv10_gcp2021","crops_fao_epic","grassland_all","bookkeeping","epic_test_rh","epic_test_npp","epic_test_fharvest","epic_test_leech","trendyv7_common","trendyv9_common","trendyv10_common","trendycommon","cbm","gcpcommon","cams","ctracker","jena_global","roxana","roxanawater","efiscencomparison","regionalinversions","lumiainversions","coco2","unfcccuncert","camseez"]
        self.possible_true_values=["true","t","yes","y"]

        parser.add_argument('--graphname', dest='graphname', action='store',required=True, choices=self.possible_graphs, help='the type of graph that you wish to plot')
        
        parser.add_argument('--plot_all_countries', dest='plot_all_countries', action='store',default="False",help='if TRUE, we will create plots for every country and region that we can.  Otherwise, we only plot for what is hard-coded.')

        parser.add_argument('--plot_meangraph', dest='lplot_meangraph', action='store',default=False,help='if TRUE, we will create additional plots of the timeseries means for every country and region that we can.  The filename is the same, except preceded by MeanBar.')

        parser.add_argument('--country_scope', dest='country_scope', action='store',default="Master",choices=["EU","Global","Africa","Master"],help='gives the country axis in the input files.  EU covers Europe, Global covers Europe with some other, and Africa covers Africa.  Master is a collection of everything made with a different script from the previous files.')


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

        self.country_scope=args.country_scope
        self.country_region_list=get_country_codes_for_netCDF_file(flag=self.country_scope)

        self.ncountries=len(self.country_region_list)
        print("Assuming the following input countries and regions in the files (total of {}): ".format(self.ncountries),self.country_region_list)



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
        # purposes.  Notice that the itest_sim is for the dataset, and
        # itest_plot is for the country/region being printed.
        self.ltest_data=True
        self.itest_sim=0
        self.itest_plot=0
        
        # Creates a horizontal line across the graph at zero.
        self.lprintzero=True
        
        # Make the Y-ranges on all the plots identical, selecting the ranges based
        # on the data.
        self.lharmonize_y=False
        
        # Make the Y-ranges on all the plots identical, imposing a range.
        # I think it's best to set this to False here, and then
        # flip it to True for certain plots.
        self.lexternal_y=False
        self.ymin_external=-800.0
        self.ymax_external=700.0
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
            # 32 years was fine before we started having data in 2020.  With
            # that and the means, the plot is now too full.  So try 33 years.
            #self.ndesiredyears=32 # use a couple extra years for padding on the right hand side
            self.ndesiredyears=34 # use a couple extra years for padding on the right hand side
            self.allyears=1990+np.arange(self.ndesiredyears)  ###1990-2023,ndesiredyears years. 
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
#            self.xplot_max=2022.5
            # Using a couple extra years since we had to elongate our timeseries.
            self.xplot_max=2024.5
        else:
            self.xplot_min=allyears[0]-0.5
            self.xplot_max=allyears[-1]+0.5
        #endif


    #enddef

    def define_country_parameters(self):

        self.all_regions_countries=get_country_codes_for_netCDF_file(flag=self.country_scope)
        
        # This gives the full country name as a function of the ISO-3166 code
        country_region_data=get_country_region_data()
        self.countrynames=get_countries_and_regions_from_cr_dict(country_region_data)
        
        # Only create plots for these countries/regions
        if not self.plot_all_countries:
            
            if self.country_scope == "Global":
                self.desired_plots=["CHN", "USA", "E28", 'FRA' ,'DEU']
            elif self.country_scope == "EU":
                self.desired_plots=['E28','FRA','DEU']
            elif self.country_scope == "Africa":
                self.desired_plots=['COD','AFR','GAB','ZAA']
            elif self.country_scope == "Master":
                self.desired_plots=["E28", "FRA", "USA", 'AFR','WLD']
                self.desired_plots=["E28", "FRA", "DEU", 'NLD','Ireland']

                # Special countries outside of Europe for COCO2
                self.desired_plots=["E28", "IDN", "COD", 'BRA','CAN','MMR','PER','VEN','COL','BOL','PRY','CHN','MNG','IND','ZAF']
                #self.desired_plots=["E28", "United Kingdom", "E27"]

                # This is for Roxana
                #self.desired_plots=["E28","Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom","MDA","UKR","BLR","CHE","NOR","WEE","CEE","NOE","SOZ","EAE"]
#                self.desired_plots=["E28","Austria","Belgium","Bulgaria","Croatia","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom","MDA","UKR","BLR"]

#                self.desired_plots=["Cyprus"]

                #self.desired_plots=["DEU", "E28", 'FRA', 'WLD']
            #endif

            self.desired_plots=convert_names_and_codes(self.desired_plots,"codes")

        else:
            self.desired_plots=self.all_regions_countries
        #endif
        print("Plotting the following countries/regions: ",self.desired_plots)
        
        # Sometimes I want to print debug information for a country.
        self.debug_country="E28"
        self.debug_country_index=self.all_regions_countries.index(self.debug_country)

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
        # Try only two panels.
#        self.npanels=3
#        self.panel_ratios=[2.7,1,1]
#        self.igrid_legend=2
#Using a total height of:  10.962962962962962 [1.0, 0.37037037037037035]

        self.npanels=2
        self.panel_ratios=[1.0,1.0/2.7]
        self.igrid_legend=1

        self.igrid_plot=0
        
        # Do not apply Normalization to Zero Mean and Unit of Energy (Z-normalization)
        # to every timeseries 
        self.ldetrend=False
        
        self.overwrite_simulations={}
        self.overwrite_coeffs={}
        self.overwrite_operations={}
        self.desired_legend=[]
        
        master_datasets={}

        # Some of these datasets have global version, i.e. 95 countries instead
        # of 79.  We need to figure out a way to do this so that it works
        # for every dataset and every possible mask file that we use.  I guess
        # templates are the best way.

        # I wrote a different script to look for every CountryTot file in a 
        # directory, pool together all the datasets for every variable, and
        # then create a new file with them all.  We can read in that file
        # here.  If no country is present, it just gets a NaN.  This was
        # needed to compare old version of spreadsheet files that I could not
        # easily make new country total files for with updated regions.

        ######
        input_filename={}        
        

        # These are done in a regular manner

        # Real database?  Or test database?
        database_dir="/home/surface8/mmcgrath/TEST_VERIFY_DATABASE/"
        #database_dir="/home/dods/verify/"
        
        
        #### ORCHIDEE file
        input_filename["ORCHIDEE-S3-V2019"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEE-S3-V2020"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V2_20200910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEEv2-S3-V2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V3_20211129_BASTRIKOV_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEEv3-S3-V2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-N-S3_LSCE_LAND_EU_1M_V3_20211129_BASTRIKOV_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        # With an update correcting a SWdown bug
        input_filename["ORCHIDEEv2-S3-V2021v2"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V3_20211209_BASTRIKOV_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEEv3-S3-V2021v2"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-N-S3_LSCE_LAND_EU_1M_V3_20211209_BASTRIKOV_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)

        input_filename["ORCHIDEE2019_GL-GL"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEE2019_GL-GL-RH"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEE2019_GL-GL-NPP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["ORCHIDEE2019_GL-GL-SOC"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        #### TRENDYv7
        input_filename["TrendyV7_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CommonTrendyv7FromCountryTot-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_ENSEMBLE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_AllTrendyv7FromCountryTot-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_ORCHIDEE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_CABLE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_CLASS"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CLASS-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_CLM5"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_DLEM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_ISAM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_JSBACH"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_JULES"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_JULES-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_LPJ"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_LPJ-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_LPX"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_LPX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_OCN"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_ORCHIDEE-CNP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_ORCHIDEE-CNP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_SDGVM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV7_SURFEX"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_SURFEX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        #### TRENDYv9
        input_filename["TrendyV9_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_CommonTrendyv9FromCountryTot-S3_exeter_LAND_GL_1M_V1_20210706_McGrath_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ENSEMBLE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_AllTrendyv9FromCountryTot-S3_exeter_LAND_GL_1M_V1_20210706_McGrath_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ORCHIDEE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ORCHIDEEv3"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_ORCHIDEEv3-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ORCHIDEE-CNP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_ORCHIDEE-CNP-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_SDGVM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_YIBs"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_YIBs-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_JULES-ES"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_JULES-ES-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_IBIS"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_IBIS-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_LPJ"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_LPJ-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_DLEM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ISAM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_LPJ-GUESS"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_LPJ-GUESS-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_ISBA-CTRIP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_ISBA-CTRIP-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_LPX-Bern"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_LPX-Bern-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_VISIT"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_VISIT-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_CLASSIC"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_CLASSIC-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_CLM5"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_CABLE-POP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_OCN"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV9_JSBACH"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        #### TRENDYv10
        input_filename["TrendyV10_ENSEMBLE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_AllTrendyv10FromCountryTot-S3_exeter_LAND_GL_1M_V2_20211019_McGrath_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_CommonTrendyv10FromCountryTot-S3_exeter_LAND_GL_1M_V2_20211019_McGrath_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_ORCHIDEE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_ORCHIDEEv3"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_ORCHIDEEv3-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_CABLE-POP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_CLASSIC-N"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_CLASSIC-N-S3_exeter_LAND_GL_1M_Period-1970-2020_TRENDY-LAND-V10_SITCH_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_CLASSIC"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_CLASSIC-S3_exeter_LAND_GL_1M_Period-1970-2020_TRENDY-LAND-V10_SITCH_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_CLM5"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_DLEM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_ISAM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_ISBA-CTRIP"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_ISBA-CTRIP-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_JSBACH"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_JULES-ES"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_JULES-ES-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_LPJ-GUESS"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_LPJ-GUESS-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_LPJwsl"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_LPJwsl-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_LPX-Bern"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_LPX-Bern-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_OCN"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["TrendyV10_SDGVM"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V10/Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20201020_Sitch_Grid-mask05_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        # GCP CO2 2019
        input_filename["GCP2019_ALL"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_AllGCP2019Inversions_XXX_LAND_GL_1M_V1_20191020_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2019_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CommonGCP2019Inversions_XXX_LAND_GL_1M_V1_20191020_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2019_JENA"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_JENA-s76-4-3-2019_bgc-jena_LAND_GL_1M_V1_20191020_Christian_WPX_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2019_CTRACKER"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2019_wur_LAND_GL_1M_V1_20191020_Wouter_WPX_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2019_CAMS"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CAMS-V18-2-2019_lsce_LAND_GL_1M_V1_20191020_Chevallier_WPX_CountryTotWithEEZ{}.nc".format(self.country_scope)

        # GCP CO2 2020
        input_filename["GCP2020_ALL"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_AllGCP2020Inversions_XXX_LAND_GL_1M_V2_20201026_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_CommonGCP2020Inversions_XXX_LAND_GL_1M_V2_20201026_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_CAMS"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_CAMS-V19-1-2020_lsce_LAND_GL_1M_V1_20201020_Chevallier_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_CTRACKER"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2020_wur_LAND_GL_1M_V1_20201020_Wouter_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_JENA-s85"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_JENA-s85-2020_bgc-jena_LAND_GL_1M_V1_20201020_Christian_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_JENA-sEXT"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_JENA-sEXT-2020_bgc-jena_LAND_GL_1M_V1_20201020_Christian_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_NIES"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_NIES-NIWA-v2020_nies_LAND_GL_1M_V1_20201020_Yosuke_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2020_UoE"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2020/Tier3TD_CO2_LandFlux_UoE-v2020_ed_LAND_GL_1M_V1_20201020_Paul_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)

        # GCP CO2 2021
        input_filename["GCP2021_ALL"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_AllGCP2021Inversions_XXX_LAND_GL_1M_V3_20211026_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_NOCAMS"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_AllGCP2021InversionsNoCAMS_XXX_LAND_GL_1M_V3_20211026_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_COMMON"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_CommonGCP2021Inversions_XXX_LAND_GL_1M_V3_20211026_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_CAMS"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_CAMS-V20-2-2021_lsce_LAND_GL_1M_V1_20201020_Chevallier_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_CAMSnoEEZ"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_CAMS-V20-2-2021_lsce_LAND_GL_1M_V1_20201020_Chevallier_Grid-mask11_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
#        input_filename["GCP2021_CMS"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_CTRACKER"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2021_wur_LAND_GL_1M_V1_20201020_Wouter_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_JENA-s99"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_JENA-s99-2021_bgc-jena_LAND_GL_1M_V1_20201020_Christian_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_JENA-sEXT"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_JENA-sEXT-2021_bgc-jena_LAND_GL_1M_V1_20201020_Christian_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_NIES"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_NIES-NIWA-v2021_nies_LAND_GL_1M_V1_20201020_Yosuke_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["GCP2021_UoE"]=database_dir + "OTHER_PROJECTS/FCO2/Inversions-GCP2021/Tier3TD_CO2_LandFlux_UoE-v2021_ed_LAND_GL_1M_V1_20201020_Paul_Grid-mask11_CountryTotWithEEZ{}.nc".format(self.country_scope)


        ### EPIC
        input_filename["EPIC2019_NBP_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2019_RH_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2019_FHARVEST_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2019_LEECH_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2019_NPP_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_NBP_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_RH_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_FHARVEST_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_LEECH_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_NPP_CRP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        # Grasslands
        input_filename["EPIC2021_NBP_GRS"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_EPIC-S1_IIASA_GRS_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_RH_GRS"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_EPIC-S1_IIASA_GRS_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_FHARVEST_GRS"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_EPIC-S1_IIASA_GRS_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_LEECH_GRS"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_EPIC-S1_IIASA_GRS_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["EPIC2021_NPP_GRS"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_EPIC-S1_IIASA_GRS_EU_1M_V3_20211026_BALKOVIC_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)

        ####### ECOSSE
        input_filename["ECOSSE2019_CL-CL"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE2019_CL-CL_0825"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200825_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE2019_CL-CL_RH"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE2019_CL-CL_NPP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE2019_CL-CL_FHARVEST"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE2019_CL-CL_us"]="/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_swheat_co2_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        # Grasslands
        input_filename["ECOSSE2019_GL-GL-lim"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-lim-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE_GL-GL-RH"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-lim-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE_GL-GL-NPP"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-lim-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE_GL-GL-SOC"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-lim-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)

        input_filename["ECOSSE_GL-GL-nolim"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-nolim-S1_UAbdn_CRP_EU_1M_V1_20200923_KUHNERT_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["ECOSSE_GL-GL_us"]="/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_gra_co2_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        ### FAO
        # Note that for 2019...would need to rerun the processing script
        # to create CountryTot files for other regions
        # This file is wrong.
        input_filename["FAO2019"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        # 2020 and 2021 should be a little more flexible.  Notice they should
        # also be identical!  I downloaded and processed them almost a year
        # apart.  The formatting had changed, but apparently not the data.
        
        input_filename["FAO2021"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V2_20211019_MCGRATH_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        #input_filename["FAO2021"]="/home/orchidee03/mmcgrath/TEST_DATABASE/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V2_20211019_MCGRATH_WPX_CountryTotWithOutEEZAllCountriesRegions.nc"

        ####### UNFCCC
        input_filename["UNFCCC2019_GL-GL"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["UNFCCC2020_FL-FL"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["UNFCCC2020_LULUCF"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_CountryTotWithEEZ{}.nc".format(self.country_scope)

        input_filename["UNFCCC2021_LULUCF"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V3_20220124_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        ####### Bookkeeping models
        input_filename["BLUE2019"]=database_dir + "OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["H&N2019"]=database_dir + "OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["H&N2021"]=database_dir + "OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V2_20211101_PONGRATZ_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        ##
        input_filename["BLUE2021_VERIFY"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_LandFlux_BLUE-2021_bgc-jena_LAND_GL_1M_V3_20211014_Pongratz_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        input_filename["BLUE2021_GCP"]=database_dir + "OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-GCB-2021_bgc-jena_LAND_GL_1M_V3_20211014_Pongratz_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope)

        ####### CSR
        input_filename["CSR-COMBINED-2020"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_AllJENA_bgc-jena_LAND_GL_1M_V2_20210522_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)

        ####### EUROCOM
        input_filename["EUROCOM_ALL_2020"]=database_dir + "OTHER_PROJECTS/FCO2/EUROCOM_UPDATE/Tier3TD_CO2_LandFlux_AllEUROCOMInversions_XXX_LAND_GL_1M_V2_20210914_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope)

        ####### LUMIA
        input_filename["LUMIA-COMBINED-v2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_LUMIA-AllInversions-V2021_nateko_LAND_Europe_1M_Period-2006-2020_INVCO2-VERIFY-V2021_MCGRATH_Grid-mask05_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["LUMIA-REF-v2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_LUMIA-REF-V2021_nateko_LAND_Europe_1M_Period-2006-2020_INVCO2-VERIFY-V2021_MONTEIL_Grid-mask05_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["LUMIA-Cor200km-v2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_LUMIA-Cor200km-V2021_nateko_LAND_Europe_1M_Period-2006-2020_INVCO2-VERIFY-V2021_MONTEIL_Grid-mask05_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["LUMIA-CoreSites-v2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_LUMIA-CoreSites-V2021_nateko_LAND_Europe_1M_Period-2006-2020_INVCO2-VERIFY-V2021_MONTEIL_Grid-mask05_CountryTotWithEEZ{}.nc".format(self.country_scope)
        input_filename["LUMIA-AlterBG-v2021"]=database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_LUMIA-AlterBG-V2021_nateko_LAND_Europe_1M_Period-2019-2020_INVCO2-VERIFY-V2021_MONTEIL_Grid-mask05_CountryTotWithEEZ{}.nc".format(self.country_scope)


        # For these, the filenames are in an irregular format because they are old
        # some stupid initialization.  Will likely be incorrect if you try
        # to use these without one of the country_scope keywords below.  Will 
        # try to phase this out.
        input_filename["UNFCCC2019_LULUCF"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope)
        master_datasets["UNFCCC2019_LULUCF"]=dataset_parameters( "UNFCCC2019_LULUCF", input_filename["UNFCCC2019_LULUCF"], "INVENTORY", "FCO2_NBP", "_", "green",displayname="UNFCCC LULUCF NGHGI (2019)")
        




        if self.country_scope == "Global":
            input_filename["UNFCCC2019_LULUCF"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_AllFluxes_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20201221_PETRESCU_WP1_CountryTotWithOutEEZGlobal.nc"
            master_datasets["UNFCCC2019_LULUCF"]=dataset_parameters( "UNFCCC2019_LULUCF", input_filename["UNFCCC2019_LULUCF"], "INVENTORY_NOERR", "FCO2_NBP", "_", "green",displayname="UNFCCC LULUCF NGHGI (2019)")

            input_filename["FAO2019"]="/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V2_20201221_PETRASCU_WPX_CountryTotWithOutEEZGlobal.nc"
            ##

        elif self.country_scope == "EU":
#            input_filename["UNFCCC2019_LULUCF"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc"
            master_datasets["UNFCCC2019_LULUCF"]=dataset_parameters( "UNFCCC2019_LULUCF", input_filename["UNFCCC2019_LULUCF"], "INVENTORY", "FCO2_NBP", "_", "green",displayname="UNFCCC LULUCF NGHGI (2019)")

            input_filename["FAO2019"]=database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc"

#            input_filename["BLUE2019"]=database_dir + "OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithOutEEZ.nc"

        ########
        elif self.country_scope == "Africa":

            # Not yet sure all of these are created.  I just copied the
            # files from the previous section and added the directory
            # where the Africa files are stored.
#            input_filename["UNFCCC2019_LULUCF"]="/home/orchidee03/mmcgrath/MOUNIA/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc"
            master_datasets["UNFCCC2019_LULUCF"]=dataset_parameters( "UNFCCC2019_LULUCF", input_filename["UNFCCC2019_LULUCF"], "INVENTORY", "FCO2_NBP", "_", "green",displayname="UNFCCC LULUCF NGHGI (2019)")

            input_filename["FAO2019"]="/home/orchidee03/mmcgrath/MOUNIA/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc"

            
#            input_filename["BLUE2019"]="/home/orchidee03/mmcgrath/MOUNIA/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithOutEEZ.nc"
            # Keep this here because it's a different directory
            #input_filename["TrendyV7_ENSEMBLE"]="/home/orchidee03/mmcgrath/MOUNIA/FCO2/Tier3BUPB_CO2_LandFlux_AllTrendyMedianMinMax-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTotWithOutEEZAfrica.nc"
            # This file is the min/max of every 2D file, and then aggregated
            #input_filename["TrendyV9_ENSEMBLE"]=database_dir + "OTHER_PROJECTS/FCO2/TrendyLand-V9/Tier3BUPB_CO2_LandFlux_AllTrendyV9-S3_exeter_LAND_GL_1M_V2_20210702_McGrath_WP3_CountryTotWithOutEEZEU.nc"
            # This file is the min/max of the files after they have been
            # aggregated into country totals
#            input_filename["TrendyV9_ENSEMBLE"]="/home/orchidee03/mmcgrath/MOUNIA/FCO2/Tier3BUPB_CO2_LandFlux_AllTrendyFromCountryTot-S3_exeter_LAND_GL_1M_V1_20210706_McGrath_Grid-mask05_CountryTotWithOutEEZAfrica.nc"
            input_filename["GCP2019_ALL"]="/home/orchidee03/mmcgrath/MOUNIA/FCO2/Tier3TD_CO2_LandFlux_AllGCPInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZAfrica.nc"
        #endif




        master_datasets["UNFCCC_totincLULUCF"]=dataset_parameters( "UNFCCC_totincLULUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_TotEmisIncLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "black")
        master_datasets["UNFCCC_totexcLULUCF"]=dataset_parameters( "UNFCCC_totexcLULUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_TotEmisExcLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "red")


        ### TRENDY V7
        master_datasets["TrendyV7_ENSEMBLE"]=dataset_parameters( "TrendyV7_ENSEMBLE", input_filename["TrendyV7_ENSEMBLE"], "MINMAX", "FCO2_NBP", "D", "grey")
        master_datasets["TrendyV7_COMMON"]=dataset_parameters( "TrendyV7_COMMON", input_filename["TrendyV7_COMMON"], "MINMAX", "FCO2_NBP", "D", "grey")
        master_datasets["TrendyV7_CABLE"]=dataset_parameters( "TrendyV7_CABLE", input_filename["TrendyV7_CABLE"], "TRENDY", "FCO2_NBP", "D", "red")
        master_datasets["TrendyV7_CLASS"]=dataset_parameters( "TrendyV7_CLASS", input_filename["TrendyV7_CLASS"], "TRENDY", "FCO2_NBP", "D", "green")
        master_datasets["TrendyV7_CLM5"]=dataset_parameters( "TrendyV7_CLM5", input_filename["TrendyV7_CLM5"], "TRENDY", "FCO2_NBP", "D", "blue")
        master_datasets["TrendyV7_DLEM"]=dataset_parameters( "TrendyV7_DLEM", input_filename["TrendyV7_DLEM"], "TRENDY", "FCO2_NBP", "D", "violet")
        master_datasets["TrendyV7_ISAM"]=dataset_parameters( "TrendyV7_ISAM", input_filename["TrendyV7_ISAM"], "TRENDY", "FCO2_NBP", "D", "yellow")
        master_datasets["TrendyV7_JSBACH"]=dataset_parameters( "TrendyV7_JSBACH", input_filename["TrendyV7_JSBACH"], "TRENDY", "FCO2_NBP", "D", "orange")
        master_datasets["TrendyV7_JULES"]=dataset_parameters( "TrendyV7_JULES", input_filename["TrendyV7_JULES"], "TRENDY", "FCO2_NBP", "D", "brown")
        master_datasets["TrendyV7_LPJ"]=dataset_parameters( "TrendyV7_LPJ", input_filename["TrendyV7_LPJ"], "TRENDY", "FCO2_NBP", "D", "gold")
        master_datasets["TrendyV7_LPX"]=dataset_parameters( "TrendyV7_LPX", input_filename["TrendyV7_LPX"], "TRENDY", "FCO2_NBP", "D", "gray")
        master_datasets["TrendyV7_OCN"]=dataset_parameters( "TrendyV7_OCN", input_filename["TrendyV7_OCN"], "TRENDY", "FCO2_NBP", "D", "limegreen")
        master_datasets["TrendyV7_ORCHIDEE-CNP"]=dataset_parameters( "TrendyV7_ORCHIDEE-CNP", input_filename["TrendyV7_ORCHIDEE-CNP"], "TRENDY", "FCO2_NBP", "D", "yellowgreen")
        master_datasets["TrendyV7_ORCHIDEE"]=dataset_parameters( "TrendyV7_ORCHIDEE", input_filename["TrendyV7_ORCHIDEE"], "TRENDY", "FCO2_NBP", "D", "none")
        master_datasets["TrendyV7_SDGVM"]=dataset_parameters( "TrendyV7_SDGVM", input_filename["TrendyV7_SDGVM"], "TRENDY", "FCO2_NBP", "D", "magenta")
        master_datasets["TrendyV7_SURFEX"]=dataset_parameters( "TrendyV7_SURFEX", input_filename["TrendyV7_SURFEX"], "TRENDY", "FCO2_NBP", "D", "pink")
        ### Trendy v9
        # These are a set of five colors recommended by ColorBrewer
        cb_green=(27.0/256.0,158.0/256.0,119.0/256.0)
        cb_orange=(217/256.0,95/256.0,2/256.0)
        cb_purple=(117/256.0,112/256.0,179/256.0)
        cb_rose=(231/256.0,41/256.0,138/256.0)
        cb_lightgreen=(102/256.0,166/256.0,30/256.0)
        master_datasets["TrendyV9_COMMON"]=dataset_parameters( "TrendyV9_COMMON", input_filename["TrendyV9_COMMON"], "MINMAX", "FCO2_NBP", "D", "silver")
        master_datasets["TrendyV9_ENSEMBLE"]=dataset_parameters( "TrendyV9_ENSEMBLE", input_filename["TrendyV9_ENSEMBLE"], "MINMAX", "FCO2_NBP", "D", "grey")
        master_datasets["TrendyV9_ORCHIDEE-CNP"]=dataset_parameters( "TrendyV9_ORCHIDEE-CNP", input_filename["TrendyV9_ORCHIDEE-CNP"], "TRENDY", "FCO2_NBP", "^", cb_green)
        master_datasets["TrendyV9_ORCHIDEE"]=dataset_parameters( "TrendyV9_ORCHIDEE", input_filename["TrendyV9_ORCHIDEE"], "TRENDY", "FCO2_NBP", "o", cb_green)
        master_datasets["TrendyV9_SDGVM"]=dataset_parameters( "TrendyV9_SDGVM", input_filename["TrendyV9_SDGVM"], "TRENDY", "FCO2_NBP", "D", cb_green)
        master_datasets["TrendyV9_YIBs"]=dataset_parameters( "TrendyV9_YIBs", input_filename["TrendyV9_YIBs"], "TRENDY", "FCO2_NBP", "P", cb_green)
        master_datasets["TrendyV9_JULES-ES"]=dataset_parameters( "TrendyV9_JULES-ES", input_filename["TrendyV9_JULES-ES"], "TRENDY", "FCO2_NBP", "^", cb_orange)
        master_datasets["TrendyV9_IBIS"]=dataset_parameters( "TrendyV9_IBIS", input_filename["TrendyV9_IBIS"], "TRENDY", "FCO2_NBP", "o", cb_orange)
        master_datasets["TrendyV9_LPJ"]=dataset_parameters( "TrendyV9_LPJ", input_filename["TrendyV9_LPJ"], "TRENDY", "FCO2_NBP", "D", cb_orange)
        master_datasets["TrendyV9_DLEM"]=dataset_parameters( "TrendyV9_DLEM", input_filename["TrendyV9_DLEM"], "TRENDY", "FCO2_NBP", "P", cb_orange)
        master_datasets["TrendyV9_ISAM"]=dataset_parameters( "TrendyV9_ISAM", input_filename["TrendyV9_ISAM"], "TRENDY", "FCO2_NBP", "^", cb_purple)
        master_datasets["TrendyV9_LPJ-GUESS"]=dataset_parameters( "TrendyV9_LPJ-GUESS", input_filename["TrendyV9_LPJ-GUESS"], "TRENDY", "FCO2_NBP", "o", cb_purple)
        master_datasets["TrendyV9_ISBA-CTRIP"]=dataset_parameters( "TrendyV9_ISBA-CTRIP", input_filename["TrendyV9_ISBA-CTRIP"], "TRENDY", "FCO2_NBP", "D", cb_purple)
        master_datasets["TrendyV9_LPX-Bern"]=dataset_parameters( "TrendyV9_LPX-Bern", input_filename["TrendyV9_LPX-Bern"], "TRENDY", "FCO2_NBP", "P", cb_purple)
        master_datasets["TrendyV9_VISIT"]=dataset_parameters( "TrendyV9_VISIT", input_filename["TrendyV9_VISIT"], "TRENDY", "FCO2_NBP", "^", cb_rose)
        master_datasets["TrendyV9_CLASSIC"]=dataset_parameters( "TrendyV9_CLASSIC", input_filename["TrendyV9_CLASSIC"], "TRENDY", "FCO2_NBP", "o", cb_rose)
        master_datasets["TrendyV9_ORCHIDEEv3"]=dataset_parameters( "TrendyV9_ORCHIDEEv3", input_filename["TrendyV9_ORCHIDEEv3"], "TRENDY", "FCO2_NBP", "D", cb_rose)
        master_datasets["TrendyV9_CLM5"]=dataset_parameters( "TrendyV9_CLM5", input_filename["TrendyV9_CLM5"], "TRENDY", "FCO2_NBP", "P", cb_rose)
        master_datasets["TrendyV9_CABLE-POP"]=dataset_parameters( "TrendyV9_CABLE-POP", input_filename["TrendyV9_CABLE-POP"], "TRENDY", "FCO2_NBP", "^", cb_lightgreen)
        master_datasets["TrendyV9_OCN"]=dataset_parameters( "TrendyV9_OCN", input_filename["TrendyV9_OCN"], "TRENDY", "FCO2_NBP", "o", cb_lightgreen)
        master_datasets["TrendyV9_JSBACH"]=dataset_parameters( "TrendyV9_JSBACH", input_filename["TrendyV9_JSBACH"], "TRENDY", "FCO2_NBP", "D", cb_lightgreen)

        ### Trendy v10.  Use the same colors as above and cycle them,
        # changing the symbols at every cycle.
        cb_green=(27.0/256.0,158.0/256.0,119.0/256.0)
        cb_orange=(217/256.0,95/256.0,2/256.0)
        cb_purple=(117/256.0,112/256.0,179/256.0)
        cb_rose=(231/256.0,41/256.0,138/256.0)
        cb_lightgreen=(102/256.0,166/256.0,30/256.0)
        master_datasets["TrendyV10_ENSEMBLE"]=dataset_parameters( "TrendyV10_ENSEMBLE", input_filename["TrendyV10_ENSEMBLE"], "MINMAX", "FCO2_NBP", "D", "grey")
        master_datasets["TrendyV10_COMMON"]=dataset_parameters( "TrendyV10_COMMON", input_filename["TrendyV10_COMMON"], "MINMAX", "FCO2_NBP", "D", "grey")

        master_datasets["TrendyV10_ORCHIDEEv3"]=dataset_parameters( "TrendyV10_ORCHIDEEv3", input_filename["TrendyV10_ORCHIDEEv3"], "TRENDY", "FCO2_NBP", "^", cb_green)
        master_datasets["TrendyV10_ORCHIDEE"]=dataset_parameters( "TrendyV10_ORCHIDEE", input_filename["TrendyV10_ORCHIDEE"], "TRENDY", "FCO2_NBP", "o", cb_green)
        master_datasets["TrendyV10_CABLE-POP"]=dataset_parameters( "TrendyV10_CABLE-POP", input_filename["TrendyV10_CABLE-POP"], "TRENDY", "FCO2_NBP", "D", cb_green)
        master_datasets["TrendyV10_CLASSIC-N"]=dataset_parameters( "TrendyV10_CLASSIC-N", input_filename["TrendyV10_CLASSIC-N"], "TRENDY", "FCO2_NBP", "*", cb_green)
        master_datasets["TrendyV10_CLASSIC"]=dataset_parameters( "TrendyV10_CLASSIC", input_filename["TrendyV10_CLASSIC"], "TRENDY", "FCO2_NBP", "^", cb_orange)
        master_datasets["TrendyV10_CLM5"]=dataset_parameters( "TrendyV10_CLM5", input_filename["TrendyV10_CLM5"], "TRENDY", "FCO2_NBP", "o", cb_orange)
        master_datasets["TrendyV10_DLEM"]=dataset_parameters( "TrendyV10_DLEM", input_filename["TrendyV10_DLEM"], "TRENDY", "FCO2_NBP", "D", cb_orange)
        master_datasets["TrendyV10_ISAM"]=dataset_parameters( "TrendyV10_ISAM", input_filename["TrendyV10_ISAM"], "TRENDY", "FCO2_NBP", "*", cb_orange)

        master_datasets["TrendyV10_ISBA-CTRIP"]=dataset_parameters( "TrendyV10_ISBA-CTRIP", input_filename["TrendyV10_ISBA-CTRIP"], "TRENDY", "FCO2_NBP", "^", cb_purple)
        master_datasets["TrendyV10_JSBACH"]=dataset_parameters( "TrendyV10_JSBACH", input_filename["TrendyV10_JSBACH"], "TRENDY", "FCO2_NBP", "o", cb_purple)
        master_datasets["TrendyV10_JULES-ES"]=dataset_parameters( "TrendyV10_JULES-ES", input_filename["TrendyV10_JULES-ES"], "TRENDY", "FCO2_NBP", "D", cb_purple)
        master_datasets["TrendyV10_LPJ-GUESS"]=dataset_parameters( "TrendyV10_LPJ-GUESS", input_filename["TrendyV10_LPJ-GUESS"], "TRENDY", "FCO2_NBP", "*", cb_purple)
        master_datasets["TrendyV10_LPJwsl"]=dataset_parameters( "TrendyV10_LPJwsl", input_filename["TrendyV10_LPJwsl"], "TRENDY", "FCO2_NBP", "^", cb_rose)
        master_datasets["TrendyV10_LPX-Bern"]=dataset_parameters( "TrendyV10_LPX-Bern", input_filename["TrendyV10_LPX-Bern"], "TRENDY", "FCO2_NBP", "o", cb_rose)
        master_datasets["TrendyV10_OCN"]=dataset_parameters( "TrendyV10_OCN", input_filename["TrendyV10_OCN"], "TRENDY", "FCO2_NBP", "D", cb_rose)
        master_datasets["TrendyV10_SDGVM"]=dataset_parameters( "TrendyV10_SDGVM", input_filename["TrendyV10_SDGVM"], "TRENDY", "FCO2_NBP", "*", cb_rose)

        ###

        master_datasets["ORCHIDEE_S0"]=dataset_parameters( "ORCHIDEE_S0", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S0_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP", "D", "magenta", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE_S1"]=dataset_parameters( "ORCHIDEE_S1", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S1_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE_S2"]=dataset_parameters( "ORCHIDEE_S2", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S2_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP", "D", "red", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE_S1_V2"]=dataset_parameters( "ORCHIDEE_S1_V2", "/home/orchidee03/mmcgrath/RUNDIR/CREATE_DRIVER_PLOTS/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S1_LSCE_LAND_EU_1M_V2_20200910_MCGRATH_WP3_CountryTotWithOutEEZEU.nc", "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE-S3-V2019"]=dataset_parameters( "ORCHIDEE-S3-V2019", input_filename["ORCHIDEE-S3-V2019"], "VERIFY_BU", "FCO2_NBP", "D", "dodgerblue", flipdatasign=True,lcheck_for_mean_overlap=True,displayname="ORCHIDEE")
        master_datasets["ORCHIDEE-S3-V2020"]=dataset_parameters( "ORCHIDEE2020", input_filename["ORCHIDEE-S3-V2020"], "VERIFY_BU", "FCO2_NBP", "D", "red", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEEv3-S3-V2021"]=dataset_parameters( "ORCHIDEEv3-S3-V2021", input_filename["ORCHIDEEv3-S3-V2021"], "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEEv2-S3-V2021"]=dataset_parameters( "ORCHIDEEv2-S3-V2021", input_filename["ORCHIDEEv2-S3-V2021"], "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEEv3-S3-V2021v2"]=dataset_parameters( "ORCHIDEEv3-S3-V2021v2", input_filename["ORCHIDEEv3-S3-V2021v2"], "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=False,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEEv2-S3-V2021v2"]=dataset_parameters( "ORCHIDEEv2-S3-V2021v2", input_filename["ORCHIDEEv2-S3-V2021v2"], "VERIFY_BU", "FCO2_NBP", "D", "green", flipdatasign=False,lcheck_for_mean_overlap=True)
#        master_datasets["ORCHIDEE-S3-V2019"]=dataset_parameters( "ORCHIDEE-S3-V2019", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "dodgerblue", flipdatasign=True,lcheck_for_mean_overlap=True)
#        master_datasets["ORCHIDEE-S3-V2020"]=dataset_parameters( "ORCHIDEE-S3-V2020", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V2_20200910_MCGRATH_WP3_CountryTotWithEEZEU.nc", "VERIFY_BU", "FCO2_NBP", "D", "dodgerblue", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE_RH"]=dataset_parameters( "ORCHIDEE_RH", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "rh", "D", "red")

        master_datasets["ORCHIDEE2019_GL-GL"]=dataset_parameters( "ORCHIDEE2019_GL-GL", input_filename["ORCHIDEE2019_GL-GL"], "VERIFY_BU", "FCO2_NBP_GRS", "D", "dodgerblue",flipdatasign=True)
        master_datasets["ORCHIDEE2019_GL-GL-RH"]=dataset_parameters( "ORCHIDEE2019_GL-GL", input_filename["ORCHIDEE2019_GL-GL-RH"], "VERIFY_BU", "FCO2_NBP_GRA", "D", "dodgerblue",flipdatasign=True)
        master_datasets["ORCHIDEE2019_GL-GL-NPP"]=dataset_parameters( "ORCHIDEE2019_GL-GL NPP", input_filename["ORCHIDEE2019_GL-GL-NPP"], "VERIFY_BU", "npp_grs", "D", "blue",flipdatasign=True)
        master_datasets["ORCHIDEE2019_GL-GL-SOC"]=dataset_parameters( "ORCHIDEE2019_GL-GL", input_filename["ORCHIDEE2019_GL-GL-SOC"], "VERIFY_BU", "FCO2_NBP_GRS", "D", "dodgerblue",flipdatasign=True)

        ### EPIC
        master_datasets["EPIC2019_NBP_CRP"]=dataset_parameters( "EPIC2019_NBP_CRP", input_filename["EPIC2019_NBP_CRP"], "VERIFY_BU", "FCO2_NBP_CRO", "o", "lightcoral",displayname="EPIC_CL")
        master_datasets["EPIC2019_RH_CRP"]=dataset_parameters( "EPIC2019_RH_CRP", input_filename["EPIC2019_RH_CRP"], "VERIFY_BU", "FCO2_RH_CRO", "o", "yellow")
        master_datasets["EPIC2019_FHARVEST_CRP"]=dataset_parameters( "EPIC2019_FHARVEST_CRP", input_filename["EPIC2019_FHARVEST_CRP"], "VERIFY_BU", "FCO2_FHARVEST_CRO", "^", "red")
        master_datasets["EPIC2019_LEECH_CRP"]=dataset_parameters( "EPIC2019_LEECH_CRP", input_filename["EPIC2019_LEECH_CRP"], "VERIFY_BU", "FCO2_CLCH_CRO", "P", "blue")
        master_datasets["EPIC2019_NPP_CRP"]=dataset_parameters( "EPIC2019_NPP_CRP", input_filename["EPIC2019_NPP_CRP"], "VERIFY_BU", "FCO2_NPP_CRO", "s", "green")
        master_datasets["EPIC2021_NBP_CRP"]=dataset_parameters( "EPIC2021_NBP_CRP", input_filename["EPIC2021_NBP_CRP"], "VERIFY_BU", "FCO2_NBP_CRP", "o", "lightcoral",displayname="EPICv2_CL")
        master_datasets["EPIC2021_RH_CRP"]=dataset_parameters( "EPIC2021_RH_CRP", input_filename["EPIC2021_RH_CRP"], "VERIFY_BU", "FCO2_RH_CRP", "X", "yellow")
        master_datasets["EPIC2021_FHARVEST_CRP"]=dataset_parameters( "EPIC2021_FHARVEST_CRP", input_filename["EPIC2021_FHARVEST_CRP"], "VERIFY_BU", "FCO2_HARVEST_CRP", "X", "red")
        master_datasets["EPIC2021_LEECH_CRP"]=dataset_parameters( "EPIC2021_LEECH_CRP", input_filename["EPIC2021_LEECH_CRP"], "VERIFY_BU", "FCO2_LEECH_CRP", "X", "blue")
        master_datasets["EPIC2021_NPP_CRP"]=dataset_parameters( "EPIC2021_NPP_CRP", input_filename["EPIC2021_NPP_CRP"], "VERIFY_BU", "FCO2_NPP_CRP", "X", "green")
        # Grasslands
        master_datasets["EPIC2021_NBP_GRS"]=dataset_parameters( "EPIC2021_NBP_GRS", input_filename["EPIC2021_NBP_GRS"], "VERIFY_BU", "FCO2_NBP_GRS", "P", "lightcoral",displayname="EPICv2_GL")
        master_datasets["EPIC2021_RH_GRS"]=dataset_parameters( "EPIC2021_RH_GRS", input_filename["EPIC2021_RH_GRS"], "VERIFY_BU", "FCO2_RH_GRS", "P", "yellow")
        master_datasets["EPIC2021_FHARVEST_GRS"]=dataset_parameters( "EPIC2021_FHARVEST_GRS", input_filename["EPIC2021_FHARVEST_GRS"], "VERIFY_BU", "FCO2_HARVEST_GRS", "P", "red")
        master_datasets["EPIC2021_LEECH_GRS"]=dataset_parameters( "EPIC2021_LEECH_GRS", input_filename["EPIC2021_LEECH_GRS"], "VERIFY_BU", "FCO2_LEECH_GRS", "P", "blue")
        master_datasets["EPIC2021_NPP_GRS"]=dataset_parameters( "EPIC2021_NPP_GRS", input_filename["EPIC2021_NPP_GRS"], "VERIFY_BU", "FCO2_NPP_GRS", "P", "green")
        
        ##
        master_datasets["CSR-COMBINED-2019"]=dataset_parameters( "CSR-COMBINED-2019", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_AllJENA_bgc-jena_LAND_GL_1M_V1_20200304_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope), "MINMAX", "FCO2_NBP", "s", "mediumblue")
        master_datasets["CSR-REG-100km"]=dataset_parameters( "CSR-REG-100km", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "khaki")
        master_datasets["CSR-REG-200km"]=dataset_parameters( "CSR-REG-200km", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-200km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "orange")
        master_datasets["CSR-REG-Core100km"]=dataset_parameters( "CSR-REG-Core100km", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-Core100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "darkorange")
        master_datasets["CSR-REG-Valid100km"]=dataset_parameters( "CSR-REG-Valid100km", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-Valid100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc", "VERIFY_TD", "FCO2_NBP", "P", "gold")
        master_datasets["CSR-COMBINED-2020"]=dataset_parameters( "CSR-COMBINED-2020", input_filename["CSR-COMBINED-2020"], "MINMAX", "FCO2_NBP", "s", "mediumblue")
        master_datasets["CSR-FluxcomCore-V2"]=dataset_parameters( "CSR-FluxcomCore-V2", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-FluxcomCore100km_bgc-jena_LAND_GL_1M_V2_20201215_Gerbig_WP3_CountryTotWithEEZEU.nc", "VERIFY_TD", "FCO2_NBP", "P", "khaki")
        master_datasets["CSR-FluxcomValid-V2"]=dataset_parameters( "CSR-FluxcomValid-V2", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-FluxcomValid100km_bgc-jena_LAND_GL_1M_V2_20201215_Gerbig_WP3_CountryTotWithEEZEU.nc", "VERIFY_TD", "FCO2_NBP", "P", "orange")
        master_datasets["CSR-VPRMCore-V2"]=dataset_parameters( "CSR-VPRMCore-V2", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-VPRMCore100km_bgc-jena_LAND_GL_1M_V2_20201215_Gerbig_WP3_CountryTotWithEEZEU.nc", "VERIFY_TD", "FCO2_NBP", "P", "darkorange")
        master_datasets["CSR-VPRMValid-V2"]=dataset_parameters( "CSR-VPRMValid-V2", database_dir + "VERIFY_OUTPUT/FCO2/Tier3TD_CO2_LandFlux_JENA-REG-VPRMValid100km_bgc-jena_LAND_GL_1M_V2_20201215_Gerbig_WP3_CountryTotWithEEZEU.nc", "VERIFY_TD", "FCO2_NBP", "P", "gold")

        ##
        master_datasets["BLUE2019"]=dataset_parameters( "BLUE2019", input_filename["BLUE2019"], "VERIFY_BU", "CD_A", "^", "tan",lcheck_for_mean_overlap=True,displayname="BLUE")
        master_datasets["BLUE2021_VERIFY"]=dataset_parameters( "BLUE2021_VERIFY", input_filename["BLUE2021_VERIFY"], "VERIFY_BU", "FCO2_LUTOT_FOR", "^", "tan",lcheck_for_mean_overlap=True,displayname="BLUEv2-VERIFY")
        master_datasets["BLUE2021_GCP"]=dataset_parameters( "BLUE2021_GCP", input_filename["BLUE2021_GCP"], "VERIFY_BU", "FCO2_LUTOT_FOR", "^", "gold",lcheck_for_mean_overlap=True,displayname="BLUEv2-GCP")
        master_datasets["H&N2019"]=dataset_parameters( "H&N2019", input_filename["H&N2019"], "NONVERIFY_BU", "FCO2_NBP_LUC", "^", "orange",lcheck_for_mean_overlap=True,displayname="H&N")
        master_datasets["H&N2021"]=dataset_parameters( "H&N2021", input_filename["H&N2021"], "NONVERIFY_BU", "FCO2_NBP_LUC", "^", "orange",lcheck_for_mean_overlap=True,displayname="H&Nv2")
        master_datasets["ORCHIDEE-MICT"]=dataset_parameters( "ORCHIDEE-MICT", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_LandUseChange_ORCHIDEEMICT-SX_LSCE_LAND_EU_1M_V1_20190925_YUE_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP", "D", "lightsteelblue", flipdatasign=True)
        master_datasets["FAOSTAT2019_FOR_TOT"]=dataset_parameters( "FAOSTAT2019_FOR_TOT", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_LUTOT_FOR", "o", "darkviolet")
        master_datasets["FAOSTAT2019_FOR_REM"]=dataset_parameters( "FAOSTAT2019_FOR_REM", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_NBP_FOR", "o", "darkviolet")
        master_datasets["FAOSTAT2019_FOR_CON"]=dataset_parameters( "FAOSTAT2019_FOR_CON", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_LUC_FOR", "o", "darkviolet")
        master_datasets["FAOSTAT2019_CRP"]=dataset_parameters( "FAOSTAT2019_CRP", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_SOIL_CRO", "P", "darkviolet")
        master_datasets["FAOSTAT2019_GRS"]=dataset_parameters( "FAOSTAT2019_GRS", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_SOIL_GRA", "X", "darkviolet")

        # FOR_TOT is the total remain + convert
        master_datasets["FAOSTAT2021_FOR_TOT"]=dataset_parameters( "FAOSTAT2021_FOR_TOT", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_NBP_FOR_TOT", "o", "darkviolet",displayname="FAOSTATv2_FL")
        master_datasets["FAOSTAT2021_FL-FL"]=dataset_parameters( "FAOSTAT2021_FOR_TOT", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet",displayname="FAOSTATv2_FL-FL")
        master_datasets["FAOSTAT2021_FOR_CON"]=dataset_parameters( "FAOSTAT2021_FOR_CON", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_LUC_FOR", "o", "darkviolet",displayname="FAOSTATv2_FL-con")
        master_datasets["FAOSTAT2021_CL-CL"]=dataset_parameters( "FAOSTAT2021_CL-CL", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_SOIL_CRO", "P", "darkviolet",displayname="FAOSTATv2_CL-CL")
        master_datasets["FAOSTAT2021_GL-GL"]=dataset_parameters( "FAOSTAT2021_GRS", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_SOIL_GRA", "X", "darkviolet",displayname="FAOSTATv2_GL-GL")

        ##
        master_datasets["EUROCOM_Carboscope"]=dataset_parameters( "EUROCOM_Carboscope", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CarboScopeRegional_bgc-jena_LAND_EU_1M_V1_20191020_Gerbig_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "khaki")
        master_datasets["EUROCOM_Flexinvert"]=dataset_parameters( "EUROCOM_Flexinvert", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_FLEXINVERT_nilu_LAND_EU_1M_V1_20191020_Thompson_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "orange")
        master_datasets["EUROCOM_Lumia"]=dataset_parameters( "EUROCOM_Lumia", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_LUMIA-ORC_nateko_LAND_EU_1M_V1_20191020_Monteil_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "darkorange")
        master_datasets["EUROCOM_Chimere"]=dataset_parameters( "EUROCOM_Chimere", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CHIMERE-ORC_lsce_LAND_EU_1M_V1_20191020_Broquet_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "gold")
        master_datasets["EUROCOM_CTE"]=dataset_parameters( "EUROCOM_CTE", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CTE_wur_LAND_EU_1M_V1_20191020_Ingrid_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "red")
        master_datasets["EUROCOM_EnKF"]=dataset_parameters( "EUROCOM_EnKF", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_EnKF-RAMS_vu_LAND_EU_1M_V1_20191020_Antoon_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "darkred")
        master_datasets["EUROCOM_NAME"]=dataset_parameters( "EUROCOM_NAME", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_NAME-HB_bristol_LAND_EU_1M_V1_20191020_White_Grid-eurocom_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "magenta")
        master_datasets["EUROCOM_ALL_2019"]=dataset_parameters( "EUROCOM_ALL_2019", database_dir + "OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_AllEUROCOMInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope), "MINMAX", "FCO2_NBP", "P", "blue")
        ##
        master_datasets["EUROCOM_ALL_2020"]=dataset_parameters( "EUROCOM_ALL_2020", input_filename["EUROCOM_ALL_2020"], "MINMAX", "FCO2_NBP", "P", "blue",flipdatasign=True)
        master_datasets["EUROCOM_Flexinvert_V2"]=dataset_parameters( "EUROCOM_Flexinvert_V2", "/home/orchidee03/mmcgrath/RUNDIR/SPATIAL_PLOTS/SAVED/EUROCOMFLEXINVERTcore-NEE_2009-01-01_2018-12-31_0f5_33.0000Nx73.0000Nx15.0000Wx35.0000E_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "P", "orange",flipdatasign=True)
        master_datasets["EUROCOM_Lumia_V2"]=dataset_parameters( "EUROCOM_Lumia_V2", "/home/orchidee03/mmcgrath/RUNDIR/SPATIAL_PLOTS/SAVED/EUROCOMLUMIAall-NEE_2009-01-01_2018-12-31_0f5_33.0000Nx73.0000Nx15.0000Wx35.0000E_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "x", "darkorange",flipdatasign=True)
        master_datasets["EUROCOM_PYVAR_V2"]=dataset_parameters( "EUROCOM_PYVAR_V2", "/home/orchidee03/mmcgrath/RUNDIR/SPATIAL_PLOTS/SAVED/EUROCOMPYVARall-NEE_2009-01-01_2018-12-31_0f5_33.0000Nx73.0000Nx15.0000Wx35.0000E_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "o", "gold",flipdatasign=True)
        master_datasets["EUROCOM_CSR_V2"]=dataset_parameters( "EUROCOM_CSR_V2", "/home/orchidee03/mmcgrath/RUNDIR/SPATIAL_PLOTS/SAVED/CSR-NEE_2009-01-01_2018-12-31_0f5_33.0000Nx73.0000Nx15.0000Wx35.0000E_CountryTotWithEEZ{}.nc".format(self.country_scope), "REGIONAL_TD", "FCO2_NBP", "s", "red",flipdatasign=True)

        # LUMIA inversions
        master_datasets["LUMIA-COMBINED-v2021"]=dataset_parameters( "LUMIA-COMBINED-v2021", input_filename["LUMIA-COMBINED-v2021"], "MINMAX", "FCO2_NBP", "s", "red",flipdatasign=False)
        master_datasets["LUMIA-REF-v2021"]=dataset_parameters( "LUMIA-REF-v2021", input_filename["LUMIA-REF-v2021"], "REGIONAL_TD", "FCO2_NBP", "P", "orange",flipdatasign=False)
        master_datasets["LUMIA-Cor200km-v2021"]=dataset_parameters( "LUMIA-Cor200km-v2021", input_filename["LUMIA-Cor200km-v2021"], "REGIONAL_TD", "FCO2_NBP", "x", "darkorange",flipdatasign=False)
        master_datasets["LUMIA-CoreSites-v2021"]=dataset_parameters( "LUMIA-CoreSites-v2021", input_filename["LUMIA-CoreSites-v2021"], "REGIONAL_TD", "FCO2_NBP", "o", "gold",flipdatasign=False)
        master_datasets["LUMIA-AlterBG-v2021"]=dataset_parameters( "LUMIA-AlterBG-v2021", input_filename["LUMIA-AlterBG-v2021"], "REGIONAL_TD", "FCO2_NBP", "s", "red",flipdatasign=False)




        # All the ECOSSE variables
        master_datasets["ECOSSE2019_CL-CL"]=dataset_parameters( "ECOSSE2019_CL-CL", input_filename["ECOSSE2019_CL-CL"], "VERIFY_BU", "FCO2_NBP_CRO", "o", "darkred")
        master_datasets["ECOSSE2019_CL-CL_0825"]=dataset_parameters( "ECOSSE2019_CL-CL_0825", input_filename["ECOSSE2019_CL-CL_0825"], "VERIFY_BU", "FCO2_NBP_CRO", "o", "blue")
        master_datasets["ECOSSE2019_CL-CL_RH"]=dataset_parameters( "ECOSSE2019_CL-CL_RH", input_filename["ECOSSE2019_CL-CL_RH"], "VERIFY_BU", "FCO2_RH_CRO", "o", "green")
        master_datasets["ECOSSE2019_CL-CL_NPP"]=dataset_parameters( "ECOSSE2019_CL-CL_NPP", input_filename["ECOSSE2019_CL-CL_NPP"], "VERIFY_BU", "FCO2_NPP_CRO", "o", "red")
        master_datasets["ECOSSE2019_CL-CL_FHARVEST"]=dataset_parameters( "ECOSSE2019_CL-CL_FHARVEST", input_filename["ECOSSE2019_CL-CL_FHARVEST"], "VERIFY_BU", "FCO2_FHARVEST_CRO", "o", "blue")
        master_datasets["ECOSSE2019_CL-CL_us"]=dataset_parameters( "ECOSSE2019_CL-CL_us", input_filename["ECOSSE2019_CL-CL_us"], "VERIFY_BU", "FCO2_SOIL_CRO", "o", "darkred")

        # Grasslands
        master_datasets["ECOSSE2019_GL-GL-lim"]=dataset_parameters( "ECOSSE_GL-GL lim", input_filename["ECOSSE2019_GL-GL-lim"], "VERIFY_BU", "FCO2_NBP_GRA", "o", "darkred")
        master_datasets["ECOSSE_GL-GL-RH"]=dataset_parameters( "ECOSSE_GL-GL RH", input_filename["ECOSSE_GL-GL-RH"], "VERIFY_BU", "FCO2_RH_GRA", "o", "red")
        master_datasets["ECOSSE_GL-GL-NPP"]=dataset_parameters( "ECOSSE_GL-GL NPP", input_filename["ECOSSE_GL-GL-NPP"], "VERIFY_BU", "FCO2_NPP_GRA", "o", "pink")
        master_datasets["ECOSSE_GL-GL-SOC"]=dataset_parameters( "ECOSSE_GL-GL SOC", input_filename["ECOSSE_GL-GL-SOC"], "VERIFY_BU", "FCO2_SOC_GRA", "o", "magenta")

        master_datasets["ECOSSE_GL-GL-nolim"]=dataset_parameters( "ECOSSE_GL-GL nolim", input_filename["ECOSSE_GL-GL-nolim"], "VERIFY_BU", "FCO2_NBP_GRA", "x", "darkred")
        master_datasets["ECOSSE_GL-GL_us"]=dataset_parameters( "ECOSSE_GL-GL_us", input_filename["ECOSSE_GL-GL_us"], "VERIFY_BU", "FCO2_SOIL_GRA", "o", "darkred")
        
        ######### testing some new UNFCCC datasets
        master_datasets["UNFCCC2020_FL-FL"]=dataset_parameters( "UNFCCC2020_FL-FL", input_filename["UNFCCC2020_FL-FL"], "INVENTORY", "FCO2_FL_REMAIN", "_", "lightgreen",displayname="UNFCCC FL-FL NGHGI (2020)")
        master_datasets["UNFCCC2020_LULUCF"]=dataset_parameters( "UNFCCC2020_LULUCF", input_filename["UNFCCC2020_LULUCF"], "INVENTORY", "FCO2_LULUCF_TOT", "_", "lightgreen",displayname="UNFCCC LULUCF NGHGI (2020)")
        master_datasets["UNFCCC2021_LULUCF"]=dataset_parameters( "UNFCCC2021_LULUCF", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_LULUCF_TOT", "_", "green",displayname="UNFCCC LULUCF NGHGI (2021)")
        master_datasets["UNFCCC2021_FL-FL"]=dataset_parameters( "UNFCCC2021_FL-FL", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_FL_REMAIN", "_", "green",displayname="UNFCCC FL-FL NGHGI (2021)")
        master_datasets["UNFCCC2021_CL-CL"]=dataset_parameters( "UNFCCC2021_CL-CL", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_CL_REMAIN", "_", "gold",displayname="UNFCCC CL-CL NGHGI (2021)")
        master_datasets["UNFCCC2021_GL-GL"]=dataset_parameters( "UNFCCC2021_GL-GL", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_GL_REMAIN", "_", "brown",displayname="UNFCCC GL-GL NGHGI (2021)")
        master_datasets["UNFCCC2021_forest_convert"]=dataset_parameters( "UNFCCC2021_forest_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_FL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_grassland_convert"]=dataset_parameters( "UNFCCC2021_grassland_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_GL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_cropland_convert"]=dataset_parameters( "UNFCCC2021_cropland_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_CL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_wetland_convert"]=dataset_parameters( "UNFCCC2021_wetland_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_WL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_settlement_convert"]=dataset_parameters( "UNFCCC2021_settlement_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_SL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_other_convert"]=dataset_parameters( "UNFCCC2021_other_convert", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_OL_CONVERT", "_", "green")
        master_datasets["UNFCCC2021_woodharvest"]=dataset_parameters( "UNFCCC2021_woodharvest", input_filename["UNFCCC2021_LULUCF"], "INVENTORY", "FCO2_HWP", "_", "green")


        #########################################

        master_datasets["EFISCEN-Spacev2019"]=dataset_parameters( "EFISCEN-Space", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_treeNEP_EFISCEN-Space-SX_WENR_FOR_EU_1M_V1_20190716_SCHELHAAS_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True)
        master_datasets["EFISCEN-Spacev2021"]=dataset_parameters( "EFISCEN-Space", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_ForestFluxes_EFISCENSpace-SX_WENR_FOR_EU_1M_V3_20211217_SCHELHAAS_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True)
        master_datasets["UNFCCC2019_FL-FL"]=dataset_parameters( "UNFCCC2019_FL-FL", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "green",displayname="UNFCCC FL-FL NGHGI (2019)")
        master_datasets["UNFCCC2019_GL-GL"]=dataset_parameters( "UNFCCC2019_GL-GL", input_filename["UNFCCC2019_GL-GL"], "INVENTORY", "FCO2_NBP", "_", "brown",displayname="UNFCCC GL-GL NGHGI (2019)")
        master_datasets["UNFCCC2019_CL-CL"]=dataset_parameters( "UNFCCC2019_CL-CL", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "gold",displayname="UNFCCC CL-CL NGHGI (2019)")
        master_datasets["ORCHIDEE2019_FL-FL"]=dataset_parameters( "ORCHIDEE2019_FL-FL", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP_FOR", "D", "dodgerblue", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["ORCHIDEE2020_FL-FL"]=dataset_parameters( "ORCHIDEE2020_FL-FL", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V2_20200910_MCGRATH_WP3_CountryTotWithEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP_FOR", "D", "dodgerblue", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["EFISCEN"]=dataset_parameters( "EFISCEN", database_dir + "OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20201103_SCHELHAAS_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "NONVERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["EFISCEN_NPP"]=dataset_parameters( "EFISCEN_NPP", database_dir + "OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NPP_FOR", "o", "orange", flipdatasign=True)
        master_datasets["EFISCEN_NEE"]=dataset_parameters( "EFISCEN_NEE", database_dir + "OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NEE_FOR", "o", "blue", flipdatasign=True)
        master_datasets["EFISCEN-unscaled"]=dataset_parameters( "EFISCEN-unscaled", database_dir + "OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", "NONVERIFY_BU", "FCO2_NBP_FOR", "o", "magenta", flipdatasign=True)
        master_datasets["CBM2019"]=dataset_parameters( "CBM2019", database_dir + "OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZMaster.nc", "NONVERIFY_BU", "FCO2_NBP", "o", "crimson", flipdatasign=True,lcheck_for_mean_overlap=True)
        master_datasets["CBM2021historical"]=dataset_parameters( "CBM2021historical", database_dir + "OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_ForestFluxes_CBM-SX_JRC_FOR_EU_1M_V3_20211110_VIZZARRI_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "NONVERIFY_BU", "FCO2_NBP_FOR", "o", "crimson", flipdatasign=True,lcheck_for_mean_overlap=True,displayname="CBMv2his_FL-FL")
        master_datasets["CBM2021simulated"]=dataset_parameters( "CBM2021simulated", database_dir + "OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_ForestFluxesSimulated_CBM-SX_JRC_FOR_EU_1M_V3_20211110_VIZZARRI_WPX_CountryTotWithOutEEZMaster.nc", "NONVERIFY_BU", "FCO2_NBP_FOR", "X", "crimson", flipdatasign=True,lcheck_for_mean_overlap=True,displayname="CBMv2sim_FL-FL")
        # This is only a single year, so calculating the overlap will not work.
        master_datasets["CBM2021simulateddrop"]=dataset_parameters( "CBM2021simulateddrop", "/home/orchidee03/mmcgrath/TEST_DATABASE/Tier3BUDD_CO2_ForestFluxesSimulatedDrop_CBM-SX_JRC_FOR_EU_1M_V3_20211110_VIZZARRI_WPX_CountryTotWithOutEEZMaster.nc", "NONVERIFY_BU", "FCO2_NBP_FOR", "X", "lightblue", flipdatasign=True,lcheck_for_mean_overlap=False)
        master_datasets["FLUXCOM_rsonlyRF_os"]=dataset_parameters( "FLUXCOM_rsonlyRF_os", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "yellowgreen")
        master_datasets["FLUXCOM_rsonlyANN_os"]=dataset_parameters( "FLUXCOM_rsonlyANN_os", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "green")
        master_datasets["FLUXCOM_rsonlyRF_ns"]=dataset_parameters( "FLUXCOM_rsonlyRF_ns", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "yellowgreen")
        master_datasets["FLUXCOM_rsonlyANN_ns"]=dataset_parameters( "FLUXCOM_rsonlyANN_ns", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP", "s", "green")
        master_datasets["FLUXCOM_FL-FL_RF"]=dataset_parameters( "FLUXCOM_FL-FL_RF", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_forest", "s", "yellowgreen")
        master_datasets["FLUXCOM_FL-FL_ANN"]=dataset_parameters( "FLUXCOM_FL-FL_ANN", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_forest", "s", "green")
        master_datasets["FLUXCOM_GL-GL_RF"]=dataset_parameters( "FLUXCOM_GL-GL_RF", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_grass", "s", "yellowgreen")
        master_datasets["FLUXCOM_GL-GL_ANN"]=dataset_parameters( "FLUXCOM_GL-GL_ANN", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_grass", "s", "green")
        master_datasets["FLUXCOM_CL-CL_RF"]=dataset_parameters( "FLUXCOM_CL-CL_RF", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_crops", "s", "yellowgreen")
        master_datasets["FLUXCOM_CL-CL_ANN"]=dataset_parameters( "FLUXCOM_CL-CL_ANN", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NEP_crops", "s", "green")

        # ORCHIDEE stuff
        

        master_datasets["ORCHIDEE2019_CL-CL"]=dataset_parameters( "ORCHIDEE2019_CL-CL", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP_CRP", "D", "dodgerblue", flipdatasign=True)

        master_datasets["TNO_biofuels"]=dataset_parameters( "TNO_biofuels", database_dir + "OTHER_PROJECTS/FCO2/TNO/Tier3BUDD_CO2_BiofuelEmissions_XXX-SX_TNO_XXX_EU_1M_V1_20191110_DERNIER_WPX_CountryTotWithOutEEZ.nc", "INVENTORY_NOERR", "FCO2_NBP_TOT", "X", "saddlebrown")
        master_datasets["UNFCCC_biofuels"]=dataset_parameters( "UNFCCC_biofuels", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_Biofuels_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY_NOERR", "FCO2_NBP", "o", "saddlebrown")
        master_datasets["rivers_lakes_reservoirs_ULB"]=dataset_parameters( "rivers_lakes_reservoirs_ULB", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_RiverLakeEmissions_XXXX-SX_ULB_INLWAT_EU_1M_V1_20190911_LAUERWALD_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_INLWAT", "o", "sandybrown")
        master_datasets["UNFCCC2019_forest_convert"]=dataset_parameters( "UNFCCC2019_forest_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_grassland_convert"]=dataset_parameters( "UNFCCC2019_grassland_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_cropland_convert"]=dataset_parameters( "UNFCCC2019_cropland_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_wetland_convert"]=dataset_parameters( "UNFCCC2019_wetland_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_settlement_convert"]=dataset_parameters( "UNFCCC2019_settlement_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_other_convert"]=dataset_parameters( "UNFCCC2019_other_convert", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["UNFCCC2019_woodharvest"]=dataset_parameters( "UNFCCC2019_woodharvest", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_HWP_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "o", "sandybrown")
        master_datasets["GCP2019_JENA"]=dataset_parameters( "GCP2019_JENA", input_filename["GCP2019_JENA"], "GLOBAL_TD", "FCO2_NBP", "o", "brown")
        master_datasets["GCP2019_CTRACKER"]=dataset_parameters( "GCP2019_CTRACKER", input_filename["GCP2019_CTRACKER"], "GLOBAL_TD", "FCO2_NBP", "o", "gold")
        master_datasets["GCP2019_CAMS"]=dataset_parameters( "GCP2019_CAMS", input_filename["GCP2019_CAMS"], "GLOBAL_TD", "FCO2_NBP", "o", "orange")
        master_datasets["GCP2019_ALL"]=dataset_parameters( "GCP2019_ALL", input_filename["GCP2019_ALL"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2019_COMMON"]=dataset_parameters( "GCP2019_COMMON", input_filename["GCP2019_COMMON"], "MINMAX", "FCO2_NBP", "s", "red")

        #### GCP 2020
        cb_green=(27.0/256.0,158.0/256.0,119.0/256.0)
        cb_orange=(217/256.0,95/256.0,2/256.0)
        cb_purple=(117/256.0,112/256.0,179/256.0)
        cb_rose=(231/256.0,41/256.0,138/256.0)
        cb_lightgreen=(102/256.0,166/256.0,30/256.0)

        master_datasets["GCP2020_ALL"]=dataset_parameters( "GCP2020_ALL", input_filename["GCP2020_ALL"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2020_COMMON"]=dataset_parameters( "GCP2020_COMMON", input_filename["GCP2020_COMMON"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2020_CAMS"]=dataset_parameters( "GCP2020_CAMS", input_filename["GCP2020_CAMS"], "GLOBAL_TD", "FCO2_NBP", "D", cb_green)
        master_datasets["GCP2020_CTRACKER"]=dataset_parameters( "GCP2020_CTRACKER", input_filename["GCP2020_CTRACKER"], "GLOBAL_TD", "FCO2_NBP", "D", cb_orange)
        master_datasets["GCP2020_JENA-s85"]=dataset_parameters( "GCP2020_JENA-s85", input_filename["GCP2020_JENA-s85"], "GLOBAL_TD", "FCO2_NBP", "D", cb_purple)
        master_datasets["GCP2020_JENA-sEXT"]=dataset_parameters( "GCP2020_JENA-sEXT", input_filename["GCP2020_JENA-sEXT"], "GLOBAL_TD", "FCO2_NBP", "D", cb_rose)
        master_datasets["GCP2020_NIES"]=dataset_parameters( "GCP2020_NIES", input_filename["GCP2020_NIES"], "GLOBAL_TD", "FCO2_NBP", "D", cb_lightgreen)
        master_datasets["GCP2020_UoE"]=dataset_parameters( "GCP2020_UoE", input_filename["GCP2020_UoE"], "GLOBAL_TD", "FCO2_NBP", "^", cb_green)



        #### GCP 2021
        master_datasets["GCP2021_ALL"]=dataset_parameters( "GCP2021_ALL", input_filename["GCP2021_ALL"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2021_COMMON"]=dataset_parameters( "GCP2021_COMMON", input_filename["GCP2021_COMMON"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2021_NOCAMS"]=dataset_parameters( "GCP2021_NOCAMS", input_filename["GCP2021_NOCAMS"], "MINMAX", "FCO2_NBP", "s", "red")
        master_datasets["GCP2021_CAMS"]=dataset_parameters( "GCP2021_CAMS", input_filename["GCP2021_CAMS"], "GLOBAL_TD", "FCO2_NBP", "h", "black")
        master_datasets["GCP2021_CAMSnoEEZ"]=dataset_parameters( "GCP2021_CAMSnoEEZ", input_filename["GCP2021_CAMSnoEEZ"], "GLOBAL_TD", "FCO2_NBP", "h", "blue")
        #master_datasets["GCP2021_CMS"]=dataset_parameters( "GCP2021_CMS", input_filename["GCP2021_CMS"], "GLOBAL_TD", "FCO2_NBP", "D", cb_orange)
        master_datasets["GCP2021_CTRACKER"]=dataset_parameters( "GCP2021_CTRACKER", input_filename["GCP2021_CTRACKER"], "GLOBAL_TD", "FCO2_NBP", "P", "black")
        master_datasets["GCP2021_JENA-s99"]=dataset_parameters( "GCP2021_JENA-s99", input_filename["GCP2021_JENA-s99"], "GLOBAL_TD", "FCO2_NBP", "o", "black")
        master_datasets["GCP2021_JENA-sEXT"]=dataset_parameters( "GCP2021_JENA-sEXT", input_filename["GCP2021_JENA-sEXT"], "GLOBAL_TD", "FCO2_NBP", "^", "black")
        master_datasets["GCP2021_NIES"]=dataset_parameters( "GCP2021_NIES", input_filename["GCP2021_NIES"], "GLOBAL_TD", "FCO2_NBP", "X", "black")
        master_datasets["GCP2021_UoE"]=dataset_parameters( "GCP2021_UoE", input_filename["GCP2021_UoE"], "GLOBAL_TD", "FCO2_NBP", ".", "black")



        master_datasets["LUH2v2_FOREST"]=dataset_parameters( "LUH2v2_FOREST", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "FOREST_AREA", "o", "orange",lignore_for_range=True)
        master_datasets["UNFCCC_FOREST"]=dataset_parameters( "UNFCCC_FOREST", database_dir + "OTHER_PROJECTS/NONFLUX/Tier1_XXXX_ForestArea_CRF2019-SX_UNFCCC_FOR_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "AREA", "o", "blue",lignore_for_range=True)
        master_datasets["LUH2v2_GRASS"]=dataset_parameters( "LUH2v2_GRASS", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "GRASSLAND_AREA", "o", "orange",lignore_for_range=True)
        master_datasets["UNFCCC_GRASS"]=dataset_parameters( "UNFCCC_GRASS", database_dir + "OTHER_PROJECTS/NONFLUX/Tier1_XXXX_GrasslandArea_CRF2019-SX_UNFCCC_GRS_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "AREA", "o", "blue",lignore_for_range=True)
        master_datasets["LUH2v2_CROP"]=dataset_parameters( "LUH2v2_CROP", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "CROPLAND_AREA", "o", "orange",lignore_for_range=True)
        master_datasets["UNFCCC_CROP"]=dataset_parameters( "UNFCCC_CROP", database_dir + "OTHER_PROJECTS/NONFLUX/Tier1_XXXX_CroplandArea_CRF2019-SX_UNFCCC_CRP_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "OTHER", "AREA", "o", "blue",lignore_for_range=True)
        master_datasets["MS-NRT"]=dataset_parameters( "MS-NRT", database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY_NOERR", "FCO2_NBP", "o", "red")
        master_datasets["UNFCCC_LUC"]=dataset_parameters( "UNFCCC_LUC", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "green")
        master_datasets["UNFCCC_LUCF"]=dataset_parameters( "UNFCCC_LUCF", "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "INVENTORY", "FCO2_NBP", "_", "green")

        # These are just placeholders.  They get overwritten below.
        master_datasets["FAOSTAT2019_LULUCF"]=dataset_parameters( "FAOSTAT2019_LULUCF", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet",lcheck_for_mean_overlap=True)
        master_datasets["FAOSTAT2021_LULUCF"]=dataset_parameters( "FAOSTAT2021_LULUCF", input_filename["FAO2021"], "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet",lcheck_for_mean_overlap=True)
        ##

        master_datasets["FAOSTAT2019_FL-FL"]=dataset_parameters( "FAOSTAT2019_FL-FL", input_filename["FAO2019"], "INVENTORY_NOERR", "FCO2_NBP_FOR", "P", "darkviolet",lcheck_for_mean_overlap=True)

        master_datasets["VERIFYBU"]=dataset_parameters( "VERIFYBU", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP", "D", "yellow")
        master_datasets["ORCHIDEE_LUC"]=dataset_parameters( "ORCHIDEE_LUC", database_dir + "VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ{}.nc".format(self.country_scope), "VERIFY_BU", "FCO2_NBP", "D", "sandybrown")
        master_datasets["ORCHIDEE_Tier2_Forest"]=dataset_parameters( "ORCHIDEE_Tier2_Forest", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR", "D", "red")
        master_datasets["ORCHIDEE_Tier2_Forest_EF1"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF1", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF1", "D", "red")
        master_datasets["ORCHIDEE_Tier2_Forest_EF2"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF2", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF2", "D", "darkgreen")
        master_datasets["ORCHIDEE_Tier2_Forest_EF3"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF3", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF3", "D", "blue")
        master_datasets["ORCHIDEE_Tier2_Forest_EF4"]=dataset_parameters( "ORCHIDEE_Tier2_Forest_EF4", "/home/users/mmcgrath/CODE.OBELIX/PYTHON/ORCHIDEE_emission_factors_Forest_CountryTotWithOutEEZ.nc", "VERIFY_BU", "FCO2_NBP_FOR_EF4", "D", "gray")

        # Change the color of the error bars for some
        master_datasets['UNFCCC_LUC'].uncert_color='darkseagreen'
        master_datasets['GCP2019_ALL'].uncert_color='red'
        master_datasets['GCP2020_ALL'].uncert_color='red'
        master_datasets['GCP2021_ALL'].uncert_color='red'
        master_datasets["TrendyV7_ENSEMBLE"].uncert_color='gray'
        master_datasets['CSR-COMBINED-2019'].uncert_color='blue'
        master_datasets['CSR-COMBINED-2020'].uncert_color='blue'
        master_datasets['UNFCCC2019_GL-GL'].uncert_color='brown'
        master_datasets['UNFCCC2021_GL-GL'].uncert_color='brown'
        master_datasets['UNFCCC2019_CL-CL'].uncert_color='gold'
        master_datasets['UNFCCC2021_CL-CL'].uncert_color='gold'
        
        # We always want these to be the same
        master_datasets['MS-NRT'].edgec=master_datasets['MS-NRT'].facec
        
        # Some we want to be just outlines
        master_datasets["ORCHIDEE_Tier2_Forest"].edgec=master_datasets["ORCHIDEE2019_FL-FL"].facec
        master_datasets["ORCHIDEE_Tier2_Forest"].facec="none"
        
        # And better names for these
        master_datasets['UNFCCC2019_LULUCF'].displayname='UNFCCC LULUCF NGHGI (2019)'
        master_datasets['UNFCCC2019_LULUCF'].displayname_err='UNFCCC LULUCF NGHGI (2019) uncertainty'
        master_datasets['UNFCCC2020_LULUCF'].displayname='UNFCCC LULUCF NGHGI (2020)'
        master_datasets['UNFCCC2020_LULUCF'].displayname_err='UNFCCC LULUCF NGHGI (2020) uncertainty'
        master_datasets['UNFCCC2021_LULUCF'].displayname='UNFCCC LULUCF NGHGI (2021)'
        master_datasets['UNFCCC2021_LULUCF'].displayname_err='UNFCCC LULUCF NGHGI (2021) uncertainty'
        master_datasets['UNFCCC2019_FL-FL'].displayname='UNFCCC FL-FL NGHGI (2019)'
        master_datasets['UNFCCC2019_FL-FL'].displayname_err='UNFCCC FL-FL NGHGI uncertainty (2019)'
        master_datasets['UNFCCC2021_FL-FL'].displayname='UNFCCC FL-FL NGHGI (2021)'
        master_datasets['UNFCCC2021_FL-FL'].displayname_err='UNFCCC FL-FL NGHGI uncertainty (2021)'
        master_datasets['UNFCCC2019_GL-GL'].displayname='UNFCCC GL-GL NGHGI (2019)'
        master_datasets['UNFCCC2019_GL-GL'].displayname_err='UNFCCC GL-GL NGHGI uncertainty (2019)'
        master_datasets['UNFCCC2019_CL-CL'].displayname='UNFCCC CL-CL NGHGI (2019)'
        master_datasets['UNFCCC2019_CL-CL'].displayname_err='UNFCCC CL-CL NGHGI uncertainty (2019)'
        master_datasets['UNFCCC2021_CL-CL'].displayname='UNFCCC CL-CL NGHGI (2021)'
        master_datasets['UNFCCC2021_CL-CL'].displayname_err='UNFCCC CL-CL NGHGI uncertainty (2021)'
        master_datasets['UNFCCC2021_GL-GL'].displayname='UNFCCC GL-GL NGHGI (2021)'
        master_datasets['UNFCCC2021_GL-GL'].displayname_err='UNFCCC GL-GL NGHGI uncertainty (2021)'
        master_datasets['FAOSTAT2019_LULUCF'].displayname='FAOSTAT_LULUCF'
        master_datasets['FAOSTAT2021_LULUCF'].displayname='FAOSTATv2_LULUCF'
        master_datasets['CSR-COMBINED-2019'].displayname='Mean of CarboScopeReg'
        master_datasets['CSR-COMBINED-2019'].displayname_err='Min/Max of CarboScopeReg'
        master_datasets['CSR-COMBINED-2020'].displayname='Mean of CarboScopeReg V2'
        master_datasets['CSR-COMBINED-2020'].displayname_err='Min/Max of CarboScopeReg V2'        
        master_datasets['EUROCOM_ALL_2019'].displayname='Mean of EUROCOM inversions'
        master_datasets['EUROCOM_ALL_2019'].displayname_err='Min/Max of EUROCOM inversions'
        master_datasets['EUROCOM_ALL_2020'].displayname='Mean of EUROCOM inversions v2'
        master_datasets['EUROCOM_ALL_2020'].displayname_err='Min/Max of EUROCOM inversions v2'
        master_datasets["TrendyV7_ENSEMBLE"].displayname='Median of TRENDY v7 DGVMs'
        master_datasets["TrendyV7_ENSEMBLE"].displayname_err='Min/Max of TRENDY v7 DGVMs'
        master_datasets["TrendyV9_ENSEMBLE"].displayname='Median of TRENDY v9 DGVMs'
        master_datasets["TrendyV9_ENSEMBLE"].displayname_err='Min/Max of TRENDY v9 DGVMs'
        master_datasets['TrendyV10_ENSEMBLE'].displayname='Median of TRENDY v10 DGVMs'
        master_datasets['TrendyV10_ENSEMBLE'].displayname_err='Min/Max of TRENDY v10 DGVMs'
        master_datasets["TrendyV7_COMMON"].displayname='Median of TRENDY v7 DGVMs'
        master_datasets["TrendyV7_COMMON"].displayname_err='Min/Max of TRENDY v7 DGVMs'
        master_datasets["TrendyV9_COMMON"].displayname='Median of TRENDY v9 DGVMs'
        master_datasets["TrendyV9_COMMON"].displayname_err='Min/Max of TRENDY v9 DGVMs'
        master_datasets['TrendyV10_COMMON'].displayname='Median of TRENDY v10 DGVMs'
        master_datasets['TrendyV10_COMMON'].displayname_err='Min/Max of TRENDY v10 DGVMs'

        master_datasets['GCP2019_ALL'].displayname="Mean of GCP inversions (2019)"
        master_datasets['GCP2019_ALL'].displayname_err="Min/Max of GCP inversions (2019)"
        master_datasets['GCP2020_ALL'].displayname="Mean of GCP inversions (2020)"
        master_datasets['GCP2020_ALL'].displayname_err="Min/Max of GCP inversions (2020)"
        master_datasets['GCP2021_ALL'].displayname="Mean of GCP inversions (2021)"
        master_datasets['GCP2021_ALL'].displayname_err="Min/Max of GCP inversions (2021)"
        
        master_datasets['ORCHIDEE_Tier2_Forest_EF1'].displayname='UNFCCC emissions / FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF2'].displayname='ORCHIDEE FL-FL emissions / LUH2v2-ESACCI FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF3'].displayname='ORCHIDEE FL-FL emissions / UNFCCC FL-FL area'
        master_datasets['ORCHIDEE_Tier2_Forest_EF4'].displayname='Created from Eq. 2.5 and ORCHIDEE'
        
        self.lplot_areas=False
        
        # Now define the actual simulation configs
        if self.graphname == "test":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'BLUE2019', \
                                  "TrendyV7_ENSEMBLE", \
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
                                  'UNFCCC2019_forest_convert', \
                                  'UNFCCC2019_grassland_convert', \
                                  'UNFCCC2019_cropland_convert', \
                                  'UNFCCC2019_wetland_convert', \
                                  'UNFCCC2019_settlement_convert', \
                                  'UNFCCC2019_other_convert', \
                                  'BLUE2019', \
                                  'H&N2019', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  'ORCHIDEE_LUC', \
                                  "ORCHIDEE-S3-V2019", \
                                  'ORCHIDEE_S2', \
                              ]   
            self.output_file_start="LUC_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use change"
            
            # Change some colors and symbols here
            master_datasets['BLUE2019'].facec='blue'
            master_datasets['H&N2019'].facec='green'
            master_datasets['ORCHIDEE-MICT'].facec='red'
            master_datasets["ORCHIDEE-S3-V2019"].facec='blue'
            
            master_datasets['BLUE2019'].plotmarker='^'
            master_datasets['H&N2019'].plotmarker='^'
            master_datasets['ORCHIDEE-MICT'].plotmarker='X'
            master_datasets["ORCHIDEE-S3-V2019"].plotmarker='X'
            
            # These simulations will be combined together.
            self.overwrite_simulations["UNFCCC_LUC"]=['UNFCCC2019_forest_convert', \
                                                 'UNFCCC2019_grassland_convert', \
                                                 'UNFCCC2019_cropland_convert', \
                                                 'UNFCCC2019_wetland_convert', \
                                                 'UNFCCC2019_settlement_convert', \
                                                 'UNFCCC2019_other_convert', \
                                             ]
            self.overwrite_operations["UNFCCC_LUC"]="sum"
            self.overwrite_coeffs["UNFCCC_LUC"]=[1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                            1.0, \
                                        ]
            self.overwrite_simulations["ORCHIDEE_LUC"]=["ORCHIDEE-S3-V2019", \
                                                   'ORCHIDEE_S2', \
                                               ]
            self.overwrite_operations["ORCHIDEE_LUC"]="sum"
            self.overwrite_coeffs["ORCHIDEE_LUC"]=[1.0, \
                                              -1.0, \
                                          ]
            
            
            # So I don't want to generally plot the components
            master_datasets['UNFCCC2019_forest_convert'].displaylegend=False
            master_datasets['UNFCCC2019_grassland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_cropland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_wetland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_settlement_convert'].displaylegend=False
            master_datasets['UNFCCC2019_other_convert'].displaylegend=False
            master_datasets["ORCHIDEE-S3-V2019"].displaylegend=False
            master_datasets['ORCHIDEE_S2'].displaylegend=False
            
            
            #if lshow_productiondata:
            #   productiondata_master['ORCHIDEE-MICT']=False
            #endif
            
        elif self.graphname == "all_orchidee":
            self.desired_simulations=[ \
#                                  'ORCHIDEE-S3-V2019', \
#                                  'ORCHIDEE-S3-V2020', \
#                                  'ORCHIDEEv3-S3-V2', \
#                                  "TrendyV7_ORCHIDEE",\
#                                  "TrendyV9_ORCHIDEE",\
#                                  "TrendyV9_ORCHIDEEv3",\
#                                  "TrendyV10_ORCHIDEE",\
#                                  "TrendyV10_ORCHIDEEv3",\
                                  "TrendyV10_ENSEMBLE",\
                              ]   
            self.output_file_start="ORCHIDEE_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all ORCHIDEE simulations"
            
            # Change some colors and symbols here
            master_datasets['ORCHIDEE-S3-V2019'].facec='blue'
            master_datasets['ORCHIDEE-S3-V2019'].plotmarker='o'
            master_datasets['ORCHIDEE-S3-V2020'].facec='red'
            master_datasets['ORCHIDEE-S3-V2020'].plotmarker='o'
            master_datasets['ORCHIDEEv3-S3-V2'].plotmarker='o'
            master_datasets['ORCHIDEEv3-S3-V2'].facec='green'
            
            master_datasets['TrendyV7_ORCHIDEE'].plotmarker='D'
            master_datasets['TrendyV7_ORCHIDEE'].plotmarker='blue'

            # Plot these as bars
            #master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            #master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
  

            
            
            
        elif self.graphname == "lucf_full":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC_LUCF', \
                                  'UNFCCC2019_forest_convert', \
                                  'UNFCCC2019_grassland_convert', \
                                  'UNFCCC2019_cropland_convert', \
                                  'UNFCCC2019_wetland_convert', \
                                  'UNFCCC2019_settlement_convert', \
                                  'UNFCCC2019_other_convert', \
                                  'UNFCCC2019_FL-FL', \
                                  'BLUE2019', \
                                  'H&N2019', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  "ORCHIDEE-S3-V2019", \
                              ]   
            self.output_file_start="LUCF_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use change and forestry"
            
            # Change some colors and symbols here
            master_datasets['BLUE2019'].facec='blue'
            master_datasets['H&N2019'].facec='green'
            master_datasets['ORCHIDEE-MICT'].facec='red'
            master_datasets["ORCHIDEE-S3-V2019"].facec='blue'
            
            master_datasets['BLUE2019'].plotmarker='^'
            master_datasets['H&N2019'].plotmarker='^'
            master_datasets['ORCHIDEE-MICT'].plotmarker='X'
            master_datasets["ORCHIDEE-S3-V2019"].plotmarker='X'
            
            # These simulations will be combined together.
            self.overwrite_simulations["UNFCCC_LUCF"]=['UNFCCC2019_forest_convert', \
                                                  'UNFCCC2019_grassland_convert', \
                                                  'UNFCCC2019_cropland_convert', \
                                                  'UNFCCC2019_wetland_convert', \
                                                  'UNFCCC2019_settlement_convert', \
                                                  'UNFCCC2019_other_convert', \
                                                  'UNFCCC2019_FL-FL',\
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
            master_datasets['UNFCCC2019_forest_convert'].displaylegend=False
            master_datasets['UNFCCC2019_grassland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_cropland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_wetland_convert'].displaylegend=False
            master_datasets['UNFCCC2019_settlement_convert'].displaylegend=False
            master_datasets['UNFCCC2019_other_convert'].displaylegend=False
            master_datasets['UNFCCC2019_FL-FL'].displaylegend=False
            
            
            #if lshow_productiondata:
            #   productiondata_master['ORCHIDEE-MICT']=False
            #endif
            
            # This is simply meant to compare UNFCCC LULUCF with the MS-NRT data
        elif self.graphname == "lulucf_msnrt":
            self.desired_simulations=[ \
                                  'UNFCCC2019_LULUCF', \
                                  'MS-NRT', \
                              ]   
            self.output_file_start="UNFCCC-LULUCF-MSNRT_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"
            
            # These simulations will be combined together.
            #self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT_Grs','FAOSTAT2019_FOR_TOT']
            #self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            #self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            # So I don't want to generally plot the components
            #master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            #master_datasets['FAOSTAT_Grs'].displaylegend=False
            #master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            
        elif self.graphname == "d6.2":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'BLUE2019', \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                       'GCP2019_ALL', \
                                       "TrendyV7_ENSEMBLE", \

                              ]   
            self.desired_legend=[\
                            master_datasets["UNFCCC2019_LULUCF"].displayname,\
                            master_datasets["FAOSTAT2019_LULUCF"].displayname,\
                            master_datasets["BLUE2019"].displayname,\
                            master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                            master_datasets['GCP2019_ALL'].displayname, master_datasets['GCP2019_ALL'].displayname_err, \

                        ]
            self.output_file_start="D6.2_"
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            # Plot these as bars
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].lplot_errorbar=True

        elif self.graphname == "lulucf_full":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'BLUE2019', \
                                  'H&N2019', \
                                  'MS-NRT', \
                                  'ORCHIDEE-MICT', \
                                  "ORCHIDEE-S3-V2019", \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                              ]   
            self.output_file_start="LULUCF_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            
        elif self.graphname == "lulucftrendy_2019":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'BLUE2019', \
                                  'H&N2019', \
                                  'MS-NRT', \
                                  #'ORCHIDEE-MICT', \
                                  #"ORCHIDEE-S3-V2019", \
                                  'ORCHIDEE-S3-V2019', \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                  "TrendyV7_ENSEMBLE", \
                              ]  
            
            self.desired_legend=[\
                            master_datasets["UNFCCC2019_LULUCF"].displayname,master_datasets["UNFCCC2019_LULUCF"].displayname_err,\
                            master_datasets["MS-NRT"].displayname,\
                            
                            master_datasets["FAOSTAT2019_LULUCF"].displayname,\
                            master_datasets["BLUE2019"].displayname,\
                            master_datasets["H&N2019"].displayname,\
                            master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                            master_datasets["ORCHIDEE-S3-V2019"].displayname,\
                        ]
            self.output_file_start="LULUCFTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 

            self.titleending=r" : Net bottom-up CO$_2$land fluxes from land use, land use change, and forestry (LULUCF)"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2019"].facec="black"
            master_datasets["TrendyV7_ORCHIDEE"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].edgec="dimgrey"
            
            # Plot these as bars
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            
            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-540.0
            self.ymax_external=390.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "lulucftrendy_2021":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2021_LULUCF', \
                                  'BLUE2021_VERIFY', \
                                  'BLUE2021_GCP', \
                                  'H&N2021', \
#                                  'MS-NRT', \
                                  #'ORCHIDEE-MICT', \
                                  #"ORCHIDEE-S3-V2019", \
                                  'ORCHIDEE-S3-V2020', \
                                  'FAOSTAT2021_LULUCF', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                                  'FAOSTAT2021_FOR_TOT', \
                                  "TrendyV10_ENSEMBLE", \
                              ]  
            
            self.desired_legend=[\
                            master_datasets["UNFCCC2021_LULUCF"].displayname,master_datasets["UNFCCC2021_LULUCF"].displayname_err,\
#                            master_datasets["MS-NRT"].displayname,\
                            
                            master_datasets["FAOSTAT2021_LULUCF"].displayname,\
                            master_datasets["BLUE2021_VERIFY"].displayname,\
                            master_datasets["BLUE2021_GCP"].displayname,\
                            master_datasets["H&N2021"].displayname,\
                            master_datasets["TrendyV10_ENSEMBLE"].displayname, master_datasets["TrendyV10_ENSEMBLE"].displayname_err, \
#                            master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                            master_datasets["ORCHIDEE-S3-V2020"].displayname,\
                            #master_datasets["ORCHIDEE-MICT"].displayname,\
                            #master_datasets["TrendyV7_ORCHIDEE"].displayname,\
                        ]
            self.output_file_start="LULUCFTrendy_"
            # Older data
            #self.output_file_end="_FCO2land_2019_v1.png" 
            # New data for UNFCCC, FAOSTAT
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Net bottom-up CO$_2$land fluxes from land use, land use change, and forestry (LULUCF)"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2021_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2021_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2020"].facec="black"
            
            # Plot these as bars
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            
            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-540.0
            self.ymax_external=390.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "orc_trendy":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'MS-NRT', \
                                  "ORCHIDEE-S3-V2019", \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                  "TrendyV7_ENSEMBLE", \
                                  "TrendyV7_ORCHIDEE",\
                              ]  
            
            master_datasets["ORCHIDEE-S3-V2019"]="ORCHIDEE-VERIFY"
            self.desired_legend=[\
                            master_datasets["FAOSTAT2019_LULUCF"].displayname,\
                            master_datasets["UNFCCC2019_LULUCF"].displayname,master_datasets["UNFCCC2019_LULUCF"].displayname_err,\
                            master_datasets["MS-NRT"].displayname,\
                            
                            master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                            master_datasets["TrendyV7_ORCHIDEE"].displayname,\
                            master_datasets["ORCHIDEE-S3-V2019"].displayname,\
                        ]
            self.output_file_start="LULUCFOrcTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2019"].facec="black"
            master_datasets["ORCHIDEE-MICT"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].edgec="dimgrey"
            master_datasets["ORCHIDEE-MICT"].edgec="black"
            #master_datasets['ORCHIDEE-MICT'].displaylegend=False
            #master_datasets['TrendyV7_ORCHIDEE'].displaylegend=False
            
            # Plot these as bars
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            
        elif self.graphname == "unfccc_fao_trendy":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'MS-NRT', \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                  "TrendyV7_ENSEMBLE", \
                                  "TrendyV7_ORCHIDEE",\
                              ]  
            
            self.desired_legend=[\
                            master_datasets["FAOSTAT2019_LULUCF"].displayname,\
                            master_datasets["UNFCCC2019_LULUCF"].displayname,master_datasets["UNFCCC2019_LULUCF"].displayname_err,\
                            master_datasets["MS-NRT"].displayname,\
                            
                            master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                            master_datasets["TrendyV7_ORCHIDEE"].displayname,\
                        ]
            self.output_file_start="UNFCCCFAOTrendy_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2019"].facec="black"
            master_datasets["ORCHIDEE-MICT"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].edgec="dimgrey"
            master_datasets["ORCHIDEE-MICT"].edgec="black"
            #master_datasets['ORCHIDEE-MICT'].displaylegend=False
            #master_datasets['TrendyV7_ORCHIDEE'].displaylegend=False
            
            # Plot these as bars
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            
        elif self.graphname == "unfccc_fao":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'UNFCCC2019_LULUCF', \
                                  'MS-NRT', \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                              ]  
            
            self.desired_legend=[\
                            master_datasets["FAOSTAT2019_LULUCF"].displayname,\
                            master_datasets["UNFCCC2019_LULUCF"].displayname,master_datasets["UNFCCC2019_LULUCF"].displayname_err,\
                            master_datasets["MS-NRT"].displayname,\
                            
                        ]
            self.output_file_start="UNFCCCFAO_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2019"].facec="black"
            master_datasets["ORCHIDEE-MICT"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].edgec="dimgrey"
            master_datasets["ORCHIDEE-MICT"].edgec="black"
            #master_datasets['ORCHIDEE-MICT'].displaylegend=False
            #master_datasets['TrendyV7_ORCHIDEE'].displaylegend=False
            
            # Plot these as bars
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            
        elif self.graphname == "faolulucfcomparison":
            self.desired_simulations=[ \
                                  # we read in data for LUC, but we replace it with the sectors below
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                  'FAOSTAT2021_LULUCF', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                                  'FAOSTAT2021_FOR_TOT', \
                             ]  
            
            self.output_file_start="FAOLULUCFComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]

            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["FAOSTAT2021_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2021_LULUCF'].plotmarker='o'

            master_datasets["FAOSTAT2019_LULUCF"].plot_lines=True
            master_datasets["FAOSTAT2019_LULUCF"].linestyle="dashed"
            master_datasets["FAOSTAT2021_LULUCF"].plot_lines=True
            master_datasets["FAOSTAT2021_LULUCF"].linestyle="solid"
            
        elif self.graphname == "fao_for":
            self.desired_simulations=[ \
                                  'FAOSTAT2019_FOR_TOT', \
#                                  'FAOSTAT2019_FOR_REM', \
#                                  'FAOSTAT2019_FOR_CON', \
                                  'FAOSTAT2021_FOR_TOT', \
#                                  'FAOSTAT2021_FOR_REM', \
#                                  'FAOSTAT2021_FOR_CON', \
                             ]  
            
            #self.desired_legend=[\
                            #                      "blah",\
            #                master_datasets["FAOSTAT2019_LULUCF"].displayname,\
            #                master_datasets["FAOSTAT2019_CRP"].displayname,\
            #                master_datasets["FAOSTAT2019_GRS"].displayname,\
            #                master_datasets["FAOSTAT2019_FOR_TOT"].displayname,\
          #                  master_datasets["FAOSTAT2020_LULUCF"].displayname,\
          #                  master_datasets["FAOSTAT2020_CRP"].displayname,\
          #                  master_datasets["FAOSTAT2020_GRS"].displayname,\
          #                  master_datasets["FAOSTAT2020_FOR_TOT"].displayname,\
#                        ]
            self.output_file_start="FAOForestComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_FOR_TOT"].facec="blue"
            master_datasets['FAOSTAT2019_FOR_TOT'].plotmarker='^'
            master_datasets["FAOSTAT2021_FOR_TOT"].facec="blue"
            master_datasets['FAOSTAT2021_FOR_TOT'].plotmarker='o'
            
            master_datasets["FAOSTAT2019_FOR_CON"].facec="red"
            master_datasets['FAOSTAT2019_FOR_CON'].plotmarker='^'
            master_datasets["FAOSTAT2021_FOR_CON"].facec="red"
            master_datasets['FAOSTAT2021_FOR_CON'].plotmarker='o'
            
            master_datasets["FAOSTAT2019_FOR_REM"].facec="green"
            master_datasets['FAOSTAT2019_FOR_REM'].plotmarker='^'
            master_datasets["FAOSTAT2021_FOR_REM"].facec="green"
            master_datasets['FAOSTAT2021_FOR_REM'].plotmarker='o'
            

        elif self.graphname == "fao_crp_grs":
            self.desired_simulations=[ \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
#                                  'FAOSTAT2020_CRP', \
#                                  'FAOSTAT2020_GRS', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                             ]  
            
            self.output_file_start="FAOCrpGrsComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_CRP"].facec="red"
            master_datasets['FAOSTAT2019_CRP'].plotmarker='^'
            master_datasets["FAOSTAT2019_GRS"].facec="green"
            master_datasets['FAOSTAT2019_GRS'].plotmarker='^'
#            master_datasets["FAOSTAT2020_CRP"].facec="red"
#            master_datasets['FAOSTAT2020_CRP'].plotmarker='o'
#            master_datasets["FAOSTAT2020_GRS"].facec="green"
#            master_datasets['FAOSTAT2020_GRS'].plotmarker='o'
            master_datasets["FAOSTAT2021_CL-CL"].facec="red"
            master_datasets['FAOSTAT2021_CL-CL'].plotmarker='X'
            master_datasets["FAOSTAT2021_GL-GL"].facec="green"
            master_datasets['FAOSTAT2021_GL-GL'].plotmarker='X'
            
        elif self.graphname == "cbm":
            self.desired_simulations=[ \
                                  'CBM2019', \
                                  'CBM2021historical', \
                                  'CBM2021simulated', \
#                                  'CBM2021simulateddrop', \
                             ]  
            
            self.output_file_start="CBMComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Bottom-up forestry CO$_2$ emissions from the CBM model"
            
            # Change some colors and symbols here
            master_datasets["CBM2019"].facec="gray"
            master_datasets["CBM2021historical"].facec="blue"
            master_datasets["CBM2021simulated"].facec="blue"


            master_datasets["CBM2019"].plot_lines=True
            master_datasets["CBM2019"].linestyle="dashed"
            master_datasets["CBM2021historical"].plot_lines=True
            master_datasets["CBM2021historical"].linestyle="solid"

        elif self.graphname == "sectorplot_full":
            self.desired_simulations=[ \
                                  "ORCHIDEE-S3-V2019", \
                                  'ECOSSE_GL-GL', \
                                  'EFISCEN', \
                                  'UNFCCC2019_FL-FL', \
                                  'UNFCCC2019_GL-GL', \
                                  'UNFCCC2019_CL-CL', \
                                  'FLUXCOM_rsonlyANN_os', \
                                  'FLUXCOM_rsonlyRF_os', \
                                  "EPIC2019_NBP_CRP", \
                                  "TrendyV7_ENSEMBLE", \
                              ]  
            self.desired_legend=[\
                            "UNFCCC2019_FL-FL","UNFCCC2019_GL-GL","UNFCCC2019_CL-CL",\
                            'Median of TRENDY v7 DGVMs', "Min/Max of TRENDY v7 DGVMs", \
                            "EFISCEN","ECOSSE_GL-GL","EPIC",\
                            "EPIC/ECOSSE/EFISCEN","ORCHIDEE-S3-V2019","FLUXCOM_rsonlyANN_os","FLUXCOM_rsonlyRF_os", \
                        ]
            
            
            self.output_file_start="AllSectorBU_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from land use (land remaining land)"
            
            master_datasets["EPIC2019_NBP_CRP"].plotmarker="P"
            
            master_datasets["EPIC2019_NBP_CRP"].facec="brown"
            
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE2019_CL-CL']=False
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            
        elif self.graphname == "unfccclulucfbar_2019":
            self.desired_simulations=[ \
                                  'UNFCCC2019_LULUCF', \
                                  'UNFCCC2019_FL-FL', \
                                  'UNFCCC2019_GL-GL', \
                                  'UNFCCC2019_CL-CL', \
                                  'UNFCCC2019_forest_convert', \
                                  'UNFCCC2019_grassland_convert', \
                                  'UNFCCC2019_cropland_convert', \
                                  'UNFCCC2019_wetland_convert', \
                                  'UNFCCC2019_settlement_convert', \
                                  'UNFCCC2019_other_convert', \
                                  'UNFCCC2019_woodharvest', \
                              ]  
            # I cannot do this until all my simulations have been plotted
            #self.desired_legend=[\
                #                 master_datasets["UNFCCC2019_LULUCF"].displayname,\
                #                'UNFCCC2019_FL-FL','UNFCCC2019_GL-GL','UNFCCC2019_CL-CL',\
                #                'UNFCCC2019_forest_convert', \
                #                      'UNFCCC2019_grassland_convert', \
                #                      'UNFCCC2019_cropland_convert', \
                #                      'UNFCCC2019_wetland_convert', \
                #                      'UNFCCC2019_settlement_convert', \
                #                      'UNFCCC2019_other_convert', \
                #                 ]
            
            
            self.output_file_start="UNFCCCLULUCFbar_"
            # v3 has colored bars, v7 has gray bars
            self.output_file_end="_FCO2land_2019_v7.png" 
            self.titleending=r" : Trends in CO$_2$land fluxes from land use, land use change, and forestry (LULUCF)"
            
            master_datasets['UNFCCC2019_LULUCF'].facec="darkgray"
            master_datasets['UNFCCC2019_forest_convert'].facec="darkgreen"
            master_datasets['UNFCCC2019_grassland_convert'].facec="magenta"
            master_datasets['UNFCCC2019_cropland_convert'].facec="violet"
            master_datasets['UNFCCC2019_wetland_convert'].facec="blue"
            master_datasets['UNFCCC2019_settlement_convert'].facec="dodgerblue"
            master_datasets['UNFCCC2019_other_convert'].facec="brown"
            master_datasets['UNFCCC2019_woodharvest'].facec="aqua"
            
            master_datasets['UNFCCC2019_FL-FL'].displayname='FL-FL'
            master_datasets['UNFCCC2019_GL-GL'].displayname='GL-GL'
            master_datasets['UNFCCC2019_CL-CL'].displayname='CL-CL'
            master_datasets['UNFCCC2019_woodharvest'].displayname='HWP'
            
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE2019_CL-CL']=False
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif

            # Set some things for the averages
            self.naverages=3
            self.syear_average=[1990, 2000, 2010]
            self.eyear_average=[1999, 2009, 2017]

        elif self.graphname == "unfccclulucfbar_2021":
            self.desired_simulations=[ \
                                  'UNFCCC2021_LULUCF', \
                                  'UNFCCC2021_FL-FL', \
                                  'UNFCCC2021_GL-GL', \
                                  'UNFCCC2021_CL-CL', \
                                  'UNFCCC2021_forest_convert', \
                                  'UNFCCC2021_grassland_convert', \
                                  'UNFCCC2021_cropland_convert', \
                                  'UNFCCC2021_wetland_convert', \
                                  'UNFCCC2021_settlement_convert', \
                                  'UNFCCC2021_other_convert', \
                                  'UNFCCC2021_woodharvest', \
                              ]  
            # I cannot do this until all my simulations have been plotted
            #self.desired_legend=[\
                #                 master_datasets["UNFCCC2021_LULUCF"].displayname,\
                #                'UNFCCC2021_FL-FL','UNFCCC2021_GL-GL','UNFCCC2021_CL-CL',\
                #                'UNFCCC2021_forest_convert', \
                #                      'UNFCCC2021_grassland_convert', \
                #                      'UNFCCC2021_cropland_convert', \
                #                      'UNFCCC2021_wetland_convert', \
                #                      'UNFCCC2021_settlement_convert', \
                #                      'UNFCCC2021_other_convert', \
                #                 ]
            
            
            self.output_file_start="UNFCCCLULUCFbar_"
            # v3 has colored bars, v7 has gray bars
            self.output_file_end="_FCO2land_2021_v7.png" 
            self.titleending=r" : Trends in CO$_2$land fluxes from land use, land use change, and forestry (LULUCF)"
            
            master_datasets['UNFCCC2021_LULUCF'].facec="darkgray"
            master_datasets['UNFCCC2021_forest_convert'].facec="darkgreen"
            master_datasets['UNFCCC2021_grassland_convert'].facec="magenta"
            master_datasets['UNFCCC2021_cropland_convert'].facec="violet"
            master_datasets['UNFCCC2021_wetland_convert'].facec="blue"
            master_datasets['UNFCCC2021_settlement_convert'].facec="dodgerblue"
            master_datasets['UNFCCC2021_other_convert'].facec="brown"
            master_datasets['UNFCCC2021_woodharvest'].facec="aqua"
            
            master_datasets['UNFCCC2021_FL-FL'].displayname='FL-FL'
            master_datasets['UNFCCC2021_GL-GL'].displayname='GL-GL'
            master_datasets['UNFCCC2021_CL-CL'].displayname='CL-CL'
            master_datasets['UNFCCC2021_woodharvest'].displayname='HWP'
            
            # Set some things for the averages
            self.naverages=3
            self.syear_average=[1990, 2000, 2010]
            self.eyear_average=[1999, 2009, 2019]

        elif self.graphname == "unfccc_woodharvest":
            self.desired_simulations=[ \
                                  #    'UNFCCC2019_LULUCF', \
                                  'UNFCCC2019_FL-FL', \
                                  'UNFCCC2019_woodharvest', \
                              ]  
            
            self.output_file_start="UNFCCCHWP_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emission trends from land use, land use change, and forestry"
            
            master_datasets['UNFCCC2019_LULUCF'].facec="darkgray"
            master_datasets['UNFCCC2019_woodharvest'].facec="aqua"
            
            master_datasets['UNFCCC2019_FL-FL'].displayname='FL-FL'
            master_datasets['UNFCCC2019_woodharvest'].displayname='HWP'
            
        elif self.graphname in ("verifybu","verifybu_detrend"):
            self.desired_simulations=[ \
                                  "ORCHIDEE-S3-V2019", \
                                  'ORCHIDEE-MICT', \
                                  'EFISCEN', \
                                  #                            'EFISCEN-unscaled', \
                                  #'EFISCEN-Space', \
                                  'FLUXCOM_rsonlyANN_os', \
                                  'FLUXCOM_rsonlyRF_os', \
                                  #'ECOSSE_GL-GL', \
                                  'ECOSSE2019_CL-CL', \
                                  #'ECOSSE_GL-GL_us', \
                                  #'ECOSSE2019_CL-CL_us', \
                                  "EPIC2019_NBP_CRP", \
                                  'BLUE2019', \
                                  #                            'VERIFYBU', \
                              ]   
            self.output_file_start="VerifyBU_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all VERIFY bottom-up models"
            self.lplot_areas=True
            
            if self.graphname == "verifybu_detrend":
                self.output_file_start="VerifyBUdetrend_"
                self.ldetrend=True
                self.titleending=r" : detrended CO$_2$ emissions from all VERIFY bottom-up models"
            #endif
                
            # These simulations will be combined together.
            #self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT',"ORCHIDEE-S3-V2019",'FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE2019']
            #self.overwrite_operations["VERIFYBU"]="mean"
            #master_datasets["VERIFYBU"].displaylegend=False
            
            master_datasets['EFISCEN'].plotmarker="P"
            master_datasets['CBM2019'].plotmarker="X"
            master_datasets['FLUXCOM_rsonlyRF_os'].plotmarker="s"
            master_datasets['FLUXCOM_rsonlyANN_os'].plotmarker="s"
            master_datasets['FAOSTAT2019_FL-FL'].plotmarker="d"
            
            master_datasets["ORCHIDEE2019_FL-FL"].edgec="black"
            master_datasets["EFISCEN"].edgec="black"
            master_datasets["CBM2019"].edgec="black"
            master_datasets["FLUXCOM_FL-FL_RF"].edgec="black"
            master_datasets["FLUXCOM_FL-FL_ANN"].edgec="black"
            master_datasets["FAOSTAT2019_FL-FL"].edgec="black"
            
            master_datasets["ORCHIDEE2019_FL-FL"].facec="black"
            master_datasets["EFISCEN-Space"].facec="blue"
            master_datasets["EFISCEN"].facec="skyblue"
            master_datasets["CBM2019"].facec="red"
            master_datasets["FLUXCOM_FL-FL_RF"].facec="orange"
            master_datasets["FLUXCOM_FL-FL_ANN"].facec="orangered"
            master_datasets["FAOSTAT2019_FL-FL"].facec="yellow"
            
            
            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif
            
        elif self.graphname == "trendyv7_all":
            self.desired_simulations=[ \
                                  "TrendyV7_ENSEMBLE", \
                                  'TrendyV7_CABLE', \
#                                  'TrendyV7_CLASS', \
                                  'TrendyV7_CLM5', \
                                  'TrendyV7_DLEM', \
                                  'TrendyV7_ISAM', \
                                  'TrendyV7_JSBACH', \
                                  'TrendyV7_JULES', \
                                  'TrendyV7_LPJ', \
                                  'TrendyV7_LPX', \
                                  'TrendyV7_OCN', \
#                                  'TrendyV7_ORCHIDEE-CNP', \
#                                  'TrendyV7_ORCHIDEE', \
#                                  'TrendyV7_SDGVM', \
                                  'TrendyV7_SURFEX', \
            ]   
            self.output_file_start="TRENDYv7All_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all TRENDY v7 bottom-up models"
            self.lplot_areas=True
            
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True

        elif self.graphname == "trendyv7_removed":
            self.desired_simulations=[ \
                                  "TrendyV7_ENSEMBLE", \
                                  'TrendyV7_CLASS', \
                                  'TrendyV7_ORCHIDEE-CNP', \
                                  'TrendyV7_ORCHIDEE', \
                                  'TrendyV7_SDGVM', \
            ]   
            self.output_file_start="TRENDYv7REMOVED_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v7 bottom-up models removed from the ensemble"
            self.lplot_areas=True
            
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True

        elif self.graphname == "trendyv7_common":
            self.desired_simulations=[ \
                                  'TrendyV7_COMMON', \
                                  'TrendyV7_CABLE', \
                                  'TrendyV7_CLM5', \
                                  'TrendyV7_DLEM', \
                                  'TrendyV7_JSBACH', \
                                  'TrendyV7_JULES', \
                                  'TrendyV7_LPX', \
                                  'TrendyV7_OCN', \
            ]   
            self.output_file_start="TRENDYv7COMMON_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v7 bottom-up models common with v9 and v10"

            master_datasets["TrendyV7_CLM5"].plotmarker="D"            
            master_datasets["TrendyV7_CLM5"].facec="blue"
            master_datasets["TrendyV7_CABLE"].plotmarker="D"            
            master_datasets["TrendyV7_CABLE"].facec="red"
            master_datasets["TrendyV7_JULES"].plotmarker="D"            
            master_datasets["TrendyV7_JULES"].facec="brown"
            master_datasets["TrendyV7_OCN"].plotmarker="D"            
            master_datasets["TrendyV7_OCN"].facec="limegreen"
            master_datasets["TrendyV7_DLEM"].plotmarker="D"            
            master_datasets["TrendyV7_DLEM"].facec="violet"
            master_datasets["TrendyV7_JSBACH"].plotmarker="D"            
            master_datasets["TrendyV7_JSBACH"].facec="orange"
            master_datasets["TrendyV7_LPX"].plotmarker="D"            
            master_datasets["TrendyV7_LPX"].facec="gold"

         

            master_datasets["TrendyV7_COMMON"].lplot_errorbar=True

        elif self.graphname == "trendyv9_all":
            self.desired_simulations=[ \
                                       "TrendyV9_ENSEMBLE", \
                                       "TrendyV9_CLASSIC", \
                                       "TrendyV9_CLM5", \
                                       "TrendyV9_ORCHIDEE-CNP", \
                                       "TrendyV9_ORCHIDEE", \
                                       "TrendyV9_ORCHIDEEv3", \
                                       "TrendyV9_SDGVM", \
                                       "TrendyV9_YIBs", \
                                       "TrendyV9_JULES-ES", \
                                       "TrendyV9_IBIS", \
                                       "TrendyV9_LPJ", \
                                       "TrendyV9_ISAM", \
                                       "TrendyV9_ISBA-CTRIP", \
                                       "TrendyV9_LPX-Bern", \
                                       "TrendyV9_VISIT", \
                                       "TrendyV9_OCN", \
                                       "TrendyV9_DLEM", \
                                       "TrendyV9_JSBACH", \
                                       "TrendyV9_CABLE-POP", \
                                       "TrendyV9_LPJ-GUESS", \
            ]   
# We removed these
            self.output_file_start="TRENDYv9All_"
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all TRENDY v9 bottom-up models"
            master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV9_ENSEMBLE"].facec="red"
            master_datasets["TrendyV9_ENSEMBLE"].uncert_color=master_datasets["TrendyV9_ENSEMBLE"].facec

        elif self.graphname == "trendyv9_removed":
            # None are removed
            self.desired_simulations=[ \
                                       "TrendyV9_ENSEMBLE", \
                                   ]
            self.output_file_start="TRENDYv9REMOVED_"
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v9 bottom-up models removed from the ensemble"
            master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV9_ENSEMBLE"].facec="red"
            master_datasets["TrendyV9_ENSEMBLE"].uncert_color=master_datasets["TrendyV9_ENSEMBLE"].facec

        elif self.graphname == "trendyv9_common":
            self.desired_simulations=[ \
                                  'TrendyV9_COMMON', \
                                  'TrendyV9_CABLE-POP', \
                                  'TrendyV9_CLM5', \
                                  'TrendyV9_DLEM', \
                                  'TrendyV9_JSBACH', \
                                  'TrendyV9_JULES-ES', \
                                  'TrendyV9_LPX-Bern', \
                                  'TrendyV9_OCN', \
            ]   
            self.output_file_start="TRENDYv9COMMON_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v9 bottom-up models common with v9 and v10"

            master_datasets["TrendyV9_CLM5"].plotmarker="D"            
            master_datasets["TrendyV9_CLM5"].facec="blue"
            master_datasets["TrendyV9_CABLE-POP"].plotmarker="D"            
            master_datasets["TrendyV9_CABLE-POP"].facec="red"
            master_datasets["TrendyV9_CABLE-POP"].displayname="TrendyV9_CABLE"
            master_datasets["TrendyV9_JULES-ES"].plotmarker="D"            
            master_datasets["TrendyV9_JULES-ES"].facec="brown"
            master_datasets["TrendyV9_JULES-ES"].displayname="TrendyV9_JULES"
            master_datasets["TrendyV9_OCN"].plotmarker="D"            
            master_datasets["TrendyV9_OCN"].facec="limegreen"
            master_datasets["TrendyV9_DLEM"].plotmarker="D"            
            master_datasets["TrendyV9_DLEM"].facec="violet"
            master_datasets["TrendyV9_JSBACH"].plotmarker="D"            
            master_datasets["TrendyV9_JSBACH"].facec="orange"
            master_datasets["TrendyV9_LPX-Bern"].plotmarker="D"            
            master_datasets["TrendyV9_LPX-Bern"].facec="gold"
            master_datasets["TrendyV9_LPX-Bern"].displayname="TrendyV9_LPX"

            master_datasets["TrendyV9_COMMON"].lplot_errorbar=True
            master_datasets["TrendyV9_COMMON"].facec="red"
            master_datasets["TrendyV9_COMMON"].uncert_color=master_datasets["TrendyV9_COMMON"].facec

        elif self.graphname == "trendyv10_all":
            self.desired_simulations=[ \
                                       "TrendyV10_ENSEMBLE", \
                                       "TrendyV10_ORCHIDEEv3", \
                                       "TrendyV10_ORCHIDEE", \
                                       "TrendyV10_CABLE-POP", \
                                       "TrendyV10_CLASSIC-N", \
                                       "TrendyV10_CLASSIC", \
                                       "TrendyV10_CLM5", \
                                       "TrendyV10_ISBA-CTRIP", \
                                       "TrendyV10_JSBACH", \
                                       "TrendyV10_JULES-ES", \
                                       "TrendyV10_LPJ-GUESS", \
                                       "TrendyV10_LPJwsl", \
                                       "TrendyV10_LPX-Bern", \
                                       "TrendyV10_OCN", \
                                       "TrendyV10_DLEM", \
                                       "TrendyV10_SDGVM", \
                                   ]
            # Removed
#                                       "TrendyV10_ISAM", \
            self.output_file_start="TRENDYv10All_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all TRENDY v10 bottom-up models"
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].facec="blue"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

        elif self.graphname == "trendyv10_removed":
            self.desired_simulations=[ \
                                       "TrendyV10_ENSEMBLE", \
                                       "TrendyV10_ISAM", \
                                       ]
            self.output_file_start="TRENDYv10REMOVED_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v10 bottom-up models removed from the ensemble"
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].facec="blue"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

        elif self.graphname == "trendyv10_common":
            self.desired_simulations=[ \
                                  'TrendyV10_COMMON', \
                                  'TrendyV10_CABLE-POP', \
                                  'TrendyV10_CLM5', \
                                  'TrendyV10_DLEM', \
                                  'TrendyV10_JSBACH', \
                                  'TrendyV10_JULES-ES', \
                                  'TrendyV10_LPX-Bern', \
                                  'TrendyV10_OCN', \
            ]   
            self.output_file_start="TRENDYv10COMMON_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from TRENDY v10 bottom-up models common with v7 and v9"

            master_datasets["TrendyV10_CLM5"].plotmarker="D"            
            master_datasets["TrendyV10_CLM5"].facec="blue"
            master_datasets["TrendyV10_CABLE-POP"].plotmarker="D"            
            master_datasets["TrendyV10_CABLE-POP"].facec="red"
            master_datasets["TrendyV10_CABLE-POP"].displayname="TrendyV10_CABLE"
            master_datasets["TrendyV10_JULES-ES"].plotmarker="D"            
            master_datasets["TrendyV10_JULES-ES"].facec="brown"
            master_datasets["TrendyV10_JULES-ES"].displayname="TrendyV10_JULES"
            master_datasets["TrendyV10_OCN"].plotmarker="D"            
            master_datasets["TrendyV10_OCN"].facec="limegreen"
            master_datasets["TrendyV10_DLEM"].plotmarker="D"            
            master_datasets["TrendyV10_DLEM"].facec="violet"
            master_datasets["TrendyV10_JSBACH"].plotmarker="D"            
            master_datasets["TrendyV10_JSBACH"].facec="orange"
            master_datasets["TrendyV10_LPX-Bern"].plotmarker="D"            
            master_datasets["TrendyV10_LPX-Bern"].facec="gold"
            master_datasets["TrendyV10_LPX-Bern"].displayname="TrendyV10_LPX"

         

            master_datasets["TrendyV10_COMMON"].lplot_errorbar=True
            master_datasets["TrendyV10_COMMON"].facec="blue"
            master_datasets["TrendyV10_COMMON"].uncert_color=master_datasets["TrendyV10_COMMON"].facec

        elif self.graphname == "trendycomparison":
            self.desired_simulations=[ \
                                       "TrendyV7_ENSEMBLE", \
                                       "TrendyV9_ENSEMBLE", \
                                       "TrendyV10_ENSEMBLE", \
                                   ]
            self.output_file_start="TRENDYComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all three versions of TRENDY bottom-up models"
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True

            master_datasets["TrendyV10_ENSEMBLE"].facec="blue"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

            master_datasets["TrendyV7_ENSEMBLE"].facec="gray"
            master_datasets["TrendyV7_ENSEMBLE"].uncert_color=master_datasets["TrendyV7_ENSEMBLE"].facec

            master_datasets["TrendyV9_ENSEMBLE"].facec="red"
            master_datasets["TrendyV9_ENSEMBLE"].uncert_color=master_datasets["TrendyV9_ENSEMBLE"].facec

            self.lexternal_y=True
            self.ymin_external=-625.0
            self.ymax_external=410.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "trendycommon":
            self.desired_simulations=[ \
                                       "TrendyV7_COMMON", \
                                       "TrendyV9_COMMON", \
                                       "TrendyV10_COMMON", \
                                   ]
            self.output_file_start="TRENDYCommon_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from versions of TRENDY bottom-up models for the common models"
            master_datasets["TrendyV7_COMMON"].lplot_errorbar=True
            master_datasets["TrendyV9_COMMON"].lplot_errorbar=True
            master_datasets["TrendyV10_COMMON"].lplot_errorbar=True

            master_datasets["TrendyV10_COMMON"].facec="blue"
            master_datasets["TrendyV10_COMMON"].uncert_color=master_datasets["TrendyV10_COMMON"].facec

            master_datasets["TrendyV7_COMMON"].facec="gray"
            master_datasets["TrendyV7_COMMON"].uncert_color=master_datasets["TrendyV7_COMMON"].facec

            master_datasets["TrendyV9_COMMON"].facec="red"
            master_datasets["TrendyV9_COMMON"].uncert_color=master_datasets["TrendyV9_COMMON"].facec

            self.lexternal_y=True
            self.ymin_external=-625.0
            self.ymax_external=410.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

            ####
        elif self.graphname == "trendyv10_gcp2021_all":
            self.desired_simulations=[ \
                                       "TrendyV10_ENSEMBLE", \
                                       "TrendyV10_ORCHIDEEv3", \
                                       "TrendyV10_ORCHIDEE", \
                                       "TrendyV10_CABLE-POP", \
                                       "TrendyV10_CLASSIC-N", \
                                       "TrendyV10_CLASSIC", \
                                       "TrendyV10_CLM5", \
                                       "TrendyV10_ISBA-CTRIP", \
                                       "TrendyV10_JSBACH", \
                                       "TrendyV10_JULES-ES", \
                                       "TrendyV10_LPJ-GUESS", \
                                       "TrendyV10_LPJwsl", \
                                       "TrendyV10_LPX-Bern", \
                                       "TrendyV10_OCN", \
                                       "TrendyV10_DLEM", \
                                       "TrendyV10_SDGVM", \
                                       'GCP2021_ALL', \
                                       'GCP2021_CAMS', \
                                       #                                  'GCP2021_CMS', \
                                       'GCP2021_CTRACKER', \
                                       'GCP2021_JENA-s99', \
                                       'GCP2021_JENA-sEXT', \
                                       'GCP2021_NIES', \
                                       'GCP2021_UoE', \
                                   ]
            self.output_file_start="GCPInversions2021Trendyv10All_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP-2021 inversions and Trendyv10 models"
            
            master_datasets['GCP2021_ALL'].lplot_errorbar=True

            master_datasets["GCP2021_ALL"].facec="gray"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].facec="blue"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

        elif self.graphname == "trendyv10_gcp2021":
            self.desired_simulations=[ \
                                       "TrendyV10_ENSEMBLE", \
                                       'GCP2021_ALL', \
                                   ]
            self.output_file_start="GCPInversions2021Trendyv10_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP-2021 inversions and Trendyv10 models"
            
            master_datasets['GCP2021_ALL'].lplot_errorbar=True

            master_datasets["GCP2021_ALL"].facec="gray"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].facec="blue"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

        elif self.graphname == "trendyv9_gcp":
            self.desired_simulations=[ \
                                       "TrendyV9_ENSEMBLE", \
                                       "TrendyV9_CLASSIC", \
                                       "TrendyV9_CLM5", \
                                       "TrendyV9_ORCHIDEE-CNP", \
                                       "TrendyV9_ORCHIDEE", \
                                       "TrendyV9_ORCHIDEEv3", \
                                       "TrendyV9_SDGVM", \
                                       "TrendyV9_YIBs", \
                                       "TrendyV9_JULES-ES", \
                                       "TrendyV9_IBIS", \
                                       "TrendyV9_LPJ", \
                                       "TrendyV9_ISAM", \
                                       "TrendyV9_ISBA-CTRIP", \
                                       "TrendyV9_LPX-Bern", \
                                       "TrendyV9_VISIT", \
                                       "TrendyV9_OCN", \
                                       "GCP2019_ALL",\
            ]   
# We removed these.
#                                       "TrendyV9_DLEM", \
#                                       "TrendyV9_JSBACH", \
#                                       "TrendyV9_CABLE-POP", \
#                                       "TrendyV9_LPJ-GUESS", \
            self.output_file_start="TRENDYv9GCP2019_"
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : CO$_2$ emissions from all TRENDY v9 bottom-up models and GCP"
            master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].lplot_errorbar=True

        elif self.graphname == "trendy_gcp":
            self.desired_simulations=[ \
                                       "TrendyV7_ENSEMBLE", \
                                       "TrendyV9_ENSEMBLE", \
                                       "GCP2019_ALL",\
            ]   
            self.output_file_start="TRENDYvsGCP2019_"
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : CO$_2$ emissions from ensemble averages of TRENDY v7,v9 and GCP"
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            master_datasets["TrendyV9_ENSEMBLE"].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].lplot_errorbar=True

            master_datasets['GCP2019_ALL'].uncert_color='green'
            master_datasets["TrendyV7_ENSEMBLE"].uncert_color='grey'
            master_datasets["TrendyV9_ENSEMBLE"].uncert_color='blue'
            master_datasets['GCP2019_ALL'].facec='green'
            master_datasets["TrendyV7_ENSEMBLE"].facec='grey'
            master_datasets["TrendyV9_ENSEMBLE"].facec='blue'

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
            
            master_datasets['FLUXCOM_rsonlyRF_os'].plotmarker="s"
            master_datasets['FLUXCOM_rsonlyANN_os'].plotmarker="s"
            master_datasets['FLUXCOM_rsonlyRF_ns'].plotmarker="o"
            master_datasets['FLUXCOM_rsonlyANN_ns'].plotmarker="o"
            master_datasets["FLUXCOM_CL-CL_RF"].plotmarker="P"
            master_datasets["FLUXCOM_FL-FL_RF"].plotmarker="X"
            master_datasets["FLUXCOM_GL-GL_RF"].plotmarker="^"
            master_datasets["FLUXCOM_CL-CL_ANN"].plotmarker="P"
            master_datasets["FLUXCOM_FL-FL_ANN"].plotmarker="X"
            master_datasets["FLUXCOM_GL-GL_ANN"].plotmarker="^"
            
            master_datasets["FLUXCOM_rsonlyRF_os"].facec="blue"
            master_datasets["FLUXCOM_rsonlyANN_os"].facec="red"
            master_datasets["FLUXCOM_rsonlyRF_ns"].facec="blue"
            master_datasets["FLUXCOM_CL-CL_RF"].facec="blue"
            master_datasets["FLUXCOM_FL-FL_RF"].facec="blue"
            master_datasets["FLUXCOM_GL-GL_RF"].facec="blue"
            master_datasets["FLUXCOM_rsonlyANN_ns"].facec="red"
            master_datasets["FLUXCOM_CL-CL_ANN"].facec="red"
            master_datasets["FLUXCOM_GL-GL_ANN"].facec="red"
            master_datasets["FLUXCOM_FL-FL_ANN"].facec="red"
            
            
            # These simulations will be combined together.
            self.overwrite_simulations["FLUXCOM_rsonlyANN_ns"]=['FLUXCOM_FL-FL_ANN','FLUXCOM_GL-GL_ANN','FLUXCOM_CL-CL_ANN']
            # So I don't want to generally plot the components
            master_datasets['FLUXCOM_FL-FL_ANN'].displaylegend=True
            master_datasets['FLUXCOM_GL-GL_ANN'].displaylegend=True
            master_datasets['FLUXCOM_CL-CL_ANN'].displaylegend=True
            
            self.overwrite_simulations["FLUXCOM_rsonlyRF_ns"]=['FLUXCOM_FL-FL_RF','FLUXCOM_GL-GL_RF','FLUXCOM_CL-CL_RF']
            # So I don't want to generally plot the components
            master_datasets['FLUXCOM_FL-FL_RF'].displaylegend=True
            master_datasets['FLUXCOM_GL-GL_RF'].displaylegend=True
            master_datasets['FLUXCOM_CL-CL_RF'].displaylegend=True
            
        elif self.graphname == "forestremain_2019":

            # Changing this removes the forest areas being
            # plotted on the graph
            self.lplot_areas=False


            self.desired_simulations=[ \
                                  'ORCHIDEE2019_FL-FL', \
                                  #'ORCHIDEE_Tier2_Forest', \
                                  'EFISCEN', \
                                  #  'EFISCEN_NPP', \
                                  #  'EFISCEN_NEE', \
                                  #   'EFISCEN-unscaled', \
                                  #                            'EFISCEN-Space', \
                                  'CBM2019', \
                                  'UNFCCC2019_FL-FL', \
                                  #'FLUXCOM_FL-FL_ANN', \
                                  #'FLUXCOM_FL-FL_RF', \
                                  'FAOSTAT2019_FL-FL', \
                                  'LUH2v2_FOREST', \
                                  'UNFCCC_FOREST', \
            ]   
            
            master_datasets['UNFCCC_FOREST'].displayname='UNFCCC_FL-FL area'
            master_datasets['LUH2v2_FOREST'].displayname='LUH2v2-ESACCI_FL-FL area (used in ORCHIDEE)'
            master_datasets['FAOSTAT2019_FL-FL'].displayname='FAOSTAT_FL-FL'
            master_datasets['ORCHIDEE2019_FL-FL'].displayname='ORCHIDEE_FL-FL'
            master_datasets['EFISCEN'].displayname='EFISCEN_FL-FL'
            master_datasets['CBM2019'].displayname='CBM_FL-FL'
            self.desired_legend=[\
                            master_datasets['UNFCCC2019_FL-FL'].displayname,master_datasets["UNFCCC2019_FL-FL"].displayname_err,\
                            master_datasets['FAOSTAT2019_FL-FL'].displayname, \
                            master_datasets['ORCHIDEE2019_FL-FL'].displayname, \
                            master_datasets['EFISCEN'].displayname, \
                            # master_datasets['EFISCEN_NPP'].displayname, \
                            # master_datasets['EFISCEN_NEE'].displayname, \
                            #                       'EFISCEN-Space', \
                            master_datasets['CBM2019'].displayname, \
                            #master_datasets['ORCHIDEE_Tier2_Forest'].displayname, \
                            #master_datasets['FLUXCOM_FL-FL_ANN'].displayname, \
                            #master_datasets['FLUXCOM_FL-FL_RF'].displayname, \
                            master_datasets['LUH2v2_FOREST'].displayname, \
                            master_datasets['UNFCCC_FOREST'].displayname, \
            ]
            
            self.output_file_start="ForestRemain_"
            # v1 has EFISCEN data from a spreadsheet sent by Mart-Jan in April 2020
            #      self.output_file_end="_FCO2land_2019_v1.png" 
            # v2 has EFISCEn data from June 2020
            self.output_file_end="_FCO2land_2019_v2.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from forest land remaining forest land (FL-FL)"
            
            self.lexternal_y=True
            self.ymin_external=-260.0
            self.ymax_external=125.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

        elif self.graphname == "forestremain_2021":

            # Changing this removes the forest areas being
            # plotted on the graph
            self.lplot_areas=False


            self.desired_simulations=[ \
                                  'ORCHIDEE2020_FL-FL', \
                                  #'ORCHIDEE_Tier2_Forest', \
                                  'EFISCEN', \
                                  #  'EFISCEN_NPP', \
                                  #  'EFISCEN_NEE', \
                                  #   'EFISCEN-unscaled', \
                                  #                            'EFISCEN-Space', \
                                  'CBM2021historical', \
                                  'CBM2021simulated', \
                                  'UNFCCC2021_FL-FL', \
                                  #'FLUXCOM_FL-FL_ANN', \
                                  #'FLUXCOM_FL-FL_RF', \
                                  'FAOSTAT2021_FL-FL', \
                                  'LUH2v2_FOREST', \
                                  'UNFCCC_FOREST', \
            ]   
            
            master_datasets['UNFCCC_FOREST'].displayname='UNFCCC_FL-FL area'
            master_datasets['LUH2v2_FOREST'].displayname='LUH2v2-ESACCI_FL-FL area (used in ORCHIDEE)'
            master_datasets['EFISCEN'].displayname='EFISCEN_FL-FL'
  
            self.desired_legend=[\
                            master_datasets['UNFCCC2021_FL-FL'].displayname,master_datasets["UNFCCC2021_FL-FL"].displayname_err,\
                            master_datasets['FAOSTAT2021_FL-FL'].displayname, \
                            master_datasets['ORCHIDEE2020_FL-FL'].displayname, \
                            master_datasets['EFISCEN'].displayname, \
                            master_datasets['CBM2021historical'].displayname, \
                            master_datasets['CBM2021simulated'].displayname, \
                            master_datasets['LUH2v2_FOREST'].displayname, \
                            master_datasets['UNFCCC_FOREST'].displayname, \
            ]
            
            self.output_file_start="ForestRemain_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from forest land remaining forest land (FL-FL)"
            
            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-260.0
            self.ymax_external=125.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif
           
            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif
            
        elif self.graphname == "grasslandremain_2019":
            self.desired_simulations=[ \
                                  'ORCHIDEE2019_GL-GL', \
                                  'ECOSSE2019_GL-GL-lim', \
                                  'UNFCCC2019_GL-GL', \
                                  'LUH2v2_GRASS', \
                                  'UNFCCC_GRASS', \
            ]   
            self.output_file_start="GrasslandRemain_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from grassland remaining grassland (GL-GL)"
            
            # Change some things from the above
            master_datasets['ECOSSE2019_GL-GL-lim'].displayname='ECOSSE_GL-GL'
            master_datasets['UNFCCC_GRASS'].displayname='UNFCCC2019_GL-GL area'
            master_datasets['LUH2v2_GRASS'].displayname='LUH2v2-ESACCI_GL-GL area (used in ORCHIDEE)'
            self.lplot_areas=False
            
            master_datasets['ECOSSE2019_GL-GL-lim'].displayname='ECOSSE_GL-GL'
            master_datasets['ORCHIDEE2019_GL-GL'].displayname='ORCHIDEE_GL-GL'

            #if lshow_productiondata:
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            self.desired_legend=[\
                            master_datasets['UNFCCC2019_GL-GL'].displayname,master_datasets["UNFCCC2019_GL-GL"].displayname_err,\
                            master_datasets['ORCHIDEE2019_GL-GL'].displayname, \
                          #  master_datasets['ORCHIDEE2019_GL-GL-NPP'].displayname, \
                            #master_datasets['ORCHIDEE_RH'].displayname, \
                            master_datasets['ECOSSE2019_GL-GL-lim'].displayname, \
                         #   master_datasets['ECOSSE_GL-GL-RH'].displayname, \
                         #   master_datasets['ECOSSE_GL-GL-NPP'].displayname, \
                          #  master_datasets['ECOSSE_GL-GL-SOC'].displayname, \
                            #master_datasets['ECOSSE_GL-GL-nolim'].displayname, \
                            # 'FLUXCOM_GL-GL_ANN', \
                            # 'FLUXCOM_GL-GL_RF', \
                            master_datasets['LUH2v2_GRASS'].displayname, \
                            master_datasets['UNFCCC_GRASS'].displayname, \
                        ]

            self.lexternal_y=True
            self.ymin_external=-140.0
            self.ymax_external=190.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "grasslandremain_2021":
            self.desired_simulations=[ \
                                  'ORCHIDEE2019_GL-GL', \
                                  'ECOSSE2019_GL-GL-lim', \
                                  'EPIC2021_NBP_GRS', \
                                  'FAOSTAT2021_GL-GL', \
                                  'UNFCCC2021_GL-GL', \
                                  'LUH2v2_GRASS', \
                                  'UNFCCC_GRASS', \
            ]   
            self.output_file_start="GrasslandRemain_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from grassland remaining grassland (GL-GL)"
            
            # Change some things from the above
            master_datasets['UNFCCC_GRASS'].displayname='UNFCCC2019_GL-GL area'
            master_datasets['LUH2v2_GRASS'].displayname='LUH2v2-ESACCI_GL-GL area (used in ORCHIDEE)'
            self.lplot_areas=False
            
            master_datasets['ECOSSE2019_GL-GL-lim'].displayname='ECOSSE_GL-GL'
            master_datasets['ORCHIDEE2019_GL-GL'].displayname='ORCHIDEE_GL-GL'
            master_datasets['FAOSTAT2021_GL-GL'].displayname='FAOSTATv2_GL-GL'
     
            #if lshow_productiondata:
            #   productiondata_master['ECOSSE_GL-GL']=False
            #endif
            self.desired_legend=[\
                            master_datasets['UNFCCC2021_GL-GL'].displayname,master_datasets["UNFCCC2021_GL-GL"].displayname_err,\
                            master_datasets['FAOSTAT2021_GL-GL'].displayname, \
                            master_datasets['ORCHIDEE2019_GL-GL'].displayname, \
                            master_datasets['ECOSSE2019_GL-GL-lim'].displayname, \
                            master_datasets['EPIC2021_NBP_GRS'].displayname, \
                            master_datasets['LUH2v2_GRASS'].displayname, \
                            master_datasets['UNFCCC_GRASS'].displayname, \
                        ]

            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-140.0
            self.ymax_external=190.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif
            
        elif self.graphname == "grassland_all":
            self.desired_simulations=[ \
                                  'ORCHIDEE2019_GL-GL', \
                                #  'ORCHIDEE2019_GL-GL-NPP', \
                                  #'ORCHIDEE_RH', \
                                  'ECOSSE2019_GL-GL-lim', \
                                #  'ECOSSE_GL-GL-RH', \
                                #  'ECOSSE_GL-GL-NPP', \
                               #   'ECOSSE_GL-GL-SOC', \
                                #  'ECOSSE_GL-GL-nolim', \
                                  #  'ECOSSE_GL-GL_us', \
                                  'UNFCCC2019_GL-GL', \
                                  "FAOSTAT2021_GL-GL", \
                                  "EPIC2021_NBP_GRS", \
                                  "EPIC2021_RH_GRS", \
            ]   
            self.output_file_start="GrasslandAll_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from grassland remaining grassland (GL-GL)"
            
            # Change some things from the above
            self.lplot_areas=False
            
            master_datasets['ECOSSE2019_GL-GL-lim'].displayname='ECOSSE (v2019) GL-GL'
            
          
        elif self.graphname == "epic_comparison":
            # Testing croplands and grasslands from EPIC
            self.desired_simulations=[ \
                                  'EPIC2019_NBP_CRP', \
#                                  'EPIC2019_RH_CRP', \
#                                  'EPIC2019_NPP_CRP', \
                                  'EPIC2021_NBP_CRP', \
#                                  'EPIC2021_RH_CRP', \
#                                  'EPIC2021_NPP_CRP', \
#                                  'EPIC2021_FHARVEST_CRP', \
#                                  'EPIC2021_LEECH_CRP', \
                                  "EPIC2021_NBP_GRS", \
#                                  "EPIC2021_RH_GRS", \
#                                  "EPIC2021_NPP_GRS", \
#                                  "EPIC2021_FHARVEST_GRS", \
#                                  "EPIC2021_LEECH_GRS", \
                              ]   
            
            self.output_file_start="EPICComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland and grasslands in EPIC"

            master_datasets["EPIC2019_NBP_CRP"].facec="gray"
            master_datasets["EPIC2021_NBP_CRP"].facec="blue"
            master_datasets["EPIC2021_NBP_GRS"].facec="red"

            master_datasets["EPIC2019_NBP_CRP"].plotmarker="s"
            master_datasets["EPIC2021_NBP_GRS"].plotmarker="s"
            master_datasets["EPIC2021_NBP_CRP"].plotmarker="s"

            master_datasets["EPIC2019_NBP_CRP"].plot_lines=True
            master_datasets["EPIC2021_NBP_CRP"].plot_lines=True
            master_datasets["EPIC2021_NBP_GRS"].plot_lines=True

            master_datasets["EPIC2019_NBP_CRP"].linestyle="dashed"

            #### 

        elif self.graphname == "croplandremain_2019":
            self.desired_simulations=[ \
                                  'ORCHIDEE2019_CL-CL', \
                                  # 'ORCHIDEE_RH', \
                                  'ECOSSE2019_CL-CL', \
                                  #       'ECOSSE2019_CL-CL_NPP', \
                                  #       'ECOSSE2019_CL-CL_FHARVEST', \
                                  #       'ECOSSE2019_CL-CL_RH', \
                                  #     'ECOSSE2019_CL-CL_us', \
                                  'UNFCCC2019_CL-CL', \
                                  #    'FLUXCOM_CL-CL_ANN', \
                                  #    'FLUXCOM_CL-CL_RF', \
                                  'EPIC2019_NBP_CRP', \
                                  # 'EPIC_RH', \
                                  'LUH2v2_CROP', \
                                  'UNFCCC_CROP', \
                              ]   
            
            master_datasets['UNFCCC_CROP'].displayname='UNFCCC_CL-CL area'
            master_datasets['LUH2v2_CROP'].displayname='LUH2v2-ESACCI_CL-CL area (used in ORCHIDEE)'
            
            self.desired_legend=[\
                            master_datasets['UNFCCC2019_CL-CL'].displayname,master_datasets["UNFCCC2019_CL-CL"].displayname_err,\
                            master_datasets['ORCHIDEE2019_CL-CL'].displayname, \
                            master_datasets['ECOSSE2019_CL-CL'].displayname, \
                            #    master_datasets['ECOSSE2019_CL-CL_RH'].displayname, \
                            #     master_datasets['ECOSSE2019_CL-CL_NPP'].displayname, \
                            #       master_datasets['ECOSSE2019_CL-CL_FHARVEST'].displayname, \
                            master_datasets['EPIC2019_NBP_CRP'].displayname, \
                            #  'FLUXCOM_CL-CL_ANN', \
                            #  'FLUXCOM_CL-CL_RF', \
                            # 'ORCHIDEE_RH', \
                            # 'EPIC_RH', \
                            master_datasets['LUH2v2_CROP'].displayname, \
                            master_datasets['UNFCCC_CROP'].displayname, \
                        ]
            
            self.output_file_start="CroplandRemain_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland remaining cropland (CL-CL)"
            
            # Change some things from the above
            self.lplot_areas=False
            
            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1


        elif self.graphname == "croplandremain_2021":
            self.desired_simulations=[ \
                                  'FAOSTAT2021_CL-CL', \
                                  'ORCHIDEE2019_CL-CL', \
                                  'ECOSSE2019_CL-CL', \
                                  'UNFCCC2021_CL-CL', \
                                  'EPIC2021_NBP_CRP', \
                              ]   
            
#            master_datasets['UNFCCC_CROP'].displayname='UNFCCC_CL-CL area'
#            master_datasets['LUH2v2_CROP'].displayname='LUH2v2-ESACCI_CL-CL area (used in ORCHIDEE)'
            
            self.desired_legend=[\
                            master_datasets['UNFCCC2021_CL-CL'].displayname,master_datasets["UNFCCC2021_CL-CL"].displayname_err,\
                            master_datasets['FAOSTAT2021_CL-CL'].displayname, \
                            master_datasets['ORCHIDEE2019_CL-CL'].displayname, \
                            master_datasets['ECOSSE2019_CL-CL'].displayname, \
                            master_datasets['EPIC2021_NBP_CRP'].displayname, \
#                            master_datasets['LUH2v2_CROP'].displayname, \
#                            master_datasets['UNFCCC_CROP'].displayname, \
                        ]
            
            self.output_file_start="CroplandRemain_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland remaining cropland (CL-CL)"
            
            # Change some things from the above
            self.lplot_areas=False
            
            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

        elif self.graphname == "crops_fao_epic":
            self.desired_simulations=[ \
                                  'EPIC2019_NBP_CRP', \
                                  'EPIC2019_RH_CRP', \
                                  'EPIC2021_NBP_CRP', \
                                  'EPIC2021_RH_CRP', \
                                       "FAOSTAT2019_CRP", \
                                       "FAOSTAT2020_CRP", \
                                       "FAOSTAT2021_CL-CL", \
#                                       "UNFCCC2019_CL-CL", \
                              ]   
            
            self.output_file_start="CroplandFAOEPIC_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland remaining cropland (CL-CL)"
            
            ####    

        elif self.graphname == "epic_test_rh":
            # Testing croplands and grasslands from EPIC, just RH
            self.desired_simulations=[ \
                                  'EPIC2019_RH_CRP', \
                                  'EPIC2021_RH_CRP', \
                                  "EPIC2021_RH_GRS", \
                              ]   
            
            self.output_file_start="EPICRh_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland and grasslands in EPIC"

            master_datasets["EPIC2019_RH_CRP"].facec="gray"
            master_datasets["EPIC2019_RH_CRP"].plotmarker="P"

            master_datasets["EPIC2021_RH_CRP"].facec="gray"
            master_datasets["EPIC2021_RH_CRP"].plotmarker="X"

            master_datasets["EPIC2021_RH_GRS"].facec="lightcoral"
            master_datasets["EPIC2021_RH_GRS"].plotmarker="o"

        elif self.graphname == "epic_test_npp":
            # Testing croplands and grasslands from EPIC, just NPP
            self.desired_simulations=[ \
                                  'EPIC2019_NPP_CRP', \
                                  'EPIC2021_NPP_CRP', \
                                  "EPIC2021_NPP_GRS", \
                              ]   
            
            self.output_file_start="EPICNpp_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland and grasslands in EPIC"

            master_datasets["EPIC2019_NPP_CRP"].facec="gray"
            master_datasets["EPIC2019_NPP_CRP"].plotmarker="P"

            master_datasets["EPIC2021_NPP_CRP"].facec="gray"
            master_datasets["EPIC2021_NPP_CRP"].plotmarker="X"

            master_datasets["EPIC2021_NPP_GRS"].facec="lightcoral"
            master_datasets["EPIC2021_NPP_GRS"].plotmarker="o"

        elif self.graphname == "epic_test_fharvest":
            # Testing croplands and grasslands from EPIC, just FHARVEST
            self.desired_simulations=[ \
                                  'EPIC2019_FHARVEST_CRP', \
                                  'EPIC2021_FHARVEST_CRP', \
                                  "EPIC2021_FHARVEST_GRS", \
                              ]   
            
            self.output_file_start="EPICFharvest_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland and grasslands in EPIC"

            master_datasets["EPIC2019_FHARVEST_CRP"].facec="gray"
            master_datasets["EPIC2019_FHARVEST_CRP"].plotmarker="P"

            master_datasets["EPIC2021_FHARVEST_CRP"].facec="gray"
            master_datasets["EPIC2021_FHARVEST_CRP"].plotmarker="X"

            master_datasets["EPIC2021_FHARVEST_GRS"].facec="lightcoral"
            master_datasets["EPIC2021_FHARVEST_GRS"].plotmarker="o"

        elif self.graphname == "epic_test_leech":
            # Testing croplands and grasslands from EPIC, just LEECH
            self.desired_simulations=[ \
                                  'EPIC2019_LEECH_CRP', \
                                  'EPIC2021_LEECH_CRP', \
                                  "EPIC2021_LEECH_GRS", \
                              ]   
            
            self.output_file_start="EPICLeech_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from cropland and grasslands in EPIC"

            master_datasets["EPIC2019_LEECH_CRP"].facec="gray"
            master_datasets["EPIC2019_LEECH_CRP"].plotmarker="P"

            master_datasets["EPIC2021_LEECH_CRP"].facec="gray"
            master_datasets["EPIC2021_LEECH_CRP"].plotmarker="X"

            master_datasets["EPIC2021_LEECH_GRS"].facec="lightcoral"
            master_datasets["EPIC2021_LEECH_GRS"].plotmarker="o"





            ####   

        elif self.graphname == "orchidees3comparison":
            self.desired_simulations=[ \
                                  'ORCHIDEEv2-S3-V2021v2', \
                                  'ORCHIDEEv3-S3-V2021v2', \
#                                  'ORCHIDEEv2-S3-V2021', \
#                                  'ORCHIDEEv3-S3-V2021', \
                                  'ORCHIDEE-S3-V2020', \
                                  'ORCHIDEE-S3-V2019', \
                              ]   
            
            master_datasets["ORCHIDEE-S3-V2019"].displayname="ORCHIDEE v2019"
            master_datasets["ORCHIDEE-S3-V2020"].displayname="ORCHIDEE v2020"
            master_datasets["ORCHIDEEv2-S3-V2021"].displayname="ORCHIDEE v2021"
            master_datasets["ORCHIDEEv3-S3-V2021"].displayname="ORCHIDEE-N v2021"
            master_datasets["ORCHIDEEv2-S3-V2021v2"].displayname="ORCHIDEE v2021"
            master_datasets["ORCHIDEEv3-S3-V2021v2"].displayname="ORCHIDEE-N v2021"
#            master_datasets["ORCHIDEEv2-S3-V2021v2"].displayname="ORCHIDEE v2021 (corrected)"
#            master_datasets["ORCHIDEEv3-S3-V2021v2"].displayname="ORCHIDEE-N v2021 (corrected)"

            self.desired_legend=[\
                            master_datasets["ORCHIDEE-S3-V2019"].displayname, \
                            master_datasets['ORCHIDEE-S3-V2020'].displayname, \
#                            master_datasets['ORCHIDEEv2-S3-V2021'].displayname, \
#                            master_datasets['ORCHIDEEv3-S3-V2021'].displayname, \
                            master_datasets['ORCHIDEEv2-S3-V2021v2'].displayname, \
                            master_datasets['ORCHIDEEv3-S3-V2021v2'].displayname, \
                        ]
            
            self.output_file_start="ORCHIDEES3Comparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from ORCHIDEE for three different dataset years"
            
            # Change some colors and symbols
            master_datasets["ORCHIDEE-S3-V2019"].plotmarker="P"
            master_datasets["ORCHIDEE-S3-V2020"].plotmarker="P"
            master_datasets["ORCHIDEEv2-S3-V2021"].plotmarker="P"
            master_datasets["ORCHIDEEv3-S3-V2021"].plotmarker="D"
            master_datasets["ORCHIDEEv2-S3-V2021v2"].plotmarker="P"
            master_datasets["ORCHIDEEv3-S3-V2021v2"].plotmarker="D"

            master_datasets["ORCHIDEE-S3-V2019"].facec="gray"
            master_datasets["ORCHIDEE-S3-V2020"].facec="red"
            master_datasets["ORCHIDEEv3-S3-V2021"].facec="skyblue"
            master_datasets["ORCHIDEEv2-S3-V2021"].facec="skyblue"
            master_datasets["ORCHIDEEv3-S3-V2021v2"].facec="blue"
            master_datasets["ORCHIDEEv2-S3-V2021v2"].facec="blue"

            master_datasets["ORCHIDEE-S3-V2019"].plot_lines=True
            master_datasets["ORCHIDEE-S3-V2019"].linestyle="dashed"
            master_datasets["ORCHIDEE-S3-V2020"].plot_lines=True
            master_datasets["ORCHIDEE-S3-V2020"].linestyle="dashed"
            master_datasets["ORCHIDEEv2-S3-V2021"].plot_lines=True
            master_datasets["ORCHIDEEv2-S3-V2021"].linestyle="dashed"
            master_datasets["ORCHIDEEv3-S3-V2021"].plot_lines=True
            master_datasets["ORCHIDEEv3-S3-V2021"].linestyle="dashed"
            master_datasets["ORCHIDEEv2-S3-V2021v2"].plot_lines=True
            master_datasets["ORCHIDEEv2-S3-V2021v2"].linestyle="solid"
            master_datasets["ORCHIDEEv3-S3-V2021v2"].plot_lines=True
            master_datasets["ORCHIDEEv3-S3-V2021v2"].linestyle="solid"


            ####          

        elif self.graphname == "biofuels":

            self.desired_simulations=[ \
                                  'UNFCCC_biofuels', \
                                  'TNO_biofuels', \
                              ]   
            self.output_file_start="biofuels_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : CO$_2$ emissions from biofuel combustion"
            master_datasets['UNFCCC_biofuels'].facec='red'
            master_datasets['TNO_biofuels'].facec='blue'
            
        elif self.graphname == "emission_factors":
            self.desired_simulations=[ \
                                  'ORCHIDEE_Tier2_Forest_EF1', \
#                                  'ORCHIDEE_Tier2_Forest_EF2', \
#                                  'ORCHIDEE_Tier2_Forest_EF3', \
                                  'ORCHIDEE_Tier2_Forest_EF4', \
                              ]   
            
            self.output_file_start="FL-FLEmissionFactors_"
            self.output_file_end="_FCO2land_2019_v1.png" 
            self.titleending=r" : FL-FL bottom-up emission factors"
            self.lplot_areas=False
            
            
        elif self.graphname == "eurocominversions":
            self.desired_simulations=[ \
                                  'EUROCOM_ALL_2019', \
                                  'EUROCOM_Carboscope', \
                                  'CSR-COMBINED-2019', \
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
            
            master_datasets['EUROCOM_ALL_2019'].lplot_errorbar=True

        elif self.graphname == "cams":
            self.desired_simulations=[ \
                                  'GCP2019_CAMS', \
                                  'GCP2020_CAMS', \
                                  'GCP2021_CAMS', \
                              ]   
            self.output_file_start="CAMSInversionsAll_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from global CAMS inversions"
            
            master_datasets["GCP2019_CAMS"].facec="gray"
            master_datasets["GCP2019_CAMS"].plotmarker="o"
            master_datasets["GCP2019_CAMS"].plot_lines=True
            master_datasets["GCP2020_CAMS"].facec="red"
            master_datasets["GCP2020_CAMS"].plotmarker="s"
            master_datasets["GCP2020_CAMS"].plot_lines=True
            master_datasets["GCP2021_CAMS"].facec="blue"
            master_datasets["GCP2021_CAMS"].plotmarker="X"
            master_datasets["GCP2021_CAMS"].plot_lines=True

        elif self.graphname == "ctracker":
            self.desired_simulations=[ \
                                  'GCP2019_CTRACKER', \
                                  'GCP2020_CTRACKER', \
                                  'GCP2021_CTRACKER', \
                              ]   
            self.output_file_start="CTRACKERInversionsAll_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from global CTRACKER inversions"
            
            master_datasets["GCP2019_CTRACKER"].facec="gray"
            master_datasets["GCP2019_CTRACKER"].plotmarker="o"
            master_datasets["GCP2019_CTRACKER"].plot_lines=True
            master_datasets["GCP2020_CTRACKER"].facec="red"
            master_datasets["GCP2020_CTRACKER"].plotmarker="s"
            master_datasets["GCP2020_CTRACKER"].plot_lines=True
            master_datasets["GCP2021_CTRACKER"].facec="blue"
            master_datasets["GCP2021_CTRACKER"].plotmarker="X"
            master_datasets["GCP2021_CTRACKER"].plot_lines=True

        elif self.graphname == "jena_global":
            self.desired_simulations=[ \
                                  'GCP2019_JENA', \
                                  'GCP2020_JENA-sEXT', \
                                  'GCP2021_JENA-sEXT', \
                              ]   
            self.output_file_start="JENAGlobalInversionsAll_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from global JENA inversions"
            
            master_datasets["GCP2019_JENA"].facec="gray"
            master_datasets["GCP2019_JENA"].plotmarker="o"
            master_datasets["GCP2019_JENA"].plot_lines=True
            master_datasets["GCP2020_JENA-sEXT"].facec="red"
            master_datasets["GCP2020_JENA-sEXT"].plotmarker="s"
            master_datasets["GCP2020_JENA-sEXT"].plot_lines=True
            master_datasets["GCP2021_JENA-sEXT"].facec="blue"
            master_datasets["GCP2021_JENA-sEXT"].plotmarker="X"
            master_datasets["GCP2021_JENA-sEXT"].plot_lines=True


        elif self.graphname == "gcp2019_all":
            self.desired_simulations=[ \
                                  'GCP2019_ALL', \
                                  'GCP2019_JENA', \
                                  'GCP2019_CTRACKER', \
                                  'GCP2019_CAMS', \
                              ]   
            self.output_file_start="GCPInversions2019_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP-2019 inversions"
            
            master_datasets['GCP2019_ALL'].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].facec="gray"
            master_datasets["GCP2019_ALL"].uncert_color=master_datasets["GCP2019_ALL"].facec

        elif self.graphname == "gcp2020_all":
            self.desired_simulations=[ \
                                  'GCP2020_ALL', \
                                  'GCP2020_JENA-s85', \
                                  'GCP2020_JENA-sEXT', \
                                  'GCP2020_CTRACKER', \
                                  'GCP2020_CAMS', \
                                  'GCP2020_NIES', \
                                  'GCP2020_UoE', \
                              ]   
            self.output_file_start="GCPInversions2020_"
            self.output_file_end="_2020_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP-2020 inversions"
            
            master_datasets['GCP2020_ALL'].lplot_errorbar=True

            master_datasets["GCP2020_ALL"].facec="red"
            master_datasets["GCP2020_ALL"].uncert_color=master_datasets["GCP2020_ALL"].facec

        elif self.graphname == "gcpinversion2021":
            self.desired_simulations=[ \
                                  'GCP2021_ALL', \
                                  'GCP2021_CAMS', \
#                                  'GCP2021_CMS', \
                                  'GCP2021_CTRACKER', \
                                  'GCP2021_JENA-s99', \
                                  'GCP2021_JENA-sEXT', \
                                  'GCP2021_NIES', \
                                  'GCP2021_UoE', \
                                   ]
            self.output_file_start="GCPInversions2021_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP-2021 inversions"
            
            master_datasets['GCP2021_ALL'].lplot_errorbar=True

            master_datasets["GCP2021_ALL"].facec="blue"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

        elif self.graphname == "gcpcomparison":
            self.desired_simulations=[ \
                                       "GCP2019_ALL", \
                                       "GCP2020_ALL", \
                                       "GCP2021_ALL", \
                                   ]
            self.output_file_start="GCPComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from GCP inversions"
            master_datasets["GCP2019_ALL"].lplot_errorbar=True
            master_datasets["GCP2020_ALL"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].lplot_errorbar=True

            master_datasets["GCP2021_ALL"].facec="blue"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["GCP2019_ALL"].facec="gray"
            master_datasets["GCP2019_ALL"].uncert_color=master_datasets["GCP2019_ALL"].facec

            master_datasets["GCP2020_ALL"].facec="red"
            master_datasets["GCP2020_ALL"].uncert_color=master_datasets["GCP2020_ALL"].facec

            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.0]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-1100.0
            self.ymax_external=600.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "gcpcommon":
            self.desired_simulations=[ \
                                       "GCP2019_COMMON", \
                                       "GCP2020_COMMON", \
                                       "GCP2021_COMMON", \
                                   ]
            self.output_file_start="GCPCommon_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from GCP inversions common between all versions"
            master_datasets["GCP2019_COMMON"].lplot_errorbar=True
            master_datasets["GCP2020_COMMON"].lplot_errorbar=True
            master_datasets["GCP2021_COMMON"].lplot_errorbar=True

            master_datasets["GCP2021_COMMON"].facec="blue"
            master_datasets["GCP2021_COMMON"].uncert_color=master_datasets["GCP2021_COMMON"].facec

            master_datasets["GCP2019_COMMON"].facec="gray"
            master_datasets["GCP2019_COMMON"].uncert_color=master_datasets["GCP2019_COMMON"].facec

            master_datasets["GCP2020_COMMON"].facec="red"
            master_datasets["GCP2020_COMMON"].uncert_color=master_datasets["GCP2020_COMMON"].facec

            self.lexternal_y=True
            self.ymin_external=-1100.0
            self.ymax_external=600.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "gcp_trendy":
            self.desired_simulations=[ \
                                       "GCP2021_ALL", \
                                       "TrendyV10_ENSEMBLE", \
                                  ]
            self.output_file_start="GCPTrendy2021_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : CO$_2$ emissions from GCP-2021 and TrendyV10_ENSEMBLE"
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].lplot_errorbar=True

            master_datasets["GCP2021_ALL"].facec="blue"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["TrendyV10_ENSEMBLE"].facec="gray"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

        elif self.graphname == "gcp2019_inversions_corrected":
            self.desired_simulations=[ \
                                  'GCP2019_ALL', \
                                  'GCP2019_JENA', \
                                  'GCP2019_CTRACKER', \
                                  'GCP2019_CAMS', \
                                  'rivers_lakes_reservoirs_ULB', \
                              ]   
            self.output_file_start="GCPInversionsCorrected_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : net land CO$_2$ fluxes from GCP inversions"
            
            master_datasets["GCP2019_ALL"].lcorrect_inversion=True
            master_datasets["GCP2019_JENA"].lcorrect_inversion=True
            master_datasets["GCP2019_CTRACKER"].lcorrect_inversion=True
            master_datasets["GCP2019_CAMS"].lcorrect_inversion=True
            
            master_datasets['GCP2019_ALL'].lplot_errorbar=True
            
        elif self.graphname in ("topdownlulucf_2021","topdownlulucfbar_2021"):
            
                                  

            self.desired_simulations=[ \
                                  'UNFCCC2021_LULUCF', \
                                  'CSR-COMBINED-2020', \
                                  'EUROCOM_ALL_2020', \
                                  'GCP2021_ALL', \
                                  'BLUE2021_GCP', \
                                  'BLUE2021_VERIFY', \
                                  'H&N2021', \
                                  'ORCHIDEE-S3-V2020', \
                                  'FAOSTAT2021_LULUCF', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                                  'FAOSTAT2021_FOR_TOT', \
                                  "TrendyV10_ENSEMBLE", \
                              ]        
            
            self.output_file_end="_FCO2land_2021_v1.png" 
            
            if self.graphname == "topdownlulucf_2021":
                self.titleending=r" : Comparison of top-down vs. bottom-up net land CO$_2$land fluxes"
                self.output_file_start="TopDownLULUCF_"
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 master_datasets['UNFCCC2021_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2021_LULUCF'].displayname_err, \
                                 master_datasets['FAOSTAT2021_LULUCF'].displayname, \
                                 master_datasets['EUROCOM_ALL_2020'].displayname,master_datasets['EUROCOM_ALL_2020'].displayname_err,\
                                 master_datasets['GCP2021_ALL'].displayname, master_datasets['GCP2021_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2020'].displayname, \
                                 master_datasets["TrendyV10_ENSEMBLE"].displayname, master_datasets["TrendyV10_ENSEMBLE"].displayname_err, \
                                 master_datasets['ORCHIDEE-S3-V2020'].displayname, \
                                 master_datasets['BLUE2021_VERIFY'].displayname, \
                                 master_datasets['BLUE2021_GCP'].displayname, \
                                 master_datasets['H&N2021'].displayname, \
                             ]
                
                master_datasets['ORCHIDEE-S3-V2020'].displaylegend=True      
                
            else:
                self.output_file_start="TopDownLULUCFbar_"
                self.titleending=r" : Comparison of top-down vs. bottom-up (aggregated) net land CO$_2$ fluxes"
                
                self.desired_simulations.append("VERIFYBU")
                
                # These simulations will be combined together.
                self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-S3-V2020','BLUE2021_VERIFY']
                self.overwrite_operations["VERIFYBU"]="mean"
                master_datasets["VERIFYBU"].displaylegend=False
                
                master_datasets["VERIFYBU"].displayname="Mean of BU estimates (VERIFY)"
                master_datasets["VERIFYBU"].displayname_err="Min/Max of BU estimates (VERIFY)"
                
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 master_datasets['UNFCCC2021_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2021_LULUCF'].displayname_err, \
                                 master_datasets['EUROCOM_ALL_2020'].displayname,master_datasets['EUROCOM_ALL_2020'].displayname_err,\
                                 master_datasets['GCP2021_ALL'].displayname, master_datasets['GCP2021_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2020'].displayname, \
                                 master_datasets["TrendyV10_ENSEMBLE"].displayname, master_datasets["TrendyV10_ENSEMBLE"].displayname_err, \
                                 master_datasets['FAOSTAT2021_LULUCF'].displayname, \
                                 master_datasets['H&N2021'].displayname, \
                                 master_datasets['BLUE2021_GCP'].displayname, \
                                 master_datasets['VERIFYBU'].displayname, \
                                 master_datasets['VERIFYBU'].displayname_err, \
                             ]

                ############## ONLY FOR PLOTTING MEAN GRAPH
                if False:
                    self.desired_legend=[ \
                                 master_datasets['UNFCCC2020_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2020_LULUCF'].displayname_err, \
                                 master_datasets['FAOSTAT2020_LULUCF'].displayname, \
                                 master_datasets['EUROCOM_ALL_2019'].displayname,master_datasets['EUROCOM_ALL_2019'].displayname_err,\
                                 master_datasets['GCP2020_ALL'].displayname, master_datasets['GCP2020_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2019'].displayname, \
                                 master_datasets["TrendyV9_ENSEMBLE"].displayname, master_datasets["TrendyV9_ENSEMBLE"].displayname_err, \
                                 master_datasets['H&N2019'].displayname, \
                                 master_datasets['VERIFYBU'].displayname, \
                                 master_datasets['VERIFYBU'].displayname_err, \
                             ]
                #endif
                ##################################3
                
                # These simulations will be combined together.
                
                # So I don't want to generally plot the components
                master_datasets['ORCHIDEE-S3-V2020'].displaylegend=False
                master_datasets['BLUE2021_VERIFY'].displaylegend=False


            #endif

            # This is a bigger legend, so the size will be closer to the
            # size of the plot.
            self.npanels=2
            self.panel_ratios=[1.0,0.7]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-800.0
            self.ymax_external=700.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]
            
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2021_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2021_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2020"].facec="black"

            
            # A couple of these plots will be displayed as bars instead of symbols
            master_datasets["EUROCOM_ALL_2020"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2020"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2020"].lwhiskerbars=True

        elif self.graphname in ("topdownlulucf_2019","topdownlulucfbar_2019"):
            
                                  

            self.desired_simulations=[ \
                                  'UNFCCC2019_LULUCF', \
                                  'MS-NRT', \
                                  #                      'rivers_lakes_reservoirs_ULB', \
                                  'CSR-COMBINED-2019', \
                                  'EUROCOM_ALL_2019', \
                                  'GCP2019_ALL', \
                                  'BLUE2019', \
                                  #    "EPIC2019_NBP_CRP", \
                                  #    'EFISCEN', \
                                  'H&N2019', \
                                  #   'FLUXCOM_rsonlyANN_os', \
                                  #   'FLUXCOM_rsonlyRF_os', \
                                  #   'ORCHIDEE-MICT', \
                                  "ORCHIDEE-S3-V2019", \
                                  'FAOSTAT2019_LULUCF', \
                                  'FAOSTAT2019_CRP', \
                                  'FAOSTAT2019_GRS', \
                                  'FAOSTAT2019_FOR_TOT', \
                                  "TrendyV7_ENSEMBLE", \
                                  # 'TrendyV7_ORCHIDEE', \
                              ]        
            
            self.output_file_end="_FCO2land_2019_v1.png" 
            
            if self.graphname == "topdownlulucf_2019":
                self.titleending=r" : Comparison of top-down vs. bottom-up net land CO$_2$land fluxes"
                self.output_file_start="TopDownLULUCF_"
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname_err, \
                                 master_datasets['FAOSTAT2019_LULUCF'].displayname, \
                                 master_datasets['MS-NRT'].displayname, \
                                 master_datasets['EUROCOM_ALL_2019'].displayname,master_datasets['EUROCOM_ALL_2019'].displayname_err,\
                                 master_datasets['GCP2019_ALL'].displayname, master_datasets['GCP2019_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2019'].displayname, \
                                 master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                                 master_datasets["ORCHIDEE-S3-V2019"].displayname, \
                                 #    master_datasets["EPIC2019_NBP_CRP"].displayname, \
                                 #    master_datasets['EFISCEN'].displayname, \
                                 master_datasets['BLUE2019'].displayname, \
                                 master_datasets['H&N2019'].displayname, \
                                 #master_datasets['TrendyV7_ORCHIDEE'].displayname, \
                                 #master_datasets['ORCHIDEE-MICT'].displayname, \
                                 #      'FLUXCOM_rsonlyANN_os', \
                                 #      'FLUXCOM_rsonlyRF_os',
                             ]
                
                master_datasets['ORCHIDEE-MICT'].displaylegend=True
                master_datasets["ORCHIDEE-S3-V2019"].displaylegend=True      
                master_datasets['TrendyV7_ORCHIDEE'].displaylegend=True

                # This is a bigger legend, so the size will be closer to the
                # size of the plot.
                self.npanels=2
                self.panel_ratios=[1.0,0.7]
                self.igrid_legend=1
                
            else:
                self.output_file_start="TopDownLULUCFbar_"
                self.titleending=r" : Comparison of top-down vs. bottom-up (aggregated) net land CO$_2$ fluxes"
                
                self.desired_simulations.append("VERIFYBU")
                
                # These simulations will be combined together.
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT',"ORCHIDEE-S3-V2019",'FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE2019']
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT',"ORCHIDEE-S3-V2019",'BLUE2019']
                self.overwrite_simulations["VERIFYBU"]=["ORCHIDEE-S3-V2019",'BLUE2019']
                self.overwrite_operations["VERIFYBU"]="mean"
                master_datasets["VERIFYBU"].displaylegend=False
                
                master_datasets["VERIFYBU"].displayname="Mean of BU estimates (VERIFY)"
                master_datasets["VERIFYBU"].displayname_err="Min/Max of BU estimates (VERIFY)"
                
                # The legend is tricky.  You can use names not definied in the above
                # simulation list if they are defined later on.  This just gives their
                # order.  Names are controled by the displayname variable, and this must
                # match those names else an error is thrown.
                self.desired_legend=[ \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname_err, \
                                 master_datasets['MS-NRT'].displayname, \
                                 master_datasets['EUROCOM_ALL_2019'].displayname,master_datasets['EUROCOM_ALL_2019'].displayname_err,\
                                 master_datasets['GCP2019_ALL'].displayname, master_datasets['GCP2019_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2019'].displayname, \
                                 master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                                 master_datasets['FAOSTAT2019_LULUCF'].displayname, \
                                 master_datasets['H&N2019'].displayname, \
                                 master_datasets['VERIFYBU'].displayname, \
                                 master_datasets['VERIFYBU'].displayname_err, \
                                 #        master_datasets["ORCHIDEE-S3-V2019"].displayname, \
                                 #        master_datasets['TrendyV7_ORCHIDEE'].displayname, \
                                 #        master_datasets['ORCHIDEE-MICT'].displayname, \
                             ]

                ############## ONLY FOR PLOTTING MEAN GRAPH
                if False:
                    self.desired_legend=[ \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname, \
                                 master_datasets['UNFCCC2019_LULUCF'].displayname_err, \
                                 master_datasets['MS-NRT'].displayname, \
                                 master_datasets['FAOSTAT2019_LULUCF'].displayname, \
                                 master_datasets['EUROCOM_ALL_2019'].displayname,master_datasets['EUROCOM_ALL_2019'].displayname_err,\
                                 master_datasets['GCP2019_ALL'].displayname, master_datasets['GCP2019_ALL'].displayname_err, \
                                 master_datasets['CSR-COMBINED-2019'].displayname, \
                                 master_datasets["TrendyV7_ENSEMBLE"].displayname, master_datasets["TrendyV7_ENSEMBLE"].displayname_err, \
                                 master_datasets['H&N2019'].displayname, \
                                 master_datasets['VERIFYBU'].displayname, \
                                 master_datasets['VERIFYBU'].displayname_err, \
                                 #        master_datasets["ORCHIDEE-S3-V2019"].displayname, \
                                 #        master_datasets['TrendyV7_ORCHIDEE'].displayname, \
                                 #        master_datasets['ORCHIDEE-MICT'].displayname, \
                             ]
                #endif
                ##################################3
                
                # These simulations will be combined together.
                #         self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT',"ORCHIDEE-S3-V2019",'BLUE2019','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os']
                #self.overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT',"ORCHIDEE-S3-V2019",'BLUE2019']
                #self.overwrite_operations["VERIFYBU"]="mean"
                
                # So I don't want to generally plot the components
                master_datasets['ORCHIDEE-MICT'].displaylegend=False
                master_datasets["ORCHIDEE-S3-V2019"].displaylegend=False
                master_datasets['BLUE2019'].displaylegend=False
                master_datasets['FLUXCOM_rsonlyANN_os'].displaylegend=False
                master_datasets['FLUXCOM_rsonlyRF_os'].displaylegend=False
                
                master_datasets['TrendyV7_ORCHIDEE'].displaylegend=False
                
                # This is a bigger legend, so the size will be closer to the
                # size of the plot.
                self.npanels=2
                self.panel_ratios=[1.0,0.7]
                self.igrid_legend=1

            #endif

            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2019_LULUCF"]=['FAOSTAT2019_CRP','FAOSTAT2019_GRS','FAOSTAT2019_FOR_TOT']
            self.overwrite_operations["FAOSTAT2019_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2019_LULUCF"]=[1.0,1.0,1.0]
            
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2019_CRP'].displaylegend=False
            master_datasets['FAOSTAT2019_GRS'].displaylegend=False
            master_datasets['FAOSTAT2019_FOR_TOT'].displaylegend=False
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2019_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2019_LULUCF'].plotmarker='^'
            master_datasets["ORCHIDEE-S3-V2019"].facec="black"
            master_datasets["ORCHIDEE-MICT"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].facec="none"
            master_datasets["TrendyV7_ORCHIDEE"].edgec="dimgrey"
            master_datasets["ORCHIDEE-MICT"].edgec="black"
            #master_datasets['ORCHIDEE-MICT'].displaylegend=False
            #master_datasets['TrendyV7_ORCHIDEE'].displaylegend=False
            
            # A couple of these plots will be displayed as bars instead of symbols
            master_datasets["EUROCOM_ALL_2019"].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].lplot_errorbar=True
            master_datasets["TrendyV7_ENSEMBLE"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lwhiskerbars=True

            self.lexternal_y=True
            self.ymin_external=-800.0
            self.ymax_external=700.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif
            
        elif self.graphname == "inversions_verify":
            self.desired_simulations=[ \
                                  'CSR-COMBINED-2019', \
                                  'CSR-REG-100km', \
                                  'CSR-REG-200km', \
                                  'CSR-REG-Core100km', \
                                  'CSR-REG-Valid100km', \
                              ]   
            self.output_file_start="inversions_verify_"
            self.output_file_end="_2019_v1.png" 
            self.titleending=r" : CO$_2$ inversion from CarboScopeReg simulations in VERIFY"

        elif self.graphname == "inversions_verify_v2":
            self.desired_simulations=[ \
                                  'CSR-COMBINED-2019', \
                                  'CSR-REG-100km', \
                                  'CSR-REG-200km', \
                                  'CSR-REG-Core100km', \
                                  'CSR-REG-Valid100km', \
                              ]   
            self.output_file_start="inversions_verify_"
            self.output_file_end="_2020_v2.png" 
            self.titleending=r" : CO$_2$ inversion from CarboScopeReg simulations in VERIFY"

        elif self.graphname == "csr_inversions_comparison":
            self.desired_simulations=[ \
                                  'CSR-COMBINED-2019', \
                                  'CSR-COMBINED-2020', \
                              ]   
            self.output_file_start="inversions_verify_bars_"
            self.output_file_end="_2020_v2.png" 
            self.titleending=r" : CO$_2$ inversion from CarboScopeReg simulations in VERIFY"

                
            self.desired_legend=[\
                            master_datasets['CSR-COMBINED-2019'].displayname, master_datasets['CSR-COMBINED-2019'].displayname_err, \
                            master_datasets['CSR-COMBINED-2020'].displayname, master_datasets['CSR-COMBINED-2020'].displayname_err, \
                        ]
            # Plot these as bars
            master_datasets["CSR-COMBINED-2019"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2020"].lplot_errorbar=True
            #master_datasets["CSR-COMBINED"].lwhiskerbars=True
            #master_datasets["CSR-COMBINED-2020"].lwhiskerbars=True
            
            # Change some colors
            master_datasets['CSR-COMBINED-2019'].uncert_color='green'
            master_datasets["CSR-COMBINED-2019"].facec="green"
            master_datasets['CSR-COMBINED-2020'].uncert_color='blue'
            master_datasets["CSR-COMBINED-2020"].facec="blue"

        elif self.graphname == "regionalinversions":
            self.desired_simulations=[ \
                                  'CSR-COMBINED-2019', \
                                  'CSR-COMBINED-2020', \
                                  'LUMIA-COMBINED-v2021', \
                              ]   
            self.output_file_start="regionalinversions_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : CO$_2$ inversions from regional models"

            # Plot these as bars
            master_datasets["CSR-COMBINED-2019"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2020"].lplot_errorbar=True
            master_datasets["LUMIA-COMBINED-v2021"].lplot_errorbar=True

            # Change some colors
            master_datasets['CSR-COMBINED-2019'].uncert_color='green'
            master_datasets["CSR-COMBINED-2019"].facec="green"
            master_datasets['CSR-COMBINED-2020'].uncert_color='blue'
            master_datasets["CSR-COMBINED-2020"].facec="blue"

        elif self.graphname == "lumiainversions":
            self.desired_simulations=[ \
                                       'LUMIA-COMBINED-v2021', \
                                       "LUMIA-REF-v2021", \
                                       "LUMIA-Cor200km-v2021", \
                                       "LUMIA-CoreSites-v2021", \
#                                       "LUMIA-AlterBG-v2021", \
                                       'EUROCOM_Lumia', \
                             ]   
            self.output_file_start="LUMIAinversions_"
            self.output_file_end="_2021_v1.png" 
            self.titleending=r" : CO$_2$ inversions from the LUMIA model"

            # Plot these as bars
            master_datasets["LUMIA-COMBINED-v2021"].lplot_errorbar=True
            
            # Change some colors
            master_datasets["EUROCOM_Lumia"].facec="blue"

            master_datasets["LUMIA-REF-v2021"].plot_lines=True
            master_datasets["LUMIA-REF-v2021"].linestyle="solid"
            master_datasets["LUMIA-Cor200km-v2021"].plot_lines=True
            master_datasets["LUMIA-Cor200km-v2021"].linestyle="solid"
            master_datasets["LUMIA-CoreSites-v2021"].plot_lines=True
            master_datasets["LUMIA-CoreSites-v2021"].linestyle="solid"
            master_datasets["EUROCOM_Lumia"].plot_lines=True
            master_datasets["EUROCOM_Lumia"].linestyle="dashed"

        elif self.graphname == "eurocomcomparison":
            self.desired_simulations=[ \
                                  'EUROCOM_ALL_2019', \
                                  'EUROCOM_ALL_2020', \
                              ]   
            self.output_file_start="EUROCOMcomparison_"
            self.output_file_end="_2020_v2.png" 
            self.titleending=r" : CO$_2$ inversions from EUROCOM ensembles"

                
            self.desired_legend=[\
                            master_datasets['EUROCOM_ALL_2019'].displayname, master_datasets['EUROCOM_ALL_2019'].displayname_err, \
                            master_datasets['EUROCOM_ALL_2020'].displayname, master_datasets['EUROCOM_ALL_2020'].displayname_err, \
                        ]
            # Plot these as bars
            master_datasets["EUROCOM_ALL_2019"].lplot_errorbar=True
            master_datasets["EUROCOM_ALL_2020"].lplot_errorbar=True
            
            # Change some colors
            master_datasets['EUROCOM_ALL_2019'].uncert_color='gray'
            master_datasets["EUROCOM_ALL_2019"].facec="gray"
            master_datasets['EUROCOM_ALL_2020'].uncert_color='red'
            master_datasets["EUROCOM_ALL_2020"].facec="red"

        elif self.graphname == "eurocominversionsv2":
            self.desired_simulations=[ \
                                  'EUROCOM_ALL_2020', \
                                  'EUROCOM_Flexinvert_V2', \
                                  'EUROCOM_Lumia_V2', \
                                  'EUROCOM_PYVAR_V2', \
                                  'EUROCOM_CSR_V2', \
                                   ]
            self.output_file_start="EUROCOMinversionsv2_"
            self.output_file_end="_2020_v2.png" 
            self.titleending=r" : CO$_2$ inversion from EUROCOM ensemble"

                
            self.desired_legend=[\
                            master_datasets['EUROCOM_ALL_2020'].displayname, master_datasets['EUROCOM_ALL_2020'].displayname_err, \
                            master_datasets['EUROCOM_Flexinvert_V2'].displayname, \
                            master_datasets['EUROCOM_Lumia_V2'].displayname, \
                            master_datasets['EUROCOM_PYVAR_V2'].displayname, \
                            master_datasets['EUROCOM_CSR_V2'].displayname, \
                        ]
            # Plot these as bars
            master_datasets["EUROCOM_ALL_2020"].lplot_errorbar=True
            
            master_datasets['EUROCOM_ALL_2020'].uncert_color='red'
            master_datasets["EUROCOM_ALL_2020"].facec="red"

        elif self.graphname in ( "topdownandinventories_2019"):
            
            self.titleending=r" : UNFCCC vs. top-down estimates of net land CO$_2$ fluxes"
            self.desired_simulations=[ \
                                       'UNFCCC2019_LULUCF', \
                                       'MS-NRT', \
                                       'rivers_lakes_reservoirs_ULB', \
                                       'CSR-COMBINED-2019', \
                                       'EUROCOM_ALL_2019', \
                                       'GCP2019_ALL', \
                                   ]   
            self.output_file_start="TopDownAndInventories_"
            
            self.desired_legend=[ \
                             master_datasets['UNFCCC2019_LULUCF'].displayname, \
                             master_datasets['UNFCCC2019_LULUCF'].displayname_err, \
                             'MS-NRT', \
                             'rivers_lakes_reservoirs_ULB', \
                             master_datasets['CSR-COMBINED-2019'].displayname, \
                             master_datasets['EUROCOM_ALL_2019'].displayname,master_datasets['EUROCOM_ALL_2019'].displayname_err,\
                             master_datasets['GCP2019_ALL'].displayname, master_datasets['GCP2019_ALL'].displayname_err, \
                         ]
            
            self.output_file_end="_FCO2land_2019_v2.png" 
            master_datasets['MS-NRT'].edgec=master_datasets['MS-NRT'].facec
            
            # A couple of these plots will be displayed as bars instead of symbols
            master_datasets["EUROCOM_ALL_2019"].lplot_errorbar=True
            master_datasets["GCP2019_ALL"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lwhiskerbars=True
            
            # And to correct some of the plots.
            master_datasets["GCP2019_ALL"].lcorrect_inversion=True
            master_datasets["CSR-COMBINED-2019"].lcorrect_inversion=True
            master_datasets["EUROCOM_ALL_2019"].lcorrect_inversion=True
           
            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.7]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-800.0
            self.ymax_external=700.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname in ( "topdownandinventories_2021"):
            
            self.titleending=r" : UNFCCC vs. top-down estimates of net land CO$_2$ fluxes"
            self.desired_simulations=[ \
                                       'UNFCCC2021_LULUCF', \
                                       'rivers_lakes_reservoirs_ULB', \
                                       'CSR-COMBINED-2019', \
                                       'EUROCOM_ALL_2020', \
                                       'GCP2021_ALL', \
                                   ]   
            self.output_file_start="TopDownAndInventories_"
            
            self.desired_legend=[ \
                             master_datasets['UNFCCC2019_LULUCF'].displayname, \
                             master_datasets['UNFCCC2019_LULUCF'].displayname_err, \
                             master_datasets['rivers_lakes_reservoirs_ULB'].displayname_err, \
                             master_datasets['CSR-COMBINED-2019'].displayname, \
                             master_datasets['EUROCOM_ALL_2020'].displayname,master_datasets['EUROCOM_ALL_2020'].displayname_err,\
                             master_datasets['GCP2021_ALL'].displayname, master_datasets['GCP2021_ALL'].displayname_err, \
                         ]
            
            self.output_file_end="_FCO2land_2021_v1.png" 
            
            # A couple of these plots will be displayed as bars instead of symbols
            master_datasets["EUROCOM_ALL_2020"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lplot_errorbar=True
            master_datasets["CSR-COMBINED-2019"].lwhiskerbars=True
            
            # And to correct some of the plots.
            master_datasets["GCP2021_ALL"].lcorrect_inversion=True
            master_datasets["CSR-COMBINED-2019"].lcorrect_inversion=True
            master_datasets["EUROCOM_ALL_2020"].lcorrect_inversion=True
           
            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.7]
            self.igrid_legend=1

            self.lexternal_y=True
            self.ymin_external=-800.0
            self.ymax_external=700.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif

        elif self.graphname == "unfccc_forest_test":

            # Changing this removes the forest areas being
            # plotted on the graph
            self.lplot_areas=False


            self.desired_simulations=[ \
                                  'UNFCCC2019_FL-FL', \
                                  'UNFCCC2020_FL-FL', \
            ]   
            
            self.desired_legend=[\
                            master_datasets['UNFCCC2019_FL-FL'].displayname,master_datasets["UNFCCC2019_FL-FL"].displayname_err,\
                            master_datasets['UNFCCC2020_FL-FL'].displayname,master_datasets["UNFCCC2020_FL-FL"].displayname_err,\
            ]
            
            self.output_file_start="UNFCCCForestTest_"
            # v1 has EFISCEN data from a spreadsheet sent by Mart-Jan in April 2020
            #      self.output_file_end="_FCO2land_2019_v1.png" 
            # v2 has EFISCEn data from June 2020
            self.output_file_end="_FCO2land_2020_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from forest land remaining forest land (FL-FL)"
            
            
            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif

        elif self.graphname == "unfccclulucfcomparison":

            # Changing this removes the forest areas being
            # plotted on the graph
            self.lplot_areas=False


            self.desired_simulations=[ \
                                  'UNFCCC2019_LULUCF', \
                                  'UNFCCC2020_LULUCF', \
                                  'UNFCCC2021_LULUCF', \
            ]   
            
            self.desired_legend=[\
            master_datasets['UNFCCC2019_LULUCF'].displayname,master_datasets["UNFCCC2019_LULUCF"].displayname_err,\
            master_datasets['UNFCCC2020_LULUCF'].displayname,master_datasets["UNFCCC2020_LULUCF"].displayname_err,\
            master_datasets['UNFCCC2021_LULUCF'].displayname,master_datasets["UNFCCC2021_LULUCF"].displayname_err,\
            ]
            
            self.output_file_start="UNFCCCLULUCFComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from land use, land use change, and forestry (LULUCF)"
            
            master_datasets["UNFCCC2019_LULUCF"].facec="gray"
            master_datasets["UNFCCC2019_LULUCF"].uncert_color=master_datasets["UNFCCC2019_LULUCF"].facec

            master_datasets["UNFCCC2020_LULUCF"].facec="red"
            master_datasets["UNFCCC2020_LULUCF"].uncert_color=master_datasets["UNFCCC2020_LULUCF"].facec

            master_datasets["UNFCCC2021_LULUCF"].facec="blue"
            master_datasets["UNFCCC2021_LULUCF"].uncert_color=master_datasets["UNFCCC2021_LULUCF"].facec

            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif

            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.1]
            self.igrid_legend=1

        elif self.graphname == "unfcccflcomparison":

            # Changing this removes the forest areas being
            # plotted on the graph
            self.lplot_areas=False


            self.desired_simulations=[ \
                                  'UNFCCC2019_FL-FL', \
#                                  'UNFCCC2020_FL-FL', \
                                  'UNFCCC2021_FL-FL', \
            ]   
            
            self.desired_legend=[\
                                 master_datasets['UNFCCC2019_FL-FL'].displayname,master_datasets["UNFCCC2019_FL-FL"].displayname_err,\
                                 master_datasets['UNFCCC2021_FL-FL'].displayname,master_datasets["UNFCCC2021_FL-FL"].displayname_err,\
            ]
            
            self.output_file_start="UNFCCCFLComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from forest remaining forests"
            
            master_datasets["UNFCCC2019_FL-FL"].facec="gray"
            master_datasets["UNFCCC2019_FL-FL"].uncert_color=master_datasets["UNFCCC2019_FL-FL"].facec

            master_datasets["UNFCCC2021_FL-FL"].facec="blue"
            master_datasets["UNFCCC2021_FL-FL"].uncert_color=master_datasets["UNFCCC2021_FL-FL"].facec

            #if lshow_productiondata:
            #   productiondata_master['FLUXCOM_FL-FL']=False
            #endif

            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

        elif self.graphname == "unfcccclcomparison":

            self.desired_simulations=[ \
                                  'UNFCCC2019_CL-CL', \
#                                  'UNFCCC2020_CL-CL', \
                                  'UNFCCC2021_CL-CL', \
            ]   
            
            self.desired_legend=[\
                                 master_datasets['UNFCCC2019_CL-CL'].displayname,master_datasets["UNFCCC2019_CL-CL"].displayname_err,\
                                 master_datasets['UNFCCC2021_CL-CL'].displayname,master_datasets["UNFCCC2021_CL-CL"].displayname_err,\
            ]
            
            self.output_file_start="UNFCCCCLComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from croplands remaining croplands"
            
            master_datasets["UNFCCC2019_CL-CL"].facec="gray"
            master_datasets["UNFCCC2019_CL-CL"].uncert_color=master_datasets["UNFCCC2019_CL-CL"].facec

            master_datasets["UNFCCC2021_CL-CL"].facec="blue"
            master_datasets["UNFCCC2021_CL-CL"].uncert_color=master_datasets["UNFCCC2021_CL-CL"].facec

            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

        elif self.graphname == "unfcccglcomparison":

            self.desired_simulations=[ \
                                  'UNFCCC2019_GL-GL', \
#                                  'UNFCCC2020_GL-GL', \
                                  'UNFCCC2021_GL-GL', \
            ]   
            
            self.desired_legend=[\
                                 master_datasets['UNFCCC2019_GL-GL'].displayname,master_datasets["UNFCCC2019_GL-GL"].displayname_err,\
                                 master_datasets['UNFCCC2021_GL-GL'].displayname,master_datasets["UNFCCC2021_GL-GL"].displayname_err,\
            ]
            
            self.output_file_start="UNFCCCGLComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from grasslands remaining grasslands"
            
            master_datasets["UNFCCC2019_GL-GL"].facec="gray"
            master_datasets["UNFCCC2019_GL-GL"].uncert_color=master_datasets["UNFCCC2019_GL-GL"].facec

            master_datasets["UNFCCC2021_GL-GL"].facec="blue"
            master_datasets["UNFCCC2021_GL-GL"].uncert_color=master_datasets["UNFCCC2021_GL-GL"].facec

            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

        elif self.graphname == "bookkeeping":
            self.desired_simulations=[ \
                                  'BLUE2019', \
                                  'BLUE2021_VERIFY', \
                                  'BLUE2021_GCP', \
                                  'H&N2019', \
                                  'H&N2021', \
                              ]  
            
            self.output_file_start="Bookkeeping_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Net bottom-up CO$_2$land fluxes from bookkeeping approaches"
            
            master_datasets["BLUE2019"].facec="blue"
            master_datasets['BLUE2019'].plotmarker='^'
            master_datasets["BLUE2021_VERIFY"].facec="forestgreen"
            master_datasets['BLUE2021_VERIFY'].plotmarker='o'
            master_datasets["BLUE2021_GCP"].facec="lime"
            master_datasets['BLUE2021_GCP'].plotmarker='o'

            master_datasets["H&N2019"].facec="tab:orange"
            master_datasets['H&N2019'].plotmarker='X'
            master_datasets["H&N2021"].facec="tab:red"
            master_datasets['H&N2021'].plotmarker='P'

            master_datasets["BLUE2019"].plot_lines=True
            master_datasets["BLUE2019"].linestyle="dashed"
            master_datasets["H&N2019"].plot_lines=True
            master_datasets["H&N2019"].linestyle="dashed"

            master_datasets["BLUE2021_VERIFY"].plot_lines=True
            master_datasets["BLUE2021_VERIFY"].linestyle="solid"
            master_datasets["BLUE2021_GCP"].plot_lines=True
            master_datasets["BLUE2021_GCP"].linestyle="solid"
            master_datasets["H&N2021"].plot_lines=True
            master_datasets["H&N2021"].linestyle="solid"

        elif self.graphname == "faostat2021":
            
                                  

            self.desired_simulations=[ \
                                       'FAOSTAT2021_LULUCF', \
                                       'FAOSTAT2021_CL-CL', \
                                       'FAOSTAT2021_GL-GL', \
                                       'FAOSTAT2021_FOR_TOT', \
                                       'FAOSTAT2021_FL-FL', \
                                       "FAOSTAT2021_FOR_CON", \
                                   ]        
            
            self.output_file_end="_FCO2land_2021_v1.png" 
            
            self.titleending=r" : Comparison of FAOSTAT LULUCF components for net land CO$_2$land fluxes"
            self.output_file_start="FAOSTAT2021_"

            
            # Change some markers and colors and add lines for easier
            # viewing
            master_datasets["FAOSTAT2021_CL-CL"].facec="gold"
            master_datasets['FAOSTAT2021_CL-CL'].plotmarker='s'
            master_datasets["FAOSTAT2021_CL-CL"].plot_lines=True
            master_datasets["FAOSTAT2021_CL-CL"].linestyle="solid"
            master_datasets["FAOSTAT2021_GL-GL"].facec="brown"
            master_datasets['FAOSTAT2021_GL-GL'].plotmarker='<'
            master_datasets["FAOSTAT2021_GL-GL"].plot_lines=True
            master_datasets["FAOSTAT2021_GL-GL"].linestyle="solid"
            master_datasets["FAOSTAT2021_FOR_TOT"].facec="green"
            master_datasets['FAOSTAT2021_FOR_TOT'].plotmarker='X'
            master_datasets["FAOSTAT2021_FOR_TOT"].plot_lines=True
            master_datasets["FAOSTAT2021_FOR_TOT"].linestyle="solid"
            master_datasets["FAOSTAT2021_FL-FL"].facec="blue"
            master_datasets['FAOSTAT2021_FL-FL'].plotmarker='X'
            master_datasets["FAOSTAT2021_FL-FL"].plot_lines=True
            master_datasets["FAOSTAT2021_FL-FL"].linestyle="solid"
            master_datasets["FAOSTAT2021_FOR_CON"].facec="red"
            master_datasets['FAOSTAT2021_FOR_CON'].plotmarker='X'
            master_datasets["FAOSTAT2021_FOR_CON"].plot_lines=True
            master_datasets["FAOSTAT2021_FOR_CON"].linestyle="solid"
                
            # This is a bigger legend, so the size will be closer to the
            # size of the plot.
            self.npanels=2
            self.panel_ratios=[1.0,1/2.0]
            self.igrid_legend=1

            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]
            
            # Here I want to plot all the components
            #master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            #master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            #master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            
            # Change some colors and symbols here
            master_datasets["FAOSTAT2021_LULUCF"].facec="yellow"
            master_datasets['FAOSTAT2021_LULUCF'].plotmarker='^'

        elif self.graphname == "roxanawater":
            self.desired_simulations=[ \
                                       "rivers_lakes_reservoirs_ULB", \
                  ]  
            
            self.output_file_start="ROXANAWATER_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Inland waters for Roxana for v2021"
            
        elif self.graphname == "roxana":
            # This is just to create .csv files for all the datasets
            # for Roxana for the year 2021.  All countries including
            # EU-27+UK, Moldova, Ukraine and Belarus
            self.desired_simulations=[ \
                                  'UNFCCC2021_LULUCF', \
                                  'BLUE2021_VERIFY', \
                                  'BLUE2021_GCP', \
                                  'H&N2021', \
                                  'FAOSTAT2021_LULUCF', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                                  'FAOSTAT2021_FOR_TOT', \
                                  "TrendyV10_ENSEMBLE", \
                                   "GCP2021_ALL", \
                                  'ECOSSE2019_GL-GL-lim', \
                                  'ECOSSE2019_CL-CL', \
                                  'EFISCEN', \
                                       "CSR-COMBINED-2020", \
                                       "EUROCOM_ALL_2020",\
                                       "rivers_lakes_reservoirs_ULB", \
                                       'EPIC2021_NBP_CRP', \
                                       'EPIC2021_NBP_GRS', \
                                       'CBM2021historical', \
                                       'CBM2021simulated', \
                                   'ORCHIDEEv2-S3-V2021v2', \
                                  'ORCHIDEEv3-S3-V2021v2', \
                     ]  
            
            self.output_file_start="ROXANA_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Fluxes for Roxana for v2021"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]
            
            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

        elif self.graphname == "coco2":
            # This creates CO2land plots for countries outside the EU-27+UK
            # for a deliverable in CoCO2.  The data products are therefore
            # a bit more limited.  Roxana also requested that we split
            # out CAMS from GCP and plot it seperately (removing it from
            # the ensemble)
            self.desired_simulations=[ \
                                  'UNFCCC2021_LULUCF', \
                                  'BLUE2021_GCP', \
                                  'H&N2021', \
                                  'FAOSTAT2021_LULUCF', \
                                  'FAOSTAT2021_CL-CL', \
                                  'FAOSTAT2021_GL-GL', \
                                  'FAOSTAT2021_FOR_TOT', \
                                  "TrendyV10_ENSEMBLE", \
                                   "GCP2021_ALL", \
#                                   "GCP2021_NOCAMS", \
#                                   "GCP2021_CAMS", \
                     ]  
            
            self.output_file_start="COCO2D8.1_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Comparison of top-down vs. bottom-up net land CO$_2$land fluxes"
            
            # These simulations will be combined together.
            self.overwrite_simulations["FAOSTAT2021_LULUCF"]=['FAOSTAT2021_CL-CL','FAOSTAT2021_GL-GL','FAOSTAT2021_FOR_TOT']
            # So I don't want to generally plot the components
            master_datasets['FAOSTAT2021_CL-CL'].displaylegend=False
            master_datasets['FAOSTAT2021_GL-GL'].displaylegend=False
            master_datasets['FAOSTAT2021_FOR_TOT'].displaylegend=False
            self.overwrite_operations["FAOSTAT2021_LULUCF"]="sum"
            self.overwrite_coeffs["FAOSTAT2021_LULUCF"]=[1.0,1.0,1.0]
            
            master_datasets["GCP2021_NOCAMS"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].lplot_errorbar=True
            master_datasets["TrendyV10_ENSEMBLE"].lplot_errorbar=True

            master_datasets["GCP2021_NOCAMS"].facec="red"
            master_datasets["GCP2021_NOCAMS"].uncert_color=master_datasets["GCP2021_NOCAMS"].facec

            master_datasets["GCP2021_ALL"].facec="red"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["TrendyV10_ENSEMBLE"].facec="gray"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

            #self.lexternal_y=True
            #self.ymin_external=-800.0
            #self.ymax_external=700.0
            #if self.lexternal_y:
            #    self.lharmonize_y=True
            #endif

            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

        elif self.graphname == "camseez":
            # This creates CO2land plots for countries outside the EU-27+UK
            # for a deliverable in CoCO2.  The data products are therefore
            # a bit more limited.  Roxana also requested that we split
            # out CAMS from GCP and plot it seperately (removing it from
            # the ensemble)
            self.desired_simulations=[ \
                                   "GCP2021_ALL", \
                                   "GCP2021_CAMS", \
                                   "GCP2021_CAMSnoEEZ", \
                     ]  
            
            self.output_file_start="CAMSEEZ_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : Comparison of including the Extended Economic Zone in the country mask"
            
            master_datasets["GCP2021_ALL"].lplot_errorbar=True
            master_datasets["GCP2021_ALL"].facec="red"
            master_datasets["GCP2021_ALL"].uncert_color=master_datasets["GCP2021_ALL"].facec

            master_datasets["TrendyV10_ENSEMBLE"].facec="gray"
            master_datasets["TrendyV10_ENSEMBLE"].uncert_color=master_datasets["TrendyV10_ENSEMBLE"].facec

            #self.lexternal_y=True
            #self.ymin_external=-800.0
            #self.ymax_external=700.0
            #if self.lexternal_y:
            #    self.lharmonize_y=True
            #endif

            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

        elif self.graphname == "unfcccuncert":
            # Just want to look at some UNFCCC runs and get numbers
            # for certain countries.
            self.desired_simulations=[ \
                                  'UNFCCC2021_LULUCF', \
                                  'UNFCCC2021_FL-FL', \
                                  'UNFCCC2021_CL-CL', \
                                  'UNFCCC2021_GL-GL', \
                     ]  
            
            self.output_file_start="UNFCCCuncert_"
            self.output_file_end="_FCO2land_2021_v1.png" 

            self.titleending=r" : UNFCCC fluxes for LULUCF"
            
            #self.lexternal_y=True
            #self.ymin_external=-800.0
            #self.ymax_external=700.0
            #if self.lexternal_y:
            #    self.lharmonize_y=True
            #endif

            self.npanels=2
            self.panel_ratios=[1.0,1.0/1.9]
            self.igrid_legend=1

        elif self.graphname == "efiscencomparison":

            self.desired_simulations=[ \
                                       'EFISCEN', \
                                       'EFISCEN-Spacev2019', \
                                       'EFISCEN-Spacev2021', \
            ]   
            
            master_datasets["EFISCEN"].displayname="EFISCEN_FL-FL"
            master_datasets["EFISCEN-Spacev2019"].displayname="EFISCENSpacev2019_FL-FL"
            master_datasets["EFISCEN-Spacev2021"].displayname="EFISCENSpacev2021_FL-FL"

            self.output_file_start="EFISCENComparison_"
            self.output_file_end="_FCO2land_2021_v1.png" 
            self.titleending=r" : Net bottom-up CO$_2$land fluxes from forest land remaining forest land (FL-FL)"
            

            master_datasets["EFISCEN"].facec="tab:gray"
            master_datasets["EFISCEN"].plotmarker="o"
            master_datasets["EFISCEN"].plot_lines=True
            master_datasets["EFISCEN"].linestyle="dashed"

            master_datasets["EFISCEN-Spacev2019"].facec="gainsboro"
            master_datasets["EFISCEN-Spacev2019"].plotmarker="o"
            master_datasets["EFISCEN-Spacev2019"].plot_lines=True
            master_datasets["EFISCEN-Spacev2019"].linestyle="dashed"

            master_datasets["EFISCEN-Spacev2021"].facec="magenta"
            master_datasets["EFISCEN-Spacev2021"].plotmarker="o"
            master_datasets["EFISCEN-Spacev2021"].plot_lines=True
            master_datasets["EFISCEN-Spacev2021"].linestyle="dashed"


            # The space for the legend needs to be a little bit bigger
            # to make sure we fit in the text.
            self.npanels=2
            self.panel_ratios=[1.0,1.0/2.4]
            self.igrid_legend=1

            self.lexternal_y=False
            self.ymin_external=-260.0
            self.ymax_external=125.0
            if self.lexternal_y:
                self.lharmonize_y=True
            #endif
           
        else:
            print("I do not understand which simulation this is:")
            print(self.graphname)
            traceback.print_stack(file=sys.stdout)
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
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif
            if not mpl.colors.is_color_like(master_datasets[simname].facec):
                print("Do not recognize face color {} for simulation {}.".format(master_datasets[simname].facec,simname))
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif
            if not mpl.colors.is_color_like(master_datasets[simname].uncert_color):
                print("Do not recognize uncert color {} for simulation {}.".format(master_datasets[simname].uncert_color,simname))
                traceback.print_stack(file=sys.stdout)
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

