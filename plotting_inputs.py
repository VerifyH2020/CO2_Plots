####################################################################
# These routines set up the input structure of our code, reading in
# arguments from the command line, creating the input parameter structure
# to hold all the variables related to the graphs that we are making.
#
####################################################################

# These are downloadable or standard modules
import argparse
import numpy as np

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

#endclass

