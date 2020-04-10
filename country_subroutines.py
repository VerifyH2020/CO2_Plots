from netCDF4 import Dataset as NetCDFFile 
import sys
import re
import numpy as np

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
    return ["ALA", "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GGY", "GEO", "GRC", "GRL", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "BNL", "CSK", "CHL", "BLT", "NAC", "DSF", "UKI", "IBE", "WEE", "WEA", "CEE", "NOE", "SWN", "SEE", "SEA", "SEZ", "EAE", "EEA", "EER", "E12", "E15", "E27", "E28", "EUR"]
#enddef



def get_country_region_data(country_region_plotting_order=["NONE"],loutput_codes=True):

    country_region_data={}

    # This gives the full country name as a function of the ISO-3166 code
    country_names={ \
                    "ALA": "Aaland Islands", \
                    "ALB": "Albania", \
                    "AND": "Andorra", \
                    "AUT": "Austria", \
                    "BEL": "Belgium", \
                    "BGR": "Bulgaria", \
                    "BIH": "Bosnia and Herzegovina", \
                    "BLR": "Belarus", \
                    "CHE": "Switzerland", \
                    "CYP": "Cyprus", \
                    "CZE": "Czech Republic", \
                    "DEU": "Germany", \
                    "DNK": "Denmark", \
                    "ESP": "Spain", \
                    "EST": "Estonia", \
                    "FIN": "Finland", \
                    "FRA": "France", \
                    "FRO": "Faroe Islands", \
                    "GBR": "United Kingdom", \
                    "GGY": "Guernsey", \
                    "GEO" : "Georgia", \
                    "GRC": "Greece", \
                    "GRL" : "Greenland", \
                    "HRV": "Croatia", \
                    "HUN": "Hungary", \
                    "IMN": "Isle of Man", \
                    "IRL" : "Ireland", \
                    "ISL" : "Iceland", \
                    "ITA" : "Italy", \
                    "JEY" : "Jersey", \
                    "LIE" : "Liechtenstein", \
                    "LTU" : "Lithuania", \
                    "LUX" : "Luxembourg", \
                    "LVA" : "Latvia", \
                    "MDA" : "Moldova, Republic of", \
                    "MKD" : "Macedonia, the former Yugoslav", \
                    "MLT" : "Malta", \
                    "MNE" : "Montenegro", \
                    "NLD" : "Netherlands", \
                    "NOR" : "Norway", \
                    "POL" : "Poland", \
                    "PRT" : "Portugal", \
                    "ROU" : "Romania", \
                    "RUS" : "Russian Federation", \
                    "SJM" : "Svalbard and Jan Mayen", \
                    "SMR" : "San Marino", \
                    "SRB" : "Serbia", \
                    "SVK" : "Slovakia", \
                    "SVN" : "Slovenia", \
                    "SWE" : "Sweden", \
                    "TUR" : "Turkey", \
                    "UKR" : "Ukraine", \
               }

    for ccode,cname in country_names.items():
        composant_countries=[]
        composant_countries.append(ccode)

        country_region_data[ccode]=countrydata(ccode,cname,composant_countries)
    #endfor

    # A couple extra possiblities
    country_region_data["MDA"].add_possible_names('Moldova, Republic of')
    country_region_data["MKD"].add_possible_names('Macedonia, the former Yugoslav')

    # Now fill out the regional data
    region_names,country_list=get_region_data(country_names,country_region_data)

    for rcode,rname in region_names.items():
        country_region_data[rcode]=countrydata(rcode,region_names[rcode],country_list[rcode])
    #endif

    # And some possible extra region names.  These show up when we read in the name of an old .nc file.
    country_region_data["IBE"].add_possible_names('Spain + Portugal')
    country_region_data["SEE"].add_possible_names('South-Eastern Europe')
    country_region_data["E28"].add_possible_names('EU-28')


    # Now make sure that all the lists of countries which make up
    # the regions and countries are consistently using either long
    # names or ISO codes
    country_region_data=harmonize_country_lists(country_region_data,True)

    # print things out to make sure they look good
    if country_region_plotting_order[0] != "NONE":
        print("Why here?")
        print("fezfe ",country_region_plotting_order[0])
        print_regions_and_countries(country_region_plotting_order,country_region_data,1,loutput_codes)
    #endif

    return country_region_data
#enddef

# This subroutine defines a list of regions and their 3-letter codes
# using a list of countries.  It returns both the region code,
# the region name, and the list of the countries inside.
def get_region_data(country_names,country_region_data):
    region_names={ \
                   # The following ISO codes don't really exist,
                   # and were just cretaed by us for these regions
                   "BNL" : "BENELUX", \
                   "UKI" : "United Kingdom + Ireland", \
                   "IBE" : "Iberia", \
                   "WEE" : "Western Europe", \
                   "WEA" : "Western Europe (alternative)", \
                   "CEE" : "Central Europe", \
                   "NOE" : "Northern Europe", \
                   "SWN" : "South-Western Europe", \
                   "SEE" : "South-Eastern Europe (all)", \
                   "SEA" : "South-Eastern Europe (non-EU)", \
                   "SEZ" : "South-Eastern Europe (EU)", \
                   "EAE" : "Eastern Europe", \
                   "EEA" : "Eastern Europe (alternative)", \
                   "EER" : "Eastern Europe (including Russia)", \
 #                  "EAZ" : "Eastern Europe (UNFCCC submissions)", \
                   "E12" : "EU-11+CHE", \
                   "E15" : "EU-15", \
                   "E27" : "EU-27", \
                   "E28" : "EU-27+UK", \
                   "EUR" : "all Europe", \
                   "CSK" : "Former Czechoslovakia", \
                   "CHL" : "Switzerland + Liechtenstein", \
                   "BLT" : "Baltic countries", \
                   "NAC" : "North Adriatic Countries", \
                   "DSF" : "Denmark, Sweden, Finland", \
                   "FMA" : "France, Monaco, Andorra", \
                   "UMB" : "Ukraine, Rep. of Moldova, Belarus", \
                   "RUG" : "Russia and Georgia", \
                   }
    
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
        elif keyval == "SEE":
            country_list[keyval]=("Albania","Bulgaria","Bosnia and Herzegovina","Cyprus","Georgia","Greece","Croatia","Moldova, Republic of","Macedonia, the former Yugoslav","Montenegro","Romania","Serbia", "Slovenia", "Turkey")
        elif keyval == "SEZ":
            country_list[keyval]=("Bulgaria","Cyprus","Greece","Croatia","Romania","Slovenia")
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
            country_list[keyval]=("Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden")
        elif keyval == "E28":
            country_list[keyval]=("Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom")
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
        elif keyval == "SEA":
            country_list[keyval]=('Albania', 'Bosnia and Herzegovina', 'Macedonia, the former Yugoslav', 'Montenegro', 'Serbia')
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

    return region_names,country_list
#enddef



# For a given NetCDF file, look for variables with the names
# country_codes and country_names and check to see which of the 
# countries and regions in the passed dictionary are present in the
# file, returning a dictionary with keys of all the country/region
# names
def find_countries_and_regions_in_file(filename,country_region_data):

    print("Looking for the countries and regions in file: ",filename)

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
    for cr_code,cr_data in country_region_data.items():
        if cr_data.is_country:
            if cr_data.file_index == cr_data.uninit_int:
                print("WARNING: Did not find {} ({}) in the .nc country mask file.".format(cr_data.long_name,cr_code))
            else:
                if not cr_data.long_name_in_file:
                    print("WARNING: Did not find a long name in the .nc country mask file for {} ({}).".format(cr_data.long_name,cr_code))

                #endif
            #endif
        #endif
    #endfor


    return country_region_data

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

    else:
        print("I do not know this print code: ",print_code)
    #endif

    

#enddef