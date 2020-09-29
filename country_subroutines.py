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
import sys
import re
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt



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
        self.possible_names.append(long_name)
        self.possible_names.append(long_name.upper()) 
        self.possible_names.append(long_name.lower())
        self.possible_names.append("'{}'".format(long_name))

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
        else:
            self.possible_names.extend(possible_name)
        #endif
    #enddef

#enddef

def get_country_codes_for_netCDF_file():
    # This is the order of country codes that I used to create
    # the country and regional masks.
    return ["ALA", "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GGY", "GEO", "GRC", "GRL", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "BNL", "CSK", "CHL", "BLT", "NAC", "DSF", "UKI", "IBE", "WEE", "WEA", "CEE", "NOE", "SOE", "SOY", "SOZ", "SWN", "SEE", "SEA", "SEZ", "EAE", "EEA", "EER", "E12", "E15", "E27", "E28", "EUR"]
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
    country_names=add_key_to_country_region_names("RUS","Russian Federation",country_names)
    country_names=add_key_to_country_region_names("SJM","Svalbard and Jan Mayen",country_names)
    country_names=add_key_to_country_region_names("SMR","San Marino",country_names)
    country_names=add_key_to_country_region_names("SRB","Serbia",country_names)
    country_names=add_key_to_country_region_names("SVK","Slovakia",country_names)
    country_names=add_key_to_country_region_names("SVN","Slovenia",country_names)
    country_names=add_key_to_country_region_names("SWE","Sweden",country_names)
    country_names=add_key_to_country_region_names("TUR","Turkey",country_names)
    country_names=add_key_to_country_region_names("UKR","Ukraine",country_names)


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
    country_region_data["BIH"].add_possible_names('BosniaandHerzegovina')
    country_region_data["RUS"].add_possible_names('Russia')

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
    country_region_data["DNK"].add_possible_names('den')

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
    country_region_data["E28"].add_possible_names("'EU-28'")
    country_region_data["E28"].add_possible_names("'European Union (Convention)'")
    country_region_data["E28"].add_possible_names("European Union (Convention)")



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
    region_names=add_key_to_country_region_names("CHL","Switzerland + Liechtenstein",region_names)
    region_names=add_key_to_country_region_names("BLT","Baltic countries",region_names)
    region_names=add_key_to_country_region_names("NAC","North Adriatic Countries",region_names)
    region_names=add_key_to_country_region_names("DSF","Denmark, Sweden, Finland",region_names)
    region_names=add_key_to_country_region_names("FMA","France, Monaco, Andorra",region_names)
    region_names=add_key_to_country_region_names("UMB","Ukraine, Rep. of Moldova, Belarus",region_names)
    region_names=add_key_to_country_region_names("RUG","Russia and Georgia",region_names)


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
            country_list[keyval]=("Aaland Islands","Albania","Andorra","Austria","Belgium","Bulgaria","Bosnia and Herzegovina","Belarus","Switzerland","Cyprus","Czech Republic","Germany","Denmark","Spain","Estonia","Finland","France","Faroe Islands","United Kingdom","Guernsey","Greece","Croatia","Hungary","Isle of Man","Ireland","Iceland","Italy","Jersey","Liechtenstein","Lithuania","Luxembourg","Latvia","Moldova, Republic of","Macedonia, the former Yugoslav","Malta","Montenegro","Netherlands","Norway","Poland","Portugal","Romania","Russian Federation","Svalbard and Jan Mayen","San Marino","Serbia","Slovakia","Slovenia","Sweden","Turkey","Ukraine")
        elif keyval == "WEA":
            country_list[keyval]=('BEL','FRA','NLD','DEU','CHE','GBR','ESP','PRT')
        elif keyval == "CSK":
            country_list[keyval]=('CZE','SVK')
        elif keyval == "CHL":
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
        else:
            print("Should not be be here.  Not a region!")
            print(keyval)
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

        #print("jfioezjef ",cr_code,country_codes_in_file)
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
            cr_data=country_region_data[ccode]
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
                        sys.exit(1)
                    #endif
                #endfor
            #endfor
        #endfor
    #endfor

    # This is also a feature I need often: printing out the current countries
    # and regions in the .nc country mask file.
    country_region_plotting_order=get_country_codes_for_netCDF_file()
    country_region_data=get_country_region_data(country_region_plotting_order,False)
    print_regions_and_countries(country_region_plotting_order,country_region_data,3,False)

#endif

def get_country_areas():

    # This is taken from our map with 79 regions.  Values are in square meters.
    # Note that this likely does not correspond exactly to reported values from
    # other sources, like the CIA World Factbook.  The reason is that our
    # maps are at 0.1 degree resolution, and areas outside our lat/long window
    # are not accounted for.  But it's the correct value for our purposes.
    
    
    country_areas={}
    country_areas["Aaland Islands"]=1578897664.0
    country_areas["Albania"]=28352174080.0
    country_areas["Andorra"]=447315584.0
    country_areas["Austria"]=83591815168.0
    country_areas["Belgium"]=30669848576.0
    country_areas["Bulgaria"]=112254164992.0
    country_areas["Bosnia and Herzegovina"]=50907799552.0
    country_areas["Belarus"]=206009483264.0
    country_areas["Switzerland"]=41593430016.0
    country_areas["Cyprus"]=5524352512.0
    country_areas["Czech Republic"]=78416461824.0
    country_areas["Germany"]=356221026304.0
    country_areas["Denmark"]=44500295680.0
    country_areas["Spain"]=498337873920.0
    country_areas["Estonia"]=45490667520.0
    country_areas["Finland"]=334269054976.0
    country_areas["France"]=547293986816.0
    country_areas["Faroe Islands"]=1354416512.0
    country_areas["United Kingdom"]=245327314944.0
    country_areas["Guernsey"]=125637592.0
    country_areas["Georgia"]=56721285120.0
    country_areas["Greece"]=131507568640.0
    country_areas["Greenland"]=28462256128.0
    country_areas["Croatia"]=56145813504.0
    country_areas["Hungary"]=92676333568.0
    country_areas["Isle of Man"]=718484352.0
    country_areas["Ireland"]=69942263808.0
    country_areas["Iceland"]=101657755648.0
    country_areas["Italy"]=299969642496.0
    country_areas["Jersey"]=126276816.0
    country_areas["Liechtenstein"]=164011744.0
    country_areas["Lithuania"]=64425762816.0
    country_areas["Luxembourg"]=2557641728.0
    country_areas["Latvia"]=64558092288.0
    country_areas["Moldova, Republic of"]=33723500544.0
    country_areas["Macedonia, the former Yugoslav"]=24797104128.0
    country_areas["Malta"]=312614048.0
    country_areas["Montenegro"]=12890724352.0
    country_areas["Netherlands"]=35655667712.0
    country_areas["Norway"]=325791744000.0
    country_areas["Poland"]=311556964352.0
    country_areas["Portugal"]=87435624448.0
    country_areas["Romania"]=236436160512.0
    country_areas["Russian Federation"]=1995897176064.0
    country_areas["Svalbard and Jan Mayen"]=251208448.0
    country_areas["San Marino"]=59646068.0
    country_areas["Serbia"]=88679014400.0
    country_areas["Slovakia"]=48968114176.0
    country_areas["Slovenia"]=19864659968.0
    country_areas["Sweden"]=447214321664.0
    country_areas["Turkey"]=791915069440.0
    country_areas["Ukraine"]=596645642240.0
    country_areas["BENELUX"]=68883161088.0
    country_areas["Former Czechoslovakia"]=127384567808.0
    country_areas["Switzerland + Liechtenstein"]=41757442048.0
    country_areas["Baltic countries"]=174474510336.0
    country_areas["North Adriatic Countries"]=76010471424.0
    country_areas["Denmark, Sweden, Finland"]=825983631360.0
    country_areas["United Kingdom + Ireland"]=315269578752.0
    country_areas["Iberia"]=585773481984.0
    country_areas["Western Europe"]=931446718464.0
    country_areas["Western Europe (alternative)"]=1842534678528.0
    country_areas["Central Europe"]=1013024096256.0
    country_areas["Northern Europe"]=1326249934848.0
    country_areas["Southern Europe (all)"]=2502051495936.0
    country_areas["Southern Europe (non-EU)"]=1054263214080.0
    country_areas["Southern Europe (EU)"]=1447788412928.0
    country_areas["South-Western Europe"]=886055698432.0
    country_areas["South-Eastern Europe (all)"]=1615995863040.0
    country_areas["South-Eastern Europe (non-EU)"]=1054263214080.0
    country_areas["South-Eastern Europe (EU)"]=561732714496.0
    country_areas["Eastern Europe"]=2832275603456.0
    country_areas["Eastern Europe (alternative)"]=1288686665728.0
    country_areas["Eastern Europe (including Russia)"]=3284583317504.0
    country_areas["EU-11+CHE"]=2273153908736.0
    country_areas["EU-15"]=3214493614080.0
    country_areas["EU-27"]=4105796583424.0
    country_areas["EU-27+UK"]=4351123783680.0
    country_areas["all Europe"]=8654811561984.0
    
    return country_areas
#enddef

# Give a possible name of a country, find out which code corresponds to
# this country, returning a None if the country isn't found 
def find_country_code(country_region_data,cname):

    return_code=None

    for ccode,cr_data in country_region_data.items():

        if cname in cr_data.possible_names:
            return_code=ccode
        #endif

    #endif

    return return_code

#enddef
