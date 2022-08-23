####################################################################
# The subroutines for plot_mean_graphs.py
#
# NOTE: Uses Python3
#
####################################################################
#!/usr/bin/env python

# These are downloadable or standard modules
import sys,traceback
import pandas as pd

# These are my own that I have created locally
from country_subroutines import get_country_region_data

#####################################################
class simulation_paramters():
    def __init__(self,desired_simulations,plotting_columns,country_code,year_index,lcolor=True,ymin=None,ymax=None):

        # Some simple checks.
        if len(desired_simulations) != len(plotting_columns):
            print("*********************************")
            print("Incorrect input!  Check desired_simulations and plotting_columns.")
            print("len(desired_simulations): ",len(desired_simulations))
            print("len(plotting_columns): ",len(plotting_columns))
            print("*********************************")
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

        self.desired_simulations={}

        for sim,col in zip(desired_simulations,plotting_columns):
            self.add_dataset(sim,col,country_code,year_index)
        #endfor
        self.plotting_columns=plotting_columns

        # If True, use the colors associated with each dataset.
        # if False, use black striping and no color.
        self.lcolor=lcolor

        # This will force the limits of the graph if not None
        self.ymin=ymin
        self.ymax=ymax

    #enddef

    def add_dataset(self,name,plotting_column,country_code,year_index):
        self.desired_simulations[name]=dataset(name,plotting_column,country_code,year_index)
    #enddef

#endclass

class dataset():
    def __init__(self,name,plotting_column,country_code,year_index):
        self.name=name
        self.plotting_column=plotting_column
        self.country_code=country_code
        self.year_index=year_index

        # Fill information from a master list
        self.fill_additional_information()

        # Needs to be called after additional information is set up
        self.get_value_from_file()

    #enddef

    # Grab the information from the .csv file.
    def get_value_from_file(self):

        df = pd.read_csv(self.input_file, sep=',',decimal='.',index_col=0,header=0)
        # Check if the year we need is present.
        index_list=df.index.tolist()
        if self.year_index not in index_list:
            print("*********************************")
            print("Had a problem getting a value of {}.".format(self.name))
            print("File: ",self.input_file)
            print("Year index: ",self.year_index)
            print("Dataframe indices: ",index_list)
            print("*********************************")
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

        # Check if one of our dataset names is present.
        nfound=0
        for column in df.columns.tolist():
            if column in self.possible_names:
                self.column_name=column
                nfound=nfound+1
            #endif
        #endfor

        # We should have exactly one hit!
        if nfound != 1:
            print("*********************************")
            print("Had a problem getting a value of {}.".format(self.name))
            print("File: ",self.input_file)
            print("Possible names: ",self.possible_names)
            print("Columns: ",df.columns.tolist())
            print("nfound: ",nfound)
            print("*********************************")
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

        self.value=df.loc[self.year_index][self.column_name]
        print("Found a value: ",self.name,self.value)

        # Do we have min/max values?
        if self.lerror:
            # Min values
            # Check if one of our dataset names is present.
            nfound=0
            for column in df.columns.tolist():
                if column in self.possible_min_names:
                    self.min_column_name=column
                    nfound=nfound+1
                #endif
            #endfor

            # We should have exactly one hit!
            if nfound != 1:
                print("*********************************")
                print("Had a problem getting a min value of {}.".format(self.name))
                print("File: ",self.input_file)
                print("Possible names: ",self.possible_min_names)
                print("Columns: ",df.columns.tolist())
                print("nfound: ",nfound)
                print("*********************************")
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif

            self.min_value=df.loc[self.year_index][self.min_column_name]
            print("  Found a min value: ",self.min_value)

            # Max values
            # Check if one of our dataset names is present.
            nfound=0
            for column in df.columns.tolist():
                if column in self.possible_max_names:
                    self.max_column_name=column
                    nfound=nfound+1
                #endif
            #endfor

            # We should have exactly one hit!
            if nfound != 1:
                print("*********************************")
                print("Had a problem getting a max value of {}.".format(self.name))
                print("File: ",self.input_file)
                print("Possible names: ",self.possible_max_names)
                print("Columns: ",df.columns.tolist())
                print("nfound: ",nfound)
                print("*********************************")
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif

            self.max_value=df.loc[self.year_index][self.max_column_name]
            print("  Found a max value: ",self.max_value)

        #endif

    #enddef

    # This holds all our possible datasets.
    def fill_additional_information(self):
        
        if self.name == "UNFCCC2019_LULUCF":
            self.lerror=True 
            self.color="green"
            self.displayname="UNFCCC LULUCF NGHGI (2019)"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)
        elif self.name == "FAOSTAT2019_LULUCF":
            self.lerror=False 
            self.color="yellow"
            self.displayname="FAOSTAT (2019)"
            self.possible_names=[self.name,self.displayname,"FAOSTAT_LULUCF"]
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "EUROCOMv1_ALL_2019":
            self.lerror=True
            self.color="blue"
            self.displayname="Mean of EUROCOMv1 inversions"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "GCP2019_ALL":
            self.lerror=True
            self.color="red"
            self.displayname="Mean of GCP inversions (2019)"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "CSR-COMBINED-2019":
            self.lerror=True
            self.color="blue"
            self.displayname="Mean of CarboScopeReg 2019"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "TrendyV7_ENSEMBLE":
            self.lerror=True
            self.color="gray"
            self.displayname="Median of TRENDY v7 DGVMs"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "ORCHIDEE-S3-V2019":
            self.lerror=False 
            self.color="yellow"
            self.displayname="ORCHIDEE"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "BLUE2019":
            self.lerror=False 
            self.color="yellow"
            self.displayname="BLUE"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "H&N2019":
            self.lerror=False 
            self.color="yellow"
            self.displayname="H&N"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./ALLDATASETS_{}_FCO2land_2019_v1.csv".format(self.country_code)

        elif self.name == "UNFCCC2021_LULUCF":
            self.lerror=True 
            self.color="green"
            self.displayname="UNFCCC LULUCF NGHGI (2021)"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)
            
        elif self.name == "FAOSTAT2021_LULUCF":
            self.lerror=False 
            self.color="yellow"
            self.displayname="FAOSTAT (2021)"
            self.possible_names=[self.name,self.displayname,"FAOSTAT-V2021 (no Romania FL)"]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "EUROCOMv2_ALL_2020":
            self.lerror=True
            self.color="blue"
            self.displayname="Mean of EUROCOM-V2021 inversions"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "GCP2021_ALL":
            self.lerror=True
            self.color="red"
            self.displayname="Mean of GCP inversions (2021)"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "CSR-COMBINED-2021":
            self.lerror=True
            self.color="blue"
            self.displayname="Mean of CarboScopeReg-V2021"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "LUMIA-COMBINED-v2021":
            self.lerror=True
            self.color="blue"
            self.displayname="Mean of LUMIA-V2021"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "TrendyV10_ENSEMBLE":
            self.lerror=True
            self.color="gray"
            self.displayname="Median of TRENDY v10 DGVMs"
            self.possible_names=[self.name,self.displayname]
            self.possible_min_names=[]
            self.possible_max_names=[]             
            for name in self.possible_names:
                self.possible_min_names.append("{} MIN VALUES".format(name))
                self.possible_max_names.append("{} MAX VALUES".format(name))
            #endfor
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "ORCHIDEEv3-S3-V2021v2":
            self.lerror=False 
            self.color="yellow"
            self.displayname="ORCHIDEE-V2021-VERIFY"
            self.possible_names=[self.name,self.displayname,'ORCHIDEE-N-V2021-VERIFY']
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "BLUE2021_GCP":
            self.lerror=False 
            self.color="yellow"
            self.displayname="BLUEvGCP-V2021"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "BLUE2021_VERIFY":
            self.lerror=False 
            self.color="yellow"
            self.displayname="BLUEvVERIFY-V2021"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "H&N2021-GCP":
            self.lerror=False 
            self.color="yellow"
            self.displayname="H&N-V2021"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "CABLE-POP-S3-V2021":
            self.lerror=False 
            self.color="yellow"
            self.displayname="CABLE-POP-V2021-VERIFY"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        elif self.name == "CIF-CHIMERE-v2021":
            self.lerror=False 
            self.color="yellow"
            self.displayname="CIF-CHIMERE-V2021"
            self.possible_names=[self.name,self.displayname]
            self.input_file="./MEANPLOTSV2_{}_FCO2land_2021_v1.csv".format(self.country_code)

        else:
            print("*********************************")
            print("Do not yet know this dataset!")
            print("self.name: ",self.name)
            print("*********************************")
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

    #enddef

#endclass

# A small class for plotting background gray bars
class create_gray_bars():
    def __init__(self,xmin,xmax,bar_color,bar_text,bar_text_xval):
        self.xmin=xmin
        self.xmax=xmax
        self.bar_color=bar_color
        self.bar_text=bar_text
        self.bar_text_xval=bar_text_xval
    #enddef
#endclass

######## Set up the simulation parameters.
# Note that the desired simulations must match what is found in the .csv
# file you get the data from!
def get_simulation_parameters(plot_version,country_code):

    cr_data=get_country_region_data()

    if plot_version == "V2019_orig":

        # In the .csv files, I store the mean as the final year.
        year_index=2023
        desired_simulations=["UNFCCC2019_LULUCF","FAOSTAT2019_LULUCF","EUROCOMv1_ALL_2019",'GCP2019_ALL',"CSR-COMBINED-2019","TrendyV7_ENSEMBLE",'ORCHIDEE-S3-V2019','BLUE2019','H&N2019']
        # This gives the column number each dataset is plotted on.
        plotting_columns=[0,1,2,3,4,5,6,7,8]

        sim_params=simulation_paramters(desired_simulations,plotting_columns,country_code,year_index,True)
        sim_params.output_file_name="MeanPlot_V2019orig_{}.png".format(country_code)
        sim_params.title="Mean of overlapping timeseries - V2019 (2006-2015)\n{} : net land CO$_2$ fluxes".format(cr_data[country_code].long_name)

        # and some information on the gray bars that we use.
        sim_params.gray_bars=[]
        sim_params.gray_bars.append(create_gray_bars(-0.5,1.5,"white","Inventories",0.5))
        sim_params.gray_bars.append(create_gray_bars(1.5,4.5,"lightgray","Top-down",3.0))
        sim_params.gray_bars.append(create_gray_bars(4.5,6.5,"white","Bottom-up\n(DGVMs)",5.5))
        sim_params.gray_bars.append(create_gray_bars(6.5,9.0,"lightgray","Bottom-up\n(bookkeeping)",7.5))

        sim_params.ymax=200.0
        sim_params.ymin=-500

    elif plot_version == "V2019_ext":

        # In the .csv files, I store the mean as the final year.
        year_index=2023
        desired_simulations=["UNFCCC2019_LULUCF","FAOSTAT2019_LULUCF","EUROCOMv1_ALL_2019",'GCP2019_ALL',"CSR-COMBINED-2019","TrendyV7_ENSEMBLE",'ORCHIDEE-S3-V2019','BLUE2019','H&N2019']
        # This gives the column number each dataset is plotted on.
        plotting_columns=[0,1,2,3,4,7,8,10,12]

        sim_params=simulation_paramters(desired_simulations,plotting_columns,country_code,year_index,True)
        sim_params.output_file_name="MeanPlot_V2019ext_{}.png".format(country_code)
        sim_params.title="Mean of overlapping timeseries - V2019 (2006-2015)\n{} : net land CO$_2$ fluxes".format(cr_data[country_code].long_name)

        # and some information on the gray bars that we use.
        sim_params.gray_bars=[]
        sim_params.gray_bars.append(create_gray_bars(-0.5,1.5,"white","Inventories",0.5))
        sim_params.gray_bars.append(create_gray_bars(1.5,6.5,"lightgray","Top-down",4.0))
        sim_params.gray_bars.append(create_gray_bars(6.5,9.5,"white","Bottom-up\n(DGVMs)",8.0))
        sim_params.gray_bars.append(create_gray_bars(9.5,13.0,"lightgray","Bottom-up\n(bookkeeping)",11.0))

        sim_params.ymax=200.0
        sim_params.ymin=-500

    elif plot_version == "V2021_orig":

        # In the .csv files, I store the mean as the final year.
        year_index=2023
        desired_simulations=["UNFCCC2021_LULUCF","FAOSTAT2021_LULUCF","EUROCOMv2_ALL_2020",'GCP2021_ALL',"CSR-COMBINED-2021","TrendyV10_ENSEMBLE",'ORCHIDEEv3-S3-V2021v2','BLUE2021_GCP','H&N2021-GCP']
        # This gives the column number each dataset is plotted on.
        plotting_columns=[0,1,2,3,4,5,6,7,8]

        sim_params=simulation_paramters(desired_simulations,plotting_columns,country_code,year_index,True)
        sim_params.output_file_name="MeanPlot_V2021orig_{}.png".format(country_code)
        sim_params.title="Mean of overlapping timeseries - V2021 (2009-2018)\n{} : net land CO$_2$ fluxes".format(cr_data[country_code].long_name)

        # and some information on the gray bars that we use.
        sim_params.gray_bars=[]
        sim_params.gray_bars.append(create_gray_bars(-0.5,1.5,"white","Inventories",0.5))
        sim_params.gray_bars.append(create_gray_bars(1.5,4.5,"lightgray","Top-down",3.0))
        sim_params.gray_bars.append(create_gray_bars(4.5,6.5,"white","Bottom-up\n(DGVMs)",5.5))
        sim_params.gray_bars.append(create_gray_bars(6.5,9.0,"lightgray","Bottom-up\n(bookkeeping)",7.5))

        sim_params.ymax=200.0
        sim_params.ymin=-500

    elif plot_version == "V2021_ext":

        # In the .csv files, I store the mean as the final year.
        year_index=2023
        desired_simulations=["UNFCCC2021_LULUCF","FAOSTAT2021_LULUCF","EUROCOMv2_ALL_2020",'GCP2021_ALL',"CSR-COMBINED-2021",'LUMIA-COMBINED-v2021','CIF-CHIMERE-v2021',"TrendyV10_ENSEMBLE",'ORCHIDEEv3-S3-V2021v2','CABLE-POP-S3-V2021','BLUE2021_GCP','BLUE2021_VERIFY','H&N2021-GCP']
        # This gives the column number each dataset is plotted on.
        plotting_columns=[0,1,2,3,4,5,6,7,8,9,10,11,12]

        sim_params=simulation_paramters(desired_simulations,plotting_columns,country_code,year_index,True)
        sim_params.output_file_name="MeanPlot_V2021ext_{}.png".format(country_code)
        sim_params.title="Mean of overlapping timeseries - V2021 (2009-2018)\n{} : net land CO$_2$ fluxes".format(cr_data[country_code].long_name)

        # and some information on the gray bars that we use.
        sim_params.gray_bars=[]
        sim_params.gray_bars.append(create_gray_bars(-0.5,1.5,"white","Inventories",0.5))
        sim_params.gray_bars.append(create_gray_bars(1.5,6.5,"lightgray","Top-down",4.0))
        sim_params.gray_bars.append(create_gray_bars(6.5,9.5,"white","Bottom-up\n(DGVMs)",8.0))
        sim_params.gray_bars.append(create_gray_bars(9.5,13.0,"lightgray","Bottom-up\n(bookkeeping)",11.0))

        sim_params.ymax=200.0
        sim_params.ymin=-500

    else:
        print("************************************")
        print("Do not recognize this plot version.")
        print(plot_version)
        print("************************************")
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    return sim_params

#enddef
