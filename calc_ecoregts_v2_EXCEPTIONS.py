#!/usr/bin/env python
import numpy as np, netCDF4, os
from mpl_toolkits.basemap import maskoceans
from grid import Grid
import sys,traceback
from string import Template
import math

######
# python calc_ecoregts_v2_EXCEPTIONS.py
######

# The purpose of this script is to look at all CountryTot files for a given
# 2D.nc filename created by the script calc_ecoregts_v2.py and make
# some modifications.

#############################################
class exception_class:
    def __init__(self,filename,varname,region_code,data,input_units):
        self.filename=filename
        self.varname=varname
        self.region_code=region_code
        self.data=data
        self.input_units=input_units
        self.current_units=input_units

    #endif

    # Change the current units of the data to the target units
    def convert_units(self,target_units):
       if self.current_units == "kg C yr-1" and target_units == "kg C yr-1 [country]":
          print("Nothing to be done.  Just changing the name.")
          self.current_units=target_units


       elif self.current_units == "kilotonnes CO2 yr-1" and target_units in ["kg C yr-1 [country]","kg C yr-1"]:
          self.data=list(np.asarray(self.data)*1e6*12.01/44.01)
          self.current_units=target_units
       else:
          print("Not sure what you want to do here.")
          print("self.current_units : ",self.current_units)
          print("target_units : ",target_units)
          traceback.print_stack(file=sys.stdout)
          sys.exit(1)
       #endif
    #endif

#endif



if __name__ == "__main__":

   ##########################################
   # These are some special cases, where the value is not equal to
   # some combination of the individual countries.  For the moment,
   # this primarily happens with the EU-27+UK, which reports emissions
   # to the UNFCCC as a group that are not included in any member state.
   # In order to deal with this, we look to see if this ISO code appears
   # in the countries/regions in the file and, if so, after the standard
   # processing is done, we change that line by some stored values.
   exceptions=[]

   # Real database?  Or test database?
   #database_dir="/home/surface8/mmcgrath/TEST_VERIFY_DATABASE/"
   database_dir="/home/dods/verify/"

   # Notice that the 'European Union (Convention)' for this year no longer
   # includes the UK.  So I add columns Q and V from 
   # UNFCCC2020_CO2_tot_and_sectors tot.xlsx.  This is a bit painful, since
   # you need to copy all this by hand from the files.  But it works.
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_LULUCF_TOT", \
                                     "E28", \
                                     [-279633.905028853,-306285.696539733,-275438.267918909,-277261.285385202,-289395.240847146,-311398.762960047,-339603.544946111,-337525.218724208,-353645.480658934,-360672.598815766,-343357.008613091,-359787.977643323,-343980.169510471,-324981.557062423,-354239.344694089,-350991.658974328,-373726.528841054,-340191.144520804,-369716.261123316,-369281.597396602,-366304.180186565,-361818.960485242,-364902.108982996,-364983.66175558,-343724.881563131,-335168.171187501,-329463.745589411,-296855.934782122,-305581.439616679], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_FL_REMAIN", \
                                     "E28", \
                                     [-373972.290334766,-407353.942653224,-379442.402593588,-379305.520951113,-378540.490497505,-390688.673370366,-414323.427162168,-407762.927365303,-419282.921015402,-423879.736757985,-395557.454516992,-410294.37549498,-381383.399943973,-357914.685069328,-376675.338081106,-371411.380539881,-385956.090756678,-356531.872113659,-404912.765978904,-415233.77463796,-397020.45138854,-398805.234136562,-409840.048673185,-414915.002573125,-390365.805666173,-375165.775062643,-373449.233903425,-344388.469951418,-350164.067271231], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_FL_CONVERT", \
                                     "E28", \
                                     [-40243.4742260039,-39492.5291100565,-40979.7856893007,-40877.9213943087,-41728.9061311557,-42635.5593613481,-44872.1471396199,-45112.3975746523,-46101.3071171609,-48021.3952218042,-47602.7563329846,-50087.0726311271,-56832.3552505203,-56941.5780752406,-60203.9826579652,-59676.1455803291,-61271.9949498823,-60765.8735247348,-61207.3199197365,-61714.8654126635,-60974.9778559334,-57270.1112665565,-55161.2940931374,-54538.8538915175,-53631.8108798814,-51334.907792326,-49535.2892683728,-43753.7408818137,-41386.6501773516], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_CL_REMAIN", \
                                     "E28", \
                                     [28555.2998562179,25551.8843138186,27843.8132802782,25668.1019426279,25117.6559863721,26039.4318253742,27289.5419975859,26784.5950403043,26048.967145927,25923.9391461007,26074.6660411651,22288.4580669127,23036.9881885449,22669.7326534346,21500.7888772769,19702.191385751,18110.9491257963,19186.2555512948,20264.9335523914,19075.5032166677,18010.8782435301,19589.9260300447,22361.3563161669,25067.2922637476,25288.3877177208,19207.1421941214,18737.7497477172,18577.8304273733,20486.824504086], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_CL_CONVERT", \
                                     "E28", \
                                     [57662.5066897402,57627.6208852392,57452.4776579298,57412.2187619084,57337.4039613689,56828.3034621172,56829.3406160014,56416.1702949142,56871.2688086177,57117.0847433705,54600.6500594322,54533.3819190831,53616.8454850355,52742.1848846338,51912.3923297095,51837.1458710086,51718.2652543499,51376.3683612647,52235.9519291014,51329.6120775182,51067.502621658,50683.9274409058,50375.7870486503,50382.6838477064,48426.3573003405,48161.899228721,47528.8453065359,47800.3082157987,47329.6223811745], \
                                     "kilotonnes CO2 yr-1"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_GL_REMAIN", \
                                     "E28", \
                                     [40927.1756080396,37163.5504511495,36507.3797902221,39091.0066809798,36225.9012311486,32591.5192526054,32011.6769906677,33823.1423770672,35061.6465042211,33118.6110712288,34692.80602841,32399.1709837479,30690.6766083907,31162.7024124087,28734.044815467,27467.5927433535,24604.3410199567,30333.1472321382,24340.275764893,24362.5909367372,22109.2786843201,23087.6599621061,25530.8126028739,20023.7758145372,19850.4544117119,19391.0123204875,19472.8068840197,21883.1338620739,18499.4379632525], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_GL_CONVERT", \
                                     "E28", \
                                     [-27220.9696902104,-27797.5518564794,-28444.5607135115,-28877.5346274325,-28779.5920336333,-30658.0526248513,-31029.7754493095,-30939.6929949583,-32877.3447362163,-31159.189033727,-31274.5715042626,-32083.6131799188,-32251.0531630232,-31681.3063090254,-30867.0212146036,-31421.4899704978,-29498.3856250884,-28863.6913194039,-29218.121255032,-29914.8192588985,-31765.1958702407,-32775.5776514146,-32567.6299638222,-31675.1508679733,-31409.1991195127,-32111.8696950011,-31134.8146225658,-30522.5030767166,-30817.4249211979], \
                                     "kilotonnes CO2 yr-1"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_WL_REMAIN", \
                                     "E28", \
                                     [9827.12685395999,9741.10542294393,10434.6673631085,9735.91563085662,11246.7673155245,10906.2889809788,10669.2550337747,10385.5449836176,9021.56163563544,10603.2507834206,9971.04815812397,10850.136453126,10750.0530882201,11546.7611623604,10909.9729570544,12177.8626794902,11922.7672717817,10563.9523445496,10136.5877599536,10268.1718362224,11112.7582393678,10714.2139487355,9991.84959627712,10997.6745717649,11073.4093189094,10685.9416007224,10730.3364392433,11595.0045860647,11279.4781670486], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_WL_CONVERT", \
                                     "E28", \
                                     [2431.63816679158,2310.86015218674,2279.09619365818,2369.61283971597,2356.28812349818,2269.87161441656,2451.99162582569,2514.31534498078,2483.3280327577,2816.18341107697,2639.02405716544,3051.25784621162,3284.88147539048,3546.11570107142,4073.50451448333,4162.66525853971,4434.81759641585,5083.75551468299,4332.32160126437,5025.26941497305,4839.65609706392,5208.46441818764,4927.07762761252,5141.04070510778,4701.30514447021,5761.79357327721,4994.79461096696,4935.61285056078,4139.4346772813], \
                                     "kilotonnes CO2 yr-1"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_SL_REMAIN", \
                                     "E28", \
                                     [5678.37790896762,5753.1238085804,5795.12436717869,5798.48649626125,5854.19302709549,5933.39318886815,6001.95965233062,6013.19193945044,6073.03490283876,6087.84677278197,6166.38994926529,6218.8929435364,6265.06771574417,6318.34168017602,6345.74845563835,6418.888547191,6492.81245742594,6461.38030822777,6446.07089655912,6532.86947346192,6555.57416810785,6579.12814847613,5920.96214491307,6146.25172068019,6130.09807082113,6066.2558996343,6150.48209230181,6619.21206016103,6744.43971237283], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_SL_CONVERT", \
                                     "E28", \
                                     [39777.1731965741,41538.0151171023,40334.2155622433,44261.110367165,41422.4484183009,42196.0701488515,39522.1226582129,40681.7981071981,40631.7271324708,41914.3847143961,40888.8418602979,40804.2120523821,41227.6971968334,42187.7359565411,44183.8975427513,44740.3948282449,46201.8083224152,48151.1906175647,49657.9215959342,47180.5056503508,46291.3723626366,45383.1888689331,45551.0229755919,45128.9127212525,46625.3394768865,46413.448428813,51935.5353436701,47164.0445054547,47289.7548200606], \
                                     "kilotonnes CO2 yr-1"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_OL_REMAIN", \
                                     "E28", \
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
                                     "kilotonnes CO2 yr-1"))
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_OL_CONVERT", \
                                     "E28", \
                                     [3150.32801814646,2515.07223042227,2256.71308034502,1948.17833926453,1784.58668597481,413.224549796839,362.515933862624,329.642968699001,293.141053637691,277.539389304998,216.942462474225,161.777673750844,-8.80787225263965,-78.8953434503982,-163.308592794768,-156.220120196777,1063.9126334948,-726.950500497443,-769.465037551567,-561.143469598617,-460.463179184794,-283.454047448851,30.1480281844258,214.230395330649,484.482494682672,533.067087349322,443.359241552088,437.113353359269,343.617668252678], \
                                     "kilotonnes CO2 yr-1"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_HWP", \
                                     "E28", \
                                     [-33558.8622734551,-21296.2907256416,-15740.075269779,-20712.1471759995,-28791.2072628595,-31892.8486117665,-31492.0039887489,-37701.5278006039,-38514.9520148547,-42472.4874910178,-50784.3272243126,-44188.6413463027,-49126.450372142,-54992.2842460842,-60455.2965281714,-61435.7162213793,-68255.8129879175,-70697.6965952756,-47574.4962542635,-32347.66344179,-42533.2677814302,-40742.9788353006,-37842.0335600214,-34050.5765756942,-37519.4952453697,-39793.8792807668,-42298.5963082142,-44334.6379924047,-46950.2738138095], \
                                     "kilotonnes CO2 yr-1"))
   #####

   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_LULUCF_TOT_ERR", \
                                     "E28", \
                                     [11.0], \
                                     "%"))

   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_FL_REMAIN", \
                                     "E28", \
                                     [-359627.416212103,-392330.732715816,-363787.388867783,-363187.023342178,-362209.525530459,-374172.945860898,-397346.880726493,-390729.857175342,-401869.770098594,-406374.511723692,-377820.019086618,-392269.521631569,-363136.574159579,-339561.367786379,-358359.936921458,-352873.430181773,-367158.411985832,-337676.865535159,-385428.287621872,-395705.109989452,-377465.968021749,-379472.957046316,-391732.15649511,-396537.291624281,-372219.424843573,-357060.471689991,-355201.130809298,-326177.346521901,-332043.945910504], \
                                     "kilotonnes CO2 yr-1"))

   ### MISTAKE!  Should be LULUCF, not FL-FL.  I used this line to change
   # it back, but now I can comment it out.
   #exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_$filetype.nc"), \
   #                                  "FCO2_NBP_ERR", \
   #                                  "FRA", \
   #                                  [21.0], \
   #                                  "%/100"))
   ######

   # This is a mistake Roxana caught in 2021.  Only France had this issue.
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_NBP_ERR", \
                                     "FRA", \
                                     [38.11], \
                                     "%/100"))

   ## All of these uncertainties were calculated by Roxana, using the combined
   # values of EU-27 and UK since they are no longer reported together.  No
   # values are given for Remain and Convert seperately, so I use the same
   # value for both.
   #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_FL_REMAIN_ERR", \
                                     "E28", \
                                     [12.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_FL_CONVERT_ERR", \
                                     "E28", \
                                     [12.0], \
                                     "%"))
 #
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_CL_REMAIN_ERR", \
                                     "E28", \
                                     [33.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_CL_CONVERT_ERR", \
                                     "E28", \
                                     [33.0], \
                                     "%"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_GL_REMAIN_ERR", \
                                     "E28", \
                                     [155.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_GL_CONVERT_ERR", \
                                     "E28", \
                                     [155.0], \
                                     "%"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_WL_REMAIN_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_WL_CONVERT_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_SL_REMAIN_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_SL_CONVERT_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_OL_REMAIN_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_OL_CONVERT_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
#
   exceptions.append(exception_class(Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V2_20210629_PETRESCU_WP1_$filetype.nc"), \
                                     "FCO2_HWP_ERR", \
                                     "E28", \
                                     [40.0], \
                                     "%"))

   ######## UNFCCC, 2021
   # Only keep the most recent V3 file, 24Jan2022.
   # Notice that the 'European Union (Convention)' for this year no longer
   # includes the UK.  So I add columns Q and V from 
   # UNFCCC2021_CO2_tot_and_sectors_tot_correct.xlsx.  This is a bit painful, 
   # since you need to copy all this by hand from the files.  But it works.
   # Notice that European Union (Convention) is now EU-27, so that needs
   # to be replaced as well.
   unfccc2021_filename=Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V3_20211105_PETRESCU_WP1_$filetype.nc")

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT", \
                                     "E28", \
                                     [-213118.739591913,-297138.490024696,-274216.914626276,-278226.563637122,-278757.196344373,-307656.118533192,-329811.858491741,-326732.309523714,-343861.19246281,-352443.232282965,-319994.648853845,-345645.547834855,-331968.031604624,-307955.909773712,-337049.875864187,-330547.8941221,-348724.359080325,-301962.304548321,-343085.475870359,-351261.764999127,-338270.426337117,-336753.651066252,-344452.205360963,-345306.592572286,-326845.750357444,-322465.019713919,-321940.282386727,-285187.254646291,-286799.619925239,-273583.344026605], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT_ERR", \
                                     "E28", \
                                     [24.59], \
                                     "%"))
   #
   
   # And now for all the sectors.

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN", \
                                     "E28", \
                                     [-334390.597988565, -421607.812860605, -400636.278572084, -400071.271169911, -389365.447304017, -409719.198170667, -427223.895677682, -419538.668150031, -432250.379840829, -436356.551261901, -393789.017099319, -419287.775124893, -398052.632802012, -372202.372261595, -389669.007463559, -381074.265468842, -389824.719611824, -348746.884289335, -403128.876020475, -423381.691322826, -394704.022662296, -395754.165495035, -407373.867116746, -411175.709218406, -391112.466600924, -381303.555837057, -383895.279367916, -351231.542523156, -347506.383796689, -332759.602106029], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT", \
                                     "E28", \
                                     [-39456.5182838354, -40754.3830599652, -42253.3966649357, -42382.1947072716, -43133.0100495957, -43074.7897209732, -45174.9107969863, -45442.403363616, -46161.9510724534, -48458.5437626914, -48152.8417510554, -50943.5273133531, -51308.6553881124, -49114.7357394702, -52189.2587083284, -51703.8985155264, -54216.2603525259, -52959.3737265884, -57290.7559342019, -56746.7735898079, -56025.7484958141, -54036.3400036149, -50940.7933552432, -51134.6429137075, -48949.8416907826, -46994.7173483444, -44660.0970100662, -38706.0843687102, -40016.7799733144, -39356.6567325569], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN", \
                                     "E28", \
                                     [38840.5338154669, 35821.8591899609, 37016.6373858597, 34733.6181839444, 34332.5083562424, 35459.5723608046, 36665.6360546042, 36208.6388754333, 35678.0594302939, 35510.5437451216, 35649.6730436408, 31699.6848707677, 32458.3962810996, 32186.7545494521, 30965.9780906335, 28912.5186096338, 27260.7605057722, 29936.9923112587, 29466.6991191648, 28314.9453872202, 26946.488751325, 28289.9928769867, 29749.0388754984, 31485.8581014078, 31478.0433919048, 23784.5977364377, 22513.3916557888, 21633.58578792, 22950.9908812819, 22623.302975503], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT", \
                                     "E28", \
                                     [60116.1493485648, 59399.2533025179, 58927.003929212, 58542.4237519617, 58144.0531832826, 57305.9959208191, 57002.6609893636, 56294.0309430021, 56467.3386826353, 56421.1790217526, 54245.8711628416, 54046.6076358601, 53011.5960547639, 52065.1472070351, 51197.4978057654, 51031.5793075249, 50843.0445618987, 50397.525568687, 51064.0371412164, 49951.7837999126, 49639.9628409372, 49397.7846883753, 41450.622649725, 41709.6882134421, 44026.9226622408, 44084.9616505803, 45131.1605512441, 45822.580990524, 45287.2507779032, 40952.3095762808
], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN", \
                                     "E28", \
                                     [55980.8196713685, 52228.147896513, 51516.7120629018, 54060.3258415532, 51148.6563901527, 47492.2796376499, 46912.4212709147, 48682.8594438269, 49922.9709816981, 47991.814039535, 49539.3922114412, 47235.8705762063, 45560.7710238747, 45955.9321446253, 43479.5870510598, 42260.3617041955, 39642.35517867, 45914.9662503441, 39923.5142652449, 39311.327404742, 37009.341330475, 38027.8448997301, 40358.0956447841, 34718.4101268296, 34236.5506238707, 33784.4651393703, 33733.8664997472, 36469.6137075907, 31718.5212485065, 31421.3253163176], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT", \
                                     "E28", \
                                     [-27280.8259175752, -27782.2917937272, -28427.9806065593, -28849.6510428287, -28717.7644709005, -30564.0482536108, -30706.4302529045, -30516.3535639889, -31576.2391101991, -30465.5330476566, -30753.2409238408, -31571.2927943744, -31732.3972924555, -31189.3636310264, -30343.8979194363, -30887.1442922062, -28847.1214011815, -28327.9224808567, -28749.4483268188, -30023.863880208, -31562.072273636, -32474.4443342198, -29363.3820840831, -28803.1825565932, -30629.1265520029, -31706.4930907927, -31418.4655322745, -30480.7771709342, -30449.1303620985, -29503.0103423378], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN", \
                                     "E28", \
                                     [9339.02337652665, 9038.96364303957, 10240.5329537503, 9474.97245157917, 11061.6463229036, 10911.9149776361, 10435.9531566989, 10344.4343218108, 9226.67951266908, 10971.7013960331, 10100.9731011962, 11623.929655228, 10907.2341927338, 11715.2642628024, 10648.7873284384, 11689.7317140425, 11342.7684162296, 9790.97302018687, 9996.28448445446, 10031.3307104274, 11008.2731872573, 10369.2070027948, 9676.39860371521, 11187.882690677, 11301.1987392557, 11075.2658869463, 10522.5336944017, 11629.5311305262, 11379.8398603183, 10949.1999678463], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT", \
                                     "E28", \
                                     [2295.02377856749, 2270.83962148009, 2172.35817263493, 2189.18972773431, 2206.54247515985, 2279.87999549271, 2403.23555902112, 2409.7037149286, 2284.3236255121, 2637.60831764973, 2645.90638906417, 3131.00692356606, 3419.55062911607, 4027.56464520257, 4363.44111346423, 4667.29504511698, 4840.04832947418, 5543.95845658975, 4891.71367624115, 5272.60853466611, 5480.0909632452, 5753.18536645454, 4117.69029120152, 4171.30531477277, 4697.31854833015, 7433.74590493175, 5023.71076769904, 4925.27746818557, 5575.55698398135, 6269.72583915181], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN", \
                                     "E28", \
                                     [4876.12291557097, 4938.58421009418, 4977.14200492742, 4962.90728972737, 5010.93216171192, 5080.02317982402, 5138.39283171565, 5140.35984345439, 5183.45983318161, 5191.83707474059, 5253.06935006921, 5280.57474530437, 5302.94941441428, 5335.46668668853, 5339.00342019956, 5352.21256171374, 5422.49256117123, 5393.83818243471, 5406.17051945351, 5457.92414305404, 5495.70993786775, 5527.81660991446, 4873.56289008561, 5079.34328768476, 5062.1000587792, 4948.14402085511, 5032.96873786462, 5509.01353437214, 5641.42754222483, 5433.75126804112], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT", \
                                     "E28", \
                                     [39312.6785126886, 40818.8019356779, 39721.1111509142, 41790.094782216, 40389.0570110756, 41148.9467455827, 38692.086121838, 39965.2341709962, 39764.4670386647, 40600.0451158988, 39645.3116433369, 41084.1488188752, 41324.1262610419, 42186.505321456, 43951.8121045605, 44287.4077107655, 45003.0743521548, 46413.7378654339, 47729.5671480074, 46781.8630586619, 44198.9076634643, 43265.1104433735, 45621.8062514598, 45413.871794814, 45107.3679256708, 45318.0804591292, 50482.0032556626, 45062.7196584388, 45233.6448727303, 45365.825811072], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN", \
                                     "E28", \
                                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT", \
                                     "E28", \
                                     [3118.51291678378, 2485.81829463971, 2230.98801872326, 1917.95560297776, 1756.7126754003, 380.301417962189, 327.367524149966, 292.660301431952, 254.542506304011, 239.931179628206, 182.395474123264, 129.090370114401, -51.7849437967745, -120.588905254184, -194.938925329175, -187.5737010454, 1285.34166497361, -506.210721043642, -519.379556732121, -343.34380731111, -263.286552390283, -245.538083302916, -150.02099990519, 41.036116488242, 539.094130263657, 572.100281508246, 498.727809738274, 401.858100093989, 316.650832419424, 486.350216954119], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP", \
                                     "E28", \
                                     [-33355.1821289926, -21581.8461721742, -16097.7490435376, -20952.2031374696, -28818.9302189617, -31782.2803332924, -31385.7852859765, -37740.9053639848, -39425.1842349592, -43851.6721625463, -51294.1336588187, -44750.2839189165, -49673.9727261307, -55371.2930722648, -61180.2324274684, -61616.1457134236, -68294.8381531843, -71160.9987497738, -48532.6141615665, -32707.2372721361, -42054.9012657365, -41822.5881670802, -39037.06494522, -35183.9343766067, -39306.6695917683, -40547.2370512881, -41849.1268000066, -43366.8650815214, -44937.7399220898, -42634.654266173], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP_ERR", \
                                     "E28", \
                                     [40.0], \
                                     "%"))

   ## And an updated version in January
   unfccc2021_filename=Template(database_dir + "OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCFsectors_Inventory-SX_UNFCCC_LAND_EU_1M_V3_20220117_PETRESCU_WP1_$filetype.nc")

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT", \
                                     "E28", \
                                     [-213118.739591913,-297138.490024696,-274216.914626276,-278226.563637122,-278757.196344373,-307656.118533192,-329811.858491741,-326732.309523714,-343861.19246281,-352443.232282965,-319994.648853845,-345645.547834855,-331968.031604624,-307955.909773712,-337049.875864187,-330547.8941221,-348724.359080325,-301962.304548321,-343085.475870359,-351261.764999127,-338270.426337117,-336753.651066252,-344452.205360963,-345306.592572286,-326845.750357444,-322465.019713919,-321940.282386727,-285187.254646291,-286799.619925239,-273583.344026605], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT_ERR", \
                                     "E28", \
                                     [24.59], \
                                     "%"))
   #
   
   # And now for all the sectors.

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN", \
                                     "E28", \
                                     [-334390.597988565, -421607.812860605, -400636.278572084, -400071.271169911, -389365.447304017, -409719.198170667, -427223.895677682, -419538.668150031, -432250.379840829, -436356.551261901, -393789.017099319, -419287.775124893, -398052.632802012, -372202.372261595, -389669.007463559, -381074.265468842, -389824.719611824, -348746.884289335, -403128.876020475, -423381.691322826, -394704.022662296, -395754.165495035, -407373.867116746, -411175.709218406, -391112.466600924, -381303.555837057, -383895.279367916, -351231.542523156, -347506.383796689, -332759.602106029], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT", \
                                     "E28", \
                                     [-39456.5182838354, -40754.3830599652, -42253.3966649357, -42382.1947072716, -43133.0100495957, -43074.7897209732, -45174.9107969863, -45442.403363616, -46161.9510724534, -48458.5437626914, -48152.8417510554, -50943.5273133531, -51308.6553881124, -49114.7357394702, -52189.2587083284, -51703.8985155264, -54216.2603525259, -52959.3737265884, -57290.7559342019, -56746.7735898079, -56025.7484958141, -54036.3400036149, -50940.7933552432, -51134.6429137075, -48949.8416907826, -46994.7173483444, -44660.0970100662, -38706.0843687102, -40016.7799733144, -39356.6567325569], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN", \
                                     "E28", \
                                     [38840.5338154669, 35821.8591899609, 37016.6373858597, 34733.6181839444, 34332.5083562424, 35459.5723608046, 36665.6360546042, 36208.6388754333, 35678.0594302939, 35510.5437451216, 35649.6730436408, 31699.6848707677, 32458.3962810996, 32186.7545494521, 30965.9780906335, 28912.5186096338, 27260.7605057722, 29936.9923112587, 29466.6991191648, 28314.9453872202, 26946.488751325, 28289.9928769867, 29749.0388754984, 31485.8581014078, 31478.0433919048, 23784.5977364377, 22513.3916557888, 21633.58578792, 22950.9908812819, 22623.302975503], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT", \
                                     "E28", \
                                     [60116.1493485648, 59399.2533025179, 58927.003929212, 58542.4237519617, 58144.0531832826, 57305.9959208191, 57002.6609893636, 56294.0309430021, 56467.3386826353, 56421.1790217526, 54245.8711628416, 54046.6076358601, 53011.5960547639, 52065.1472070351, 51197.4978057654, 51031.5793075249, 50843.0445618987, 50397.525568687, 51064.0371412164, 49951.7837999126, 49639.9628409372, 49397.7846883753, 41450.622649725, 41709.6882134421, 44026.9226622408, 44084.9616505803, 45131.1605512441, 45822.580990524, 45287.2507779032, 40952.3095762808
], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN", \
                                     "E28", \
                                     [55980.8196713685, 52228.147896513, 51516.7120629018, 54060.3258415532, 51148.6563901527, 47492.2796376499, 46912.4212709147, 48682.8594438269, 49922.9709816981, 47991.814039535, 49539.3922114412, 47235.8705762063, 45560.7710238747, 45955.9321446253, 43479.5870510598, 42260.3617041955, 39642.35517867, 45914.9662503441, 39923.5142652449, 39311.327404742, 37009.341330475, 38027.8448997301, 40358.0956447841, 34718.4101268296, 34236.5506238707, 33784.4651393703, 33733.8664997472, 36469.6137075907, 31718.5212485065, 31421.3253163176], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT", \
                                     "E28", \
                                     [-27280.8259175752, -27782.2917937272, -28427.9806065593, -28849.6510428287, -28717.7644709005, -30564.0482536108, -30706.4302529045, -30516.3535639889, -31576.2391101991, -30465.5330476566, -30753.2409238408, -31571.2927943744, -31732.3972924555, -31189.3636310264, -30343.8979194363, -30887.1442922062, -28847.1214011815, -28327.9224808567, -28749.4483268188, -30023.863880208, -31562.072273636, -32474.4443342198, -29363.3820840831, -28803.1825565932, -30629.1265520029, -31706.4930907927, -31418.4655322745, -30480.7771709342, -30449.1303620985, -29503.0103423378], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN", \
                                     "E28", \
                                     [9339.02337652665, 9038.96364303957, 10240.5329537503, 9474.97245157917, 11061.6463229036, 10911.9149776361, 10435.9531566989, 10344.4343218108, 9226.67951266908, 10971.7013960331, 10100.9731011962, 11623.929655228, 10907.2341927338, 11715.2642628024, 10648.7873284384, 11689.7317140425, 11342.7684162296, 9790.97302018687, 9996.28448445446, 10031.3307104274, 11008.2731872573, 10369.2070027948, 9676.39860371521, 11187.882690677, 11301.1987392557, 11075.2658869463, 10522.5336944017, 11629.5311305262, 11379.8398603183, 10949.1999678463], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT", \
                                     "E28", \
                                     [2295.02377856749, 2270.83962148009, 2172.35817263493, 2189.18972773431, 2206.54247515985, 2279.87999549271, 2403.23555902112, 2409.7037149286, 2284.3236255121, 2637.60831764973, 2645.90638906417, 3131.00692356606, 3419.55062911607, 4027.56464520257, 4363.44111346423, 4667.29504511698, 4840.04832947418, 5543.95845658975, 4891.71367624115, 5272.60853466611, 5480.0909632452, 5753.18536645454, 4117.69029120152, 4171.30531477277, 4697.31854833015, 7433.74590493175, 5023.71076769904, 4925.27746818557, 5575.55698398135, 6269.72583915181], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN", \
                                     "E28", \
                                     [4876.12291557097, 4938.58421009418, 4977.14200492742, 4962.90728972737, 5010.93216171192, 5080.02317982402, 5138.39283171565, 5140.35984345439, 5183.45983318161, 5191.83707474059, 5253.06935006921, 5280.57474530437, 5302.94941441428, 5335.46668668853, 5339.00342019956, 5352.21256171374, 5422.49256117123, 5393.83818243471, 5406.17051945351, 5457.92414305404, 5495.70993786775, 5527.81660991446, 4873.56289008561, 5079.34328768476, 5062.1000587792, 4948.14402085511, 5032.96873786462, 5509.01353437214, 5641.42754222483, 5433.75126804112], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT", \
                                     "E28", \
                                     [39312.6785126886, 40818.8019356779, 39721.1111509142, 41790.094782216, 40389.0570110756, 41148.9467455827, 38692.086121838, 39965.2341709962, 39764.4670386647, 40600.0451158988, 39645.3116433369, 41084.1488188752, 41324.1262610419, 42186.505321456, 43951.8121045605, 44287.4077107655, 45003.0743521548, 46413.7378654339, 47729.5671480074, 46781.8630586619, 44198.9076634643, 43265.1104433735, 45621.8062514598, 45413.871794814, 45107.3679256708, 45318.0804591292, 50482.0032556626, 45062.7196584388, 45233.6448727303, 45365.825811072], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN", \
                                     "E28", \
                                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT", \
                                     "E28", \
                                     [3118.51291678378, 2485.81829463971, 2230.98801872326, 1917.95560297776, 1756.7126754003, 380.301417962189, 327.367524149966, 292.660301431952, 254.542506304011, 239.931179628206, 182.395474123264, 129.090370114401, -51.7849437967745, -120.588905254184, -194.938925329175, -187.5737010454, 1285.34166497361, -506.210721043642, -519.379556732121, -343.34380731111, -263.286552390283, -245.538083302916, -150.02099990519, 41.036116488242, 539.094130263657, 572.100281508246, 498.727809738274, 401.858100093989, 316.650832419424, 486.350216954119], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP", \
                                     "E28", \
                                     [-33355.1821289926, -21581.8461721742, -16097.7490435376, -20952.2031374696, -28818.9302189617, -31782.2803332924, -31385.7852859765, -37740.9053639848, -39425.1842349592, -43851.6721625463, -51294.1336588187, -44750.2839189165, -49673.9727261307, -55371.2930722648, -61180.2324274684, -61616.1457134236, -68294.8381531843, -71160.9987497738, -48532.6141615665, -32707.2372721361, -42054.9012657365, -41822.5881670802, -39037.06494522, -35183.9343766067, -39306.6695917683, -40547.2370512881, -41849.1268000066, -43366.8650815214, -44937.7399220898, -42634.654266173], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP_ERR", \
                                     "E28", \
                                     [40.0], \
                                     "%"))

exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT", \
                                     "E28", \
                                     [-213118.739591913,-297138.490024696,-274216.914626276,-278226.563637122,-278757.196344373,-307656.118533192,-329811.858491741,-326732.309523714,-343861.19246281,-352443.232282965,-319994.648853845,-345645.547834855,-331968.031604624,-307955.909773712,-337049.875864187,-330547.8941221,-348724.359080325,-301962.304548321,-343085.475870359,-351261.764999127,-338270.426337117,-336753.651066252,-344452.205360963,-345306.592572286,-326845.750357444,-322465.019713919,-321940.282386727,-285187.254646291,-286799.619925239,-273583.344026605], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_LULUCF_TOT_ERR", \
                                     "E28", \
                                     [24.59], \
                                     "%"))
   #
   
   # And now for all the sectors.

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN", \
                                     "E28", \
                                     [-334390.597988565, -421607.812860605, -400636.278572084, -400071.271169911, -389365.447304017, -409719.198170667, -427223.895677682, -419538.668150031, -432250.379840829, -436356.551261901, -393789.017099319, -419287.775124893, -398052.632802012, -372202.372261595, -389669.007463559, -381074.265468842, -389824.719611824, -348746.884289335, -403128.876020475, -423381.691322826, -394704.022662296, -395754.165495035, -407373.867116746, -411175.709218406, -391112.466600924, -381303.555837057, -383895.279367916, -351231.542523156, -347506.383796689, -332759.602106029], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_REMAIN_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT", \
                                     "E28", \
                                     [-39456.5182838354, -40754.3830599652, -42253.3966649357, -42382.1947072716, -43133.0100495957, -43074.7897209732, -45174.9107969863, -45442.403363616, -46161.9510724534, -48458.5437626914, -48152.8417510554, -50943.5273133531, -51308.6553881124, -49114.7357394702, -52189.2587083284, -51703.8985155264, -54216.2603525259, -52959.3737265884, -57290.7559342019, -56746.7735898079, -56025.7484958141, -54036.3400036149, -50940.7933552432, -51134.6429137075, -48949.8416907826, -46994.7173483444, -44660.0970100662, -38706.0843687102, -40016.7799733144, -39356.6567325569], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_FL_CONVERT_ERR", \
                                     "E28", \
                                     [13.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN", \
                                     "E28", \
                                     [38840.5338154669, 35821.8591899609, 37016.6373858597, 34733.6181839444, 34332.5083562424, 35459.5723608046, 36665.6360546042, 36208.6388754333, 35678.0594302939, 35510.5437451216, 35649.6730436408, 31699.6848707677, 32458.3962810996, 32186.7545494521, 30965.9780906335, 28912.5186096338, 27260.7605057722, 29936.9923112587, 29466.6991191648, 28314.9453872202, 26946.488751325, 28289.9928769867, 29749.0388754984, 31485.8581014078, 31478.0433919048, 23784.5977364377, 22513.3916557888, 21633.58578792, 22950.9908812819, 22623.302975503], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_REMAIN_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT", \
                                     "E28", \
                                     [60116.1493485648, 59399.2533025179, 58927.003929212, 58542.4237519617, 58144.0531832826, 57305.9959208191, 57002.6609893636, 56294.0309430021, 56467.3386826353, 56421.1790217526, 54245.8711628416, 54046.6076358601, 53011.5960547639, 52065.1472070351, 51197.4978057654, 51031.5793075249, 50843.0445618987, 50397.525568687, 51064.0371412164, 49951.7837999126, 49639.9628409372, 49397.7846883753, 41450.622649725, 41709.6882134421, 44026.9226622408, 44084.9616505803, 45131.1605512441, 45822.580990524, 45287.2507779032, 40952.3095762808
], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_CL_CONVERT_ERR", \
                                     "E28", \
                                     [48.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN", \
                                     "E28", \
                                     [55980.8196713685, 52228.147896513, 51516.7120629018, 54060.3258415532, 51148.6563901527, 47492.2796376499, 46912.4212709147, 48682.8594438269, 49922.9709816981, 47991.814039535, 49539.3922114412, 47235.8705762063, 45560.7710238747, 45955.9321446253, 43479.5870510598, 42260.3617041955, 39642.35517867, 45914.9662503441, 39923.5142652449, 39311.327404742, 37009.341330475, 38027.8448997301, 40358.0956447841, 34718.4101268296, 34236.5506238707, 33784.4651393703, 33733.8664997472, 36469.6137075907, 31718.5212485065, 31421.3253163176], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_REMAIN_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT", \
                                     "E28", \
                                     [-27280.8259175752, -27782.2917937272, -28427.9806065593, -28849.6510428287, -28717.7644709005, -30564.0482536108, -30706.4302529045, -30516.3535639889, -31576.2391101991, -30465.5330476566, -30753.2409238408, -31571.2927943744, -31732.3972924555, -31189.3636310264, -30343.8979194363, -30887.1442922062, -28847.1214011815, -28327.9224808567, -28749.4483268188, -30023.863880208, -31562.072273636, -32474.4443342198, -29363.3820840831, -28803.1825565932, -30629.1265520029, -31706.4930907927, -31418.4655322745, -30480.7771709342, -30449.1303620985, -29503.0103423378], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_GL_CONVERT_ERR", \
                                     "E28", \
                                     [752.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN", \
                                     "E28", \
                                     [9339.02337652665, 9038.96364303957, 10240.5329537503, 9474.97245157917, 11061.6463229036, 10911.9149776361, 10435.9531566989, 10344.4343218108, 9226.67951266908, 10971.7013960331, 10100.9731011962, 11623.929655228, 10907.2341927338, 11715.2642628024, 10648.7873284384, 11689.7317140425, 11342.7684162296, 9790.97302018687, 9996.28448445446, 10031.3307104274, 11008.2731872573, 10369.2070027948, 9676.39860371521, 11187.882690677, 11301.1987392557, 11075.2658869463, 10522.5336944017, 11629.5311305262, 11379.8398603183, 10949.1999678463], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_REMAIN_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT", \
                                     "E28", \
                                     [2295.02377856749, 2270.83962148009, 2172.35817263493, 2189.18972773431, 2206.54247515985, 2279.87999549271, 2403.23555902112, 2409.7037149286, 2284.3236255121, 2637.60831764973, 2645.90638906417, 3131.00692356606, 3419.55062911607, 4027.56464520257, 4363.44111346423, 4667.29504511698, 4840.04832947418, 5543.95845658975, 4891.71367624115, 5272.60853466611, 5480.0909632452, 5753.18536645454, 4117.69029120152, 4171.30531477277, 4697.31854833015, 7433.74590493175, 5023.71076769904, 4925.27746818557, 5575.55698398135, 6269.72583915181], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_WL_CONVERT_ERR", \
                                     "E28", \
                                     [55.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN", \
                                     "E28", \
                                     [4876.12291557097, 4938.58421009418, 4977.14200492742, 4962.90728972737, 5010.93216171192, 5080.02317982402, 5138.39283171565, 5140.35984345439, 5183.45983318161, 5191.83707474059, 5253.06935006921, 5280.57474530437, 5302.94941441428, 5335.46668668853, 5339.00342019956, 5352.21256171374, 5422.49256117123, 5393.83818243471, 5406.17051945351, 5457.92414305404, 5495.70993786775, 5527.81660991446, 4873.56289008561, 5079.34328768476, 5062.1000587792, 4948.14402085511, 5032.96873786462, 5509.01353437214, 5641.42754222483, 5433.75126804112], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_REMAIN_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT", \
                                     "E28", \
                                     [39312.6785126886, 40818.8019356779, 39721.1111509142, 41790.094782216, 40389.0570110756, 41148.9467455827, 38692.086121838, 39965.2341709962, 39764.4670386647, 40600.0451158988, 39645.3116433369, 41084.1488188752, 41324.1262610419, 42186.505321456, 43951.8121045605, 44287.4077107655, 45003.0743521548, 46413.7378654339, 47729.5671480074, 46781.8630586619, 44198.9076634643, 43265.1104433735, 45621.8062514598, 45413.871794814, 45107.3679256708, 45318.0804591292, 50482.0032556626, 45062.7196584388, 45233.6448727303, 45365.825811072], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_SL_CONVERT_ERR", \
                                     "E28", \
                                     [26.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN", \
                                     "E28", \
                                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_REMAIN_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT", \
                                     "E28", \
                                     [3118.51291678378, 2485.81829463971, 2230.98801872326, 1917.95560297776, 1756.7126754003, 380.301417962189, 327.367524149966, 292.660301431952, 254.542506304011, 239.931179628206, 182.395474123264, 129.090370114401, -51.7849437967745, -120.588905254184, -194.938925329175, -187.5737010454, 1285.34166497361, -506.210721043642, -519.379556732121, -343.34380731111, -263.286552390283, -245.538083302916, -150.02099990519, 41.036116488242, 539.094130263657, 572.100281508246, 498.727809738274, 401.858100093989, 316.650832419424, 486.350216954119], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_OL_CONVERT_ERR", \
                                     "E28", \
                                     [144.0], \
                                     "%"))
   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP", \
                                     "E28", \
                                     [-33355.1821289926, -21581.8461721742, -16097.7490435376, -20952.2031374696, -28818.9302189617, -31782.2803332924, -31385.7852859765, -37740.9053639848, -39425.1842349592, -43851.6721625463, -51294.1336588187, -44750.2839189165, -49673.9727261307, -55371.2930722648, -61180.2324274684, -61616.1457134236, -68294.8381531843, -71160.9987497738, -48532.6141615665, -32707.2372721361, -42054.9012657365, -41822.5881670802, -39037.06494522, -35183.9343766067, -39306.6695917683, -40547.2370512881, -41849.1268000066, -43366.8650815214, -44937.7399220898, -42634.654266173], \
                                     "kilotonnes CO2 yr-1"))

   exceptions.append(exception_class(unfccc2021_filename, \
                                     "FCO2_HWP_ERR", \
                                     "E28", \
                                     [40.0], \
                                     "%"))

   #

   ##########################################
   
   possible_file_types=["CountryTotWithEEZEU","CountryTotWithOutEEZEU","CountryTotWithEEZ","CountryTotWithOutEEZ","CountryTotWithEEZGlobal","CountryTotWithOutEEZGlobal","CountryTotWithEEZAllCountriesRegions","CountryTotWithOutEEZAllCountriesRegions","CountryTotWithEEZMaster","CountryTotWithOutEEZMaster"]

   for exception in exceptions:
      print("*****************************************")
      print("Checking exception: {},{}".format(exception.varname,exception.region_code))
      for filetype in possible_file_types:

         # Check to see if the file exists.  If so, open it and check to see
         # if the variable and the region that we want to change exist.  If not,
         # we can go to the next file.
         filename=exception.filename.substitute(filetype=filetype)
         try:
            srcnc = netCDF4.Dataset(filename,"r+")
            print("Checking file: ",filename)
            
         except:
            #print(filename + " does not exist.  Skipping.")
            continue
         #endtry

         if exception.varname not in srcnc.variables.keys():
            print("Cannot find variable {} in this file.  Skipping".format(exception.varname))
            print(srcnc.variables.keys())
            continue
         #endif

         regcode = srcnc.variables["country_code"][:]
         code_index=-1
         for idx in range(regcode.shape[0]):

            ccode="".join([letter.decode('UTF-8') for letter in regcode[idx] if letter is not np.ma.masked])
            if ccode == exception.region_code:
               code_index=idx
            #endif
         #endif

         if code_index == -1:
            print("Region {} not found.  Skipping.".format(exception.region_code))
            continue
         #endif

         # Check the units
         if srcnc.variables[exception.varname].units != exception.current_units:
            print("Converting units from {} to {}.".format(exception.current_units,srcnc.variables[exception.varname].units))
            exception.convert_units(srcnc.variables[exception.varname].units)
         #endif

         print("Replacing data.")
         # Replace the data
         if len(exception.data) == 1: # replace all values (this happens with uncertainties)
            for itime in range(srcnc.variables[exception.varname].shape[0]):
               srcnc.variables[exception.varname][itime,code_index]=exception.data[0]
            #endfor
         elif len(exception.data) == srcnc.variables[exception.varname].shape[0]:
            srcnc.variables[exception.varname][:,code_index]=exception.data[:]
         elif (srcnc.variables[exception.varname].shape[0] % len(exception.data)) == 0 and (srcnc.variables[exception.varname].shape[0]/len(exception.data)) == 12:
            # This is a shortcut.  It assumes that you gave it annual values and
            # it's copying them to a monthly timeseries using the same value
            # for all months in a year.
            for itime in range(srcnc.variables[exception.varname].shape[0]):
               jtime=math.floor(itime/12)
               srcnc.variables[exception.varname][itime,code_index]=exception.data[jtime]
            #endfor
         else:
            print("Data you want to replace is not the same length as what it's replacing!")
            print(exception.varname,exception.varname,exception.varname)
            print("Length of data requested: ",len(exception.data))
            print("Shape of data to overwrite: ",srcnc.variables[exception.varname].shape)
            traceback.print_stack(file=sys.stdout)
            sys.exit(1)
         #endif

         # Add a note
         srcnc.setncatts({'data_{}_{}'.format(exception.region_code,exception.varname) : 'The data for region {} and variable {} is not taken from the 2D file, but rather added afterwards by the script calc_ecoregts_v2_EXCEPTIONS.py'.format(exception.region_code,exception.varname)})

         srcnc.close()

      #endfor

   #endfor

#endif main
     





