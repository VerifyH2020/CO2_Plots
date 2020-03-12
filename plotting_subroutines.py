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
                  'UNFCCC_totincLULUCF' : invdir + 'Tier1_CO2_TotEmisIncLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'UNFCCC_totexcLULUCF' : invdir + 'Tier1_CO2_TotEmisExcLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'UNFCCC_LULUCF' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  
                  'TrendyV7' : '/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/Tier3BUPB_CO2_LandFlux_AllTrendyMedianMinMax-S3_exeter_LAND_GL_1M_V1_20191020_McGrath_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_CABLE' : otherdir + 'Tier3BUPB_CO2_LandFlux_CABLE-POP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_CLASS' : otherdir + 'Tier3BUPB_CO2_LandFlux_CLASS-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_CLM5' : otherdir + 'Tier3BUPB_CO2_LandFlux_CLM5-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_DLEM' : otherdir + 'Tier3BUPB_CO2_LandFlux_DLEM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_ISAM' : otherdir + 'Tier3BUPB_CO2_LandFlux_ISAM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_JSBACH' : otherdir + 'Tier3BUPB_CO2_LandFlux_JSBACH-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_JULES' : otherdir + 'Tier3BUPB_CO2_LandFlux_JULES-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_LPJ' : otherdir + 'Tier3BUPB_CO2_LandFlux_LPJ-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_LPX' : otherdir + 'Tier3BUPB_CO2_LandFlux_LPX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_OCN' : otherdir + 'Tier3BUPB_CO2_LandFlux_OCN-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_ORCHIDEE-CNP' : otherdir + 'Tier3BUPB_CO2_LandFlux_ORCHIDEE-CNP-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_ORCHIDEE' : otherdir + 'Tier3BUPB_CO2_LandFlux_ORCHIDEE-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_SDGVM' : otherdir + 'Tier3BUPB_CO2_LandFlux_SDGVM-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'TrendyV7_SURFEX' : otherdir + 'Tier3BUPB_CO2_LandFlux_SURFEX-S3_exeter_LAND_GL_1M_V1_20191020_Sitch_Grid-mask11_CountryTot.nc', \
                  'ORCHIDEE' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'ORCHIDEE_RH' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'EPIC' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTot.nc', \
                  'EPIC_RH' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTot.nc', \
                  'JENA-COMBINED' : verifydir + 'Tier3TD_CO2_LandFlux_AllJENA_bgc-jena_LAND_GL_1M_V1_20200304_McGrath_WP3_CountryTot.nc', \
                  'JENA-REG-100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-200km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-200km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-Core100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Core100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-Valid100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Valid100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'BLUE' : '/home/dods/verify/OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTot.nc', \
                  'H&N' : '/home/dods/verify/OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTot.nc', \
                  'ORCHIDEE-MICT' : '/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_LandUseChange_ORCHIDEEMICT-SX_LSCE_LAND_EU_1M_V1_20190925_YUE_WP3_CountryTot.nc', \
                  'FAOSTAT_For' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_Crp' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_Grs' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  #'EDGARv4' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/EDGAR_TEST.nc', \
                  # This is the same as the VERIFY inverions.  And Cristoph does not like this version that he used.  So we will replace it with the mean of the VERIFY inverions.
                  'EUROCOM_Carboscope' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CarboScopeRegional_bgc-jena_LAND_EU_1M_V1_20191020_Gerbig_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Flexinvert' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_FLEXINVERT_nilu_LAND_EU_1M_V1_20191020_Thompson_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Lumia' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_LUMIA-ORC_nateko_LAND_EU_1M_V1_20191020_Monteil_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Chimere' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CHIMERE-ORC_lsce_LAND_EU_1M_V1_20191020_Broquet_Grid-eurocom_CountryTot.nc', \
                  'ECOSSE_CL-CL': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CropFluxes_ECOSSE-SX_UAbdn_CRP_EU_1M_V1_20200218_KUHNERT_WP3_CountryTot.nc",\
                  'ECOSSE_GL-GL': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_GrassFluxes_ECOSSE-SX_UAbdn_GRS_EU_1M_V1_20200218_KUHNERT_WP3_CountryTot.nc", \
                  'ECOSSE_CL-CL_us': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_swheat_co2_CountryTot.nc",\
                  'ECOSSE_GL-GL_us': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/EU28_gra_co2_CountryTot.nc", \
                  'EFISCEN-Space': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_treeNEP_EFISCEN-Space-SX_WENR_FOR_EU_1M_V1_20190716_SCHELHAAS_WP3_CountryTot.nc",\
                  'UNFCCC_FL-FL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_GL-GL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_CL-CL': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'ORCHIDEE_FL-FL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'EFISCEN' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTot.nc", \
                  'EFISCEN-unscaled' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTot.nc", \
                  'CBM' : "/home/dods/verify/OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTot.nc", \
                  'FLUXCOM_rsonlyRF_os' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_rsonlyANN_os' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_rsonlyRF_ns' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_rsonlyANN_ns' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_FL-FL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_FL-FL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_GL-GL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_GL-GL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_CL-CL_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_CL-CL_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'ORCHIDEE_GL-GL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'ORCHIDEE_CL-CL' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'TNO_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/TNO/Tier3BUDD_CO2_BiofuelEmissions_XXX-SX_TNO_XXX_EU_1M_V1_20191110_DERNIER_WPX_CountryTot.nc", \
                  'UNFCCC_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_Biofuels_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'ULB_lakes_rivers' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_RiverLakeEmissions_XXXX-SX_ULB_INLWAT_EU_1M_V1_20190911_LAUERWALD_WP3_CountryTot.nc", \
                  'UNFCCC_forest_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_grassland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_cropland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_wetland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_settlement_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_other_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_woodharvest' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WoodHarvest_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'GCP_JENA' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_JENA-s76-4-3-2019_bgc-jena_LAND_GL_1M_V1_20191020_Christian_WPX_CountryTot.nc', \
                  'GCP_CTRACKER' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2019_wur_LAND_GL_1M_V1_20191020_Wouter_WPX_CountryTot.nc', \
                  'GCP_CAMS' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CAMS-V18-2-2019_lsce_LAND_GL_1M_V1_20191020_Chevallier_WPX_CountryTot.nc', \
                  'LUH2v2_FOREST' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_2000_2018_CountryTot.nc', \
                  'UNFCCC_FOREST' : '/home/dods/verify/OTHER_PROJECTS/NONFLUX/Tier1_XXXX_ForestArea_CRF2019-SX_UNFCCC_FOR_EU_1Y_V1_20200221_MCGRATH_WPX_CountryTot.nc', \
                  'MS-NRT' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_CountryTot.nc', \
                  # These will all get overwritten below
                  'UNFCCC_LUC' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'UNFCCC_LUCF' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'FAOSTAT_LULUCF' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_FL-FL' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'VERIFYBU' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycle_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \

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
                      'VERIFYBU' : 'VERIFY_BU', \
                      'ORCHIDEE_RH' : 'VERIFY_BU', \
                      'FLUXCOM_rsonlyANN_os' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyRF_os' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyANN_ns' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyRF_ns' :  'VERIFY_BU', \
                      'EPIC' :  'VERIFY_BU', \
                      'EPIC_RH' :  'VERIFY_BU', \
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
                    'LUH2v2_FOREST' : 'OTHER', \
                    'UNFCCC_FOREST' : 'OTHER', \
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
                      'ORCHIDEE_RH' : 'rh', \
                      'FLUXCOM_rsonlyANN_os' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyRF_os' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyANN_ns' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyRF_ns' :  'FCO2_NEP', \
                      'EPIC' :  'FCO2_NBP_CRO', \
                      'EPIC_RH' :  'rh', \
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
                      'ECOSSE_CL-CL': "FCO2_SOIL_CRO", \
                    'ECOSSE_GL-GL': "FCO2_SOIL_GRA", \
                      'ECOSSE_CL-CL_us': "FCO2_SOIL_CRO", \
                    'ECOSSE_GL-GL_us': "FCO2_SOIL_GRA", \
                    'EFISCEN-Space': "FCO2_NBP_FOR", \
                    'UNFCCC_FL-FL': "FCO2_NBP", \
                    'UNFCCC_GL-GL': "FCO2_NBP", \
                    'UNFCCC_CL-CL': "FCO2_NBP", \
                      'ORCHIDEE_FL-FL' : "FCO2_NBP_FOR", \
                      'EFISCEN' : "FCO2_NEE_FOR", \
                      'EFISCEN-unscaled' : "FCO2_NEE_FOR", \
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
                     'LUH2v2_FOREST' : 'FOREST_AREA', \
                     'UNFCCC_FOREST' : 'AREA', \
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
                       'ORCHIDEE_RH' : 'D', \
                       'FLUXCOM_rsonlyANN_os' :  's', \
                       'FLUXCOM_rsonlyRF_os' :  's', \
                       'FLUXCOM_rsonlyANN_ns' :  's', \
                       'FLUXCOM_rsonlyRF_ns' :  's', \
                       'EPIC' :  'o', \
                       'EPIC_RH' :  'o', \
                       'JENA-COMBINED' :  'P', \
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
                    'LUH2v2_FOREST' : 'o', \
                    'UNFCCC_FOREST' : 'o', \
                    'MS-NRT' : 'o', \
                    }
   facec_master={ \
                  'UNFCCC_totincLULUCF' :  'black', \
                  'UNFCCC_totexcLULUCF' :  'red', \
                  'UNFCCC_LULUCF' :  'green', \
                  'UNFCCC_LUC' :  'green', \
                  'UNFCCC_LUCF' :  'green', \
                  'TrendyV7' :  'none', \
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
                  'ORCHIDEE_RH' : 'red', \
                  'FLUXCOM_rsonlyANN_os' :  'green', \
                  'FLUXCOM_rsonlyRF_os' :  'yellowgreen', \
                  'FLUXCOM_rsonlyANN_ns' :  'green', \
                  'FLUXCOM_rsonlyRF_ns' :  'yellowgreen', \
                  'EPIC' :  'lightcoral', \
                  'EPIC_RH' :  'pink', \
                  'JENA-COMBINED' :  'blue', \
                  'JENA-REG-100km' :  'khaki', \
                  'JENA-REG-200km' :  'orange', \
                  'JENA-REG-Core100km' :  'darkorange', \
                  'JENA-REG-Valid100km' :  'gold', \
                  'BLUE' :  'gold', \
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
                     'GCP_JENA' : 'sandybrown', \
                    'GCP_CTRACKER' : 'sandybrown', \
                    'GCP_CAMS' : 'sandybrown', \
                     'UNFCCC_FOREST' : 'blue', \
                    'LUH2v2_FOREST' : 'orange', \
                'MS-NRT' : 'red', \
             }

   # set some default values, to save space.  Can be changed below.
   edgec_master={}
   uncert_color_master={}
   markersize_master={}
   productiondata_master={}
   displayname_master={}
   displaylegend_master={}
   flipdatasign_master={}
   for simname in files_master.keys():
      edgec_master[simname]="black"
      uncert_color_master[simname]=facec_master[simname]
      markersize_master[simname]=60
      productiondata_master[simname]=True
      displayname_master[simname]=simname
      displaylegend_master[simname]=True
      flipdatasign_master[simname]=False
   #endif

   # Some of the simulations have an inverted sign convention from what
   # we want (we want negative to be a terrestrial sink, positive to be
   # a source).  This flag flips the data on read-in.
   flipdatasign_master["ORCHIDEE"]=True
   flipdatasign_master["ORCHIDEE_GL-GL"]=True
   flipdatasign_master["ORCHIDEE_FL-FL"]=True
   flipdatasign_master["ORCHIDEE_CL-CL"]=True
   flipdatasign_master["CBM"]=True
   flipdatasign_master["EFISCEN"]=True
   flipdatasign_master["EFISCEN-Space"]=True
   flipdatasign_master["EFISCEN-unscaled"]=True
   flipdatasign_master["ORCHIDEE-MICT"]=True



   # We always want these to be the same
   edgec_master['MS-NRT']=facec_master['MS-NRT']

   # And better names for these two
   displayname_master['UNFCCC_LULUCF']='UNFCCC LULUCF NGHGI 2019'
   displayname_master['FAOSTAT_LULUCF']='FAOSTAT'

   lplot_areas=False
   
   # Now define the actual simulation configs
   if graphname == 'full_global':
#      datasource='TRENDY/EUROCOM/MPI-BGC/LSCE/IIASA/UMunich'
      output_file_start="CO2_BU_GLOBALTD_"
      output_file_end="_2019_v1.png"
   elif graphname == 'full_verify':
#      datasource='TRENDY/MPI-BGC/LSCE/IIASA/UMunich'
      output_file_start="CO2_BU_VERIFYTD_"
      output_file_end="_2019_v1.png" 
   elif graphname == "test":
      desired_simulations=[ \
                            # we read in data for LUC, but we replace it with the sectors below
                            'UNFCCC_LULUCF', \
                            'BLUE', \
                            'TrendyV7', \
        ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="TEST_"
      output_file_end="_FCO2Nat_2019_v1.png" 
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
                            'ORCHIDEE', \
        ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LUC_"
      output_file_end="_FCO2Nat_2019_v1.png" 
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

      # So I don't want to generally plot the components
      displaylegend_master['UNFCCC_forest_convert']=False
      displaylegend_master['UNFCCC_grassland_convert']=False
      displaylegend_master['UNFCCC_cropland_convert']=False
      displaylegend_master['UNFCCC_wetland_convert']=False
      displaylegend_master['UNFCCC_settlement_convert']=False
      displaylegend_master['UNFCCC_other_convert']=False

      uncert_color_master['UNFCCC_LUC']='darkseagreen'

      #if lshow_productiondata:
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
      output_file_end="_FCO2Nat_2019_v1.png" 
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

      uncert_color_master['UNFCCC_LUCF']='darkseagreen'

      #if lshow_productiondata:
      #   productiondata_master['ORCHIDEE-MICT']=False
      #endif

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
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=r" : CO$_2$ emissions from land use, land use change, and forestry"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False

      uncert_color_master['UNFCCC_LULUCF']='darkseagreen'

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
                      displayname_master["ORCHIDEE"],\
                      displayname_master["ORCHIDEE-MICT"],\
                      displayname_master["BLUE"],\
                      displayname_master["H&N"],\
                      "Median of TRENDY v7 DGVMs",\
                      "Min/Max of TRENDY v7 DGVMs",\
                      displayname_master["TrendyV7_ORCHIDEE"],\
     ]
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LULUCFTrendy_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=r" : Bottom-up land use change, land use change, and forestry CO$_2$ emissions"

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

      # Change some colors and symbols here

      uncert_color_master['UNFCCC_LULUCF']='darkseagreen'

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
      output_file_end="_FCO2Nat_2019_v1.png" 
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
      output_file_end="_FCO2Nat_2019_v1.png" 
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
      displayname_master['UNFCCC_woodharvest']='WH'

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
      output_file_end="_FCO2Nat_2019_v1.png" 
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
      output_file_end="_FCO2Nat_2019_v1.png" 
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
      output_file_end="_FCO2Nat_2019_v1.png" 
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
                         #   'EFISCEN-unscaled', \
#                            'EFISCEN-Space', \
                            'CBM', \
                            'UNFCCC_FL-FL', \
                            'FLUXCOM_FL-FL_ANN', \
                            'FLUXCOM_FL-FL_RF', \
                            'FAOSTAT_FL-FL', \
                            'LUH2v2_FOREST', \
                            'UNFCCC_FOREST', \
                         ]   

      displayname_master['UNFCCC_FOREST']='UNFCCC_FL-FL area'
      displayname_master['LUH2v2_FOREST']='LUH2v2-ESACCI_FL-FL area'

      desired_legend=[\
                       displayname_master['UNFCCC_FL-FL'],"UNFCCC_FL-FL uncertainty",\
                       displayname_master['FAOSTAT_FL-FL'], \
                       displayname_master['ORCHIDEE_FL-FL'], \
                       displayname_master['EFISCEN'], \
#                       'EFISCEN-Space', \
                       displayname_master['CBM'], \
                       displayname_master['FLUXCOM_FL-FL_ANN'], \
                       displayname_master['FLUXCOM_FL-FL_RF'], \
                       displayname_master['LUH2v2_FOREST'], \
                       displayname_master['UNFCCC_FOREST'], \
                      ]

#      datasource='UNFCCC/MPI-BGC/JRC/WEnR/LSCE/FAOSTAT'
      output_file_start="ForestRemain_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=r" : FL-FL bottom-up net CO$_2$ emissions"
      lplot_areas=True


      #if lshow_productiondata:
      #   productiondata_master['FLUXCOM_FL-FL']=False
      #endif

   elif graphname == "grassland_full":
      desired_simulations=[ \
                            'ORCHIDEE_GL-GL', \
                         #   'ORCHIDEE_RH', \
                            'ECOSSE_GL-GL', \
                          #  'ECOSSE_GL-GL_us', \
                            'UNFCCC_GL-GL', \
                            'FLUXCOM_GL-GL_ANN', \
                            'FLUXCOM_GL-GL_RF', \
                         ]   
#      datasource='UNFCCC/MPI-BGC/UAbdn/LSCE'
      output_file_start="GrasslandRemain_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=r" : GL-GL bottom-up net CO$_2$ emissions"

      # Change some things from the above


      #if lshow_productiondata:
      #   productiondata_master['ECOSSE_GL-GL']=False
      #endif
      uncert_color_master['UNFCCC_GL-GL']='brown'

      desired_legend=[\
                       "UNFCCC_GL-GL","UNFCCC_GL-GL uncertainty",\
                       'ORCHIDEE_GL-GL', \
                       'ECOSSE_GL-GL', \
                       'FLUXCOM_GL-GL_ANN', \
                       'FLUXCOM_GL-GL_RF', \
                       ]


   elif graphname == "crops_full":
      desired_simulations=[ \
                            'ORCHIDEE_CL-CL', \
                           # 'ORCHIDEE_RH', \
                            'ECOSSE_CL-CL', \
                       #     'ECOSSE_CL-CL_us', \
                            'UNFCCC_CL-CL', \
                            'FLUXCOM_CL-CL_ANN', \
                            'FLUXCOM_CL-CL_RF', \
                            'EPIC', \
                           # 'EPIC_RH', \
                         ]   
      desired_legend=[\
                       "UNFCCC_CL-CL","UNFCCC_CL-CL uncertainty",\
                       'ORCHIDEE_CL-CL', \
                       'ECOSSE_CL-CL', \
                       'EPIC_CL-CL', \
                       'FLUXCOM_CL-CL_ANN', \
                       'FLUXCOM_CL-CL_RF', \
                     # 'ORCHIDEE_RH', \
                     # 'EPIC_RH', \

                       ]

#      datasource='UNFCCC/IIASA/MPI-BGC/UAbdn/LSCE'
      output_file_start="CroplandRemain_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=r" : CL-CL bottom-up net CO$_2$ emissions"

      # Change some things from the above
                           
      uncert_color_master['UNFCCC_CL-CL']='gold'

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

   elif graphname in ("inversions_combined","inversions_combinedbar"):


      desired_simulations=[ \
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
                            'ULB_lakes_rivers', \
                            'JENA-REG-100km', \
                            'JENA-REG-200km', \
                            'JENA-REG-Core100km', \
                            'JENA-REG-Valid100km', \
                            'EUROCOM_Carboscope', \
                            'EUROCOM_Flexinvert', \
                            'EUROCOM_Lumia', \
                            'EUROCOM_Chimere', \
                            'GCP_JENA', \
                            'GCP_CTRACKER', \
                            'GCP_CAMS', \
                            'BLUE', \
                            'H&N', \
                            'FLUXCOM_rsonlyANN_os', \
                            'FLUXCOM_rsonlyRF_os', \
                            'ORCHIDEE-MICT', \
                            'ORCHIDEE', \
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
                            'TrendyV7', \
                          'TrendyV7_ORCHIDEE', \
      ]        

      output_file_end="_FCO2Nat_2019_v1.png" 

      if graphname == "inversions_combined":
         titleending=r" : Reconciliation of top-down vs bottom-up net CO$_2$ emissions"
         output_file_start="TopDownLULUCF_"
         # The legend is tricky.  You can use names not definied in the above
         # simulation list if they are defined later on.  This just gives their
         # order.  Names are controled by the displayname variable, and this must
         # match those names else an error is thrown.
         desired_legend=[ \
                          'UNFCCC LULUCF NGHGI 2019', \
                          'UNFCCC LULUCF NGHGI 2019 uncertainty', \
                          'MS-NRT', \
                          'FAOSTAT', \
                          'ULB_lakes_rivers', \
                          'Mean of CarboScopeReg (removing ULB_lakes_rivers)', \
                          'Mean of EUROCOM (removing ULB_lakes_rivers)',"Min/Max of EUROCOM",\
                          'Mean of GCP (removing ULB_lakes_rivers)',"Min/Max of GCP", \
                          'BLUE', \
                          'H&N', \
                          'Median of TRENDY v7 DGVMs', "Min/Max of TRENDY v7 DGVMs", \
                          'ORCHIDEE', \
                          'TrendyV7_ORCHIDEE', \
                          'ORCHIDEE-MICT', \
                          'FLUXCOM_rsonlyANN_os', \
                          'FLUXCOM_rsonlyRF_os',
                       ]
      else:
         output_file_start="TopDownLULUCFbar_"
         titleending=r" : Reconciliation of top-down vs bottom-up (aggregated) net CO$_2$ emissions"

         desired_simulations.append("VERIFYBU")

         # These simulations will be combined together.
         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os','BLUE']
         overwrite_operations["VERIFYBU"]="mean"
         displaylegend_master["VERIFYBU"]=False

         displayname_master["VERIFYBU"]="Mean of VERIFY BU simulation"

         # The legend is tricky.  You can use names not definied in the above
         # simulation list if they are defined later on.  This just gives their
         # order.  Names are controled by the displayname variable, and this must
         # match those names else an error is thrown.
         desired_legend=[ \
                          'UNFCCC LULUCF NGHGI 2019', \
                          'UNFCCC LULUCF NGHGI 2019 uncertainty', \
                          'MS-NRT', \
                          'FAOSTAT', \
                          'ULB_lakes_rivers', \
                          'Mean of CarboScopeReg (removing ULB_lakes_rivers)', \
                          'Mean of EUROCOM (removing ULB_lakes_rivers)',"Min/Max of EUROCOM",\
                          'Mean of GCP (removing ULB_lakes_rivers)',"Min/Max of GCP", \
                          'Median of TRENDY v7 DGVMs', "Min/Max of TRENDY v7 DGVMs", \
                          'H&N', \
                          displayname_master['VERIFYBU'], \
                          "Min/Max of VERIFY BU simulation", \
                       ]

         # These simulations will be combined together.
         overwrite_simulations["VERIFYBU"]=['ORCHIDEE-MICT','ORCHIDEE','BLUE','FLUXCOM_rsonlyANN_os','FLUXCOM_rsonlyRF_os']
         overwrite_operations["VERIFYBU"]="mean"

         # So I don't want to generally plot the components
         displaylegend_master['ORCHIDEE-MICT']=False
         displaylegend_master['ORCHIDEE']=False
         displaylegend_master['BLUE']=False
         displaylegend_master['FLUXCOM_rsonlyANN_os']=False
         displaylegend_master['FLUXCOM_rsonlyRF_os']=False

         displaylegend_master['TrendyV7_ORCHIDEE']=False

      #endif

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      overwrite_operations["FAOSTAT_LULUCF"]="sum"
      overwrite_coeffs["FAOSTAT_LULUCF"]=[1.0,1.0,1.0]

      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False

      # Change some colors and symbols here
      

      uncert_color_master['UNFCCC_LULUCF']='darkseagreen'

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
         titleending=r" : UNFCCC vs top-down net CO$_2$ emissions - TEST (not complete dataset)"
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
         titleending=r" : UNFCCC vs top-down net CO$_2$ emissions"
         desired_simulations=[ \
                               'UNFCCC_LULUCF', \
                               'MS-NRT', \
                               'ULB_lakes_rivers', \
                               'JENA-REG-100km', \
                               'JENA-REG-200km', \
                               'JENA-REG-Core100km', \
                               'JENA-REG-Valid100km', \
                               'EUROCOM_Carboscope', \
                               'EUROCOM_Flexinvert', \
                               'EUROCOM_Lumia', \
                               'EUROCOM_Chimere', \
                               'GCP_JENA', \
                               'GCP_CTRACKER', \
                               'GCP_CAMS', \
                           ]   
         output_file_start="TopDownAndInventories_"
      #endif

      desired_legend=[ \
                       'UNFCCC LULUCF NGHGI 2019', \
                       'UNFCCC LULUCF NGHGI 2019 uncertainty', \
                       'MS-NRT', \
                       'ULB_lakes_rivers', \
                       'Mean of CarboScopeReg (removing ULB_lakes_rivers)', \
                       'Mean of EUROCOM (removing ULB_lakes_rivers)',"Min/Max of EUROCOM",\
                       'Mean of GCP (removing ULB_lakes_rivers)',"Min/Max of GCP", \
      ]

#      datasource='UNFCCC/GCP/EUROCOM/MPI-Jena/ULB'
      output_file_end="_FCO2Nat_2019_v2.png" 
      edgec_master['MS-NRT']=facec_master['MS-NRT']
      
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
   return desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,overwrite_coeffs,overwrite_operations,desired_legend,flipdatasign_master
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

def readfile(filename,variablename,ndesiredyears,lconvert_units,starting_year):
   # The goal of this routine is to read in a slice from starting_year
   # until 2018.
   # The time axes for all these files starts as days from 1900-01-01,
   # the axis itself might start at a different year (1901, 1970).
   # We need to find the indices corresponding to the year starting_year.
   FCO2=np.zeros((ndesiredyears,12,64))
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
   desired_enddate=date(2018,12,15)-date(1900,1,1)
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
def group_input(inputvar,inputerr,inputmin,inputmax,desired_plots,luncert,ndesiredyears,numplot,countries65,desired_simulation):
   outputvar=np.zeros((ndesiredyears,numplot))*np.nan
   outputerr=np.zeros((ndesiredyears,numplot))*np.nan
   outputmin=np.zeros((ndesiredyears,numplot))*np.nan
   outputmax=np.zeros((ndesiredyears,numplot))*np.nan

   for igroup in range(numplot):
      indices=[]
      if desired_plots[igroup] in countries65:
         #outputvar[:,igroup]=inputvar[:,countries65.index(desired_plots[igroup])]
         indices.append(countries65.index(desired_plots[igroup]))
      elif desired_plots[igroup] == "EU-28":
         #outputvar[:,igroup]=inputvar[:,E28]
         indices.append(countries65.index('E28)'))
      elif desired_plots[igroup] == "EAE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # European Russia, Estonia, Latvia, Lithuania, Belarus, Poland, Ukraine
         # Ignore European Russia, since we just have the totals for Russia
          indices.append(countries65.index('EST'))
          indices.append(countries65.index('LVA'))
          indices.append(countries65.index('LTU'))
          indices.append(countries65.index('BLR'))
          indices.append(countries65.index('POL'))
          indices.append(countries65.index('UKR'))
      elif desired_plots[igroup] == "WEE2":
         # This is from Hui Yang, for the Eastern Europe taskforce
         # Belgium, France, Netherlands, Germany, Switzerland, UK, Spain, Portugal
         indices.append(countries65.index('BEL'))
         indices.append(countries65.index('FRA'))
         indices.append(countries65.index('NLD'))
         indices.append(countries65.index('DEU'))
         indices.append(countries65.index('CHE'))
         indices.append(countries65.index('GBR'))
         indices.append(countries65.index('ESP'))
         indices.append(countries65.index('PRT'))
      elif desired_plots[igroup] == "IBE2":
         # This is a test to compare against the IBE from the file, just to
         # see if the results are the same.
         indices.append(countries65.index('ESP'))
         indices.append(countries65.index('PRT'))
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
      numplot=simulation_data.shape[2]

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

      temp_data=np.zeros((ntempsims,ndesiredyears,numplot))*np.nan

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

   src = nc.Dataset("/home/dods/verify/VERIFY_INPUT/COUNTRY_MASKS/eurocomCountryMaskEEZ_304x560.nc","r")
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

      print("country_areas[\"{0}\"]={1}".format(cname,area))
   #endfor

   src.close()

   return
#enddef
   

def get_country_areas():

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
   country_areas["Greece"]=131507568640.0
   country_areas["Croatia"]=56145813504.0
   country_areas["Hungary"]=92676333568.0
   country_areas["Isle of Man"]=718484352.0
   country_areas["Ireland"]=69942263808.0
   country_areas["Iceland"]=8021662720.0
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
   country_areas["Russian Federation"]=571430600704.0
   country_areas["Svalbard and Jan Mayen"]=251208448.0
   country_areas["San Marino"]=59646068.0
   country_areas["Serbia"]=88679014400.0
   country_areas["Slovakia"]=48968114176.0
   country_areas["Slovenia"]=19864659968.0
   country_areas["Sweden"]=447214321664.0
   country_areas["Turkey"]=400744775680.0
   country_areas["Ukraine"]=472574918656.0
   country_areas["BENELUX"]=68883161088.0
   country_areas["United Kingdom + Ireland"]=315988049920.0
   country_areas["Spain + Portugal"]=585773481984.0
   country_areas["Western Europe"]=932417175552.0
   country_areas["Central Europe"]=1013188198400.0
   country_areas["Northern Europe"]=1327828828160.0
   country_areas["Southern Europe"]=886562684928.0
   country_areas["South-Eastern Europe"]=1201827872768.0
   country_areas["Eastern Europe"]=1250015051776.0
   country_areas["EU-15"]=3217714053120.0
   country_areas["EU-27"]=4298198482944.0
   country_areas["EU-28"]=4354344222720.0
   country_areas["all Europe"]=6611839483904.0
   country_areas["Europe"]=6621466984448.0

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

   # For the data itself
   dfdata=pd.read_csv(filepath_or_buffer=base_name+".csv",index_col=0,header=0)
   values=dfdata.loc[simname]
   outputvar=values.tolist()

   # For the data error
   dfdata=pd.read_csv(filepath_or_buffer=base_name+"_err.csv",index_col=0,header=0)
   values=dfdata.loc[simname]
   outputerr=values.tolist()

# For the data min
   dfdata=pd.read_csv(filepath_or_buffer=base_name+"_min.csv",index_col=0,header=0)
   values=dfdata.loc[simname]
   outputerr=values.tolist()

# For the data max
   dfdata=pd.read_csv(filepath_or_buffer=base_name+"_max.csv",index_col=0,header=0)
   values=dfdata.loc[simname]
   outputerr=values.tolist()

   return outputvar,outputerr,outputmin,outputmax
#enddef
