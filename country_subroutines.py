##########################################
#
# This file mostly contains subroutines that you can call from
# other files, to create structures that contain various information
# on countries and regions, indexed by 3-letter ISO codes.  For example,
# the long name of the country/region, is a particular ISO code a country,
# and the list of countries found in a give region.
#
# In addition, if you just run this file with
#
#   python country_subroutines.py
#
# it will do a quick check to make sure that no names are conflicting
# and also print out a summary of the information found in the NetCDF file
# that contains country and regional masks.
#
##########################################

# These are downloadable or standard modules
from netCDF4 import Dataset as NetCDFFile 
import sys,traceback
import re
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import maskoceans

# Locally written module
from grid import Grid


# The purpose of this class is to store information about
# countries and regions: their three letter ISO code, a 
# full country name, other possible ways to spell the full
# country name.  If we are checking to see if this
# country is present in a .nc file, it also stores the name
# of the country as found in the file and the index number.
class countrydata:
    def __init__(self, iso_code,long_name,composant_countries):
        self.iso_code = iso_code
        self.long_name = long_name
        self.composant_countries = composant_countries
        if len(composant_countries) == 1:
            self.is_country = True
        else:
            self.is_country = False
        #endif
        self.possible_names = []

        # Create a list of common possible names
        self.possible_names.append(iso_code)
        self.possible_names.append(long_name)
        self.possible_names.append(long_name.upper()) 
        self.possible_names.append(long_name.lower())
        self.possible_names.append("'{}'".format(long_name))
        # H&N file removed spaces between words.
        self.possible_names.append(long_name.replace(" ",""))
        self.possible_names.append(long_name.upper().replace(" ","")) 
        self.possible_names.append(long_name.lower().replace(" ",""))
        self.uninit_int=-999

        # This is set if we search a file for the name of the country
        self.long_name_in_file=""

        # This is set if we search a file for this country
        self.file_index=self.uninit_int

    #enddef

    def replace_country_list(self,new_composant_countries):
        self.composant_countries=new_composant_countries.copy()
    #enddef

    # possible_name can be either a list or a string, append should
    # still work
    def add_possible_names(self,possible_name):
        if isinstance(possible_name,str):
            self.possible_names.append(possible_name)
            self.possible_names.append("'{}'".format(possible_name))
        else:
            self.possible_names.extend(possible_name)
            self.possible_names.extend("'{}'".format(possible_name))
        #endif

        # Clean them to make sure we don't have duplicates.
        self.possible_names = list( dict.fromkeys(self.possible_names) )

    #enddef

#enddef

# Store the names of the mask files
def get_country_region_mask_file_name(flag):

    if flag == 'afr':

        return "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/african_global_country_region_masks_0.1x0.1.nc"

    elif flag == 'test':


        return "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/test_country_region_masks_0.1x0.1.nc"

    elif flag == "all_countries":

        return "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/all_countries_masks_0.1x0.1.nc"

    elif flag == "all_countries_regions":

        return "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/all_countries_and_regions_masks_0.1x0.1.nc"

    else:
        print("Need to write this!")
        print("flag ",flag)
        sys.exit(1)
    #endif

#enddef

def get_country_codes_for_netCDF_file(flag="eur"):
    # This is the order of country codes that I used to create
    # the country and regional masks.
    #return ["ARG", "AUS", "BRA", "CAN", "CHN", "COD", "IND", "IDN", "IRN", "JPN", "MEX", "NGA", "RUS", "SAU", "ZAF", "USA" ]
    #return ["ALA", "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GGY", "GEO", "GRC", "GRL", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "BNL", "CSK", "SWL", "BLT", "NAC", "DSF", "UKI", "IBE", "WEE", "WEA", "CEE", "NOE", "SOE", "SOY", "SOZ", "SWN", "SEE", "SEA", "SEZ", "EAE", "EEA", "EER", "E12", "E15", "E27", "E28", "EUR"]

    country_region_data=get_country_region_data(loutput_codes=True)
    possible_country_list=get_countries_from_cr_dict(country_region_data)


    # This is the total list
    if flag.lower() in ["eur","eu"]:

        return ["ALA", "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GGY", "GEO", "GRC", "GRL", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "BNL", "CSK", "SWL", "BLT", "NAC", "DSF", "UKI", "IBE", "WEE", "WEA", "CEE", "NOE", "SOE", "SOY", "SOZ", "SWN", "SEE", "SEA", "SEZ", "EAE", "EEA", "EER", "E12", "E15", "E27", "E28", "EUR"]

    elif flag.lower() == "global":

        return ["ALA", "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GGY", "GEO", "GRC", "GRL", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "VRU", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "BNL", "CSK", "SWL", "BLT", "NAC", "DSF", "UKI", "IBE", "WEE", "WEA", "CEE", "NOE", "SOE", "SOY", "SOZ", "SWN", "SEE", "SEA", "SEZ", "EAE", "EEA", "EER", "E12", "E15", "E27", "E28", "EUR", "ARG", "AUS", "BRA", "CAN", "CHN", "COD", "IND", "IDN", "IRN", "JPN", "MEX", "NGA", "RUS", "SAU", "ZAF", "USA"]

    elif flag.lower() == "africa":
        # A list covering Africa.  Notice that
        # the code requires all countries in a region to be present in a file
        # as well, so that it it's clear what countries make up which regions.
        return ["COD", "NGA", "ZAF", "DZA", "SDN", "LBY", "TCD", "NER", "AGO", "MLI", "ETH", "MRT", "EGY", "TZA", "NAM", 'ERI','MAR','TUN', 'BEN','BFA','CIV','CPV','GHA','GIN','GMB','GNB', 'LBR', 'SEN', 'SLE', 'STP', 'TGO', 'CAF','CMR','COG','GAB','SSD', 'BDI','COM','DJI','KEN','SYC','UGA', 'SOM','MDG','MOZ','MUS','MWI','ZMB','ZWE','LSO','SWZ','BWA', "NAF", "SSA", "CNA", "HAF", "SAF", "ZAA", "AFR"]

    elif flag.lower() == "all_countries":
        # This tries to grab all possible countries that we know about.

        country_region_data=get_country_region_data(loutput_codes=True)

        country_list=[]

        for ccode,cr in country_region_data.items():
            if cr.is_country:
                country_list.append(ccode)
            #endif
        #endfor


        return country_list

    elif flag.lower() in ["all_countries_regions","master","allcountriesregions"]:
        # Grab everything

        country_region_data=get_country_region_data(loutput_codes=True)

        country_list=[]

        for ccode,cr in country_region_data.items():
            country_list.append(ccode)
        #endfor


        return country_list

    elif flag in possible_country_list:

        return flag

    elif flag.lower() == "test":

        return ["FRA","BEL","LUX"]

    else:

        print("Do not recognize this country listing!")
        print(flag)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
        
    #endif

#enddef



def get_country_region_data(country_region_plotting_order=["NONE"],loutput_codes=True):

    country_region_data={}

    # This gives the full country name as a function of the ISO-3166 code
    
    # This way lets me check if a key already exists before I add it, in order
    # to prevent trying to use the same ISO code for two different countries.
    # This is more of a problem for regions where we invent ISO codes, as
    # opposed to countries which have them already uniquely assigned.
    country_names={}
    country_names=add_key_to_country_region_names("ALA","Aaland Islands",country_names)
    country_names=add_key_to_country_region_names("ALB","Albania",country_names)
    country_names=add_key_to_country_region_names("AND","Andorra",country_names)
    country_names=add_key_to_country_region_names("AUT","Austria",country_names)
    country_names=add_key_to_country_region_names("BEL","Belgium",country_names)
    country_names=add_key_to_country_region_names("BGR","Bulgaria",country_names)
    country_names=add_key_to_country_region_names("BIH","Bosnia and Herzegovina",country_names)
    country_names=add_key_to_country_region_names("BLR","Belarus",country_names)
    country_names=add_key_to_country_region_names("CHE","Switzerland",country_names)
    country_names=add_key_to_country_region_names("CYP","Cyprus",country_names)
    country_names=add_key_to_country_region_names("CZE","Czech Republic",country_names)
    country_names=add_key_to_country_region_names("DEU","Germany",country_names)
    country_names=add_key_to_country_region_names("DNK","Denmark",country_names)
    country_names=add_key_to_country_region_names("ESP","Spain",country_names)
    country_names=add_key_to_country_region_names("EST","Estonia",country_names)
    country_names=add_key_to_country_region_names("FIN","Finland",country_names)
    country_names=add_key_to_country_region_names("FRA","France",country_names)
    country_names=add_key_to_country_region_names("FRO","Faroe Islands",country_names)
    country_names=add_key_to_country_region_names("GBR","United Kingdom",country_names)
    country_names=add_key_to_country_region_names("GGY","Guernsey",country_names)
    country_names=add_key_to_country_region_names("GEO","Georgia",country_names)
    country_names=add_key_to_country_region_names("GRC","Greece",country_names)
    country_names=add_key_to_country_region_names("GRL","Greenland",country_names)
    country_names=add_key_to_country_region_names("HRV","Croatia",country_names)
    country_names=add_key_to_country_region_names("HUN","Hungary",country_names)
    country_names=add_key_to_country_region_names("IMN","Isle of Man",country_names)
    country_names=add_key_to_country_region_names("IRL","Ireland",country_names)
    country_names=add_key_to_country_region_names("ISL","Iceland",country_names)
    country_names=add_key_to_country_region_names("ITA","Italy",country_names)
    country_names=add_key_to_country_region_names("JEY","Jersey",country_names)
    country_names=add_key_to_country_region_names("LIE","Liechtenstein",country_names)
    country_names=add_key_to_country_region_names("LTU","Lithuania",country_names)
    country_names=add_key_to_country_region_names("LUX","Luxembourg",country_names)
    country_names=add_key_to_country_region_names("LVA","Latvia",country_names)
    country_names=add_key_to_country_region_names("MDA","Moldova, Republic of",country_names)
    country_names=add_key_to_country_region_names("MKD","Macedonia, the former Yugoslav",country_names)
    country_names=add_key_to_country_region_names("MLT","Malta",country_names)
    country_names=add_key_to_country_region_names("MNE","Montenegro",country_names)
    country_names=add_key_to_country_region_names("NLD","Netherlands",country_names)
    country_names=add_key_to_country_region_names("NOR","Norway",country_names)
    country_names=add_key_to_country_region_names("POL","Poland",country_names)
    country_names=add_key_to_country_region_names("PRT","Portugal",country_names)
    country_names=add_key_to_country_region_names("ROU","Romania",country_names)
    country_names=add_key_to_country_region_names("VRU","Russian Federation (VERIFY region)",country_names)
    country_names=add_key_to_country_region_names("SJM","Svalbard and Jan Mayen",country_names)
    country_names=add_key_to_country_region_names("SMR","San Marino",country_names)
    country_names=add_key_to_country_region_names("SRB","Serbia",country_names)
    country_names=add_key_to_country_region_names("SVK","Slovakia",country_names)
    country_names=add_key_to_country_region_names("SVN","Slovenia",country_names)
    country_names=add_key_to_country_region_names("SWE","Sweden",country_names)
    country_names=add_key_to_country_region_names("TUR","Turkey",country_names)
    country_names=add_key_to_country_region_names("UKR","Ukraine",country_names)

# Non-EU countries
    country_names=add_key_to_country_region_names("USA","United States of America",country_names)
    country_names=add_key_to_country_region_names("CHN","China",country_names)
    country_names=add_key_to_country_region_names("AUS","Australia",country_names)
    country_names=add_key_to_country_region_names("ARG","Argentina",country_names)
    country_names=add_key_to_country_region_names("BRA","Brazil",country_names)
    country_names=add_key_to_country_region_names("CAN","Canada",country_names)
    country_names=add_key_to_country_region_names("COD","Democratic Republic of the Congo",country_names)
    country_names=add_key_to_country_region_names("IND","India",country_names)
    country_names=add_key_to_country_region_names("IDN","Indonesia",country_names)
    country_names=add_key_to_country_region_names("IRN","Iran",country_names)
    country_names=add_key_to_country_region_names("JPN","Japan",country_names)
    country_names=add_key_to_country_region_names("MEX","Mexico",country_names)
    country_names=add_key_to_country_region_names("NGA","Nigeria",country_names)
    country_names=add_key_to_country_region_names("RUS","Russian Federation",country_names)
    country_names=add_key_to_country_region_names("SAU","Saudi Arabia",country_names)
    country_names=add_key_to_country_region_names("ZAF","South Africa",country_names)

    # Additional global countries
    country_names=add_key_to_country_region_names("AFG","Afghanistan",country_names)
    country_names=add_key_to_country_region_names("DZA","Algeria",country_names)
    country_names=add_key_to_country_region_names("AGO","Angola",country_names)
    country_names=add_key_to_country_region_names("AZE","Azerbaijan",country_names)
    country_names=add_key_to_country_region_names("BGD","Bangladesh",country_names)
    country_names=add_key_to_country_region_names("BEN","Benin",country_names)
    country_names=add_key_to_country_region_names("BTN","Bhutan",country_names)
    country_names=add_key_to_country_region_names("BOL","Bolivia",country_names)
    country_names=add_key_to_country_region_names("BWA","Botswana",country_names)
    country_names=add_key_to_country_region_names("BRN","Brunei",country_names)
    country_names=add_key_to_country_region_names("BFA","Burkina Faso",country_names)
    country_names=add_key_to_country_region_names("BDI","Burundi",country_names)
    country_names=add_key_to_country_region_names("KHM","Cambodia",country_names)
    country_names=add_key_to_country_region_names("CMR","Cameroon",country_names)

    country_names=add_key_to_country_region_names("CPV","Cape Verde",country_names)
    country_names=add_key_to_country_region_names("CAF","Central African Republic",country_names)
    country_names=add_key_to_country_region_names("TCD","Chad",country_names)
    country_names=add_key_to_country_region_names("CHL","Chile",country_names)
    country_names=add_key_to_country_region_names("COL","Colombia",country_names)
    country_names=add_key_to_country_region_names("COM","Comores",country_names)
    country_names=add_key_to_country_region_names("CRI","Costa Rica",country_names)
    country_names=add_key_to_country_region_names("CUB","Cuba",country_names)
    country_names=add_key_to_country_region_names("DJI","Djibouti",country_names)
    country_names=add_key_to_country_region_names("DMA","Dominica",country_names)
    country_names=add_key_to_country_region_names("DOM","Dominican Republic",country_names)
    country_names=add_key_to_country_region_names("TLS","East Timor",country_names)
    country_names=add_key_to_country_region_names("ECU","Ecuador",country_names)
    country_names=add_key_to_country_region_names("EGY","Egypt",country_names)
    country_names=add_key_to_country_region_names("SLV","El Salvador",country_names)
    country_names=add_key_to_country_region_names("GNQ","Equatorial Guinea",country_names)
    country_names=add_key_to_country_region_names("ERI","Eritrea",country_names)
    country_names=add_key_to_country_region_names("ETH","Ethiopia",country_names)
    country_names=add_key_to_country_region_names("SOM","Federal Republic of Somalia",country_names)
    country_names=add_key_to_country_region_names("FJI","Fiji",country_names)

    country_names=add_key_to_country_region_names("GUF","French Guiana",country_names)
    country_names=add_key_to_country_region_names("GAB","Gabon",country_names)
    country_names=add_key_to_country_region_names("GMB","Gambia",country_names)
    country_names=add_key_to_country_region_names("GHA","Ghana",country_names)
    country_names=add_key_to_country_region_names("GIB","Gibraltar",country_names)
    country_names=add_key_to_country_region_names("GRD","Grenada",country_names)
    country_names=add_key_to_country_region_names("GLP","Guadeloupe",country_names)
    country_names=add_key_to_country_region_names("GUM","Guam",country_names)
    country_names=add_key_to_country_region_names("GTM","Guatemala",country_names)
    country_names=add_key_to_country_region_names("GIN","Guinea",country_names)
    country_names=add_key_to_country_region_names("GNB","Guinea-Bissau",country_names)
    country_names=add_key_to_country_region_names("GUY","Guyana",country_names)
    country_names=add_key_to_country_region_names("HTI","Haiti",country_names)
    country_names=add_key_to_country_region_names("HND","Honduras",country_names)
    country_names=add_key_to_country_region_names("IRQ","Iraq",country_names)
    country_names=add_key_to_country_region_names("ISR","Israel",country_names)
    country_names=add_key_to_country_region_names("CIV","Ivory Coast",country_names)
    country_names=add_key_to_country_region_names("JOR","Jordan",country_names)
    country_names=add_key_to_country_region_names("KAZ","Kazakhstan",country_names)
    country_names=add_key_to_country_region_names("KEN","Kenya",country_names)
    country_names=add_key_to_country_region_names("KWT","Kuwait",country_names)
    country_names=add_key_to_country_region_names("KGZ","Kyrgyzstan",country_names)
    country_names=add_key_to_country_region_names("LAO","Laos",country_names)
    country_names=add_key_to_country_region_names("LBN","Lebanon",country_names)
    country_names=add_key_to_country_region_names("LSO","Lesotho",country_names)
    country_names=add_key_to_country_region_names("LBR","Liberia",country_names)
    country_names=add_key_to_country_region_names("LBY","Libya",country_names)
    country_names=add_key_to_country_region_names("MDG","Madagascar",country_names)
    country_names=add_key_to_country_region_names("MWI","Malawi",country_names)
    country_names=add_key_to_country_region_names("MYS","Malaysia",country_names)
    country_names=add_key_to_country_region_names("MLI","Mali",country_names)
    country_names=add_key_to_country_region_names("MRT","Mauritania",country_names)
    country_names=add_key_to_country_region_names("MNG","Mongolia",country_names)
    country_names=add_key_to_country_region_names("MAR","Morocco",country_names)
    country_names=add_key_to_country_region_names("MOZ","Mozambique",country_names)
    country_names=add_key_to_country_region_names("MMR","Myanmar",country_names)
    country_names=add_key_to_country_region_names("NAM","Namibia",country_names)
    country_names=add_key_to_country_region_names("NPL","Nepal",country_names)
    country_names=add_key_to_country_region_names("NZL","New Zealand",country_names)
    country_names=add_key_to_country_region_names("NIC","Nicaragua",country_names)
    country_names=add_key_to_country_region_names("NER","Niger",country_names)
    country_names=add_key_to_country_region_names("PRK","North Korea",country_names)
    country_names=add_key_to_country_region_names("OMN","Oman",country_names)
    country_names=add_key_to_country_region_names("PAK","Pakistan",country_names)
    country_names=add_key_to_country_region_names("PAN","Panama",country_names)
    country_names=add_key_to_country_region_names("PNG","Papua New Guinea",country_names)
    country_names=add_key_to_country_region_names("PRY","Paraguay",country_names)
    country_names=add_key_to_country_region_names("PER","Peru",country_names)
    country_names=add_key_to_country_region_names("PHL","Philippines",country_names)
    country_names=add_key_to_country_region_names("QAT","Qatar",country_names)
    country_names=add_key_to_country_region_names("MUS","Republic of Mauritius",country_names)
    country_names=add_key_to_country_region_names("COG","Republic of the Congo",country_names)
    country_names=add_key_to_country_region_names("RWA","Rwanda",country_names)
    country_names=add_key_to_country_region_names("STP","Sao Tome and Principe",country_names)
    country_names=add_key_to_country_region_names("SEN","Senegal",country_names)
    country_names=add_key_to_country_region_names("SYC","Seychelles",country_names)
    country_names=add_key_to_country_region_names("SLE","Sierra Leone",country_names)
    country_names=add_key_to_country_region_names("SGP","Singapore",country_names)
    country_names=add_key_to_country_region_names("KOR","South Korea",country_names)
    country_names=add_key_to_country_region_names("SSD","South Sudan",country_names)
    country_names=add_key_to_country_region_names("LKA","Sri Lanka",country_names)
    country_names=add_key_to_country_region_names("SDN","Sudan",country_names)
    country_names=add_key_to_country_region_names("SUR","Suriname",country_names)
    country_names=add_key_to_country_region_names("SWZ","Swaziland",country_names)
    country_names=add_key_to_country_region_names("SYR","Syria",country_names)
    country_names=add_key_to_country_region_names("TWN","Taiwan",country_names)
    country_names=add_key_to_country_region_names("TJK","Tajikistan",country_names)
    country_names=add_key_to_country_region_names("TZA","Tanzania",country_names)
    country_names=add_key_to_country_region_names("THA","Thailand",country_names)
    country_names=add_key_to_country_region_names("TGO","Togo",country_names)
    country_names=add_key_to_country_region_names("TUN","Tunisia",country_names)
    country_names=add_key_to_country_region_names("TKM","Turkmenistan",country_names)
    country_names=add_key_to_country_region_names("UGA","Uganda",country_names)
    country_names=add_key_to_country_region_names("ARE","United Arab Emirates",country_names)
    country_names=add_key_to_country_region_names("URY","Uruguay",country_names)
    country_names=add_key_to_country_region_names("UZB","Uzbekistan",country_names)
    country_names=add_key_to_country_region_names("VEN","Venezuela",country_names)
    country_names=add_key_to_country_region_names("VNM","Vietnam",country_names)
    country_names=add_key_to_country_region_names("ESH","Western Sahara",country_names)
    country_names=add_key_to_country_region_names("YEM","Yemen",country_names)
    country_names=add_key_to_country_region_names("ZMB","Zambia",country_names)
    country_names=add_key_to_country_region_names("ZWE","Zimbabwe",country_names)

    country_names=add_key_to_country_region_names("PSE","Palestine",country_names)
    country_names=add_key_to_country_region_names("FSM","Micronesia (Federated States of)",country_names)
    country_names=add_key_to_country_region_names("MCO","Monaco",country_names)
    country_names=add_key_to_country_region_names("BLZ","Belize",country_names)
    country_names=add_key_to_country_region_names("BHR","Bahrain",country_names)
    country_names=add_key_to_country_region_names("ARM","Armenia",country_names)


    for ccode,cname in country_names.items():
        composant_countries=[]
        composant_countries.append(ccode)
        country_region_data[ccode]=countrydata(ccode,cname,composant_countries)
    #endfor

    # A couple extra possiblities
    country_region_data["MDA"].add_possible_names('Moldova, Republic of')
    country_region_data["MDA"].add_possible_names('Moldova')
    country_region_data["MDA"].add_possible_names('Republic of Moldova')
    country_region_data["MKD"].add_possible_names('Macedonia, the former Yugoslav')
    country_region_data["MKD"].add_possible_names('Macedonia')
    country_region_data["MKD"].add_possible_names('North Macedonia')
    country_region_data["CZE"].add_possible_names('Czech Rep')
    country_region_data["CZE"].add_possible_names('CzechRepublic')
    country_region_data["CZE"].add_possible_names('Czechia')
    country_region_data["GBR"].add_possible_names('UK')
    country_region_data["GBR"].add_possible_names('UnitedKingdom')
    country_region_data["GBR"].add_possible_names('United Kingdom inc. territories (ex. Bermuda)')
    country_region_data["GBR"].add_possible_names('United Kingdom of Great Britain and Northern Ireland')
    country_region_data["BIH"].add_possible_names('BosniaandHerzegovina')
    # This was in H&N.  Assuming it's correct?
    country_region_data["BIH"].add_possible_names('Bosnia')
    country_region_data["RUS"].add_possible_names('Russia')

    country_region_data["FRA"].add_possible_names('France inc. EU territories')

    country_region_data["FRO"].add_possible_names('Faeroe')
    country_region_data["LUX"].add_possible_names('Grand Duchy of Luxembourg')
    country_region_data["SJM"].add_possible_names('Jan Mayen')
    country_region_data["USA"].add_possible_names('United States')
#    country_region_data["USA"].add_possible_names('USA')

    # These are all used in EFISCEN...lowercase values of the code
    for ccode,cname in country_names.items():
        country_region_data[ccode].add_possible_names(ccode.lower())
    #endfor
    # And some special ones
    country_region_data["DEU"].add_possible_names('ger')
    country_region_data["ROU"].add_possible_names('rom')
    country_region_data["SVN"].add_possible_names('slo')
    country_region_data["ESP"].add_possible_names('spa')
    country_region_data["NLD"].add_possible_names('nla')
    country_region_data["BGR"].add_possible_names('bul')
    country_region_data["GBR"].add_possible_names('uka')
    country_region_data["IRL"].add_possible_names('ire')
    country_region_data["CHE"].add_possible_names('swi')
    country_region_data["LTU"].add_possible_names('lit')
    country_region_data["HRV"].add_possible_names('cro')
    country_region_data["GRC"].add_possible_names('gre')
    country_region_data["PRT"].add_possible_names('por')
    country_region_data["LVA"].add_possible_names('lat')
    country_region_data["SVK"].add_possible_names('slr')
    country_region_data["SVK"].add_possible_names('Slovak Republic')
    country_region_data["DNK"].add_possible_names('den')
    country_region_data["MDA"].add_possible_names('mol')
    country_region_data["NOR"].add_possible_names('nor')
    country_region_data["UKR"].add_possible_names('ukr')
    country_region_data["BLR"].add_possible_names('blr')
    country_region_data["NLD"].add_possible_names('The Netherlands')
    country_region_data["CZE"].add_possible_names('Czeck Republick')

    country_region_data["VNM"].add_possible_names('Viet Nam')
    country_region_data["VEN"].add_possible_names('Venezuela (Bolivarian Republic of)')
    country_region_data["TZA"].add_possible_names('United Republic of Tanzania')
    country_region_data["TLS"].add_possible_names('Timor-Leste')
    country_region_data["TLS"].add_possible_names('TimorLeste')
    country_region_data["SYR"].add_possible_names('Syrian Arab Republic')
    country_region_data["SJM"].add_possible_names('Svalbard and Jan Mayen Islands')
    country_region_data["SOM"].add_possible_names('Somalia')
    country_region_data["KOR"].add_possible_names('Republic of Korea')
    country_region_data["PRK"].add_possible_names('Democratic People\'s Republic of Korea')
    country_region_data["LAO"].add_possible_names('Lao People\'s Democratic Republic')
    country_region_data["IRN"].add_possible_names('Iran (Islamic Republic of)')
    country_region_data["ETH"].add_possible_names('Ethiopia PDR')
    country_region_data["SWZ"].add_possible_names('Eswatini')
    country_region_data["CIV"].add_possible_names('Côte d\'Ivoire')
    country_region_data["COG"].add_possible_names('Congo')
    country_region_data["BRN"].add_possible_names('Brunei Darussalam')
    country_region_data["BOL"].add_possible_names('Bolivia (Plurinational State of)')
    country_region_data["FSM"].add_possible_names('Micronesia')

    # These are typos in various files
    country_region_data["HUN"].add_possible_names('Hungay')
    country_region_data["ESP"].add_possible_names('Spania')

    # This is in H&N files
    country_region_data["PRK"].add_possible_names('NorthKorea')
    country_region_data["KOR"].add_possible_names('SouthKorea')
    country_region_data["COD"].add_possible_names('DRC')


    # Now fill out the regional data
    region_names,country_list=get_region_data(country_names,country_region_data)

    for rcode,rname in region_names.items():
        country_region_data[rcode]=countrydata(rcode,region_names[rcode],country_list[rcode])
    #endif

    # And some possible extra region names.  These show up when we read in the name of an old .nc file.
    country_region_data["IBE"].add_possible_names('Spain + Portugal')
    country_region_data["SEE"].add_possible_names('South-Eastern Europe')
    country_region_data["SOE"].add_possible_names('Southern Europe')
    country_region_data["E28"].add_possible_names('EU-28')
    country_region_data["E28"].add_possible_names('TOT EU28') # For H&N
    # Don't use the single quotes...they are added automatically above
    #country_region_data["E28"].add_possible_names("'EU-28'")
    #country_region_data["E28"].add_possible_names("'European Union (Convention)'")
    country_region_data["E28"].add_possible_names("Tot EU")
    country_region_data["E28"].add_possible_names("EU27+UK")
    country_region_data["E28"].add_possible_names("European Union (28)")

    # This changed! Now it's only the EU-27 reported by the UNFCCC.  Need
    # to be careful about this.
    country_region_data["E27"].add_possible_names("European Union (Convention)")



    # Now make sure that all the lists of countries which make up
    # the regions and countries are consistently using either long
    # names or ISO codes
    country_region_data=harmonize_country_lists(country_region_data,True)

    # print things out to make sure they look good
    if country_region_plotting_order[0] != "NONE":
        print("Why here? You must have requested data only on specific countries.")
        print_regions_and_countries(country_region_plotting_order,country_region_data,4,loutput_codes)
    #endif

    return country_region_data
#enddef

# often times I have a country name and I want to know what the ISO code is
def convert_country_to_code(cname,country_region_data):
    output_code=""

    for ccode in country_region_data.keys():
        if cname == country_region_data[ccode].long_name or cname in country_region_data[ccode].possible_names:
            output_code=ccode
        #endif
    #endif

    if not output_code:
        print("Could not find the ISO code for this country: ",cname)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    return output_code

#enddef

# I am concerned about adding an existing key.  So add all
# new keys with a wrapper that checks the existing dictionary.
def add_key_to_country_region_names(keyname,keyvalue,names):
    #country_region_data=add_country_region_data(ccode,cname,composant_countries)
    #country_region_data[ccode]=countrydata(ccode,cname,composant_count

    try:
        testvar=names[keyname]
        lexists=True
    except:
        lexists=False
    #endtry

    if lexists:
        print("Key already exists in the country_region_data!")
        print("Should not happen.  Check your 3-letter ISO codes, as one seems to be used more than once.")
        print("Offending code: ",keyname,keyvalue)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    names[keyname]=keyvalue

    return names

#enddef

# This subroutine defines a list of regions and their 3-letter codes
# using a list of countries.  It returns both the region code,
# the region name, and the list of the countries inside.
def get_region_data(country_names,country_region_data):


    # I do it this way because I can check if a key already exists or
    # not.  I don't want to overwrite a key with the same ISO code.
    region_names={}
    # The following ISO codes don't really exist,
    # and were just cretaed by us for these regions
    region_names=add_key_to_country_region_names("BNL","BENELUX",region_names)
    region_names=add_key_to_country_region_names("UKI","United Kingdom + Ireland",region_names)
    region_names=add_key_to_country_region_names("IBE","Iberia",region_names)
    region_names=add_key_to_country_region_names("WEE","Western Europe",region_names)
    region_names=add_key_to_country_region_names("WEA","Western Europe (alternative)",region_names)
    region_names=add_key_to_country_region_names("CEE","Central Europe",region_names)
    region_names=add_key_to_country_region_names("NOE","Northern Europe",region_names)
    region_names=add_key_to_country_region_names("SOE","Southern Europe (all)",region_names)
    region_names=add_key_to_country_region_names("SOY","Southern Europe (non-EU)",region_names)
    region_names=add_key_to_country_region_names("SOZ","Southern Europe (EU)",region_names)
    region_names=add_key_to_country_region_names("SWN","South-Western Europe",region_names)
    region_names=add_key_to_country_region_names("SEE","South-Eastern Europe (all)",region_names)
    region_names=add_key_to_country_region_names("SEA","South-Eastern Europe (non-EU)",region_names)
    region_names=add_key_to_country_region_names("SEZ","South-Eastern Europe (EU)",region_names)
    region_names=add_key_to_country_region_names("EAE","Eastern Europe",region_names)
    region_names=add_key_to_country_region_names("EEA","Eastern Europe (alternative)",region_names)
    region_names=add_key_to_country_region_names("EER","Eastern Europe (including Russia)",region_names)
    region_names=add_key_to_country_region_names("E12","EU-11+CHE",region_names)
    region_names=add_key_to_country_region_names("E15","EU-15",region_names)
    region_names=add_key_to_country_region_names("E27","EU-27",region_names)
    region_names=add_key_to_country_region_names("E28","EU-27+UK",region_names)
    region_names=add_key_to_country_region_names("EUR","all Europe",region_names)
    region_names=add_key_to_country_region_names("CSK","Former Czechoslovakia",region_names)
    # This conflicted with Chile
    #region_names=add_key_to_country_region_names("CHL","Switzerland + Liechtenstein",region_names)
    region_names=add_key_to_country_region_names("SWL","Switzerland + Liechtenstein",region_names)
    region_names=add_key_to_country_region_names("BLT","Baltic countries",region_names)
    region_names=add_key_to_country_region_names("NAC","North Adriatic Countries",region_names)
    region_names=add_key_to_country_region_names("DSF","Denmark, Sweden, Finland",region_names)
    region_names=add_key_to_country_region_names("FMA","France, Monaco, Andorra",region_names)
    region_names=add_key_to_country_region_names("UMB","Ukraine, Rep. of Moldova, Belarus",region_names)
    region_names=add_key_to_country_region_names("RUG","Russia and Georgia",region_names)

    # For Africa
    region_names=add_key_to_country_region_names("NAF","North Africa",region_names)
    region_names=add_key_to_country_region_names("SSA","Subsahelian West Africa",region_names)
    region_names=add_key_to_country_region_names("CNA","Central Africa",region_names)
    region_names=add_key_to_country_region_names("HAF","Horn of Africa",region_names)
    region_names=add_key_to_country_region_names("SAF","Southern Africa",region_names)
    region_names=add_key_to_country_region_names("ZAA","South Africa and enclaves",region_names)

    # Continents
    region_names=add_key_to_country_region_names("AFR","Africa",region_names)
    region_names=add_key_to_country_region_names("NOA","North America",region_names)
    region_names=add_key_to_country_region_names("SOA","South America",region_names)
    region_names=add_key_to_country_region_names("AIS","Asia",region_names)

    region_names=add_key_to_country_region_names("WLD","World",region_names)

    country_list={}

    # Notice that in some of the regional country groups, I ignore some countries that are small.  Like Andorra or the Aaland Islands.
    for keyval,cval in region_names.items():
        if keyval == "BNL":
            country_list[keyval]=("Belgium","Netherlands","Luxembourg")
        elif keyval == "UKI":
            country_list[keyval]=("United Kingdom","Ireland")
        elif keyval == "IBE":
            country_list[keyval]=("Spain","Portugal")
        elif keyval == "WEE":
            country_list[keyval]=("Belgium","France","United Kingdom","Ireland","Luxembourg","Netherlands")
        elif keyval == "CEE":
            country_list[keyval]=("Austria","Switzerland","Czech Republic","Germany","Hungary","Poland","Slovakia")
        elif keyval == "NOE":
            country_list[keyval]=("Denmark","Estonia","Finland","Lithuania","Latvia", "Norway","Sweden")
        elif keyval == "SOE":
            country_list[keyval]=("Albania","Bulgaria","Bosnia and Herzegovina","Cyprus","Georgia","Greece","Croatia","Macedonia, the former Yugoslav","Montenegro","Romania","Serbia", "Slovenia", "Turkey", "Italy","Malta","Portugal","Spain")
        elif keyval == "SOY":
            country_list[keyval]=('Albania', 'Bosnia and Herzegovina', "Georgia", 'Macedonia, the former Yugoslav', 'Montenegro', 'Serbia', "Turkey")
        elif keyval == "SOZ":
            country_list[keyval]=("Bulgaria","Cyprus","Greece","Croatia","Romania","Slovenia","Italy","Malta","Portugal","Spain")
        elif keyval == "SEE":
            country_list[keyval]=("Albania","Bulgaria","Bosnia and Herzegovina","Cyprus","Georgia","Greece","Croatia","Macedonia, the former Yugoslav","Montenegro","Romania","Serbia", "Slovenia", "Turkey")
        elif keyval == "SEZ":
            country_list[keyval]=("Bulgaria","Cyprus","Greece","Croatia","Romania","Slovenia")
        elif keyval == "SEA":
            country_list[keyval]=('Albania', 'Bosnia and Herzegovina', "Georgia", 'Macedonia, the former Yugoslav', 'Montenegro', 'Serbia', "Turkey")
        elif keyval == "SWN":
            country_list[keyval]=("Italy","Malta","Portugal","Spain")
        elif keyval == "EAE":
            country_list[keyval]=("Belarus","Moldova, Republic of","Russian Federation","Ukraine")
        elif keyval == "EEA":
            country_list[keyval]=("Estonia","Latvia","Lithuania","Belarus", "Poland", "Ukraine")
        elif keyval == "EER":
            country_list[keyval]=("Estonia","Latvia","Lithuania","Belarus", "Poland", "Ukraine","Russian Federation")
        elif keyval == "E12":
            country_list[keyval]=("Portugal","Spain","France","Belgium","Luxembourg","Netherlands","United Kingdom","Germany","Denmark","Italy","Austria","Switzerland")
        elif keyval == "E15":
            country_list[keyval]=("Austria","Belgium","Denmark","Finland","France","Germany","Greece","Ireland","Italy","Luxembourg","Netherlands","Portugal","Spain","Sweden","United Kingdom")
        elif keyval == "E27":
            country_list[keyval]=("Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden")
        elif keyval == "E28":
            country_list[keyval]=("Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom")
        elif keyval == "EUR":
            country_list[keyval]=("Albania","Andorra","Austria","Belgium","Bulgaria","Bosnia and Herzegovina","Belarus","Switzerland","Cyprus","Czech Republic","Germany","Denmark","Spain","Estonia","Finland","France","Faroe Islands","United Kingdom","Guernsey","Greece","Croatia","Hungary","Ireland","Iceland","Italy","Jersey","Liechtenstein","Lithuania","Luxembourg","Latvia","Moldova, Republic of","Macedonia, the former Yugoslav","Malta","Montenegro","Netherlands","Norway","Poland","Portugal","Romania","Russian Federation","Svalbard and Jan Mayen","San Marino","Serbia","Slovakia","Slovenia","Sweden","Turkey","Ukraine")
        elif keyval == "WEA":
            country_list[keyval]=('BEL','FRA','NLD','DEU','CHE','GBR','ESP','PRT')
        elif keyval == "CSK":
            country_list[keyval]=('CZE','SVK')
        elif keyval == "SWL":
            country_list[keyval]=('CHE','LIE')
        elif keyval == "BLT":
            country_list[keyval]=('EST','LTU','LVA')
        elif keyval == "NAC":
            country_list[keyval]=('SVN','HRV')
        elif keyval == "DSF":
            country_list[keyval]=('SWE','DNK','FIN')
        elif keyval == "FMA":
            country_list[keyval]=('FRA','AND')
        elif keyval == "UMB":
            country_list[keyval]=('UKR','MDA','BLR')
        elif keyval == "RUG":
            country_list[keyval]=('RUS','GEO')
            # Regions in Africa
        elif keyval == "NAF": # For North Africa 
            country_list[keyval]=('DZA','EGY','ERI','LBY','MAR','MLI','MRT','NER','SDN','TCD','TUN') 
        elif keyval == "SSA": # For Subsahelian western countries   
            country_list[keyval]=('BEN','BFA','CIV','CPV','GHA','GIN','GMB','GNB', 'LBR','NGA', 'SEN', 'SLE', 'STP', 'TGO') 

        elif keyval == "CNA":  # For Central African (wet) countries.  CAF is
            # already taken by the Central African Republic
            country_list[keyval]=('CAF','CMR','COD','COG','GAB','SSD') 
        elif keyval == "HAF":  # For Countries in the Horn of Africa 
            country_list[keyval]=('BDI','COM','DJI','ETH','KEN','SYC','TZA','UGA', 'SOM') 
        elif keyval == "SAF":  # For Southern countries   
            country_list[keyval]=('AGO','MDG','MOZ','MUS','MWI','NAM','ZMB','ZWE') 
        elif keyval == "ZAA":  # For South Africa & its enclaves 
            country_list[keyval]=('LSO','SWZ','ZAF','BWA') 
        elif keyval == "AFR":  # all the above regions: NAF, SSA, CNA, HAF, SAF, ZAA
            country_list[keyval]=('LSO','SWZ','ZAF','BWA','AGO','MDG','MOZ','MUS','MWI','NAM','ZMB','ZWE', 'BDI','COM','DJI','ETH','KEN','SYC','TZA','UGA', 'SOM', 'CAF','CMR','COD','COG','GAB','SSD','BEN','BFA','CIV','CPV','GHA','GIN','GMB','GNB', 'LBR','NGA', 'SEN', 'SLE', 'STP', 'TGO','DZA','EGY','ERI','LBY','MAR','MLI','MRT','NER','SDN','TCD','TUN')
        elif keyval == "NOA":  # North America
            country_list[keyval]=("BLZ","CAN","CRI","CUB","DMA","DOM","SLV","GRD","GTM","HTI","MEX","NIC","PAN","USA")
        elif keyval == "SOA":  # South America
            country_list[keyval]=("ARG","BOL","BRA","CHL","COL","ECU","GUY","PRY","PER","SUR","URY","VEN")
        elif keyval == "AIS":  # Asia
            country_list[keyval]=("AFG","ARM","AZE","BHR","BGD","BTN","BRN","KHM","CHN","GEO","IND","IDN","IRN","IRQ","ISR","JPN","JOR","KAZ","KWT","KGZ","LAO","LBN","MYS","MNG","MMR","NPL","PRK","OMN","PAK","PSE","PHL","QAT","RUS","SAU","SGP","KOR","LKA","SYR","TWN","TJK","THA","TLS","TUR","TKM","ARE","UZB","VNM","YEM")
        elif keyval == "WLD": # All of the countries in the world
            country_list[keyval]=("ALB","AND","AUT","BEL","BGR","BIH","BLR","CHE","CYP","CZE","DEU","DNK","ESP","EST","FIN","FRA","FRO","GBR","GGY","GEO","GRC","GRL","HRV","HUN","IMN","IRL","ISL","ITA","JEY","LIE","LTU","LUX","LVA","MDA","MKD","MLT","MNE","NLD","NOR","POL","PRT","ROU","SJM","SMR","SRB","SVK","SVN","SWE","TUR","UKR","USA","CHN","AUS","ARG","BRA","CAN","COD","IND","IDN","IRN","JPN","MEX","NGA","RUS","SAU","ZAF","AFG","DZA","AGO","AZE","BGD","BEN","BTN","BOL","BWA","BRN","BFA","BDI","KHM","CMR","CPV","CAF","TCD","CHL","COL","COM","CRI","CUB","DJI","DMA","DOM","TLS","ECU","EGY","SLV","GNQ","ERI","ETH","SOM","FJI","GUF","GAB","GMB","GHA","GIB","GRD","GLP","GUM","GTM","GIN","GNB","GUY","HTI","HND","IRQ","ISR","CIV","JOR","KAZ","KEN","KWT","KGZ","LAO","LBN","LSO","LBR","LBY","MDG","MWI","MYS","MLI","MRT","MNG","MAR","MOZ","MMR","NAM","NPL","NZL","NIC","NER","PRK","OMN","PAK","PAN","PNG","PRY","PER","PHL","QAT","MUS","COG","RWA","STP","SEN","SYC","SLE","SGP","KOR","SSD","LKA","SDN","SUR","SWZ","SYR","TWN","TJK","TZA","THA","TGO","TUN","TKM","UGA","ARE","URY","UZB","VEN","VNM","ESH","YEM","ZMB","ZWE","PSE","FSM","MCO","BLZ","BHR","ARM")
        else:
            print("Should not be be here.  Not a region!")
            print(keyval)
            traceback.print_stack(file=sys.stdout)
            sys.exit() 
        #endif

        # Turn all country names to codes
        for country in country_list[keyval]:
            if country not in country_region_data.keys():
                ccode=""
                for cr_code in country_region_data.keys():
                    if country_region_data[cr_code].long_name == country or country in country_region_data[cr_code].possible_names:
                        ccode=cr_code
                    #endif
                #endif
                        
                if not ccode:
                    print("Did not find a code for country: {}".format(country))
                    traceback.print_stack(file=sys.stdout)
                    sys.exit(1)
                #endif


            #endif
        #endif
        
        # Now pass a filter to only keep certain countries, and print out the resulting string.
        EU28countries=get_selected_country_list("UNFCCC",country_region_data,True)
        modified_string="   elif keyval == \"{} (excluding non-EU-27+UK)\":\n     country_list[keyval] = (".format(keyval)
        for country in EU28countries:
            if country in country_list[keyval]:
                modified_string=modified_string + " \"{}\",".format(country)
            #endif
        #endfor
        modified_string=re.sub(",$",")",modified_string)
        #print(modified_string)

    #endfor
    #print(modified_string)

    # Sort the country list in alphabetical order, just because it's nicer.
    for keyname,keyvalue in country_list.items():
        temp_list=list(keyvalue)
        temp_list.sort()
        country_list[keyname]=tuple(temp_list)
    #endfor

    return region_names,country_list
#enddef



# For a given NetCDF file, look for variables with the names
# country_codes and country_names and check to see which of the 
# countries and regions in the passed dictionary are present in the
# file, returning a dictionary with keys of all the country/region
# names
def find_countries_and_regions_in_file(filename,country_region_data,lremove_unfound=False):

    print("Looking for the countries and regions in file: ",filename)
    if lremove_unfound:
        print("We will remove any countries we don't find in this file from our dict.")
    #endif

    # Open up the file
    srcnc=NetCDFFile(filename,"r")

    # Both country names and country codes are stored as byte strings.
    country_codes_in_file=srcnc["country_code"][:]
    country_codes_in_file = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in country_codes_in_file]
    country_names_in_file = srcnc.variables["country_name"][:]
    country_names_in_file = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in country_names_in_file]

    # Loop over all the country/region names that we went to find.
    for cr_code,cr_data in country_region_data.items():
        cr_data.filename=filename

#        print("jfioezjef ",cr_code,country_codes_in_file)
        if cr_code in country_codes_in_file:
            cr_data.file_index=country_codes_in_file.index(cr_code)

            # Does the name in the file match one of the names we have
            # for this country or region?
            if country_names_in_file[cr_data.file_index] != cr_data.long_name:
                if country_names_in_file[cr_data.file_index] not in cr_data.possible_names:
                    print("Country name in file doesn't match the list of names we have!")
                    print("Code: {}, Long name: \"{}\"".format(cr_code,country_names_in_file[cr_data.file_index]))
                    print("Possible names: ",cr_data.possible_names)
                    print("Please add it to the possible names list.")
                    traceback.print_stack(file=sys.stdout)
                    sys.exit(1)

                else:
                    cr_data.long_name_in_file=cr_data.possible_names.index(country_names_in_file[cr_data.file_index])
                #endif
            else:
                cr_data.long_name_in_file=cr_data.long_name
            #endif
        else:
            cr_data.file_index=cr_data.uninit_int
        #endif
    #endif

    srcnc.close()

    # Print out any countries that we did not find as a warning.
    if lremove_unfound:
        trimmed_cr_data={}
    #endif

    for cr_code,cr_data in country_region_data.items():

        if cr_data.file_index == cr_data.uninit_int:
            print("WARNING: Did not find {} ({}) in the .nc country mask file.".format(cr_data.long_name,cr_code))
        else:
            if not cr_data.long_name_in_file:
                print("WARNING: Did not find a long name in the .nc country mask file for {} ({}).".format(cr_data.long_name,cr_code))
                
            #endif

            if lremove_unfound:
                trimmed_cr_data[cr_code]=cr_data
            #endif

        #endif
    #endfor

    if lremove_unfound:
        return trimmed_cr_data
    else:
        return country_region_data
    #endif

#enddef

def get_selected_country_list(list_name,country_region_data,loutput_codes):


    if list_name == "EU-27+UK":
        return_countries=["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom"]
    elif list_name == "UNFCCC":
        # EU-27+UK along with a couple extra, which submit annual reports to the UNFCCC
        return_countries=["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom","Switzerland","Norway","Iceland"]
    else:
        print("I do not know what this list name is!")
        print(list_name)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    # translate the countries to three letter codes, if need be
    if loutput_codes:
        for country in return_countries:
            ccode=""
            for cr_code in country_region_data.keys():
                if country_region_data[cr_code].long_name == country or country in country_region_data[cr_code].possible_names:
                    ccode=cr_code
                #endif
            #endif

            if not ccode:
                print("Did not find a code for country: {}".format(country))
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endif
        #endif

    #endif

    return return_countries

def harmonize_country_lists(country_region_data,loutput_codes):

    # Harmonize the list to be either country codes or country names.

    country_names=get_countries_from_cr_dict(country_region_data)

    for cr_code,cr_data in country_region_data.items():

        clist=cr_data.composant_countries

        new_country_list=[]

        # Are we listing codes?
        lcodes=False
        if clist[0] in country_names.keys():
            lcodes=True
        #endif

        if not loutput_codes:
            # We want to print out country names
            if lcodes:
                for country in clist:
                    new_country_list.append(country_names[country])
                #endfor
            else:
                # Nothing to change
                for country in clist:
                    new_country_list.append(country)
                #endfor
            #endif

        else:
            # We want to print out the codes
            if not lcodes:
                # Search for this code based on the name.
                for country in clist:
                    for cr_code2,cr_data2 in country_region_data.items():
                        if cr_data2.long_name == country:
                            new_country_list.append(cr_code2)
                        else:
                            
                            for possible_name in cr_data2.possible_names:
                                if possible_name == country:
                                    new_country_list.append(cr_code2)
                                #endif
                            #endfor
                            
                        #endif
                    #endfor
                #endfor

            else:
                # Nothing to change
                for country in clist:
                    new_country_list.append(country)
                #endfor
            #endif

        #endif
        
        if len(new_country_list) != len(cr_data.composant_countries):
            print("Messed up in replacing the composant countries list!")
            print("Lists should be the same length.")
            print("New countries: ",new_country_list)
            print("Old countries: ",cr_data.composant_countries)
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif
        cr_data.replace_country_list(new_country_list)
      
    #endfor

    return country_region_data
#enddef

# This takes a dictionary of country_region datatypes and returns
# a dictionary of all the countries, with the key being the ISO code
# and the value being the full country name
def get_countries_from_cr_dict(country_region_data):

    country_list={}

    for ccode,cr_data in country_region_data.items():
        if cr_data.is_country:
            country_list[cr_data.iso_code]=cr_data.long_name
        #endif
    #endif

    return country_list
#enddef

# The same as above, but now look for regions as well.  
def get_countries_and_regions_from_cr_dict(country_region_data):

    cr_list={}

    for ccode,cr_data in country_region_data.items():
        cr_list[cr_data.iso_code]=cr_data.long_name
    #endif

    return cr_list
#enddef

# The same as above, but now only look for regions  
def get_regions_from_cr_dict(country_region_data):

    r_list={}

    for ccode,cr_data in country_region_data.items():
        if not cr_data.is_country:
            r_list[cr_data.iso_code]=cr_data.long_name
        #endif
    #endif

    return r_list
#enddef

# print the countries, regions, and composant countries in a nice
# way that I can possible share with others or use in other
# scripts
def print_regions_and_countries(country_region_plotting_order,country_region_data,print_code,loutput_codes):

    if print_code == 1:
        print("Listing all countries and regions.")
        
        for ccode,cr_data in country_region_data.items():
            if loutput_codes:
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),cr_data.composant_countries)
            else:
                clist=[]
                for tempc in cr_data.composant_countries:
                    clist.append(country_region_data[tempc].long_name)
                #endif
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),clist)
            #endif            
        #endfor

    elif print_code == 2:
        # Print this out for use elsewhere

        print_string="country_region_plotting_order=["
        for ccode,cr_data in country_region_data.items():
            print_string=print_string+"\"{}\", ".format(ccode)
        #endfor    
        # Remove the trailing comma and space
        print_string=re.sub(", $","]",print_string)
        print(print_string)

    elif print_code == 3:

        for icount,country in enumerate(country_region_plotting_order):
            temp_list=country_region_data[country].composant_countries.copy()
            temp_list.sort()
            if loutput_codes:
                print("      Index {0}, \"{2}\" ({1}) : ".format(icount+1,country,country_region_data[country].long_name),temp_list)
            else:
                clist=[]
                for tempc in temp_list:
                    clist.append(country_region_data[tempc].long_name)
                #endif
                print("      Index {0}, \"{2}\" ({1}) : ".format(icount+1,country,country_region_data[country].long_name),clist)

            #endif            
        #endfor

    elif print_code == 4:

        print("Listing only certain countries and regions.")
        
        for icount,country in enumerate(country_region_plotting_order):
            ccode=country
            try:
                cr_data=country_region_data[ccode]
            except:
                print("Code does not exist! ",ccode)
                traceback.print_stack(file=sys.stdout)
                traceback.print_stack(file=sys.stdout)
                sys.exit(1)
            #endtry
            if loutput_codes:
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),cr_data.composant_countries)
            else:
                clist=[]
                for tempc in cr_data.composant_countries:
                    clist.append(country_region_data[tempc].long_name)
                #endif
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),clist)
            #endif            
        #endfor

    elif print_code == 5:

        filename="regions.csv"
        print("Creating {} file for Robbie Andrew.".format(filename))
        f=open(filename,"w+")

        ncountries_max=len(country_region_plotting_order)
        # Need on column for the index, one for the name, one for the code, and then
        # however many may be used for the list of countries
        
        # I do not see a good way to do this with dataframes
        for icount,country in enumerate(country_region_plotting_order):
            ccode=country
            cr_data=country_region_data[ccode]

            print_string="{},\"{}\",{},".format(icount+1,country_region_data[ccode].long_name,ccode)
            for jcount in range(ncountries_max):
                if jcount < len(cr_data.composant_countries):
                    print_string=print_string + "\"{}\",".format(country_region_data[cr_data.composant_countries[jcount]].long_name)
                else:
                    print_string=print_string + ","
                #endif
            #endfor
            print_string=print_string + "\n"
            f.write(print_string)
        #endfor

        f.close()

    # Doesn't matter if it's codes or names here
    elif print_code == 6:

        print("Printing the countries/codes requested.")
        
        for icount,country in enumerate(country_region_plotting_order):
            ccode=country
            cr_data=None
            try:
                cr_data=country_region_data[ccode]
            except:

                for temp_code in country_region_data.keys():
                    if country in country_region_data[temp_code].possible_names:
                        ccode=temp_code
                        cr_data=country_region_data[ccode]
                    #endif
                #endfor

                if cr_data is None:
                    print("Could not find country name or code: ",country)
                    traceback.print_stack(file=sys.stdout)
                    sys.exit(1)
                #endif
            #endtry
            if loutput_codes:
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),cr_data.composant_countries)
            else:
                clist=[]
                for tempc in cr_data.composant_countries:
                    clist.append(country_region_data[tempc].long_name)
                #endif
                print("{1} ({0}) : ".format(ccode,cr_data.long_name),clist)
            #endif            
        #endfor

    else:
        print("I do not know this print code: ",print_code)
    #endif

    

#enddef

# NOTE:  I had to modify this routine, I think because it was global and the bounds went from
# 180W:180E so there was overlap?
def plot_map(data,lat,lon,plot_filename,plot_title):
    # it seems that pcolormesh expects the boundaries of the polygons/mesh, not the centers.
    # This function tries to create the boundaries from the lon and lat
    def setBounds(nodes):
        bounds = (nodes[1:] + nodes[:-1])/2.
        bound0 = nodes[0] - (nodes[1]-nodes[0])/2.
        boundN = nodes[-1] + (nodes[-1]-nodes[-2])/2.
        return np.append(np.append(bound0, bounds), boundN)
        
    meshlat = np.clip(setBounds(lat), -90, 90)
    meshlon = np.clip(setBounds(lon), -180, 180)

    # this was the line that needed modification, reducing the array size
    #meshlon, meshlat = np.meshgrid(meshlon[0:360], meshlat[0:180])
    meshlon, meshlat = np.meshgrid(meshlon, meshlat)
    #print("jfioez lon: ",meshlon.shape,lon)
    #print("jfioez lat: ",meshlat.shape,lat)
    #print("jfioez data: ",data.shape)

    fig=plt.figure()

    #rbb = np.loadtxt('cmaps/runoff-brownblue.txt')/255;
    #rbb = mpl.colors.ListedColormap(rbb)
    #map.pcolormesh(x,y,ch4_mean,vmin=0.0,vmax=100.0, rasterized=False, edgecolor='0.6', linewidth=0)
    fig=plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
    # In order to get the full resolution, I needed to download another package
    # conda install -c conda-forge basemap-data-hires
    map = Basemap(projection='cyl',llcrnrlon=-25.,llcrnrlat=35.,urcrnrlon=45.,urcrnrlat=73.,resolution='i') # projection, lat/lon extents and resolution of polygons to draw
    # resolutions: c - crude, l - low, i - intermediate, h - high, f - full
    #map.pcolormesh(x,y,ch4_mean)
    
    #print \"JIOFE\",data.shape
    #print len(meshlon),len(meshlat)
    map.drawcoastlines()
    cmap = plt.cm.Reds # for difference maps it's better to use 'plt.cm.seismic'
    cmesh = map.pcolormesh(meshlon, meshlat,data, shading="flat", cmap=cmap, latlon=True)
    cbar = map.colorbar(cmesh, pad = 0.08)
    
    plt.title(plot_title)
    

#    plt.imshow(newnc["country_mask"][country_region_data_new[ccode].file_index,:,:], cmap='hot', interpolation='nearest')
    fig.savefig(plot_filename)
    plt.close()
#enddef

# If you run this routine by itself, it will do a check of the  names to
# make sure no common errors are commit.

if __name__ == '__main__':

    country_region_data=get_country_region_data()

    # I am concerned about key repetition, but I deal with that above.  This
    # prints out some lines useful for me, but only rarely.
    if False:
        for ccode,cr_data in country_region_data.items():
            if not cr_data.is_country:
                print("    region_names=add_key_to_country_region_names(\"{}\",\"{}\",region_names)".format(ccode,cr_data.long_name))
            else:
                print("    country_names=add_key_to_country_region_names(\"{}\",\"{}\",country_names)".format(ccode,cr_data.long_name))
            #endif
        #endfor
    #endif

    # Check to make sure that none of the long names are repeated.  Because
    # I was once smart (even though I forget this), the long_name is already
    # included in the possible_names.  So I just need to loop through those.
    country_region_data=get_country_region_data()
    print("**********************************************************")
    print("Checking to see if any possible country names are repeated.")
    print("**********************************************************")
    for ccode,cr_data in country_region_data.items():
        if cr_data.is_country:
            print("Testing country: {} ({})".format(cr_data.long_name,ccode))
        else:
            print("Testing region: {} ({})".format(cr_data.long_name,ccode))
        #endif

        for country in cr_data.possible_names:
            for ccode2,cr_data2 in country_region_data.items():
                # The same country will obviously have the same names
                if ccode == ccode2:
                    continue
                #endif
                for country2 in cr_data2.possible_names:
                    if country == country2:
                        print("Two countries/regions have the same possible name!")
                        print("{} ({})".format(country,ccode))
                        print("{} ({})".format(country2,ccode2))
                        traceback.print_stack(file=sys.stdout)
                        sys.exit(1)
                    #endif
                #endfor
            #endfor
        #endfor
    #endfor

    # This is also a feature I need often: printing out the current countries
    # and regions in the .nc country mask file.
    country_region_plotting_order=get_country_codes_for_netCDF_file('all_countries')
    country_region_data=get_country_region_data(country_region_plotting_order,False)
    print_regions_and_countries(country_region_plotting_order,country_region_data,3,False)

    # Something I use from time to time: from country symbols/names, print
    # out names.
    #print("***********************************************")    
    #print("***********************************************")
    #temp_countries=['FRA','ESP','Belgium','Germany','HUN','Ireland','Italy','LUX','NLD','Poland','Romania','Slovakia','Sweden','CHE','CZE','Norway']
    #print_regions_and_countries(temp_countries,country_region_data,6,False)
    
    country_region_plotting_order=get_country_codes_for_netCDF_file('all_countries_regions')
    country_region_data=get_country_region_data(country_region_plotting_order,False)
    for ccode in country_region_plotting_order:
        print(country_region_data[ccode].long_name,end=', ')
    #endfor

#endif

def get_country_areas():

    # This is taken from our map with 231 regions.  Values are in square meters.
    # Note that this likely does not correspond exactly to reported values from
    # other sources, like the CIA World Factbook.  The reason is that our
    # maps are at 0.1 degree resolution, and different islands may or may
    # not be included for different countries.
    # But it's the correct value for our purposes.
    
    
    country_areas={}
    country_areas["ALA"]=0.0
    country_areas["Aaland Islands"]=0.0
    country_areas["ALB"]=28403729964.533092
    country_areas["Albania"]=28403729964.533092
    country_areas["AND"]=467339618.26239836
    country_areas["Andorra"]=467339618.26239836
    country_areas["AUT"]=83748548378.0139
    country_areas["Austria"]=83748548378.0139
    country_areas["BEL"]=30507407847.67136
    country_areas["Belgium"]=30507407847.67136
    country_areas["BGR"]=110794845627.58957
    country_areas["Bulgaria"]=110794845627.58957
    country_areas["BIH"]=50892196600.18733
    country_areas["Bosnia and Herzegovina"]=50892196600.18733
    country_areas["BLR"]=206744026372.2419
    country_areas["Belarus"]=206744026372.2419
    country_areas["CHE"]=41173435818.76799
    country_areas["Switzerland"]=41173435818.76799
    country_areas["CYP"]=9513605364.135891
    country_areas["Cyprus"]=9513605364.135891
    country_areas["CZE"]=78583121937.57463
    country_areas["Czech Republic"]=78583121937.57463
    country_areas["DEU"]=356597496940.14374
    country_areas["Germany"]=356597496940.14374
    country_areas["DNK"]=44282759405.7745
    country_areas["Denmark"]=44282759405.7745
    country_areas["ESP"]=499014620746.97473
    country_areas["Spain"]=499014620746.97473
    country_areas["EST"]=44435815746.95287
    country_areas["Estonia"]=44435815746.95287
    country_areas["FIN"]=335009537265.25946
    country_areas["Finland"]=335009537265.25946
    country_areas["FRA"]=548281675248.06555
    country_areas["France"]=548281675248.06555
    country_areas["FRO"]=1158914740.7913857
    country_areas["Faroe Islands"]=1158914740.7913857
    country_areas["GBR"]=244179574861.43985
    country_areas["United Kingdom"]=244179574861.43985
    country_areas["GGY"]=80386254.91157633
    country_areas["Guernsey"]=80386254.91157633
    country_areas["GEO"]=69545435837.88736
    country_areas["Georgia"]=69545435837.88736
    country_areas["GRC"]=132632295326.31711
    country_areas["Greece"]=132632295326.31711
    country_areas["GRL"]=2148418183679.8105
    country_areas["Greenland"]=2148418183679.8105
    country_areas["HRV"]=57432208149.80404
    country_areas["Croatia"]=57432208149.80404
    country_areas["HUN"]=92758085842.22244
    country_areas["Hungary"]=92758085842.22244
    country_areas["IMN"]=0.0
    country_areas["Isle of Man"]=0.0
    country_areas["IRL"]=70376306240.37564
    country_areas["Ireland"]=70376306240.37564
    country_areas["ISL"]=101379044008.18846
    country_areas["Iceland"]=101379044008.18846
    country_areas["ITA"]=300630072490.7499
    country_areas["Italy"]=300630072490.7499
    country_areas["JEY"]=80713916.22927046
    country_areas["Jersey"]=80713916.22927046
    country_areas["LIE"]=158966779.4316861
    country_areas["Liechtenstein"]=158966779.4316861
    country_areas["LTU"]=64560432490.915825
    country_areas["Lithuania"]=64560432490.915825
    country_areas["LUX"]=2587131008.421216
    country_areas["Luxembourg"]=2587131008.421216
    country_areas["LVA"]=64137018229.44409
    country_areas["Latvia"]=64137018229.44409
    country_areas["MDA"]=33747329045.029793
    country_areas["Moldova, Republic of"]=33747329045.029793
    country_areas["MKD"]=25402634628.62013
    country_areas["Macedonia, the former Yugoslav"]=25402634628.62013
    country_areas["MLT"]=400528138.612553
    country_areas["Malta"]=400528138.612553
    country_areas["MNE"]=13739613620.7069
    country_areas["Montenegro"]=13739613620.7069
    country_areas["NLD"]=35210041538.28647
    country_areas["Netherlands"]=35210041538.28647
    country_areas["NOR"]=323609880277.346
    country_areas["Norway"]=323609880277.346
    country_areas["POL"]=310582664237.88336
    country_areas["Poland"]=310582664237.88336
    country_areas["PRT"]=89355276715.31728
    country_areas["Portugal"]=89355276715.31728
    country_areas["ROU"]=236942550565.27542
    country_areas["Romania"]=236942550565.27542
    country_areas["VRU"]=0.0
    country_areas["Russian Federation (VERIFY region)"]=0.0
    country_areas["SJM"]=281912751.39908695
    country_areas["Svalbard and Jan Mayen"]=281912751.39908695
    country_areas["SMR"]=60545543.22146265
    country_areas["San Marino"]=60545543.22146265
    country_areas["SRB"]=88158467496.20255
    country_areas["Serbia"]=88158467496.20255
    country_areas["SVK"]=48878657696.59709
    country_areas["Slovakia"]=48878657696.59709
    country_areas["SVN"]=20145893399.826733
    country_areas["Slovenia"]=20145893399.826733
    country_areas["SWE"]=447987652064.10236
    country_areas["Sweden"]=447987652064.10236
    country_areas["TUR"]=780314085755.859
    country_areas["Turkey"]=780314085755.859
    country_areas["UKR"]=597228267471.4784
    country_areas["Ukraine"]=597228267471.4784
    country_areas["USA"]=7945097358056.648
    country_areas["United States of America"]=7945097358056.648
    country_areas["CHN"]=9373603223691.232
    country_areas["China"]=9373603223691.232
    country_areas["AUS"]=7703725444299.86
    country_areas["Australia"]=7703725444299.86
    country_areas["ARG"]=2780389413459.763
    country_areas["Argentina"]=2780389413459.763
    country_areas["BRA"]=8508548673700.444
    country_areas["Brazil"]=8508548673700.444
    country_areas["CAN"]=9929164446392.24
    country_areas["Canada"]=9929164446392.24
    country_areas["COD"]=2339539118145.888
    country_areas["Democratic Republic of the Congo"]=2339539118145.888
    country_areas["IND"]=3155397248175.8125
    country_areas["India"]=3155397248175.8125
    country_areas["IDN"]=1899543491759.521
    country_areas["Indonesia"]=1899543491759.521
    country_areas["IRN"]=1682537655545.9219
    country_areas["Iran"]=1682537655545.9219
    country_areas["JPN"]=373085465629.33044
    country_areas["Japan"]=373085465629.33044
    country_areas["MEX"]=1960822920298.7317
    country_areas["Mexico"]=1960822920298.7317
    country_areas["NGA"]=913778575565.5973
    country_areas["Nigeria"]=913778575565.5973
    country_areas["RUS"]=16914279148081.172
    country_areas["Russian Federation"]=16914279148081.172
    country_areas["SAU"]=1930110156233.9976
    country_areas["Saudi Arabia"]=1930110156233.9976
    country_areas["ZAF"]=1221293672141.8518
    country_areas["South Africa"]=1221293672141.8518
    country_areas["AFG"]=642125588882.7921
    country_areas["Afghanistan"]=642125588882.7921
    country_areas["DZA"]=2317127437857.8687
    country_areas["Algeria"]=2317127437857.8687
    country_areas["AGO"]=1252404974718.7832
    country_areas["Angola"]=1252404974718.7832
    country_areas["AZE"]=166367710247.79614
    country_areas["Azerbaijan"]=166367710247.79614
    country_areas["BGD"]=140223377467.76868
    country_areas["Bangladesh"]=140223377467.76868
    country_areas["BEN"]=115879107428.06175
    country_areas["Benin"]=115879107428.06175
    country_areas["BTN"]=40102969225.3669
    country_areas["Bhutan"]=40102969225.3669
    country_areas["BOL"]=1086349364369.755
    country_areas["Bolivia"]=1086349364369.755
    country_areas["BWA"]=579636193917.893
    country_areas["Botswana"]=579636193917.893
    country_areas["BRN"]=5772558977.731426
    country_areas["Brunei"]=5772558977.731426
    country_areas["BFA"]=275090510072.5573
    country_areas["Burkina Faso"]=275090510072.5573
    country_areas["BDI"]=26950535402.53504
    country_areas["Burundi"]=26950535402.53504
    country_areas["KHM"]=181791295658.5821
    country_areas["Cambodia"]=181791295658.5821
    country_areas["CMR"]=467165071869.8608
    country_areas["Cameroon"]=467165071869.8608
    country_areas["CPV"]=4161968009.7531824
    country_areas["Cape Verde"]=4161968009.7531824
    country_areas["CAF"]=622976534806.5375
    country_areas["Central African Republic"]=622976534806.5375
    country_areas["TCD"]=1275383683156.3767
    country_areas["Chad"]=1275383683156.3767
    country_areas["CHL"]=757954559479.7275
    country_areas["Chile"]=757954559479.7275
    country_areas["COL"]=1141850206818.395
    country_areas["Colombia"]=1141850206818.395
    country_areas["COM"]=1694343314.1047904
    country_areas["Comores"]=1694343314.1047904
    country_areas["CRI"]=51273204627.45103
    country_areas["Costa Rica"]=51273204627.45103
    country_areas["CUB"]=110219761920.26
    country_areas["Cuba"]=110219761920.26
    country_areas["DJI"]=21630871957.62253
    country_areas["Djibouti"]=21630871957.62253
    country_areas["DMA"]=715166775.1916752
    country_areas["Dominica"]=715166775.1916752
    country_areas["DOM"]=48775913294.378105
    country_areas["Dominican Republic"]=48775913294.378105
    country_areas["TLS"]=14479137568.18766
    country_areas["East Timor"]=14479137568.18766
    country_areas["ECU"]=249459550228.98538
    country_areas["Ecuador"]=249459550228.98538
    country_areas["EGY"]=983629773201.4208
    country_areas["Egypt"]=983629773201.4208
    country_areas["SLV"]=20316892281.853947
    country_areas["El Salvador"]=20316892281.853947
    country_areas["GNQ"]=26752578892.394943
    country_areas["Equatorial Guinea"]=26752578892.394943
    country_areas["ERI"]=121257148056.9079
    country_areas["Eritrea"]=121257148056.9079
    country_areas["ETH"]=1133816763066.5762
    country_areas["Ethiopia"]=1133816763066.5762
    country_areas["SOM"]=634836948198.8097
    country_areas["Federal Republic of Somalia"]=634836948198.8097
    country_areas["FJI"]=18277289962.67599
    country_areas["Fiji"]=18277289962.67599
    country_areas["GUF"]=82684732092.43335
    country_areas["French Guiana"]=82684732092.43335
    country_areas["GAB"]=264535477261.3062
    country_areas["Gabon"]=264535477261.3062
    country_areas["GMB"]=10371152346.774075
    country_areas["Gambia"]=10371152346.774075
    country_areas["GHA"]=239759684232.79828
    country_areas["Ghana"]=239759684232.79828
    country_areas["GIB"]=46942718.61660928
    country_areas["Gibraltar"]=46942718.61660928
    country_areas["GRD"]=362740923.615077
    country_areas["Grenada"]=362740923.615077
    country_areas["GLP"]=1662254258.953976
    country_areas["Guadeloupe"]=1662254258.953976
    country_areas["GUM"]=481084335.73081803
    country_areas["Guam"]=481084335.73081803
    country_areas["GTM"]=109844225845.32791
    country_areas["Guatemala"]=109844225845.32791
    country_areas["GIN"]=245935164401.5874
    country_areas["Guinea"]=245935164401.5874
    country_areas["GNB"]=34428342130.71771
    country_areas["Guinea-Bissau"]=34428342130.71771
    country_areas["GUY"]=211605039454.75156
    country_areas["Guyana"]=211605039454.75156
    country_areas["HTI"]=27608995143.334095
    country_areas["Haiti"]=27608995143.334095
    country_areas["HND"]=113265833995.51172
    country_areas["Honduras"]=113265833995.51172
    country_areas["IRQ"]=437505529646.8777
    country_areas["Iraq"]=437505529646.8777
    country_areas["ISR"]=20746226882.149605
    country_areas["Israel"]=20746226882.149605
    country_areas["CIV"]=323570806179.01447
    country_areas["Ivory Coast"]=323570806179.01447
    country_areas["JOR"]=89399781030.96234
    country_areas["Jordan"]=89399781030.96234
    country_areas["KAZ"]=2828915956234.09
    country_areas["Kazakhstan"]=2828915956234.09
    country_areas["KEN"]=586067931510.2465
    country_areas["Kenya"]=586067931510.2465
    country_areas["KWT"]=17403760273.50218
    country_areas["Kuwait"]=17403760273.50218
    country_areas["KGZ"]=199396774036.09842
    country_areas["Kyrgyzstan"]=199396774036.09842
    country_areas["LAO"]=230493888740.39655
    country_areas["Laos"]=230493888740.39655
    country_areas["LBN"]=10203548980.37331
    country_areas["Lebanon"]=10203548980.37331
    country_areas["LSO"]=30590722847.48671
    country_areas["Lesotho"]=30590722847.48671
    country_areas["LBR"]=96327383750.51065
    country_areas["Liberia"]=96327383750.51065
    country_areas["LBY"]=1619104624205.637
    country_areas["Libya"]=1619104624205.637
    country_areas["MDG"]=594300718446.775
    country_areas["Madagascar"]=594300718446.775
    country_areas["MWI"]=118988083350.91748
    country_areas["Malawi"]=118988083350.91748
    country_areas["MYS"]=331120563193.0198
    country_areas["Malaysia"]=331120563193.0198
    country_areas["MLI"]=1256519336979.918
    country_areas["Mali"]=1256519336979.918
    country_areas["MRT"]=1042378089366.7018
    country_areas["Mauritania"]=1042378089366.7018
    country_areas["MNG"]=1560941359857.5664
    country_areas["Mongolia"]=1560941359857.5664
    country_areas["MAR"]=406310645588.0444
    country_areas["Morocco"]=406310645588.0444
    country_areas["MOZ"]=788647672584.5015
    country_areas["Mozambique"]=788647672584.5015
    country_areas["MMR"]=671509805946.8481
    country_areas["Myanmar"]=671509805946.8481
    country_areas["NAM"]=827336324129.0366
    country_areas["Namibia"]=827336324129.0366
    country_areas["NPL"]=147522990653.09576
    country_areas["Nepal"]=147522990653.09576
    country_areas["NZL"]=269216637568.30383
    country_areas["New Zealand"]=269216637568.30383
    country_areas["NIC"]=129198749731.9308
    country_areas["Nicaragua"]=129198749731.9308
    country_areas["NER"]=1185086610022.303
    country_areas["Niger"]=1185086610022.303
    country_areas["PRK"]=122299898595.31816
    country_areas["North Korea"]=122299898595.31816
    country_areas["OMN"]=308802771388.3172
    country_areas["Oman"]=308802771388.3172
    country_areas["PAK"]=873753807256.1276
    country_areas["Pakistan"]=873753807256.1276
    country_areas["PAN"]=75106744382.37599
    country_areas["Panama"]=75106744382.37599
    country_areas["PNG"]=467073074624.61755
    country_areas["Papua New Guinea"]=467073074624.61755
    country_areas["PRY"]=401708410465.88196
    country_areas["Paraguay"]=401708410465.88196
    country_areas["PER"]=1298001228410.8037
    country_areas["Peru"]=1298001228410.8037
    country_areas["PHL"]=296572775183.66125
    country_areas["Philippines"]=296572775183.66125
    country_areas["QAT"]=11434194501.487688
    country_areas["Qatar"]=11434194501.487688
    country_areas["MUS"]=1972509287.9617226
    country_areas["Republic of Mauritius"]=1972509287.9617226
    country_areas["COG"]=343906651834.36975
    country_areas["Republic of the Congo"]=343906651834.36975
    country_areas["RWA"]=25436453186.48775
    country_areas["Rwanda"]=25436453186.48775
    country_areas["STP"]=865555777.1559033
    country_areas["Sao Tome and Principe"]=865555777.1559033
    country_areas["SEN"]=197288929979.9065
    country_areas["Senegal"]=197288929979.9065
    country_areas["SYC"]=613783255.1460347
    country_areas["Seychelles"]=613783255.1460347
    country_areas["SLE"]=72883804670.50806
    country_areas["Sierra Leone"]=72883804670.50806
    country_areas["SGP"]=584697733.4522979
    country_areas["Singapore"]=584697733.4522979
    country_areas["KOR"]=99733519348.43994
    country_areas["South Korea"]=99733519348.43994
    country_areas["SSD"]=635316232070.4131
    country_areas["South Sudan"]=635316232070.4131
    country_areas["LKA"]=66052609512.99855
    country_areas["Sri Lanka"]=66052609512.99855
    country_areas["SDN"]=1877537241346.0352
    country_areas["Sudan"]=1877537241346.0352
    country_areas["SUR"]=146238435329.08807
    country_areas["Suriname"]=146238435329.08807
    country_areas["SWZ"]=17414059422.170784
    country_areas["Swaziland"]=17414059422.170784
    country_areas["SYR"]=187771183171.93817
    country_areas["Syria"]=187771183171.93817
    country_areas["TWN"]=35992885838.724236
    country_areas["Taiwan"]=35992885838.724236
    country_areas["TJK"]=142310835054.88702
    country_areas["Tajikistan"]=142310835054.88702
    country_areas["TZA"]=944123890237.4835
    country_areas["Tanzania"]=944123890237.4835
    country_areas["THA"]=516919865966.75616
    country_areas["Thailand"]=516919865966.75616
    country_areas["TGO"]=56981658744.712875
    country_areas["Togo"]=56981658744.712875
    country_areas["TUN"]=155312977669.75787
    country_areas["Tunisia"]=155312977669.75787
    country_areas["TKM"]=549574363964.98047
    country_areas["Turkmenistan"]=549574363964.98047
    country_areas["UGA"]=242595522086.42502
    country_areas["Uganda"]=242595522086.42502
    country_areas["ARE"]=70977108668.2415
    country_areas["United Arab Emirates"]=70977108668.2415
    country_areas["URY"]=177979385432.38406
    country_areas["Uruguay"]=177979385432.38406
    country_areas["UZB"]=446652586958.7213
    country_areas["Uzbekistan"]=446652586958.7213
    country_areas["VEN"]=915139397499.4437
    country_areas["Venezuela"]=915139397499.4437
    country_areas["VNM"]=328883531922.08624
    country_areas["Vietnam"]=328883531922.08624
    country_areas["ESH"]=270909500006.36896
    country_areas["Western Sahara"]=270909500006.36896
    country_areas["YEM"]=455702549413.3471
    country_areas["Yemen"]=455702549413.3471
    country_areas["ZMB"]=754013445256.9473
    country_areas["Zambia"]=754013445256.9473
    country_areas["ZWE"]=391888320610.12494
    country_areas["Zimbabwe"]=391888320610.12494
    country_areas["PSE"]=6208537679.336817
    country_areas["Palestine"]=6208537679.336817
    country_areas["FSM"]=857843883.3652279
    country_areas["Micronesia (Federated States of)"]=857843883.3652279
    country_areas["MCO"]=16978472.15597799
    country_areas["Monaco"]=16978472.15597799
    country_areas["BLZ"]=23032203836.19505
    country_areas["Belize"]=23032203836.19505
    country_areas["BHR"]=669145414.8170683
    country_areas["Bahrain"]=669145414.8170683
    country_areas["ARM"]=29707085156.504025
    country_areas["Armenia"]=29707085156.504025
    country_areas["BNL"]=68304580376.18573
    country_areas["BENELUX"]=68304580376.18573
    country_areas["UKI"]=314555881106.3246
    country_areas["United Kingdom + Ireland"]=314555881106.3246
    country_areas["IBE"]=588369897424.3368
    country_areas["Iberia"]=588369897424.3368
    country_areas["WEE"]=931142136734.0924
    country_areas["Western Europe"]=931142136734.0924
    country_areas["WEA"]=1844319529655.1924
    country_areas["Western Europe (alternative)"]=1844319529655.1924
    country_areas["CEE"]=1012322010858.0117
    country_areas["Central Europe"]=1012322010858.0117
    country_areas["NOE"]=1324023095475.4663
    country_areas["Northern Europe"]=1324023095475.4663
    country_areas["SOE"]=2513318060345.7095
    country_areas["Southern Europe (all)"]=2513318060345.7095
    country_areas["SOY"]=1056456163857.9772
    country_areas["Southern Europe (non-EU)"]=1056456163857.9772
    country_areas["SOZ"]=1456861896509.854
    country_areas["Southern Europe (EU)"]=1456861896509.854
    country_areas["SWN"]=889400498053.6991
    country_areas["South-Western Europe"]=889400498053.6991
    country_areas["SEE"]=1623917562288.8496
    country_areas["South-Eastern Europe (all)"]=1623917562288.8496
    country_areas["SEA"]=1056456163857.9772
    country_areas["South-Eastern Europe (non-EU)"]=1056456163857.9772
    country_areas["SEZ"]=567461398452.9948
    country_areas["South-Eastern Europe (EU)"]=567461398452.9948
    country_areas["EAE"]=17751998770921.242
    country_areas["Eastern Europe"]=17751998770921.242
    country_areas["EEA"]=1287688224535.7583
    country_areas["Eastern Europe (alternative)"]=1287688224535.7583
    country_areas["EER"]=18201967372589.3
    country_areas["Eastern Europe (including Russia)"]=18201967372589.3
    country_areas["E12"]=2275568040915.4844
    country_areas["EU-11+CHE"]=2275568040915.4844
    country_areas["E15"]=3220400395985.2227
    country_areas["EU-15"]=3220400395985.2227
    country_areas["E27"]=4115386248583.687
    country_areas["EU-27"]=4115386248583.687
    country_areas["E28"]=4359565823449.636
    country_areas["EU-27+UK"]=4359565823449.636
    country_areas["EUR"]=23566926462107.133
    country_areas["all Europe"]=23566926462107.133
    country_areas["CSK"]=127461779621.59377
    country_areas["Former Czechoslovakia"]=127461779621.59377
    country_areas["SWL"]=41332402594.12012
    country_areas["Switzerland + Liechtenstein"]=41332402594.12012
    country_areas["BLT"]=173133266456.40247
    country_areas["Baltic countries"]=173133266456.40247
    country_areas["NAC"]=77578101547.92053
    country_areas["North Adriatic Countries"]=77578101547.92053
    country_areas["DSF"]=827279948742.7716
    country_areas["Denmark, Sweden, Finland"]=827279948742.7716
    country_areas["FMA"]=548749014866.83673
    country_areas["France, Monaco, Andorra"]=548749014866.83673
    country_areas["UMB"]=837719622864.343
    country_areas["Ukraine, Rep. of Moldova, Belarus"]=837719622864.343
    country_areas["RUG"]=16983824583927.598
    country_areas["Russia and Georgia"]=16983824583927.598
    country_areas["NAF"]=12239647567319.156
    country_areas["North Africa"]=12239647567319.156
    country_areas["SSA"]=2587322643297.5386
    country_areas["Subsahelian West Africa"]=2587322643297.5386
    country_areas["CNA"]=4673439086093.647
    country_areas["Central Africa"]=4673439086093.647
    country_areas["HAF"]=3592330589112.7456
    country_areas["Horn of Africa"]=3592330589112.7456
    country_areas["SAF"]=4729552048515.692
    country_areas["Southern Africa"]=4729552048515.692
    country_areas["ZAA"]=1848934648290.9885
    country_areas["South Africa and enclaves"]=1848934648290.9885
    country_areas["AFR"]=29671226582580.883
    country_areas["Africa"]=29671226582580.883
    country_areas["NOA"]=20431539323256.02
    country_areas["North America"]=20431539323256.02
    country_areas["SOA"]=17675202274370.383
    country_areas["South America"]=17675202274370.383
    country_areas["AIS"]=48465010513493.76
    country_areas["Asia"]=48465010513493.76
    country_areas["WLD"]=133244135658830.34
    country_areas["World"]=133244135658830.34

    return country_areas
#enddef

# Give a possible name of a country, find out which code corresponds to
# this country, returning a None if the country isn't found 
def find_country_code(country_region_data,cname,lstop=False):

    return_code=None

    for ccode,cr_data in country_region_data.items():

        if cname in cr_data.possible_names:
            return_code=ccode
        #endif

    #endif

    if not return_code and lstop:
        print("Could not find a country code for: ",cname)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    return return_code

#enddef

# When we get a new mask file, I need to create country definitions from
# that match up, with the ISO code and a country name.  I do that above,
# but creating those lines by hand for a couple hundred countries is tedious.
# This routine reads in a .nc file and creates the lines for me, which
# I can then copy above.
def create_country_list_from_file(filename):

    # Open up the file
    srcnc=NetCDFFile(filename,"r")

    # Both country names and country codes are stored as byte strings.
    country_codes_in_file=srcnc["country_code"][:]
    country_codes_in_file = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in country_codes_in_file]
    country_names_in_file = srcnc.variables["country_name"][:]
    country_names_in_file = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in country_names_in_file]

    for ccode,cname in zip(country_codes_in_file,country_names_in_file):
        print("country_names=add_key_to_country_region_names(\"{}\",\"{}\",country_names)".format(ccode,cname))
    #endfor

    srcnc.close()
              
    print("Stopping early.")
    traceback.print_stack(file=sys.stdout)
    sys.exit(1)
#enddef

######################################################
# This calculates all the country areas, based on a mask file.
# It then outputs it in a format that one of the above
# routines can use so that we don't have to calculate them 
# all the time.
# country_areas["Western Europe (alternative)"]=1842534678528.0
def calculate_country_areas():
    #print("Mask files have EEZs!  These values will not be correct.  Need to change.")
    #sys.exit(1)
    path_mask = "/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/all_countries_and_regions_masks_0.1x0.1.nc"
    print("Calculating mask file area.")
    print("File: ",path_mask)

    ncmask = NetCDFFile(path_mask)
    clat = ncmask.variables["latitude"][:]
    clon = ncmask.variables["longitude"][:]
    cmask = ncmask.variables["country_mask"][:]
    cname = ncmask.variables["country_name"][:]
    ccode = ncmask.variables["country_code"][:]
    ncmask.close()

    cgrid = Grid(lat = clat, lon = clon)

    country_region_data=get_country_region_data()
    clons, clats = np.meshgrid(clon, clat)

    if True:

        for icount in range(cmask.shape[0]):
            
            ccode_mask=b"".join([letter for letter in ccode[icount] if letter is not np.ma.masked])
            #print("Making mask without EEZ for {}".format(ccode_mask))
            ccode_mask=ccode_mask.decode('UTF-8')

            # Something for speed, since I generally only add new regions
            if country_region_data[ccode_mask].is_country:
                continue
            #endif

            
            cmaskNoEEZ = maskoceans(clons, clats, cmask[icount], inlands = False, resolution = "f", grid = 1.25).filled(0)
            
            area=np.where(cmaskNoEEZ, cmaskNoEEZ * cgrid.area, 0).sum(axis=(-1,-2))
            
            print('    country_areas["{}"]={}'.format(ccode_mask,area))
            print('    country_areas["{}"]={}'.format(country_region_data[ccode_mask].long_name,area))

            #for name in country_region_data[ccode_mask].possible_names:
            #print(" Area for {} ({}): {} m**2".format(cname_mask[-1],ccode_mask[-1],country_region_areas[-1]))
            #    print('    country_areas["{}"]={}'.format(name,area))
            #endfor
        #endfor 
    #endif

    if False:
        # Also print out all the countries so I can make a global map.  This is
        # used right now so I can compare BLUE against values submitted to the
        # Global Carbon Project
        print("country_list[keyval]=(")
        for icount in range(cmask.shape[0]):
            
            ccode_mask=b"".join([letter for letter in ccode[icount] if letter is not np.ma.masked])
            ccode_mask=ccode_mask.decode('UTF-8')
            if country_region_data[ccode_mask].is_country:
                print('"' +ccode_mask + '",',end='')
            #endif
        #endfor
    #endif
    sys.exit(1)
#endfor

#enddef

#######################################################


# Sometimes I have a list of a mix of names and country codes, and I want
# to return a list of either names or country codes.  This routine does that.
def convert_names_and_codes(list_of_names,flag):

    if flag not in ["names","codes"]:
        print("Do not understand this flag!")
        print(flag)
        traceback.print_stack(file=sys.stdout)
        sys.exit(1)
    #endif

    country_region_data=get_country_region_data()

    output_names=[]

    for item in list_of_names:
        
        if flag == "codes":
            if item in country_region_data.keys():
                # Already a code
                output_names.append(item)
            else:
                # Find the code for this name.
                ccode=find_country_code(country_region_data,item)
                if ccode is None:
                    print('Could not find a code for this name!')
                    print(item)
                    traceback.print_stack(file=sys.stdout)
                    sys.exit(1)
                #endif
                output_names.append(ccode)
            #endif
        else:
            print('Not yet ready for this flag.')
            print(flag)
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

    #endfor

    return output_names

#enddef

# Takes the name of a country file along with a list of countries
# and returns a mask from these countries: an array where the value
# is False everywhere except for these countries, where it is True.
# If lfrac=True, this includes fractional pixels.  If not, only pixels
# only occupied by a single country are selected.
def create_country_logical_mask(filename,country_list,lfrac=True):

    srcnc = NetCDFFile(filename,"r")

    # Find the list of country codes in this file
    ccodes = srcnc.variables["country_code"][:]
    ccodes = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in ccodes]

    nlats=len(srcnc["lat"][:])
    nlons=len(srcnc["lon"][:])
    country_mask=np.zeros((nlats,nlons))*np.nan

    if country_list is None:
         print("--> No country list given.  Returning.")
         # want all the values to be False in this case
         country_mask=np.where(np.isnan(country_mask), False, True)
         srcnc.close()
         return country_mask
    #endif

    # Make sure we are dealing with all codes
    country_list=convert_names_and_codes(country_list,"codes")

    # For each country, put non-NaN values where that country exists
    # on our map.
    for country in country_list:

        # Find the index of the country in this file.
        if country not in ccodes:
            print("You passed a country that does not exist in this file.")
            print("Country code: ",country)
            print("Filename: ",filename)
            print("Stopping early.")
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
        #endif

        cindex=ccodes.index(country)
        print("Masking: ",country,cindex)
        if lfrac:
            country_mask=np.where(srcnc["country_mask"][cindex,:,:] > 0.0, 1.0, country_mask)
        else:
            country_mask=np.where(srcnc["country_mask"][cindex,:,:] >= 1.0, 1.0, country_mask)
        #endif
    #endif

    srcnc.close()

    country_mask=np.where(np.isnan(country_mask), False, True)

    return country_mask

#enddef
