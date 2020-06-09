import numpy as np
from datetime import date, timedelta
from calendar import isleap
import math
import netCDF4 as nc
import sys
from mpl_toolkits.basemap import maskoceans
import matplotlib as mpl
import pandas as pd

##########################################################################
def get_simulation_parameters(graphname,lshow_productiondata):

   # Here are some dictionaries the define parameters for each simulation.
   # These may be varied below for each individual plot, but this is a first try.

   titleending="NO TITLE ENDING CHOSEN"
   
   # Turn this to True if you want to print a disclaimer on the plots about fake data being used.
   # Should be used in combination with lines like the following:
   #if lshow_productiondata:
   #   productiondata_master['ORCHIDEE-MICT']=False
   #endif
   # which will make the data print lighter.
   printfakewarning=False
   # Roxana proposes using this for all plots
   datasource='VERIFY Project'

   overwrite_simulations={}
   overwrite_coeffs={}
   overwrite_operations={}
   desired_legend=[]

   otherdir='/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/'
   verifydir='/home/dods/verify/VERIFY_OUTPUT/FCO2/'
   invdir='/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/'
   files_master={ \
                  'UNFCCC_totincLULUCF' : invdir + 'Tier1_CO2_TotEmisIncLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_totexcLULUCF' : invdir + 'Tier1_CO2_TotEmisExcLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_LULUCF' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc', \
                  
                  'TrendyV7' : '/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_AllTrendyMedianMinMax-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_CABLE' : otherdir + 'Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_CLASS' : otherdir + 'Tier3BUPB_CO2_LandFlux_CLASS-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_CLM5' : otherdir + 'Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_DLEM' : otherdir + 'Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_ISAM' : otherdir + 'Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_JSBACH' : otherdir + 'Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_JULES' : otherdir + 'Tier3BUPB_CO2_LandFlux_JULES-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_LPJ' : otherdir + 'Tier3BUPB_CO2_LandFlux_LPJ-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_LPX' : otherdir + 'Tier3BUPB_CO2_LandFlux_LPX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_OCN' : otherdir + 'Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_ORCHIDEE-CNP' : otherdir + 'Tier3BUPB_CO2_LandFlux_ORCHIDEE-CNP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_ORCHIDEE' : otherdir + 'Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_SDGVM' : otherdir + 'Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'TrendyV7_SURFEX' : otherdir + 'Tier3BUPB_CO2_LandFlux_SURFEX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTotWithOutEEZ.nc', \
                  'ORCHIDEE_S0' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S0_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_S1' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S1_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_S2' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S2_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_RH' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'EPIC' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithEEZ.nc', \
#                  'EPIC' : "/home/users/mmcgrath/CODE.OBELIX/PYTHON/EPIC_process_CountryTotWithEEZ.nc", \
                  'EPIC_RH' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc', \
                  'EPIC_fHarvest' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc', \
                  'EPIC_clch' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc', \
                  'EPIC_npp' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTotWithOutEEZ.nc', \
                  'JENA-COMBINED' : verifydir + 'Tier3TD_CO2_LandFlux_AllJENA_bgc-jena_LAND_GL_1M_V1_20200304_McGrath_WP3_CountryTotWithEEZ.nc', \
                  'JENA-REG-100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc', \
                  'JENA-REG-200km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-200km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc', \
                  'JENA-REG-Core100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Core100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc', \
                  'JENA-REG-Valid100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Valid100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTotWithEEZ.nc', \
                  'BLUE' : '/home/dods/verify/OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTotWithOutEEZ.nc', \
                  'H&N' : '/home/dods/verify/OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZ.nc', \
                  'ORCHIDEE-MICT' : '/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_LandUseChange_ORCHIDEEMICT-SX_LSCE_LAND_EU_1M_V1_20190925_YUE_WP3_CountryTotWithOutEEZ.nc', \
                  'FAOSTAT_For' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc', \
                  'FAOSTAT_Crp' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc', \
                  'FAOSTAT_Grs' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc', \
                  #'EDGARv4' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/EDGAR_TEST.nc', \
                  # This is the same as the VERIFY inverions.  And Cristoph does not like this version that he used.  So we will replace it with the mean of the VERIFY inverions.  I call this JENA-COMBINED above.
                  'EUROCOM_Carboscope' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CarboScopeRegional_bgc-jena_LAND_EU_1M_V1_20191020_Gerbig_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_Flexinvert' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_FLEXINVERT_nilu_LAND_EU_1M_V1_20191020_Thompson_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_Lumia' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_LUMIA-ORC_nateko_LAND_EU_1M_V1_20191020_Monteil_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_Chimere' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CHIMERE-ORC_lsce_LAND_EU_1M_V1_20191020_Broquet_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_CTE' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CTE_wur_LAND_EU_1M_V1_20191020_Ingrid_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_EnKF' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_EnKF-RAMS_vu_LAND_EU_1M_V1_20191020_Antoon_Grid-eurocom_CountryTotWithEEZ.nc', \
                  'EUROCOM_NAME' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_NAME-HB_bristol_LAND_EU_1M_V1_20191020_White_Grid-eurocom_CountryTotWithEEZ.nc', \
                  # All EUROCOM simulations combined
                  'EUROCOM_ALL' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_AllEUROCOMInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZ.nc', \
                  'ECOSSE_CL-CL': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-SX_UAbdn_CRP_EU28_1M_V1_20200518_KUHNERT_WP3_CountryTotWithOutEEZ.nc",\
                  'ECOSSE_GL-GL': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-SX_UAbdn_GRS_EU28_1M_V1_20200518_KUHNERT_WP3_CountryTotWithOutEEZ.nc", \
                  'ECOSSE_CL-CL_us': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_swheat_co2_CountryTotWithOutEEZ.nc",\
                  'ECOSSE_GL-GL_us': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_gra_co2_CountryTotWithOutEEZ.nc", \
                  'EFISCEN-Space': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_treeNEP_EFISCEN-Space-SX_WENR_FOR_EU_1M_V1_20190716_SCHELHAAS_WP3_CountryTotWithOutEEZ.nc",\
                  'UNFCCC_FL-FL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_GL-GL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_CL-CL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_FL-FL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'EFISCEN' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", \
                  'EFISCEN_NPP' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", \
                  'EFISCEN_NEE' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", \
                  'EFISCEN-unscaled' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTotWithOutEEZ.nc", \
                  'CBM' : "/home/dods/verify/OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_rsonlyRF_os' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_rsonlyANN_os' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_rsonlyRF_ns' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_rsonlyANN_ns' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_FL-FL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_FL-FL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_GL-GL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_GL-GL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_CL-CL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'FLUXCOM_CL-CL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_GL-GL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_CL-CL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'TNO_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/TNO/Tier3BUDD_CO2_BiofuelEmissions_XXX-SX_TNO_XXX_EU_1M_V1_20191110_DERNIER_WPX_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_Biofuels_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'ULB_lakes_rivers' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_RiverLakeEmissions_XXXX-SX_ULB_INLWAT_EU_1M_V1_20190911_LAUERWALD_WP3_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_forest_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_grassland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_cropland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_wetland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_settlement_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_other_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'UNFCCC_woodharvest' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_HWP_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc", \
                  'GCP_JENA' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_JENA-s76-4-3-2019_bgc-jena_LAND_GL_1M_V1_20191020_Christian_WPX_CountryTotWithEEZ.nc', \
                  'GCP_CTRACKER' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2019_wur_LAND_GL_1M_V1_20191020_Wouter_WPX_CountryTotWithEEZ.nc', \
                  'GCP_CAMS' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CAMS-V18-2-2019_lsce_LAND_GL_1M_V1_20191020_Chevallier_WPX_CountryTotWithEEZ.nc', \
                  'GCP_ALL' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_AllGCPInversions_XXX_LAND_GL_1M_V1_202003021_McGrath_WP3_CountryTotWithEEZ.nc', \
                  'LUH2v2_FOREST' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_FOREST' : '/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_ForestArea_CRF2019-SX_UNFCCC_FOR_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc', \
                  'LUH2v2_GRASS' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_GRASS' : '/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_GrasslandArea_CRF2019-SX_UNFCCC_GRS_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc', \
                  'LUH2v2_CROP' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_1990_2018_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_CROP' : '/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_CroplandArea_CRF2019-SX_UNFCCC_CRP_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTotWithOutEEZ.nc', \
                  'MS-NRT' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_CountryTotWithOutEEZ.nc', \
                  # These will all get overwritten below
                  'UNFCCC_LUC' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc', \
                  'UNFCCC_LUCF' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTotWithOutEEZ.nc', \
                  'FAOSTAT_LULUCF' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc', \
                  'FAOSTAT_FL-FL' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/Tier1_CO2_AllFluxes_FAOSTAT-SX_FAO_LAND_EU_1M_V1_20191212_PETRASCU_WPX_CountryTotWithOutEEZ.nc', \
                  'VERIFYBU' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \
                  'ORCHIDEE_LUC' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTotWithOutEEZ.nc", \

               }
   
   # certain simulations will be treated in identical ways
   simtype_master={ \
                      'UNFCCC_totincLULUCF' : 'INVENTORY', \
                      'UNFCCC_totexcLULUCF' : 'INVENTORY', \
                      'UNFCCC_LULUCF' : 'INVENTORY', \
                      'UNFCCC_LUC' : 'INVENTORY', \
                      'UNFCCC_LUCF' : 'INVENTORY', \
                      'TrendyV7' : 'MINMAX', \
                      'TrendyV7_CABLE' : 'TRENDY', \
                      'TrendyV7_CLASS': 'TRENDY', \
                      'TrendyV7_CLM5' : 'TRENDY', \
                      'TrendyV7_DLEM' : 'TRENDY', \
                      'TrendyV7_ISAM' : 'TRENDY', \
                      'TrendyV7_JSBACH' : 'TRENDY', \
                      'TrendyV7_JULES' : 'TRENDY', \
                      'TrendyV7_LPJ' : 'TRENDY', \
                      'TrendyV7_LPX' : 'TRENDY', \
                      'TrendyV7_OCN' : 'TRENDY', \
                      'TrendyV7_ORCHIDEE-CNP' : 'TRENDY', \
                      'TrendyV7_ORCHIDEE' : 'TRENDY', \
                      'TrendyV7_SDGVM' : 'TRENDY', \
                      'TrendyV7_SURFEX' : 'TRENDY', \
                      'ORCHIDEE' : 'VERIFY_BU', \
                      'ORCHIDEE_S2' : 'VERIFY_BU', \
                      'ORCHIDEE_S1' : 'VERIFY_BU', \
                      'ORCHIDEE_S0' : 'VERIFY_BU', \
                      'ORCHIDEE_LUC' : 'VERIFY_BU', \
                      'VERIFYBU' : 'VERIFY_BU', \
                      'ORCHIDEE_RH' : 'VERIFY_BU', \
                      'FLUXCOM_rsonlyANN_os' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyRF_os' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyANN_ns' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyRF_ns' :  'VERIFY_BU', \
                      'EPIC' :  'VERIFY_BU', \
                      'EPIC_RH' :  'VERIFY_BU', \
                      'EPIC_fHarvest' :  'VERIFY_BU', \
                      'EPIC_clch' :  'VERIFY_BU', \
                      'EPIC_npp' :  'VERIFY_BU', \
                      'ORCHIDEE-MICT' :  'VERIFY_BU', \
                      'FAOSTAT_LULUCF' :  'INVENTORY_NOERR', \
                      'FAOSTAT_FL-FL' :  'INVENTORY_NOERR', \
                      'FAOSTAT_For' :  'INVENTORY_NOERR', \
                      'FAOSTAT_Crp' :  'INVENTORY_NOERR', \
                      'FAOSTAT_Grs' :  'INVENTORY_NOERR', \
                      'EDGARv4' :  'INVENTORY_NOERR', \
                      'H&N' :  'NONVERIFY_BU', \
                      'JENA-COMBINED' :  'MINMAX', \
                      'JENA-REG-100km' :  'VERIFY_TD', \
                      'JENA-REG-200km' :  'VERIFY_TD', \
                      'JENA-REG-Core100km' :  'VERIFY_TD', \
                      'JENA-REG-Valid100km' :  'VERIFY_TD', \
                      'BLUE' :  'VERIFY_BU', \
                      'EUROCOM_Carboscope' : 'REGIONAL_TD', \
                      'EUROCOM_Flexinvert' : 'REGIONAL_TD', \
                      'EUROCOM_Lumia' :  'REGIONAL_TD', \
                      'EUROCOM_Chimere' :  'REGIONAL_TD', \
                      'EUROCOM_CTE' :  'REGIONAL_TD', \
                      'EUROCOM_EnKF' :  'REGIONAL_TD', \
                      'EUROCOM_NAME' :  'REGIONAL_TD', \
                      'EUROCOM_ALL' :  'MINMAX', \
                    'ECOSSE_CL-CL': "VERIFY_BU", \
                    'ECOSSE_GL-GL': "VERIFY_BU", \
                    'ECOSSE_CL-CL_us': "VERIFY_BU", \
                    'ECOSSE_GL-GL_us': "VERIFY_BU", \
                    'EFISCEN-Space': "VERIFY_BU", \
                    'UNFCCC_FL-FL': "INVENTORY", \
                    'UNFCCC_GL-GL': "INVENTORY", \
                    'UNFCCC_CL-CL': "INVENTORY", \
                    'ORCHIDEE_FL-FL' : "VERIFY_BU", \
                    'EFISCEN' : "NONVERIFY_BU", \
                    'EFISCEN_NPP' : "NONVERIFY_BU", \
                    'EFISCEN_NEE' : "NONVERIFY_BU", \
                    'EFISCEN-unscaled' : "NONVERIFY_BU", \
                    'CBM' : "NONVERIFY_BU", \
                    'FLUXCOM_FL-FL_RF' : "VERIFY_BU", \
                    'FLUXCOM_FL-FL_ANN' : "VERIFY_BU", \
                    'FLUXCOM_GL-GL_RF' : "VERIFY_BU", \
                    'FLUXCOM_GL-GL_ANN' : "VERIFY_BU", \
                    'FLUXCOM_CL-CL_RF' : "VERIFY_BU", \
                    'FLUXCOM_CL-CL_ANN' : "VERIFY_BU", \
                  'ORCHIDEE_GL-GL' : "VERIFY_BU", \
                 'ORCHIDEE_CL-CL' : "VERIFY_BU", \
                    'TNO_biofuels' : "INVENTORY_NOERR", \
                    'UNFCCC_biofuels' : "INVENTORY_NOERR", \
                  'ULB_lakes_rivers' : "VERIFY_BU", \
                    'UNFCCC_forest_convert' : "INVENTORY", \
                    'UNFCCC_grassland_convert' : "INVENTORY", \
                    'UNFCCC_cropland_convert' : "INVENTORY", \
                    'UNFCCC_wetland_convert' : "INVENTORY", \
                    'UNFCCC_settlement_convert' : "INVENTORY", \
                    'UNFCCC_other_convert' : "INVENTORY", \
                    'UNFCCC_woodharvest' : "INVENTORY", \
                    'GCP_JENA' : 'GLOBAL_TD', \
                    'GCP_CTRACKER' : 'GLOBAL_TD', \
                    'GCP_CAMS' : 'GLOBAL_TD', \
                    'GCP_ALL' : 'MINMAX', \
                    'LUH2v2_FOREST' : 'OTHER', \
                    'UNFCCC_FOREST' : 'OTHER', \
                    'LUH2v2_GRASS' : 'OTHER', \
                    'UNFCCC_GRASS' : 'OTHER', \
                    'LUH2v2_CROP' : 'OTHER', \
                    'UNFCCC_CROP' : 'OTHER', \
                    'MS-NRT' : 'INVENTORY_NOERR', \
                 }

   variables_master={ \
                      'UNFCCC_totincLULUCF' : 'FCO2_NBP', \
                      'UNFCCC_totexcLULUCF' : 'FCO2_NBP', \
                      'UNFCCC_LULUCF' : 'FCO2_NBP', \
                      'UNFCCC_LUC' : 'FCO2_NBP', \
                      'UNFCCC_LUCF' : 'FCO2_NBP', \
                      'TrendyV7' : 'FCO2_NBP', \
                      'TrendyV7_CABLE' : 'FCO2_NBP', \
                      'TrendyV7_CLASS': 'FCO2_NBP', \
                      'TrendyV7_CLM5' : 'FCO2_NBP', \
                      'TrendyV7_DLEM' : 'FCO2_NBP', \
                      'TrendyV7_ISAM' : 'FCO2_NBP', \
                      'TrendyV7_JSBACH' : 'FCO2_NBP', \
                      'TrendyV7_JULES' : 'FCO2_NBP', \
                      'TrendyV7_LPJ' : 'FCO2_NBP', \
                      'TrendyV7_LPX' : 'FCO2_NBP', \
                      'TrendyV7_OCN' : 'FCO2_NBP', \
                      'TrendyV7_ORCHIDEE-CNP' : 'FCO2_NBP', \
                      'TrendyV7_ORCHIDEE' : 'FCO2_NBP', \
                      'TrendyV7_SDGVM' : 'FCO2_NBP', \
                      'TrendyV7_SURFEX' : 'FCO2_NBP', \
                      'VERIFYBU' : 'FCO2_NBP', \
                      'ORCHIDEE' : 'FCO2_NBP', \
                      'ORCHIDEE_S2' : 'FCO2_NBP', \
                      'ORCHIDEE_S1' : 'FCO2_NBP', \
                      'ORCHIDEE_S0' : 'FCO2_NBP', \
                      'ORCHIDEE_LUC' : 'FCO2_NBP', \
                      'ORCHIDEE_RH' : 'rh', \
                      'FLUXCOM_rsonlyANN_os' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyRF_os' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyANN_ns' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyRF_ns' :  'FCO2_NEP', \
                      'EPIC' :  'FCO2_NBP_CRO', \
                      'EPIC_RH' :  'FCO2_RH_CRO', \
                      'EPIC_fHarvest' :  'FCO2_FHARVEST_CRO', \
                      'EPIC_clch' :  'FCO2_CLCH_CRO', \
                      'EPIC_npp' :  'FCO2_NPP_CRO', \
                      'JENA-COMBINED' :  'FCO2_NBP', \
                      'JENA-REG-100km' :  'FCO2_NBP', \
                      'JENA-REG-200km' :  'FCO2_NBP', \
                      'JENA-REG-Core100km' :  'FCO2_NBP', \
                      'JENA-REG-Valid100km' :  'FCO2_NBP', \
                      'BLUE' :  'CD_A', \
                      'H&N' :  'FCO2_NBP', \
                      'ORCHIDEE-MICT' :  'FCO2_NBP', \
                      'EDGARv4' :  'CD_A', \
                      'FAOSTAT_LULUCF' :  'FCO2_NBP_FOR', \
                      'FAOSTAT_FL-FL' :  'FCO2_NBP_FOR', \
                      'FAOSTAT_For' :  'FCO2_LUTOT_FOR', \
                      'FAOSTAT_Crp' :  'FCO2_SOIL_CRO', \
                      'FAOSTAT_Grs' :  'FCO2_SOIL_GRA', \
                      'EUROCOM_Carboscope' : 'FCO2_NBP', \
                      'EUROCOM_Flexinvert' : 'FCO2_NBP', \
                      'EUROCOM_Lumia' :  'FCO2_NBP', \
                      'EUROCOM_Chimere' :  'FCO2_NBP', \
                      'EUROCOM_CTE' :  'FCO2_NBP', \
                      'EUROCOM_EnKF' :  'FCO2_NBP', \
                      'EUROCOM_NAME' :  'FCO2_NBP', \
                      'EUROCOM_ALL' :  'FCO2_NBP', \
                      'ECOSSE_CL-CL': "FCO2_NEP_CRO", \
                    'ECOSSE_GL-GL': "FCO2_NEP_GRA", \
                      'ECOSSE_CL-CL_us': "FCO2_SOIL_CRO", \
                    'ECOSSE_GL-GL_us': "FCO2_SOIL_GRA", \
                    'EFISCEN-Space': "FCO2_NBP_FOR", \
                    'UNFCCC_FL-FL': "FCO2_NBP", \
                    'UNFCCC_GL-GL': "FCO2_NBP", \
                    'UNFCCC_CL-CL': "FCO2_NBP", \
                      'ORCHIDEE_FL-FL' : "FCO2_NBP_FOR", \
                      'EFISCEN' : "FCO2_NBP_FOR", \
                      'EFISCEN_NPP' : "FCO2_NPP_FOR", \
                      'EFISCEN_NEE' : "FCO2_NEE_FOR", \
                      'EFISCEN-unscaled' : "FCO2_NBP_FOR", \
                      'CBM' : "FCO2_NBP", \
                      'FLUXCOM_FL-FL_RF' : "FCO2_NEP_forest", \
                      'FLUXCOM_FL-FL_ANN' : "FCO2_NEP_forest", \
                      'FLUXCOM_GL-GL_RF' : "FCO2_NEP_grass", \
                      'FLUXCOM_GL-GL_ANN' : "FCO2_NEP_grass", \
                      'FLUXCOM_CL-CL_RF' : "FCO2_NEP_crops", \
                      'FLUXCOM_CL-CL_ANN' : "FCO2_NEP_crops", \
                  'ORCHIDEE_GL-GL' : "FCO2_NBP_GRS", \
                 'ORCHIDEE_CL-CL' : "FCO2_NBP_CRP", \
                      'TNO_biofuels' : "FCO2_NBP_TOT", \
                      'UNFCCC_biofuels' : "FCO2_NBP", \
                      'ULB_lakes_rivers' : "FCO2_INLWAT", \
                   'UNFCCC_forest_convert' : "FCO2_NBP", \
                    'UNFCCC_grassland_convert' : "FCO2_NBP", \
                    'UNFCCC_cropland_convert' : "FCO2_NBP", \
                    'UNFCCC_wetland_convert' : "FCO2_NBP", \
                    'UNFCCC_settlement_convert' : "FCO2_NBP", \
                    'UNFCCC_other_convert' : "FCO2_NBP", \
                    'UNFCCC_woodharvest' : "FCO2_NBP", \
                    'GCP_JENA' : 'FCO2_NBP', \
                    'GCP_CTRACKER' : 'FCO2_NBP', \
                    'GCP_CAMS' : 'FCO2_NBP', \
                    'GCP_ALL' : 'FCO2_NBP', \
                     'LUH2v2_FOREST' : 'FOREST_AREA', \
                     'UNFCCC_FOREST' : 'AREA', \
                     'LUH2v2_GRASS' : 'GRASSLAND_AREA', \
                     'UNFCCC_GRASS' : 'AREA', \
                     'LUH2v2_CROP' : 'CROPLAND_AREA', \
                     'UNFCCC_CROP' : 'AREA', \
                    'MS-NRT' : 'FCO2_NBP', \
                 }
   
   plotmarker_master={ \
                       'UNFCCC_totincLULUCF' : '_', \
                       'UNFCCC_totexcLULUCF' : '_', \
                       'UNFCCC_LULUCF' : '_', \
                       'UNFCCC_LUC' : '_', \
                       'UNFCCC_LUCF' : '_', \
                       'TrendyV7' : 'D', \
                       'TrendyV7_CABLE' : 'D', \
                       'TrendyV7_CLASS': 'D', \
                       'TrendyV7_CLM5' : 'D', \
                       'TrendyV7_DLEM' : 'D', \
                       'TrendyV7_ISAM' : 'D', \
                       'TrendyV7_JSBACH' : 'D', \
                       'TrendyV7_JULES' : 'D', \
                       'TrendyV7_LPJ' : 'D', \
                       'TrendyV7_LPX' : 'D', \
                       'TrendyV7_OCN' : 'D', \
                       'TrendyV7_ORCHIDEE-CNP' : 'D', \
                       'TrendyV7_ORCHIDEE' : 'D', \
                       'TrendyV7_SDGVM' : 'D', \
                       'TrendyV7_SURFEX' : 'D', \
                       'VERIFYBU' : 'D', \
                       'ORCHIDEE' : 'D', \
                       'ORCHIDEE_S2' : 'D', \
                       'ORCHIDEE_S1' : 'D', \
                       'ORCHIDEE_S0' : 'D', \
                       'ORCHIDEE_LUC' : 'D', \
                       'ORCHIDEE_RH' : 'D', \
                       'FLUXCOM_rsonlyANN_os' :  's', \
                       'FLUXCOM_rsonlyRF_os' :  's', \
                       'FLUXCOM_rsonlyANN_ns' :  's', \
                       'FLUXCOM_rsonlyRF_ns' :  's', \
                       'EPIC' :  'o', \
                       'EPIC_RH' :  'o', \
                       'EPIC_fHarvest' :  '^', \
                       'EPIC_npp' :  's', \
                       'EPIC_clch' :  'P', \
                       'JENA-COMBINED' :  's', \
                       'JENA-REG-100km' :  'P', \
                       'JENA-REG-200km' :  'P', \
                       'JENA-REG-Core100km' :  'P', \
                       'JENA-REG-Valid100km' :  'P', \
                       'BLUE' :  '^', \
                       'H&N' :  '^', \
                       'ORCHIDEE-MICT' :  'D', \
                       'EDGARv4' :  '_', \
                       'FAOSTAT_LULUCF' :  'P', \
                       'FAOSTAT_FL-FL' :  'P', \
                       'FAOSTAT_For' :  'o', \
                       'FAOSTAT_Crp' :  'P', \
                       'FAOSTAT_Grs' :  'X', \
                       'EUROCOM_Carboscope' :  'P', \
                       'EUROCOM_Flexinvert' :  'P', \
                       'EUROCOM_Lumia' :  'P', \
                       'EUROCOM_Chimere' :  'P', \
                       'EUROCOM_CTE' :  'P', \
                       'EUROCOM_EnKF' :  'P', \
                       'EUROCOM_NAME' :  'P', \
                       'EUROCOM_ALL' :  'P', \
                       'ECOSSE_CL-CL': "o", \
                       'ECOSSE_GL-GL': "o", \
                       'ECOSSE_CL-CL_us': "o", \
                       'ECOSSE_GL-GL_us': "o", \
                    'EFISCEN-Space': "o", \
                    'UNFCCC_FL-FL': "_", \
                    'UNFCCC_GL-GL': "_", \
                    'UNFCCC_CL-CL': "_", \
                     'ORCHIDEE_FL-FL' : "D", \
                     'EFISCEN' : "o", \
                     'EFISCEN_NEE' : "o", \
                     'EFISCEN_NPP' : "o", \
                     'EFISCEN-unscaled' : "o", \
                     'CBM' : "o", \
                     'FLUXCOM_FL-FL_RF' : "s", \
                     'FLUXCOM_FL-FL_ANN' : "s", \
                     'FLUXCOM_GL-GL_RF' : "s", \
                     'FLUXCOM_GL-GL_ANN' : "s", \
                     'FLUXCOM_CL-CL_RF' : "s", \
                     'FLUXCOM_CL-CL_ANN' : "s", \
                  'ORCHIDEE_GL-GL' : "D", \
                 'ORCHIDEE_CL-CL' : "D", \
                     'TNO_biofuels' : "X", \
                     'UNFCCC_biofuels' : "o", \
                     'ULB_lakes_rivers' : "o", \
                   'UNFCCC_forest_convert' : "o", \
                    'UNFCCC_grassland_convert' : "o", \
                    'UNFCCC_cropland_convert' : "o", \
                    'UNFCCC_wetland_convert' : "o", \
                    'UNFCCC_settlement_convert' : "o", \
                    'UNFCCC_other_convert' : "o", \
                    'UNFCCC_woodharvest' : "o", \
                    'GCP_JENA' : 'o', \
                    'GCP_CTRACKER' : 'o', \
                    'GCP_CAMS' : 'o', \
                    'GCP_ALL' : 's', \
                    'LUH2v2_FOREST' : 'o', \
                    'UNFCCC_FOREST' : 'o', \
                    'LUH2v2_GRASS' : 'o', \
                    'UNFCCC_GRASS' : 'o', \
                    'LUH2v2_CROP' : 'o', \
                    'UNFCCC_CROP' : 'o', \
                    'MS-NRT' : 'o', \
                    }
   facec_master={ \
                  'UNFCCC_totincLULUCF' :  'black', \
                  'UNFCCC_totexcLULUCF' :  'red', \
                  'UNFCCC_LULUCF' :  'green', \
                  'UNFCCC_LUC' :  'green', \
                  'UNFCCC_LUCF' :  'green', \
                  'TrendyV7' :  'grey', \
                  'TrendyV7_CABLE' :  'red', \
                  'TrendyV7_CLASS':  'green', \
                  'TrendyV7_CLM5' :  'blue', \
                  'TrendyV7_DLEM' :  'violet', \
                  'TrendyV7_ISAM' :  'yellow', \
                  'TrendyV7_JSBACH' :  'orange', \
                  'TrendyV7_JULES' :  'brown', \
                  'TrendyV7_LPJ' :  'gold', \
                  'TrendyV7_LPX' :  'gray', \
                  'TrendyV7_OCN' :  'limegreen', \
                  'TrendyV7_ORCHIDEE-CNP' :  'yellowgreen', \
                  'TrendyV7_ORCHIDEE' :  'none', \
                  'TrendyV7_SDGVM' :  'magenta', \
                  'TrendyV7_SURFEX' :  'pink', \
                  'VERIFYBU' : 'blue', \
                  'ORCHIDEE' : 'dodgerblue', \
                  'ORCHIDEE_S2' : 'red', \
                  'ORCHIDEE_S1' : 'green', \
                  'ORCHIDEE_S0' : 'magenta', \
                    'ORCHIDEE_LUC' : 'sandybrown', \
                  'ORCHIDEE_RH' : 'red', \
                  'FLUXCOM_rsonlyANN_os' :  'green', \
                  'FLUXCOM_rsonlyRF_os' :  'yellowgreen', \
                  'FLUXCOM_rsonlyANN_ns' :  'green', \
                  'FLUXCOM_rsonlyRF_ns' :  'yellowgreen', \
                  'EPIC' :  'lightcoral', \
                  'EPIC_RH' :  'pink', \
                  'EPIC_fHarvest' :  'red', \
                  'EPIC_npp' :  'green', \
                  'EPIC_clch' :  'blue', \
                  'JENA-COMBINED' :  'mediumblue', \
                  'JENA-REG-100km' :  'khaki', \
                  'JENA-REG-200km' :  'orange', \
                  'JENA-REG-Core100km' :  'darkorange', \
                  'JENA-REG-Valid100km' :  'gold', \
                  'BLUE' :  'tan', \
                  'H&N' :  'orange', \
                  'ORCHIDEE-MICT' :  'lightsteelblue', \
                  'EDGARv4' :  'blue', \
                  'FAOSTAT_LULUCF' :  'darkviolet', \
                  'FAOSTAT_FL-FL' :  'darkviolet', \
                  'FAOSTAT_For' :  'darkviolet', \
                  'FAOSTAT_Crp' :  'darkviolet', \
                  'FAOSTAT_Grs' :  'darkviolet', \
                  'EUROCOM_Carboscope' :  'khaki', \
                  'EUROCOM_Flexinvert' :  'orange', \
                  'EUROCOM_Lumia' :  'darkorange', \
                  'EUROCOM_Chimere' :  'gold', \
                  'EUROCOM_CTE' :  'red', \
                  'EUROCOM_EnKF' :  'darkred', \
                  'EUROCOM_NAME' :  'magenta', \
                  'EUROCOM_ALL' :  'blue', \
                  'ECOSSE_CL-CL': "darkred", \
                    'ECOSSE_GL-GL': "darkred", \
                  'ECOSSE_CL-CL_us': "darkred", \
                    'ECOSSE_GL-GL_us': "darkred", \
                    'EFISCEN-Space': "green", \
                    'UNFCCC_FL-FL': "green", \
                    'UNFCCC_GL-GL': "brown", \
                  'UNFCCC_CL-CL': "gold", \
                  'ORCHIDEE_FL-FL' : "dodgerblue", \
                  'EFISCEN' : "magenta", \
                  'EFISCEN_NEE' : "blue", \
                  'EFISCEN_NPP' : "orange", \
                  'EFISCEN-unscaled' : "magenta", \
                  'CBM' : "crimson", \
                  'FLUXCOM_FL-FL_RF' : "yellowgreen", \
                  'FLUXCOM_FL-FL_ANN' : "green", \
                  'FLUXCOM_CL-CL_RF' : "yellowgreen", \
                  'FLUXCOM_CL-CL_ANN' : "green", \
                  'FLUXCOM_GL-GL_RF' : "yellowgreen", \
                  'FLUXCOM_GL-GL_ANN' : "green", \
                  'ORCHIDEE_GL-GL' : "dodgerblue", \
                  'ORCHIDEE_CL-CL' : "dodgerblue", \
                  'UNFCCC_biofuels' : "saddlebrown", \
                  'TNO_biofuels' : "saddlebrown", \
                  'ULB_lakes_rivers' : "sandybrown", \
                   'UNFCCC_forest_convert' : "sandybrown", \
                    'UNFCCC_grassland_convert' : "sandybrown", \
                    'UNFCCC_cropland_convert' : "sandybrown", \
                    'UNFCCC_wetland_convert' : "sandybrown", \
                    'UNFCCC_settlement_convert' : "sandybrown", \
                    'UNFCCC_other_convert' : "sandybrown", \
                    'UNFCCC_woodharvest' : "sandybrown", \
                     'GCP_JENA' : 'brown', \
                    'GCP_CTRACKER' : 'gold', \
                    'GCP_CAMS' : 'orange', \
                    'GCP_ALL' : 'red', \
                     'UNFCCC_FOREST' : 'blue', \
                    'LUH2v2_FOREST' : 'orange', \
                     'UNFCCC_GRASS' : 'blue', \
                    'LUH2v2_GRASS' : 'orange', \
                     'UNFCCC_CROP' : 'blue', \
                    'LUH2v2_CROP' : 'orange', \
                'MS-NRT' : 'red', \
             }

   # set some default values, to save space.  Can be changed below.
   # The color around the edge of the symbol.
   edgec_master={}
   # Allows for different colors for the error bars.
   uncert_color_master={}
   # Controls the size of the plotting symbol
   markersize_master={}
   # If False, the symbols will be shown lighter (indicating the data
   # has been made up).
   productiondata_master={}
   # This indicates the text displayed in the plot legend.
   displayname_master={}
   # This indicates the text displayed in the plot legend for the error bars.
   displayname_err_master={}
   # This indicates if the dataset will be displayed on the plot.  Sometimes we read in datasets
   # that we combine in various ways and we don't want the individual datasets shown.
   displaylegend_master={}
   # If true, the dataset will be multiplied by -1 on loading.  This is used to
   # make sources and sinks always follow the same sign convention.
   flipdatasign_master={}
   # If true, this dataset will be adjusted by the "correction" datasets
   # defined elsewhere.
   lcorrect_inversion_master={}
   # If True, this dataset will be plotted with error bars
   lplot_errorbar_master={}
   # This is a flag which, if True, plots whisker error bars.  If False,
   # plots rectangles for the error bars.
   lwhiskerbars_master={}
   for simname in files_master.keys():
      edgec_master[simname]="black"
      uncert_color_master[simname]=facec_master[simname]
      markersize_master[simname]=60
      productiondata_master[simname]=True
      displayname_master[simname]=simname
      displayname_err_master[simname]=simname
      displaylegend_master[simname]=True
      flipdatasign_master[simname]=False
      lcorrect_inversion_master[simname]=False
      lplot_errorbar_master[simname]=False
      lwhiskerbars_master[simname]=False
   #endif

   # Some of the simulations have an inverted sign convention from what
   # we want (we want negative to be a terrestrial sink, positive to be
   # a source).  This flag flips the data on read-in.
   flipdatasign_master["ORCHIDEE"]=True
   flipdatasign_master["ORCHIDEE_GL-GL"]=True
   flipdatasign_master["ORCHIDEE_FL-FL"]=True
   flipdatasign_master["ORCHIDEE_CL-CL"]=True
   flipdatasign_master["ORCHIDEE_S2"]=True
   flipdatasign_master["ORCHIDEE_S1"]=True
   flipdatasign_master["ORCHIDEE_S0"]=True
   flipdatasign_master["CBM"]=True
   flipdatasign_master["EFISCEN"]=True
   flipdatasign_master["EFISCEN_NPP"]=True
   flipdatasign_master["EFISCEN_NEE"]=True
   flipdatasign_master["EFISCEN-Space"]=True
   flipdatasign_master["EFISCEN-unscaled"]=True
   flipdatasign_master["ORCHIDEE-MICT"]=True
   flipdatasign_master["EPIC"]=True

   # Change the color of the error bars for some
   uncert_color_master['UNFCCC_LUC']='darkseagreen'
   uncert_color_master['GCP_ALL']='red'
   uncert_color_master['TrendyV7']='gray'
   uncert_color_master['JENA-COMBINED']='blue'
   uncert_color_master['UNFCCC_GL-GL']='brown'
   uncert_color_master['UNFCCC_CL-CL']='gold'

   # We always want these to be the same
   edgec_master['MS-NRT']=facec_master['MS-NRT']

   # And better names for these two
   displayname_master['UNFCCC_LULUCF']='UNFCCC LULUCF NGHGI 2019'
   displayname_err_master['UNFCCC_LULUCF']='UNFCCC LULUCF NGHGI 2019 uncertainty'
   displayname_master['FAOSTAT_LULUCF']='FAOSTAT'
   displayname_master['GCP_ALL']='Mean of GCP inversions'
   displayname_err_master['GCP_ALL']='Min/Max of GCP inversions'
   displayname_master['JENA-COMBINED']='Mean of CarboScopeReg'
   displayname_err_master['JENA-COMBINED']='Min/Max of CarboScopeReg'
   displayname_master['EUROCOM_ALL']='Mean of EUROCOM inversions'
   displayname_err_master['EUROCOM_ALL']='Min/Max of EUROCOM inversions'
   displayname_master['TrendyV7']='Median of TRENDY v7 DGVMs'
   displayname_err_master['TrendyV7']='Min/Max of TRENDY v7 DGVMs'

   # Temporary one
   #displayname_master['EFISCEN']="EFSICEN NBP"

   lplot_areas=False
   
   # Now define the actual simulation configs
   if graphname == "test":
      desired_simulations=[ \
                            # we read in data for LUC, but we replace it with the sectors below
                            'UNFCCC_LULUCF', \
                            'BLUE', \
                            'TrendyV7', \
        ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="TEST_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use change"
#      datasource='TRENDY/MPI-BGC/LSCE'
      output_file_start="test_"
      output_file_end="_2019_v1.png" 
   elif graphname == "luc_full":
      desired_simulations=[ \
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
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LUC_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use change"

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
      overwrite_simulations["UNFCCC_LUC"]=['UNFCCC_forest_convert', \
                            'UNFCCC_grassland_convert', \
                            'UNFCCC_cropland_convert', \
                            'UNFCCC_wetland_convert', \
                            'UNFCCC_settlement_convert', \
                            'UNFCCC_other_convert', \
      ]
      overwrite_operations["UNFCCC_LUC"]="sum"
      overwrite_coeffs["UNFCCC_LUC"]=[1.0, \
                            1.0, \
                            1.0, \
                            1.0, \
                            1.0, \
                            1.0, \
      ]
      overwrite_simulations["ORCHIDEE_LUC"]=['ORCHIDEE', \
                            'ORCHIDEE_S2', \
      ]
      overwrite_operations["ORCHIDEE_LUC"]="sum"
      overwrite_coeffs["ORCHIDEE_LUC"]=[1.0, \
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
      
   elif graphname == "all_orchidee":
      desired_simulations=[ \
                            'ORCHIDEE-MICT', \
                            'ORCHIDEE_LUC', \
                            'ORCHIDEE', \
                            'ORCHIDEE_S2', \
                            'ORCHIDEE_S1', \
                            'ORCHIDEE_S0', \
                      "TrendyV7_ORCHIDEE",\
        ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="ORCHIDEE_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from all ORCHIDEE simulations"

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
      overwrite_simulations["ORCHIDEE_LUC"]=['ORCHIDEE', \
                            'ORCHIDEE_S2', \
      ]
      overwrite_operations["ORCHIDEE_LUC"]="sum"
      overwrite_coeffs["ORCHIDEE_LUC"]=[1.0, \
                            -1.0, \
      ]



      #   productiondata_master['ORCHIDEE-MICT']=False
      #endif

   elif graphname == "lucf_full":
      desired_simulations=[ \
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
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LUCF_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use change and forestry"

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
      overwrite_simulations["UNFCCC_LUCF"]=['UNFCCC_forest_convert', \
                            'UNFCCC_grassland_convert', \
                            'UNFCCC_cropland_convert', \
                            'UNFCCC_wetland_convert', \
                            'UNFCCC_settlement_convert', \
                            'UNFCCC_other_convert', \
                            'UNFCCC_FL-FL',\
      ]
      overwrite_operations["UNFCCC_LUCF"]="sum"
      overwrite_coeffs["UNFCCC_LUCF"]=[1.0, \
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
   elif graphname == "lulucf_msnrt":
      desired_simulations=[ \
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
         ]   
      output_file_start="UNFCCC-LULUCF-MSNRT_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"

      # These simulations will be combined together.
      #overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      #overwrite_operations["FAOSTAT_LULUCF"]="sum"
      #overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
      # So I don't want to generally plot the components
      #displaylegend_master['FAOSTAT_Crp']=False
      #displaylegend_master['FAOSTAT_Grs']=False
      #displaylegend_master['FAOSTAT_For']=False

   elif graphname == "lulucf_full":
      desired_simulations=[ \
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
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LULUCF_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False

   elif graphname == "lulucf_trendy":
      desired_simulations=[ \
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
                            'TrendyV7', \
                      "TrendyV7_ORCHIDEE",\
         ]  
      
      desired_legend=[\
                      displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                      displayname_master["MS-NRT"],\
             
                      displayname_master["FAOSTAT_LULUCF"],\
                      displayname_master["BLUE"],\
                      displayname_master["H&N"],\
                          displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                      displayname_master["ORCHIDEE"],\
                      displayname_master["ORCHIDEE-MICT"],\
                      displayname_master["TrendyV7_ORCHIDEE"],\
     ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LULUCFTrendy_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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

   elif graphname == "orc_trendy":
      desired_simulations=[ \
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
      desired_legend=[\
                      displayname_master["FAOSTAT_LULUCF"],\
                      displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                      displayname_master["MS-NRT"],\
             
                      displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                      displayname_master["TrendyV7_ORCHIDEE"],\
                      displayname_master["ORCHIDEE"],\
     ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LULUCFOrcTrendy_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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

   elif graphname == "unfccc_fao_trendy":
      desired_simulations=[ \
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
      
      desired_legend=[\
                      displayname_master["FAOSTAT_LULUCF"],\
                      displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                      displayname_master["MS-NRT"],\
             
                      displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                      displayname_master["TrendyV7_ORCHIDEE"],\
     ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="UNFCCCFAOTrendy_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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

   elif graphname == "unfccc_fao":
      desired_simulations=[ \
                            # we read in data for LUC, but we replace it with the sectors below
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
         ]  
      
      desired_legend=[\
                      displayname_master["FAOSTAT_LULUCF"],\
                      displayname_master["UNFCCC_LULUCF"],displayname_master["UNFCCC_LULUCF"]+ " uncertainty",\
                      displayname_master["MS-NRT"],\
             
     ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="UNFCCCFAO_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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

   elif graphname == "fao":
      desired_simulations=[ \
                            # we read in data for LUC, but we replace it with the sectors below
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
         ]  
      
      desired_legend=[\
#                      "blah",\
                      displayname_master["FAOSTAT_LULUCF"],\
                   ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="FAO_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : Bottom-up land use, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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

   elif graphname == "sectorplot_full":
      desired_simulations=[ \
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
      desired_legend=[\
                       "UNFCCC_FL-FL","UNFCCC_GL-GL","UNFCCC_CL-CL",\
                      'Median of TRENDY v7 DGVMs', "Min/Max of TRENDY v7 DGVMs", \
                       "EFISCEN","ECOSSE_GL-GL","EPIC",\
                       "EPIC/ECOSSE/EFISCEN","ORCHIDEE","FLUXCOM_rsonlyANN_os","FLUXCOM_rsonlyRF_os", \
                       ]

 
#      datasource='UNFCCC/IIASA/WEnR/UAbdn/MPI-BGC/LSCE/TRENDY'
      output_file_start="AllSectorBU_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use (land remaining land)"

      plotmarker_master['EPIC']="P"

      facec_master['EPIC']="brown"

      #if lshow_productiondata:
      #   productiondata_master['ECOSSE_CL-CL']=False
      #   productiondata_master['ECOSSE_GL-GL']=False
      #endif

   elif graphname == "unfccc_lulucf_bar":
      desired_simulations=[ \
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
      #desired_legend=[\
      #                 displayname_master["UNFCCC_LULUCF"],\
      #                'UNFCCC_FL-FL','UNFCCC_GL-GL','UNFCCC_CL-CL',\
      #                'UNFCCC_forest_convert', \
      #                      'UNFCCC_grassland_convert', \
      #                      'UNFCCC_cropland_convert', \
      #                      'UNFCCC_wetland_convert', \
      #                      'UNFCCC_settlement_convert', \
      #                      'UNFCCC_other_convert', \
      #                 ]

 
#      datasource='UNFCCC/IIASA/WEnR/UAbdn/MPI-BGC/LSCE/TRENDY'
      output_file_start="UNFCCCLULUCFbar_"
      output_file_end="_FCO2land_2019_v7.png" 
      titleending=r" : CO$_2$ emission trends from land use, land use change, and forestry"

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

   elif graphname == "verifybu":
      desired_simulations=[ \
                            'ORCHIDEE', \
                            'ORCHIDEE-MICT', \
                            'EFISCEN', \
#                            'EFISCEN-unscaled', \
                            'EFISCEN-Space', \
                            'FLUXCOM_rsonlyANN_os', \
                            'FLUXCOM_rsonlyRF_os', \
                            'ECOSSE_GL-GL', \
                            'ECOSSE_CL-CL', \
                            #'ECOSSE_GL-GL_us', \
                            #'ECOSSE_CL-CL_us', \
                            'EPIC', \
                            'BLUE', \
                            'VERIFYBU', \
                         ]   
#      datasource='UNFCCC/MPI-BGC/JRC/WEnR/LSCE/FAOSTAT'
      output_file_start="VerifyBU_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from all VERIFY bottom-up models"
      lplot_areas=True

      # These simulations will be combined together.
      overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE']
      overwrite_operations["VERIFYBU"]="mean"
      displaylegend_master["VERIFYBU"]=False

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

   elif graphname == "trendy":
      desired_simulations=[ \
                            'TrendyV7', \
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
      output_file_start="TRENDY_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from all TRENDY v7 bottom-up models"
      lplot_areas=True

      plotmarker_master['EFISCEN']="P"

      edgec_master["ORCHIDEE_FL-FL"]="black"
      
      facec_master["ORCHIDEE_FL-FL"]="black"

   elif graphname == "fluxcom":
      desired_simulations=[ \
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
      output_file_start="FLUXCOM_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from FLUXCOM with both the original and new LUH2v2-ESACCI land cover fractions"

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
      overwrite_simulations["FLUXCOM_rsonlyANN_ns"]=['FLUXCOM_FL-FL_ANN','FLUXCOM_GL-GL_ANN','FLUXCOM_CL-CL_ANN']
      # So I don't want to generally plot the components
      displaylegend_master['FLUXCOM_FL-FL_ANN']=True
      displaylegend_master['FLUXCOM_GL-GL_ANN']=True
      displaylegend_master['FLUXCOM_CL-CL_ANN']=True

      overwrite_simulations["FLUXCOM_rsonlyRF_ns"]=['FLUXCOM_FL-FL_RF','FLUXCOM_GL-GL_RF','FLUXCOM_CL-CL_RF']
      # So I don't want to generally plot the components
      displaylegend_master['FLUXCOM_FL-FL_RF']=True
      displaylegend_master['FLUXCOM_GL-GL_RF']=True
      displaylegend_master['FLUXCOM_CL-CL_RF']=True

   elif graphname == "forestry_full":
      desired_simulations=[ \
                            'ORCHIDEE_FL-FL', \
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

      desired_legend=[\
                       displayname_master['UNFCCC_FL-FL'],"UNFCCC_FL-FL uncertainty",\
                       displayname_master['FAOSTAT_FL-FL'], \
                       displayname_master['ORCHIDEE_FL-FL'], \
                       displayname_master['EFISCEN'], \
                      # displayname_master['EFISCEN_NPP'], \
                      # displayname_master['EFISCEN_NEE'], \
#                       'EFISCEN-Space', \
                       displayname_master['CBM'], \
                       #displayname_master['FLUXCOM_FL-FL_ANN'], \
                       #displayname_master['FLUXCOM_FL-FL_RF'], \
                       displayname_master['LUH2v2_FOREST'], \
                       displayname_master['UNFCCC_FOREST'], \
                      ]

#      datasource='UNFCCC/MPI-BGC/JRC/WEnR/LSCE/FAOSTAT'
      output_file_start="ForestRemain_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : FL-FL bottom-up net CO$_2$ emissions"
      lplot_areas=True


      #if lshow_productiondata:
      #   productiondata_master['FLUXCOM_FL-FL']=False
      #endif

   elif graphname == "grassland_full":
      desired_simulations=[ \
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
#      datasource='UNFCCC/MPI-BGC/UAbdn/LSCE'
      output_file_start="GrasslandRemain_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : GL-GL bottom-up net CO$_2$ emissions"

      # Change some things from the above
      displayname_master['UNFCCC_GRASS']='UNFCCC_GL-GL area'
      displayname_master['LUH2v2_GRASS']='LUH2v2-ESACCI_GL-GL area (used in ORCHIDEE)'
      lplot_areas=True

      displayname_master['ECOSSE_GL-GL']='ECOSSE GL-GL RH'

      #if lshow_productiondata:
      #   productiondata_master['ECOSSE_GL-GL']=False
      #endif
      desired_legend=[\
                       "UNFCCC_GL-GL","UNFCCC_GL-GL uncertainty",\
                       displayname_master['ORCHIDEE_GL-GL'], \
                       #displayname_master['ORCHIDEE_RH'], \
                       displayname_master['ECOSSE_GL-GL'], \
                      # 'FLUXCOM_GL-GL_ANN', \
                      # 'FLUXCOM_GL-GL_RF', \
                       displayname_master['LUH2v2_GRASS'], \
                       displayname_master['UNFCCC_GRASS'], \
                       ]


   elif graphname == "epic":
      desired_simulations=[ \
                            'ORCHIDEE_CL-CL', \
                            'EPIC', \
                            'EPIC_RH', \
                            'EPIC_clch', \
                            'EPIC_fHarvest', \
                            'EPIC_npp', \
                         ]   


      output_file_start="EPICComparison_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CL-CL CO$_2$ emissions"

   elif graphname == "crops_full":
      desired_simulations=[ \
                            'ORCHIDEE_CL-CL', \
                           # 'ORCHIDEE_RH', \
                            'ECOSSE_CL-CL', \
                       #     'ECOSSE_CL-CL_us', \
                            'UNFCCC_CL-CL', \
                        #    'FLUXCOM_CL-CL_ANN', \
                        #    'FLUXCOM_CL-CL_RF', \
                            'EPIC', \
                           # 'EPIC_RH', \
                            'LUH2v2_CROP', \
                            'UNFCCC_CROP', \
                         ]   

      displayname_master['UNFCCC_CROP']='UNFCCC_CL-CL area'
      displayname_master['LUH2v2_CROP']='LUH2v2-ESACCI_CL-CL area (used in ORCHIDEE)'

      desired_legend=[\
                       "UNFCCC_CL-CL","UNFCCC_CL-CL uncertainty",\
                       'ORCHIDEE_CL-CL', \
                       'ECOSSE_CL-CL', \
                       'EPIC_CL-CL', \
                     #  'FLUXCOM_CL-CL_ANN', \
                     #  'FLUXCOM_CL-CL_RF', \
                     # 'ORCHIDEE_RH', \
                     # 'EPIC_RH', \
                      displayname_master['LUH2v2_CROP'], \
                       displayname_master['UNFCCC_CROP'], \
                       ]

#      datasource='UNFCCC/IIASA/MPI-BGC/UAbdn/LSCE'
      output_file_start="CroplandRemain_"
      output_file_end="_FCO2land_2019_v1.png" 
      titleending=r" : CL-CL bottom-up net CO$_2$ emissions"

      # Change some things from the above
      lplot_areas=True
                           
      displayname_master['EPIC']='EPIC_CL-CL'

 

      #if lshow_productiondata:
      #   productiondata_master['ECOSSE_CL-CL']=False
      #   productiondata_master['FLUXCOM_crops']=False
      #endif

   elif graphname == "biofuels":
      desired_simulations=[ \
                            'UNFCCC_biofuels', \
                            'TNO_biofuels', \
                         ]   
#      datasource='UNFCCC/TNO'
      output_file_start="biofuels_"
      output_file_end="_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from biofuel combustion"
      facec_master['UNFCCC_biofuels']='red'
      facec_master['TNO_biofuels']='blue'

   elif graphname == "eurocom_inversions":
      desired_simulations=[ \
                            'EUROCOM_ALL', \
                            'EUROCOM_Carboscope', \
                            'JENA-COMBINED', \
                            'EUROCOM_Flexinvert', \
                            'EUROCOM_Lumia', \
                            'EUROCOM_Chimere', \
                            'EUROCOM_CTE', \
                            'EUROCOM_EnKF', \
                            'EUROCOM_NAME', \
                         ]   
      output_file_start="EUROCOMInversions_"
      output_file_end="_2019_v1.png" 
      titleending=r" : net natural CO$_2$ fluxes from EUROCOM inversions"

      lplot_errorbar_master['EUROCOM_ALL']=True

   elif graphname == "gcp_inversions":
      desired_simulations=[ \
                            'GCP_ALL', \
                            'GCP_JENA', \
                            'GCP_CTRACKER', \
                            'GCP_CAMS', \
                         ]   
      output_file_start="GCPInversions_"
      output_file_end="_2019_v1.png" 
      titleending=r" : net natural CO$_2$ fluxes from GCP inversions"

      displayname_master['GCP_ALL']="Mean of GCP inversions"
      displayname_err_master['GCP_ALL']="Min/Max of GCP inversions"

      lplot_errorbar_master['GCP_ALL']=True

   elif graphname == "gcp_inversions_corrected":
      desired_simulations=[ \
                            'GCP_ALL', \
                            'GCP_JENA', \
                            'GCP_CTRACKER', \
                            'GCP_CAMS', \
                            'ULB_lakes_rivers', \
                         ]   
      output_file_start="GCPInversionsCorrected_"
      output_file_end="_2019_v1.png" 
      titleending=r" : net natural CO$_2$ fluxes from GCP inversions"

      lcorrect_inversion_master["GCP_ALL"]=True
      lcorrect_inversion_master["GCP_JENA"]=True
      lcorrect_inversion_master["GCP_CTRACKER"]=True
      lcorrect_inversion_master["GCP_CAMS"]=True

      lplot_errorbar_master['GCP_ALL']=True

   elif graphname in ("inversions_combined","inversions_combinedbar"):

      desired_simulations=[ \
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
      #                      'ULB_lakes_rivers', \
                            'JENA-COMBINED', \
                            'EUROCOM_ALL', \
                            'GCP_ALL', \
                            'BLUE', \
                            'H&N', \
                         #   'FLUXCOM_rsonlyANN_os', \
                         #   'FLUXCOM_rsonlyRF_os', \
                            'ORCHIDEE-MICT', \
                            'ORCHIDEE', \
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
                            'TrendyV7', \
                          'TrendyV7_ORCHIDEE', \
      ]        

      output_file_end="_FCO2land_2019_v1.png" 

      if graphname == "inversions_combined":
         titleending=r" : Reconciliation of top-down vs. bottom-up net natural CO$_2$ fluxes"
         output_file_start="TopDownLULUCF_"
         # The legend is tricky.  You can use names not definied in the above
         # simulation list if they are defined later on.  This just gives their
         # order.  Names are controled by the displayname variable, and this must
         # match those names else an error is thrown.
         desired_legend=[ \
                          displayname_master['UNFCCC_LULUCF'], \
                          displayname_err_master['UNFCCC_LULUCF'], \
                          displayname_master['MS-NRT'], \
                          displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                          displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
                          displayname_master['JENA-COMBINED'], \
                          displayname_master['FAOSTAT_LULUCF'], \
                          displayname_master['BLUE'], \
                          displayname_master['H&N'], \
                          displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                          displayname_master['ORCHIDEE'], \
                          displayname_master['TrendyV7_ORCHIDEE'], \
                          displayname_master['ORCHIDEE-MICT'], \
                    #      'FLUXCOM_rsonlyANN_os', \
                    #      'FLUXCOM_rsonlyRF_os',
                       ]
      else:
         output_file_start="TopDownLULUCFbar_"
         titleending=r" : Reconciliation of top-down vs. bottom-up (aggregated) net natural CO$_2$ fluxes"

         desired_simulations.append("VERIFYBU")

         # These simulations will be combined together.
#         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE']
         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE']
         overwrite_operations["VERIFYBU"]="mean"
         displaylegend_master["VERIFYBU"]=False

         displayname_master["VERIFYBU"]="Mean of VERIFY BU simulation"
         displayname_err_master["VERIFYBU"]="Min/Max of VERIFY BU simulation"

         # The legend is tricky.  You can use names not definied in the above
         # simulation list if they are defined later on.  This just gives their
         # order.  Names are controled by the displayname variable, and this must
         # match those names else an error is thrown.
         desired_legend=[ \
                          displayname_master['UNFCCC_LULUCF'], \
                          displayname_err_master['UNFCCC_LULUCF'], \
                          displayname_master['MS-NRT'], \
                          displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                          displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
                          displayname_master['JENA-COMBINED'], \
                          displayname_master['TrendyV7'], displayname_err_master['TrendyV7'], \
                          displayname_master['FAOSTAT_LULUCF'], \
                          displayname_master['H&N'], \
                          displayname_master['VERIFYBU'], \
                          displayname_err_master['VERIFYBU'], \
                          displayname_master['ORCHIDEE'], \
                          displayname_master['TrendyV7_ORCHIDEE'], \
                          displayname_master['ORCHIDEE-MICT'], \
                       ]

         # These simulations will be combined together.
#         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os']
         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE']
         overwrite_operations["VERIFYBU"]="mean"

         # So I don't want to generally plot the components
         displaylegend_master['ORCHIDEE-MICT']=True
         displaylegend_master['ORCHIDEE']=True
         displaylegend_master['BLUE']=False
         displaylegend_master['FLUXCOM_rsonlyANN_os']=False
         displaylegend_master['FLUXCOM_rsonlyRF_os']=False

         displaylegend_master['TrendyV7_ORCHIDEE']=True

      #endif

      displaylegend_master['ORCHIDEE-MICT']=True
      displaylegend_master['ORCHIDEE']=True      
      displaylegend_master['TrendyV7_ORCHIDEE']=True

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

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
      lplot_errorbar_master["JENA-COMBINED"]=True
      lwhiskerbars_master["JENA-COMBINED"]=True

   elif graphname == "inversions_verify":
      desired_simulations=[ \
                            'JENA-COMBINED', \
                            'JENA-REG-100km', \
                            'JENA-REG-200km', \
                            'JENA-REG-Core100km', \
                            'JENA-REG-Valid100km', \
                         ]   
#      datasource='JENA'
      output_file_start="inversions_verify_"
      output_file_end="_2019_v1.png" 
      titleending=r" : CO$_2$ inversion from CarboScopeReg simulations in VERIFY"

   elif graphname in ( "inversions_test", "inversions_full"):

      if graphname == "inversions_test":
         titleending=r" : UNFCCC vs. net natural CO$_2$ fluxes - TEST (not complete dataset)"
         desired_simulations=[ \
                               'UNFCCC_LULUCF', \
                               'MS-NRT', \
                               'ULB_lakes_rivers', \
                               'JENA-REG-100km', \
                               'JENA-REG-200km', \
                               'EUROCOM_Carboscope', \
                               'EUROCOM_Flexinvert', \
                               'GCP_JENA', \
                               'GCP_CAMS', \
                            ]   
         output_file_start="inversions_test_"
      else:
         titleending=r" : UNFCCC vs. net natural CO$_2$ fluxes"
         desired_simulations=[ \
                               'UNFCCC_LULUCF', \
                               'MS-NRT', \
                               'ULB_lakes_rivers', \
                               'JENA-COMBINED', \
                               'EUROCOM_ALL', \
                               'GCP_ALL', \
                           ]   
         output_file_start="TopDownAndInventories_"
      #endif

      desired_legend=[ \
                       'UNFCCC LULUCF NGHGI 2019', \
                       'UNFCCC LULUCF NGHGI 2019 uncertainty', \
                       'MS-NRT', \
                       'ULB_lakes_rivers', \
                       displayname_master['JENA-COMBINED'], \
                       displayname_master['EUROCOM_ALL'],displayname_err_master['EUROCOM_ALL'],\
                       displayname_master['GCP_ALL'], displayname_err_master['GCP_ALL'], \
      ]

#      datasource='UNFCCC/GCP/EUROCOM/MPI-Jena/ULB'
      output_file_end="_FCO2land_2019_v2.png" 
      edgec_master['MS-NRT']=facec_master['MS-NRT']

      # A couple of these plots will be displayed as bars instead of symbols
      lplot_errorbar_master["EUROCOM_ALL"]=True
      lplot_errorbar_master["GCP_ALL"]=True
      lplot_errorbar_master["JENA-COMBINED"]=True
      lwhiskerbars_master["JENA-COMBINED"]=True

      # And to correct some of the plots.
      lcorrect_inversion_master["GCP_ALL"]=True
      lcorrect_inversion_master["JENA-COMBINED"]=True
      lcorrect_inversion_master["EUROCOM_ALL"]=True

   else:
      print("I do not understand which simulation this is:")
      print(graphname)
      sys.exit(1)
   #endif

   # Run some simple checks to make sure we don't crash later.
   for simname in files_master.keys():
      if not mpl.colors.is_color_like(edgec_master[simname]):
         print("Do not recognize edge color {} for simulation {}.".format(edgec_master[simname],simname))
         sys.exit(1)
      #endif
      if not mpl.colors.is_color_like(facec_master[simname]):
         print("Do not recognize face color {} for simulation {}.".format(facec_master[simname],simname))
         sys.exit(1)
      #endif
      if not mpl.colors.is_color_like(uncert_color_master[simname]):
         print("Do not recognize uncert color {} for simulation {}.".format(uncert_color_master[simname],simname))
         sys.exit(1)
      #endif
   #endif


#   return linclude_inventories,desired_inventories,desired_others,desired_verify,datasource,output_file_start,output_file_end
   return desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displayname_err_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,overwrite_coeffs,overwrite_operations,desired_legend,flipdatasign_master,lcorrect_inversion_master,lplot_errorbar_master,lwhiskerbars_master
#enddef
##########################################################################

########################################################Define functions
def find_date(since19000101):
   start = date(1900,1,1)
   delta = timedelta(since19000101)
   offset = start + delta
   year=offset.year
   month=offset.month
   return year,month

def get_cumulated_array(data, **kwargs):
         cum = data.clip(**kwargs)
         cum = np.cumsum(cum, axis=0)
         d = np.zeros(np.shape(data))
         d[1:] = cum[:-1]
         return d  

def readfile(filename,variablename,ndesiredyears,lconvert_units,starting_year,ending_year):
   # The goal of this routine is to read in a slice from starting_year
   # until ending_ear.
   # The time axes for all these files starts as days from 1900-01-01,
   # the axis itself might start at a different year (1901, 1970).
   # We need to find the indices corresponding to the year starting_year.
   # The 79 here is the number of countries and regions we have in the
   # CountryTot.nc files, so if that changes, this must change.  By hardcoding
   # it here, this serves as a check that we are using the files we think
   # we are using.
   FCO2=np.zeros((ndesiredyears,12,79))*np.nan
   print("************************************************************")
   print("Reading in file: ",filename)
   print("************************************************************")
   ncfile=nc.Dataset(filename)
   FCO2_file=ncfile.variables[variablename][:]  #kg C yr-1
   
   # we only need to convert units if we are not dealing with uncertainties,
   # since uncertainties are given as a fraction
   if lconvert_units:
      if ncfile.variables[variablename].units == "kg C yr-1":
         print("Converting units from {0} to Tg C yr-1".format(ncfile.variables[variablename].units))
         FCO2_TOT=FCO2_file/1e+9   #kg CO2/yr -->  Tg C/ year
      else:
         print("Not changing units from file: ",ncfile.variables[variablename].units)
         FCO2_TOT=FCO2_file*1.0
         print("Shape of input array: ",FCO2_TOT.shape)
         print("Shape of input array: ",FCO2_TOT.mask)
      #endif
   else:
      print("Not changing units from file: ",ncfile.variables[variablename].units)
      FCO2_TOT=FCO2_file*1.0
   #endif
   timeperiod=ncfile.variables['time'][:]  ##days since 1900-01-01, middle of each month
   startday=np.float(timeperiod[0]);endday=np.float(timeperiod[-1])
   startyear,startmonth=find_date(startday)  ## to convert to date 
   endyear,endmonth=find_date(endday)
   print("Timeseries starts at: {0}/{1}".format(startmonth,startyear))
   print("Timeseries starts at: {0}/{1}".format(endmonth,endyear))
   
   # This is something I added to distinguish more clearly between the two sets of dates we have.
   desired_startdate=date(starting_year,1,15)-date(1900,1,1)
   desired_enddate=date(ending_year,12,15)-date(1900,1,1)
   data_startdate=date(startyear,startmonth,15)-date(1900,1,1)
   data_enddate=date(endyear,endmonth,15)-date(1900,1,1)

   # this is a slow way to do it, but it works.
   mm=1
   yy=starting_year
   for iyear in range(ndesiredyears):
      for imonth in range(12):
         # does a member of our data exist in this month?
         firstdaymonth=date(yy,mm,1)-date(1900,1,1)
         if mm in (1,3,5,7,8,10,12):
            lastdaymonth=date(yy,mm,31)-date(1900,1,1)
         elif mm in (4,6,9,11):
            lastdaymonth=date(yy,mm,30)-date(1900,1,1)
         else:
            if isleap(yy):
               lastdaymonth=date(yy,mm,29)-date(1900,1,1)
            else:
               lastdaymonth=date(yy,mm,28)-date(1900,1,1)
            #endif
         #endif

         for jtime,jval in enumerate(ncfile.variables['time'][:]):
            if jval >= firstdaymonth.days and jval <= lastdaymonth.days:
               FCO2[iyear,imonth,:]=FCO2_TOT[jtime,:]
            #endif
         mm=mm+1
         if mm > 12:
            mm=1
            yy=yy+1
         #endif
      #endfor
   #endfor

   return FCO2


   #################################

   # Create an axis that covers both of them completely.  Copy all of the data onto that axis.  Then take the chunk I want.
   lowerbound=min(desired_startdate.days,data_startdate.days)
   upperbound=max(desired_enddate.days,data_enddate.days)


   # There are four possible cases for the data we are looking at vs. the time period we want.
   # 1) The period that we want is completely covered by the data.  
   # 2) The starting point of the data falls in the period we want. 
   # 3) The ending point of the data falls in the period we want.  
   # 4) Both fall in the period we want.  

  
   # The period we want is completely covered by the data we have
   if desired_startdate.days > data_startdate.days and desired_enddate.days < data_enddate.days:
      istart=0
      iend=ndesiredyears*12-1

      # Loop over our data to find indend and indstart
      for itime,ival in enumerate(ncfile.variables['time'][:]):
         if abs(ival-desired_startdate.days) < 5:
            # Here is the index we start from
            print("Found starting index! ",itime,ival,desired_startdate.days)
            indstart=itime
         #endif
         if abs(ival-desired_enddate.days) < 5:
            # Here is the index we start from
            print("Found ending index! ",itime,ival,desired_enddate.days)
            indend=itime
         #endif

      #endfor

      # the data is completely inside the data that we want
   elif data_startdate.days > desired_startdate.days and data_enddate.days < desired_enddate.days:
      # here, indstart and indend cover our full data range, but we need to adapt istart and iend
      indstart=0
      iendend=len(ncfile.variables['time'][:])

      # loop over the desired timelength to find istart and iend
      loopdate = desired_startdate.days
      yy=desired_startdate.year
      mm=desired_startdate.month
      iindex=0
      while yy <= desired_enddate.year and mm <= desired_enddate.year:
         if yy == data_enddate.year and mm == data_enddate.month:
            iend=iindex
         if yy == data_startdate.year and mm == data_startdate.month:
            istart=iindex
         iindex=iindex+1
         mm=mm+1
         if mm > 12:
            yy=yy+1
            mm=1
         #endif
      #endwhile

   else:
      print("Need to write!")
      print(desired_startdate.year,desired_startdate.month)
      print(desired_enddate.year,desired_enddate.month)
      print(data_startdate.year,data_startdate.month)
      print(data_enddate.year,data_enddate.month)
      sys.exit(1)
   #endif


   FCO2[istart:iend,:]=FCO2_TOT[indstart:indend,:]  # extract the slice we are interested in
   return FCO2
#enddef
#####################################################################


#####################################################################
# This subroutine aims to select the countries/regions that you wish to plot
# from the whole list of data available after reading in from the files
# I read in the uncertainties and the real data at the same time.
# If there is no min/max or error values, no worries.
# This is a bit tricky.  We can only propogate error if we have a symmetric distribution, which
# we may not have for min/max values.  So I calculate min/max values after this routine.
def group_input(inputvar,inputerr,inputmin,inputmax,desired_plots,luncert,ndesiredyears,nplots,all_regions_countries,desired_simulation):
   
   # Notice that the inputvar will be the size of the number of regions
   # in the .nc file, while outputvar will be the size of a number
   # of plots.  Our job here is to make the two correspond.
   outputvar=np.zeros((ndesiredyears,nplots))*np.nan
   outputerr=np.zeros((ndesiredyears,nplots))*np.nan
   outputmin=np.zeros((ndesiredyears,nplots))*np.nan
   outputmax=np.zeros((ndesiredyears,nplots))*np.nan

   for igroup in range(nplots):
      indices=[]
      if desired_plots[igroup] in all_regions_countries:
         #outputvar[:,igroup]=inputvar[:,all_regions_countries.index(desired_plots[igroup])]
         indices.append(all_regions_countries.index(desired_plots[igroup]))
      elif desired_plots[igroup] == "EU-28":
         #outputvar[:,igroup]=inputvar[:,E28]
         indices.append(all_regions_countries.index('E28'))
      elif desired_plots[igroup] == "EAE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # European Russia, Estonia, Latvia, Lithuania, Belarus, Poland, Ukraine
         # Ignore European Russia, since we just have the totals for Russia
         indices.append(all_regions_countries.index('EST'))
         indices.append(all_regions_countries.index('LVA'))
         indices.append(all_regions_countries.index('LTU'))
         indices.append(all_regions_countries.index('BLR'))
         indices.append(all_regions_countries.index('POL'))
         indices.append(all_regions_countries.index('UKR'))
      elif desired_plots[igroup] == "WEE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # Belgium, France, Netherlands, Germany, Switzerland, UK, Spain, Portugal
         indices.append(all_regions_countries.index('BEL'))
         indices.append(all_regions_countries.index('FRA'))
         indices.append(all_regions_countries.index('NLD'))
         indices.append(all_regions_countries.index('DEU'))
         indices.append(all_regions_countries.index('CHE'))
         indices.append(all_regions_countries.index('GBR'))
         indices.append(all_regions_countries.index('ESP'))
         indices.append(all_regions_countries.index('PRT'))
         #################################################
         # note that most of the 3-letter codes below should be obsolete, now in the 
         # NetCDF file
         #################################################
      elif desired_plots[igroup] == "CSK":
         # This is from Roxana
         # Former Czechoslovakia (CSK)
         # Czechia (CZE), Slovakia (SVK)
         indices.append(all_regions_countries.index('CZE'))
         indices.append(all_regions_countries.index('SVK'))
      elif desired_plots[igroup] == "CHL":
         # This is from Roxana
         # Switzerland + Liechtenstein (CHL)
         # Switzerland (CHE), Liechtenstein (LIE)
         indices.append(all_regions_countries.index('CHE'))
         indices.append(all_regions_countries.index('LIE'))
      elif desired_plots[igroup] == "BLT":
         # This is from Roxana
         # Baltic countries (BLT)
         # Estonia (EST), Lithuania (LTU), Latvia (LVA)
         indices.append(all_regions_countries.index('EST'))
         indices.append(all_regions_countries.index('LTU'))
         indices.append(all_regions_countries.index('LVA'))
      elif desired_plots[igroup] == "NAC":
         # This is from Roxana
         # North Adriatic Countries (NAC)
         # Slovenia (SVN), Croatia (HRV)
         indices.append(all_regions_countries.index('SVN'))
         indices.append(all_regions_countries.index('HRV'))
      elif desired_plots[igroup] == "DSF":
         # This is from Roxana
         # Denmark, Sweden, Finland (DSF)
         # Sweden (SWE), Denmark (DNK), Finland (FIN)
         indices.append(all_regions_countries.index('SWE'))
         indices.append(all_regions_countries.index('DNK'))
         indices.append(all_regions_countries.index('FIN'))
      elif desired_plots[igroup] == "FMA":
         # This is from Roxana
         # France, Monaco, Andorra (FMA)
         # France (FRA), Monaco (MCO), Andorra (AND)
         # Note that Monaco is already combined with France in our
         # mask.
         indices.append(all_regions_countries.index('FRA'))
         indices.append(all_regions_countries.index('AND'))
      elif desired_plots[igroup] == "UMB":
         # This is from Roxana
         # Ukraine, Rep. of Moldova, Belarus (UMB)
         # Ukraine (UKR), Moldova, Republic of (MDA), Belarus (BLR)
         indices.append(all_regions_countries.index('UKR'))
         indices.append(all_regions_countries.index('MDA'))
         indices.append(all_regions_countries.index('BLR'))
      elif desired_plots[igroup] == "SEA":
         # This is from Roxana
         # South-Eastern Europe alternate (SEA)
         # Serbia (SRB), Montenegro (MNE),Kosovo (RKS), Bosnia and Herzegovina (BIH), Albania (ALB), Macedonia, the former Yugoslav (MKD)
         # Notice that Kosovo is included in Serbia and Montenegro in our mask.
         indices.append(all_regions_countries.index('SRB'))
         indices.append(all_regions_countries.index('MNE'))
         indices.append(all_regions_countries.index('BIH'))
         indices.append(all_regions_countries.index('ALB'))
         indices.append(all_regions_countries.index('MKD'))
      elif desired_plots[igroup] == "IBE2":
         # This is a test to compare against the IBE from the file, just to
         # see if the results are the same.
         indices.append(all_regions_countries.index('ESP'))
         indices.append(all_regions_countries.index('PRT'))
      else:
         print("Do not know what this country group is!")
         print(desired_plots[igroup])
         sys.exit(1)
      #endif
      for iindex in range(len(indices)):
         value=indices[iindex]
         # This is necessary because I initialize the arrays with nan
         if iindex == 0:
            outputvar[:,igroup]=inputvar[:,value]
            outputmin[:,igroup]=inputmin[:,value]
            outputmax[:,igroup]=inputmax[:,value]
            if luncert:
               outputerr[:,igroup]=(inputerr[:,value]*inputvar[:,value])**2
            #endif
         else:
            outputvar[:,igroup]=outputvar[:,igroup]+inputvar[:,value]
            outputmin[:,igroup]=outputmin[:,igroup]+inputmin[:,value]
            outputmax[:,igroup]=outputmax[:,igroup]+inputmax[:,value]
            if luncert:
               outputerr[:,igroup]=outputerr[:,igroup]+(inputerr[:,value]*inputvar[:,value])**2
            #endif
         #endif
      #endfor

      if luncert:
         # now convert uncertainty back to a percentage
         for iyear,rval in enumerate(outputerr[:,igroup]):
            if outputvar[iyear,igroup] != 0.0 and not np.isnan(outputvar[iyear,igroup]):
               outputerr[iyear,igroup]=math.sqrt(outputerr[iyear,igroup])/abs(outputvar[iyear,igroup])
            #endif
         #endfor
      #endif

      # I am concerned about leakage with some plots.  For example, EFISCEN-Space only has data
      # for three countries.  If our maps are not perfectly in line, a couple pixels make leak
      # over to other countries.  This should be enforced in the CountryTot graphs, not here.
      if desired_simulation == "EFISCEN-Space" and desired_plots[igroup] not in ("FRA","IRL","NLD"):
         outputvar[:,igroup]=np.nan
         outputerr[:,igroup]=np.nan
         outputmin[:,igroup]=np.nan
         outputmax[:,igroup]=np.nan
      #endif

   #endfor

   return outputvar,outputerr,outputmin,outputmax
#enddef
####################################################################




#####################################################################
# This subroutine combines a specificed list of existing simulations
# and puts the results into a specific simulation.
# I use this because sometimes I need to combine variables from
# a NetCDF file into a single simulation result.
# It overwrites the existing simulation_data and returns it.
def combine_simulations(overwrite_simulations,overwrite_coeffs,overwrite_operations,simulation_data,simulation_min,simulation_max,simulation_err,desired_simulations,graphname):

   if not overwrite_simulations:
      print("No simulations need to be combined.")
      return simulation_data,simulation_min,simulation_max,simulation_err
   #endif

# In the case of the UNFCCC LUC, this is a sum of six different timeseries.
# Those are all in different files, so I combine them here, propogate the
# error, and then only print out this in the actual plot.
   #temp_desired_sims=('UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert')

   for osim,temp_sims in overwrite_simulations.items():

      ntempsims=len(temp_sims)
      ndesiredyears=simulation_data.shape[1]
      nplots=simulation_data.shape[2]

      ioverwrite=desired_simulations.index(osim)
      if ioverwrite < 0:
         print("******************************************************************")
         print("For the graph {0}, you need to be sure to include the simulation {1}!".format(graphname,osim))
         print("******************************************************************")
         sys.exit(1)
      #endif
      print("Combining simulations: ",temp_sims)
      print("with operation {0}.".format(overwrite_operations[osim]))

      simulation_data[ioverwrite,:,:]=0.0
      simulation_err[ioverwrite,:,:]=0.0

      temp_data=np.zeros((ntempsims,ndesiredyears,nplots))*np.nan

      if overwrite_operations[osim] == "sum":
         coeffs=overwrite_coeffs[osim]

         for isim,csim in enumerate(temp_sims):
            simulation_data[ioverwrite,:,:]=simulation_data[ioverwrite,:,:]+coeffs[isim]*simulation_data[desired_simulations.index(csim),:,:]
            # Do a simple propogation of error, as well
            simulation_err[ioverwrite,:,:]=simulation_err[ioverwrite,:,:]+(simulation_err[desired_simulations.index(csim),:,:]*coeffs[isim]*simulation_data[desired_simulations.index(csim),:,:])**2
         #endfor
            
         # don't like doing this in a loop, but the sqrt function doesn't seem to work on arrays?
         for iplot in range(len(simulation_err[0,0,:])):
            for itime in range(len(simulation_err[0,:,0])):
               simulation_err[ioverwrite,itime,iplot]=math.sqrt(simulation_err[ioverwrite,itime,iplot])/simulation_data[ioverwrite,itime,iplot]
            #endfor
         #endfor
   
      elif overwrite_operations[osim] == "mean":
         for isim,csim in enumerate(temp_sims):
            temp_data[isim,:,:]=simulation_data[desired_simulations.index(csim),:,:]
         #endfor

         # If I ignore nan here, then I get a value where not all simulations are present.
         # I only want values when all simulations are present.
         simulation_data[ioverwrite,:,:]=temp_data.mean(axis=0)
         simulation_min[ioverwrite,:,:]=np.min(temp_data,axis=0)
         simulation_max[ioverwrite,:,:]=np.max(temp_data,axis=0)

      else:
         print("Do not recognize operation for {}!".format(osim))
         print(overwrite_operations[ioverwrite])
         sys.exit(1)
      #endif

            

         
      # make any zero elements nan so they don't plot.  Hopefully this doesn't lead to undesired
      # results.
      for iplot in range(len(simulation_err[0,0,:])):
         for itime in range(len(simulation_err[0,:,0])):
            if simulation_data[ioverwrite,itime,iplot] == 0.0:
               simulation_data[ioverwrite,itime,iplot]= np.nan
            #endif
         #endfor
      #endfor

   #endfor
   
   return simulation_data,simulation_min,simulation_max,simulation_err
#enddef
####################################################################

#####################################################################
# Create a dictionary of areas of countries/regions in square meters,
# based on our country masks.  The first routine calculates them,
# and prints out the values in a nice Python list so that I can
# copy them to the second routine, which just returns the list.
# Calculating the values is too expensive to do every time.
#
# The areas that it gives are close to what Google gives (within 1% for Estonia, larger difference for
# France but France in Google likely has overseas territories).
def calculate_country_areas():

#   src = nc.Dataset("/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/eurocomCountryMaskEEZ_304x560.nc","r")
   src = nc.Dataset("/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/extended_eurocomCountryMaskEEZ_304x560_35.06N72.94N_24.94W44.94E.nc","r")
   latcoord="lat"
   loncoord="lon"
   names = src.variables["country_name"][:]
   names = ["".join([letter.decode('utf-8') for letter in item if letter is not np.ma.masked]) for item in names]
   lat = src.variables[latcoord][:]
   lon = src.variables[loncoord][:]
   lons, lats = np.meshgrid(lon, lat)

   for iname,cname in enumerate(names):

      # find the area of this country/region

      # The mask we have is for the extended economic zones, which includes territory in the oceans.
      # Filter that out here.
      filtered_mask = maskoceans(lons, lats, src.variables["country_mask"][iname,:,:], inlands = False, resolution = "f", grid = 1.25)
      #filtered_mask = src.variables["country_mask"][iname,:,:]
   
      area_2D=filtered_mask*src.variables["area"][:,:]
      area=np.nansum(area_2D)
      filtered_mask=filtered_mask[:,:].filled(fill_value=0.0)
      #filtered_mask[ filtered_mask > 0.0 ]=1.0
      #print(np.nansum(filtered_mask[:,:]))

      print("   country_areas[\"{0}\"]={1}".format(cname,area))
   #endfor

   src.close()

   return
#enddef
   

def get_country_areas():

   # This is taken from our map with 79 regions.


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
####################################################################

#######################################
# This loads some fake data so that we can work more quickly on 
# the graphs.  I took this from results for EU-27+UK.
def read_fake_data(ndesiredyears,simname):
   outputvar=np.zeros((ndesiredyears))*np.nan
   outputerr=np.zeros((ndesiredyears))*np.nan
   outputmin=np.zeros((ndesiredyears))*np.nan
   outputmax=np.zeros((ndesiredyears))*np.nan

   base_name="fake_data"
   dfdata=pd.read_csv(filepath_or_buffer=base_name+".csv",index_col=0,header=0)

   #print("column names ",dfdata.columns)

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,simname]
      outputvar=values.tolist()
   except:
      print("Could not find data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_MIN".format(simname)]
      outputmin=values.tolist()
   except:
      print("Could not find minimum data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_MAX".format(simname)]
      outputmax=values.tolist()
   except:
      print("Could not find maximum data for {}.".format(simname))
   #endif

   # check to see if the following timeseries exist.
   try:
      values=dfdata.loc[:,"{}_ERR".format(simname)]
      outputerr=values.tolist()
   except:
      print("Could not find error data for {}.".format(simname))
   #endif

   return outputvar,outputerr,outputmin,outputmax
#enddef

#####
def print_test_data(ltest_data,simulation_data,simulation_err,simulation_min,simulation_max,itest_sim,itest_plot,desired_simulations,desired_plots,checkpoint_string):

   if ltest_data:
      print("**************************************************")
      print(checkpoint_string)
      print("Simulation: ",desired_simulations[itest_sim])
      print("Plot: ",desired_plots[itest_plot])
      print("simulation data  ",simulation_data[itest_sim,:,itest_plot])
      print("simulation err ",simulation_err[itest_sim,:,itest_plot])
      print("simulation min ",simulation_err[itest_sim,:,itest_plot])
      print("simulation max ",simulation_err[itest_sim,:,itest_plot])
      print("**************************************************")
   #endif
#####


#### Not sure this is currently working
def create_sectorplot_full():
   temp_desired_sims=("EPIC","ECOSSE_GL-GL","EFISCEN")
   temp_data=np.zeros((len(temp_desired_sims),ndesiredyears))
   for isim,csim in enumerate(temp_desired_sims):
      temp_data[isim,:]=simulation_data[desired_simulations.index(csim),:,iplot]
   #endfor
      
   # plot the whole sum of these three runs
   p1=ax1.scatter(allyears,np.nansum(temp_data,axis=0),marker="P",label="EPIC/ECOSSE/EFISCEN",facecolors="blue", edgecolors="blue",s=60,alpha=production_alpha)
   legend_axes.append(p1)
   legend_titles.append("EPIC/ECOSSE/EFISCEN")

   # This is where things get really clever.  I want to show stacked bars of the three component fluxes.  However, there
   # are sometimes positive, and sometimes negative values, which means I cannot always use the same base of the bars.
   # I am adapting code I found on stackexchange

   # Take negative and positive data apart and cumulate
   cumulated_data = get_cumulated_array(temp_data, min=0)
   cumulated_data_neg = get_cumulated_array(temp_data, max=0)
         
   # Re-merge negative and positive data.
   row_mask = (temp_data<0)
   cumulated_data[row_mask] = cumulated_data_neg[row_mask]
   data_stack = cumulated_data

   temp_data[temp_data == 0.0]=np.nan

   barwidth=0.3
   for isim,csim in enumerate(temp_desired_sims):
      if productiondata[desired_simulations.index(csim)]:
         p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=production_alpha)
      else:
         p1=ax1.bar(allyears, temp_data[isim,:], bottom=data_stack[isim,:], color=facec[desired_simulations.index(csim)],width=barwidth,alpha=nonproduction_alpha)
      #endif
      legend_axes.append(p1)
      legend_titles.append(csim)
   #endfor
