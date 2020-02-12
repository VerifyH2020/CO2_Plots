import numpy as np
from datetime import date, timedelta
from calendar import isleap
import math
import netCDF4 as nc
import sys

##########################################################################
def get_simulation_parameters(graphname,lshow_productiondata):

   # Here are some dictionaries the define parameters for each simulation.
   # These may be varied below for each individual plot, but this is a first try.

   titleending="NO TITLE ENDING CHOSEN"
   printfakewarning=True
   # Roxana proposes using this for all plots
   datasource='VERIFY Project'

   overwrite_simulations={}
   desired_legend=[]

   otherdir='/home/dods/verify/OTHER_PROJECTS/FCO2/TrendyLand-V7/'
   verifydir='/home/dods/verify/VERIFY_OUTPUT/FCO2/'
   invdir='/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/INVENTORIES/'
   files_master={ \
                  'UNFCCC_totincLULUCF' : invdir + 'Tier1_CO2_TotEmisIncLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'UNFCCC_totexcLULUCF' : invdir + 'Tier1_CO2_TotEmisExcLULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'UNFCCC_LULUCF' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
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
                  'EPIC' : verifydir + 'Tier3BUPB_CO2_CropFluxes_EPIC-S1_IIASA_CRP_EU_1M_V1_20190911_BALKOVIC_WP3_CountryTot.nc', \
                  'JENA-REG-100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-200km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-200km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-Core100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Core100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'JENA-REG-Valid100km' : verifydir + 'Tier3TD_CO2_LandFlux_JENA-REG-Valid100km_bgc-jena_LAND_GL_1M_V1_20191020_Gerbig_WP3_CountryTot.nc', \
                  'BLUE' : '/home/dods/verify/OTHER_PROJECTS/FCO2/BLUE/Tier3BUPB_CO2_LandFlux_BLUE-2019_bgc-jena_LAND_GL_1M_V1_20191020_Pongratz_WP3_CountryTot.nc', \
                  'H&N' : '/home/dods/verify/OTHER_PROJECTS/FCO2/HN/Tier3BUDD_CO2_LandUseChange_HN-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTot.nc', \
                  'ORCHIDEE-MICT' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/MICT_TEST.nc', \
                  # This dataset is a placeholder.  There are three variables
                  # in the file that must be summed for the full LULUCF emissions
                  # for FAOSTAT.
                  'FAOSTAT_LULUCF' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_F-F' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  # Ths sum of these three give FAOSTAT_LULUCF
                  'FAOSTAT_For' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_Crp' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'FAOSTAT_Grs' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/FAOSTAT/FAOSTAT_CO2_all_data.nc', \
                  'EDGARv4' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/EDGAR_TEST.nc', \
                  # This is the same as the VERIFY inverions.  And Cristoph does not like this version that he used.  So we will replace it with the mean of the VERIFY inverions.
                  'EUROCOM_Carboscope' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CarboScopeRegional_bgc-jena_LAND_EU_1M_V1_20191020_Gerbig_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Flexinvert' : '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_FLEXINVERT_nilu_LAND_EU_1M_V1_20191020_Thompson_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Lumia' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_LUMIA-ORC_nateko_LAND_EU_1M_V1_20191020_Monteil_Grid-eurocom_CountryTot.nc', \
                  'EUROCOM_Chimere' :  '/home/dods/verify/OTHER_PROJECTS/FCO2/EUROCOM/Tier3TD_CO2_LandFlux_CHIMERE-ORC_lsce_LAND_EU_1M_V1_20191020_Broquet_Grid-eurocom_CountryTot.nc', \
                  'ECOSSE_crops': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/ECOSSE_crop_TEST.nc", \
                  'ECOSSE_grass': "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/ECOSSE_grass_TEST.nc", \
                  'EFISCEN-Space': "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_treeNEP_EFISCEN-Space-SX_WENR_FOR_EU_1M_V1_20190716_SCHELHAAS_WP3_CountryTot.nc",\
                  'UNFCCC_F-F': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_grass': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_crops': "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandRemain_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'ORCHIDEE_F-F' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'EFISCEN' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_TreesLUH2v2_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTot.nc", \
                  'EFISCEN-unscaled' : "/home/dods/verify/OTHER_PROJECTS/FCO2/EFISCEN/Tier3BUDD_CO2_Trees_EFISCEN-SX_WENR_FOR_EU_1M_V1_20191212_SCHELHAAS_WPX_CountryTot.nc", \
                  'CBM' : "/home/dods/verify/OTHER_PROJECTS/FCO2/CBM/Tier3BUDD_CO2_NBP_CBM-SX_JRC_FOR_EU_1Y_V1_20191212_PETRESCU_WPX_CountryTot.nc", \
                  'FLUXCOM_rsonlyRF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_rsonlyANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_F-F_RF' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-RFmissLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'FLUXCOM_F-F_ANN' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_LandFlux_Fluxcom-ANNnoPFTLUH2v2_bgc-jena_LAND_GL_1M_V1_20191020_Jung_WP3_CountryTot.nc", \
                  'ORCHIDEE_grass' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'FLUXCOM_grass' : "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/FLUXCOM_grass_TEST.nc", \
                  'ORCHIDEE_crops' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUPB_CO2_CarbonCycleEcosystem_ORCHIDEE-S3_LSCE_LAND_EU_1M_V0_20190910_MCGRATH_WP3_CountryTot.nc", \
                  'FLUXCOM_crops' : "/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/TESTFILES/FLUXCOM_crops_TEST.nc", \
                  'TNO_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/TNO/Tier3BUDD_CO2_BiofuelEmissions_XXX-SX_TNO_XXX_EU_1M_V1_20191110_DERNIER_WPX_CountryTot.nc", \
                  'UNFCCC_biofuels' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_Biofuels_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'ULB_Inland_waters' : "/home/dods/verify/VERIFY_OUTPUT/FCO2/Tier3BUDD_CO2_RiverLakeEmissions_XXXX-SX_ULB_INLWAT_EU_1M_V1_20190911_LAUERWALD_WP3_CountryTot.nc", \
                  'UNFCCC_forest_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_ForestConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_grassland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_GrasslandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_cropland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_CroplandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_wetland_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_WetlandConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_settlement_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_SettlementConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  'UNFCCC_other_convert' : "/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/UNFCCC/Tier1_CO2_OtherConvert_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc", \
                  # this ends up being a dummy variable for the plots
                  'UNFCCC_LUC' : invdir + 'Tier1_CO2_LULUCF_Inventory-SX_UNFCCC_LAND_EU_1Y_V1_20191112_PETRESCU_WP1_CountryTot.nc', \
                  'GCP_JENA' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_JENA-s76-4-3-2019_bgc-jena_LAND_GL_1M_V1_20191020_Christian_WPX_CountryTot.nc', \
                  'GCP_CTRACKER' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CTRACKER-EU-v2019_wur_LAND_GL_1M_V1_20191020_Wouter_WPX_CountryTot.nc', \
                  'GCP_CAMS' : '/home/dods/verify/OTHER_PROJECTS/FCO2/Inversions-GCP2019/Tier3TD_CO2_LandFlux_CAMS-V18-2-2019_lsce_LAND_GL_1M_V1_20191020_Chevallier_WPX_CountryTot.nc', \
                  'LUH2v2_FOREST' : '/home/surface5/mmcgrath/ORIGINAL_VERIFY_DATA_FILES/WP3/luh2v2_ecosystem_area_2000_2018_CountryTot.nc', \
                  'MS-NRT' : '/home/dods/verify/OTHER_PROJECTS/FCO2/INVENTORIES/Tier2_CO2_LULUCF_MSNRT-SX_JRC_LAND_EU_1M_V1_20200205_PETRESCU_WPX_CountryTot.nc', \

               }
   
   # certain simulations will be treated in identical ways
   simtype_master={ \
                      'UNFCCC_totincLULUCF' : 'INVENTORY', \
                      'UNFCCC_totexcLULUCF' : 'INVENTORY', \
                      'UNFCCC_LULUCF' : 'INVENTORY', \
                      'UNFCCC_LUC' : 'INVENTORY', \
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
                      'FLUXCOM-rsmeteo' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyANN' :  'VERIFY_BU', \
                      'FLUXCOM_rsonlyRF' :  'VERIFY_BU', \
                      'EPIC' :  'VERIFY_BU', \
                      'ORCHIDEE-MICT' :  'VERIFY_BU', \
                      'FAOSTAT_LULUCF' :  'INVENTORY_NOERR', \
                      'FAOSTAT_F-F' :  'INVENTORY_NOERR', \
                      'FAOSTAT_For' :  'INVENTORY_NOERR', \
                      'FAOSTAT_Crp' :  'INVENTORY_NOERR', \
                      'FAOSTAT_Grs' :  'INVENTORY_NOERR', \
                      'EDGARv4' :  'INVENTORY_NOERR', \
                      'H&N' :  'NONVERIFY_BU', \
                      'JENA-REG-100km' :  'VERIFY_TD', \
                      'JENA-REG-200km' :  'VERIFY_TD', \
                      'JENA-REG-Core100km' :  'VERIFY_TD', \
                      'JENA-REG-Valid100km' :  'VERIFY_TD', \
                      'BLUE' :  'VERIFY_BU', \
                      'EUROCOM_Carboscope' : 'REGIONAL_TD', \
                      'EUROCOM_Flexinvert' : 'REGIONAL_TD', \
                      'EUROCOM_Lumia' :  'REGIONAL_TD', \
                      'EUROCOM_Chimere' :  'REGIONAL_TD', \
                    'ECOSSE_crops': "VERIFY_BU", \
                    'ECOSSE_grass': "VERIFY_BU", \
                    'EFISCEN-Space': "VERIFY_BU", \
                    'UNFCCC_F-F': "INVENTORY", \
                    'UNFCCC_grass': "INVENTORY", \
                    'UNFCCC_crops': "INVENTORY", \
                    'ORCHIDEE_F-F' : "VERIFY_BU", \
                    'EFISCEN' : "NONVERIFY_BU", \
                    'EFISCEN-unscaled' : "NONVERIFY_BU", \
                    'CBM' : "NONVERIFY_BU", \
                    'FLUXCOM_F-F_RF' : "VERIFY_BU", \
                    'FLUXCOM_F-F_ANN' : "VERIFY_BU", \
                  'ORCHIDEE_grass' : "VERIFY_BU", \
                  'FLUXCOM_grass' : "VERIFY_BU", \
                 'ORCHIDEE_crops' : "VERIFY_BU", \
                  'FLUXCOM_crops' : "VERIFY_BU", \
                    'TNO_biofuels' : "INVENTORY_NOERR", \
                    'UNFCCC_biofuels' : "INVENTORY_NOERR", \
                  'ULB_Inland_waters' : "VERIFY_BU", \
                    'UNFCCC_forest_convert' : "INVENTORY", \
                    'UNFCCC_grassland_convert' : "INVENTORY", \
                    'UNFCCC_cropland_convert' : "INVENTORY", \
                    'UNFCCC_wetland_convert' : "INVENTORY", \
                    'UNFCCC_settlement_convert' : "INVENTORY", \
                    'UNFCCC_other_convert' : "INVENTORY", \
                    'GCP_JENA' : 'GLOBAL_TD', \
                    'GCP_CTRACKER' : 'GLOBAL_TD', \
                    'GCP_CAMS' : 'GLOBAL_TD', \
                    'LUH2v2_FOREST' : 'OTHER', \
                    'MS-NRT' : 'INVENTORY_NOERR', \
                 }

   variables_master={ \
                      'UNFCCC_totincLULUCF' : 'FCO2_NBP', \
                      'UNFCCC_totexcLULUCF' : 'FCO2_NBP', \
                      'UNFCCC_LULUCF' : 'FCO2_NBP', \
                      'UNFCCC_LUC' : 'FCO2_NBP', \
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
                      'ORCHIDEE' : 'FCO2_NBP', \
                      'FLUXCOM-rsmeteo' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyANN' :  'FCO2_NEP', \
                      'FLUXCOM_rsonlyRF' :  'FCO2_NEP', \
                      'EPIC' :  'FCO2_NBP_CRO', \
                      'JENA-REG-100km' :  'FCO2_NBP', \
                      'JENA-REG-200km' :  'FCO2_NBP', \
                      'JENA-REG-Core100km' :  'FCO2_NBP', \
                      'JENA-REG-Valid100km' :  'FCO2_NBP', \
                      'BLUE' :  'CD_A', \
                      'H&N' :  'FCO2_NBP', \
                      'ORCHIDEE-MICT' :  'CD_A', \
                      'EDGARv4' :  'CD_A', \
                      'FAOSTAT_LULUCF' :  'FCO2_NBP_FOR', \
                      'FAOSTAT_F-F' :  'FCO2_NBP_FOR', \
                      'FAOSTAT_For' :  'FCO2_LUTOT_FOR', \
                      'FAOSTAT_Crp' :  'FCO2_SOIL_CRO', \
                      'FAOSTAT_Grs' :  'FCO2_SOIL_GRA', \
                      'EUROCOM_Carboscope' : 'FCO2_NBP', \
                      'EUROCOM_Flexinvert' : 'FCO2_NBP', \
                      'EUROCOM_Lumia' :  'FCO2_NBP', \
                      'EUROCOM_Chimere' :  'FCO2_NBP', \
                      'ECOSSE_crops': "FCO2_NBP", \
                    'ECOSSE_grass': "FCO2_NBP", \
                    'EFISCEN-Space': "FCO2_NBP_FOR", \
                    'UNFCCC_F-F': "FCO2_NBP", \
                    'UNFCCC_grass': "FCO2_NBP", \
                    'UNFCCC_crops': "FCO2_NBP", \
                      'ORCHIDEE_F-F' : "FCO2_NBP_FOR", \
                      'EFISCEN' : "FCO2_NEE_FOR", \
                      'EFISCEN-unscaled' : "FCO2_NEE_FOR", \
                      'CBM' : "FCO2_NBP", \
                      'FLUXCOM_F-F_RF' : "FCO2_NEP", \
                      'FLUXCOM_F-F_ANN' : "FCO2_NEP", \
                  'ORCHIDEE_grass' : "FCO2_NBP_GRS", \
                  'FLUXCOM_grass' : "FCO2_NEP", \
                 'ORCHIDEE_crops' : "FCO2_NBP_CRP", \
                  'FLUXCOM_crops' : "FCO2_NEP", \
                      'TNO_biofuels' : "FCO2_NBP_TOT", \
                      'UNFCCC_biofuels' : "FCO2_NBP", \
                      'ULB_Inland_waters' : "FCO2_INLWAT", \
                   'UNFCCC_forest_convert' : "FCO2_NBP", \
                    'UNFCCC_grassland_convert' : "FCO2_NBP", \
                    'UNFCCC_cropland_convert' : "FCO2_NBP", \
                    'UNFCCC_wetland_convert' : "FCO2_NBP", \
                    'UNFCCC_settlement_convert' : "FCO2_NBP", \
                    'UNFCCC_other_convert' : "FCO2_NBP", \
                    'GCP_JENA' : 'FCO2_NBP', \
                    'GCP_CTRACKER' : 'FCO2_NBP', \
                    'GCP_CAMS' : 'FCO2_NBP', \
                     'LUH2v2_FOREST' : 'FOREST_AREA', \
                    'MS-NRT' : 'FCO2_NBP', \
                 }
   
   plotmarker_master={ \
                       'UNFCCC_totincLULUCF' : '_', \
                       'UNFCCC_totexcLULUCF' : '_', \
                       'UNFCCC_LULUCF' : '_', \
                       'UNFCCC_LUC' : '_', \
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
                       'ORCHIDEE' : 'D', \
                       'FLUXCOM-rsmeteo' :  'o', \
                       'FLUXCOM_rsonlyANN' :  'o', \
                       'FLUXCOM_rsonlyRF' :  'o', \
                       'EPIC' :  'X', \
                       'JENA-REG-100km' :  'P', \
                       'JENA-REG-200km' :  'P', \
                       'JENA-REG-Core100km' :  'P', \
                       'JENA-REG-Valid100km' :  'P', \
                       'BLUE' :  '^', \
                       'H&N' :  '^', \
                       'ORCHIDEE-MICT' :  'X', \
                       'EDGARv4' :  '_', \
                       'FAOSTAT_LULUCF' :  'X', \
                       'FAOSTAT_F-F' :  '_', \
                       'FAOSTAT_For' :  'o', \
                       'FAOSTAT_Crp' :  'P', \
                       'FAOSTAT_Grs' :  'X', \
                       'EUROCOM_Carboscope' :  'P', \
                       'EUROCOM_Flexinvert' :  'P', \
                       'EUROCOM_Lumia' :  'P', \
                       'EUROCOM_Chimere' :  'P', \
                       'ECOSSE_crops': "P", \
                    'ECOSSE_grass': "P", \
                    'EFISCEN-Space': "P", \
                    'UNFCCC_F-F': "_", \
                    'UNFCCC_grass': "_", \
                    'UNFCCC_crops': "_", \
                     'ORCHIDEE_F-F' : "o", \
                     'EFISCEN' : "o", \
                     'EFISCEN-unscaled' : "o", \
                     'CBM' : "o", \
                     'FLUXCOM_F-F_RF' : "o", \
                     'FLUXCOM_F-F_ANN' : "o", \
                  'ORCHIDEE_grass' : "o", \
                  'FLUXCOM_grass' : "o", \
                 'ORCHIDEE_crops' : "o", \
                  'FLUXCOM_crops' : "o", \
                     'TNO_biofuels' : "X", \
                     'UNFCCC_biofuels' : "o", \
                     'ULB_Inland_waters' : "o", \
                   'UNFCCC_forest_convert' : "o", \
                    'UNFCCC_grassland_convert' : "o", \
                    'UNFCCC_cropland_convert' : "o", \
                    'UNFCCC_wetland_convert' : "o", \
                    'UNFCCC_settlement_convert' : "o", \
                    'UNFCCC_other_convert' : "o", \
                    'GCP_JENA' : 'o', \
                    'GCP_CTRACKER' : 'o', \
                    'GCP_CAMS' : 'o', \
                    'LUH2v2_FOREST' : 'o', \
                    'MS-NRT' : 'o', \
                    }
   facec_master={ \
                  'UNFCCC_totincLULUCF' :  'black', \
                  'UNFCCC_totexcLULUCF' :  'red', \
                  'UNFCCC_LULUCF' :  'green', \
                  'UNFCCC_LUC' :  'green', \
                  'TrendyV7_CABLE' :  'none', \
                  'TrendyV7_CLASS':  'none', \
                  'TrendyV7_CLM5' :  'none', \
                  'TrendyV7_DLEM' :  'none', \
                  'TrendyV7_ISAM' :  'none', \
                  'TrendyV7_JSBACH' :  'none', \
                  'TrendyV7_JULES' :  'none', \
                  'TrendyV7_LPJ' :  'none', \
                  'TrendyV7_LPX' :  'none', \
                  'TrendyV7_OCN' :  'none', \
                  'TrendyV7_ORCHIDEE-CNP' :  'none', \
                  'TrendyV7_ORCHIDEE' :  'none', \
                  'TrendyV7_SDGVM' :  'none', \
                  'TrendyV7_SURFEX' :  'none', \
                  'ORCHIDEE' : 'blue', \
                  'FLUXCOM-rsmeteo' :  'blue', \
                  'FLUXCOM_rsonlyANN' :  'orchid', \
                  'FLUXCOM_rsonlyRF' :  'darkviolet', \
                  'EPIC' :  'red', \
                  'JENA-REG-100km' :  'khaki', \
                  'JENA-REG-200km' :  'orange', \
                  'JENA-REG-Core100km' :  'darkorange', \
                  'JENA-REG-Valid100km' :  'gold', \
                  'BLUE' :  'blue', \
                  'H&N' :  'green', \
                  'ORCHIDEE-MICT' :  'red', \
                  'EDGARv4' :  'blue', \
                  'FAOSTAT_LULUCF' :  'green', \
                  'FAOSTAT_F-F' :  'green', \
                  'FAOSTAT_For' :  'blue', \
                  'FAOSTAT_Crp' :  'red', \
                  'FAOSTAT_Grs' :  'orange', \
                  'EUROCOM_Carboscope' :  'khaki', \
                  'EUROCOM_Flexinvert' :  'orange', \
                  'EUROCOM_Lumia' :  'darkorange', \
                  'EUROCOM_Chimere' :  'gold', \
                  'ECOSSE_crops': "brown", \
                    'ECOSSE_grass': "gold", \
                    'EFISCEN-Space': "green", \
                    'UNFCCC_F-F': "green", \
                    'UNFCCC_grass': "gold", \
                  'UNFCCC_crops': "brown", \
                  'ORCHIDEE_F-F' : "forestgreen", \
                  'EFISCEN' : "limegreen", \
                  'EFISCEN-unscaled' : "limegreen", \
                  'CBM' : "mediumseagreen", \
                  'FLUXCOM_F-F_RF' : "lime", \
                  'FLUXCOM_F-F_ANN' : "lime", \
                  'ORCHIDEE_grass' : "darkgoldenrod", \
                  'FLUXCOM_grass' : "goldenrod", \
                  'ORCHIDEE_crops' : "saddlebrown", \
                  'FLUXCOM_crops' : "sandybrown", \
                  'UNFCCC_biofuels' : "saddlebrown", \
                  'TNO_biofuels' : "saddlebrown", \
                  'ULB_Inland_waters' : "sandybrown", \
                   'UNFCCC_forest_convert' : "sandybrown", \
                    'UNFCCC_grassland_convert' : "sandybrown", \
                    'UNFCCC_cropland_convert' : "sandybrown", \
                    'UNFCCC_wetland_convert' : "sandybrown", \
                    'UNFCCC_settlement_convert' : "sandybrown", \
                    'UNFCCC_other_convert' : "sandybrown", \
                     'GCP_JENA' : 'sandybrown', \
                    'GCP_CTRACKER' : 'sandybrown', \
                    'GCP_CAMS' : 'sandybrown', \
                     'LUH2v2_FOREST' : 'blue', \
                     'MS-NRT' : 'red', \
             }

   # set some default values, to save space.  Can be changed below.
   edgec_master={}
   uncert_color_master={}
   markersize_master={}
   productiondata_master={}
   displayname_master={}
   displaylegend_master={}
   for simname in files_master.keys():
      edgec_master[simname]="black"
      uncert_color_master[simname]=facec_master[simname]
      markersize_master[simname]=60
      productiondata_master[simname]=True
      displayname_master[simname]=simname
      displaylegend_master[simname]=True
   #endif

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
#      datasource='TRENDY/MPI-BGC/LSCE'
      output_file_start="test_"
      output_file_end="_2019_v1.png" 
   elif graphname == "LUC_full":
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
                            #'ORCHIDEE-MICT', \
         ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LUC_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=" - CO2 emissions from land use change"
      printfakewarning=False

      # Change some colors and symbols here
      facec_master['BLUE']='blue'
      facec_master['H&N']='green'
      facec_master['ORCHIDEE-MICT']='red'

      plotmarker_master['BLUE']='^'
      plotmarker_master['H&N']='^'
      plotmarker_master['ORCHIDEE-MICT']='X'

      uncert_color_master['UNFCCC_LUC']='darkseagreen'

      if lshow_productiondata:
         productiondata_master['ORCHIDEE-MICT']=False
      #endif

   elif graphname == "LULUCF_full":
      desired_simulations=[ \
                            # we read in data for LUC, but we replace it with the sectors below
                            'UNFCCC_LULUCF', \
                            'BLUE', \
                            'H&N', \
                            'MS-NRT', \
                            #'ORCHIDEE-MICT', \
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
         ]   
#      datasource='UNFCCC/LMU/LSCE/FAO'
      output_file_start="LULUCF_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=" - CO2 emissions from land use, land use change, and forestry"
      printfakewarning=False

      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False

      # Change some colors and symbols here
      facec_master['BLUE']='blue'
      facec_master['H&N']='green'
      facec_master['ORCHIDEE-MICT']='red'
      facec_master['FAOSTAT_LULUCF']='orange'

      plotmarker_master['BLUE']='^'
      plotmarker_master['H&N']='^'
      plotmarker_master['ORCHIDEE-MICT']='X'

      uncert_color_master['UNFCCC_LUC']='darkseagreen'

      if lshow_productiondata:
         productiondata_master['ORCHIDEE-MICT']=False
      #endif

   elif graphname == "sectorplot_full":
      desired_simulations=[ \
                            'ORCHIDEE', \
                            'ECOSSE_grass', \
                            'EFISCEN', \
                            'UNFCCC_F-F', \
                            'UNFCCC_grass', \
                            'UNFCCC_crops', \
                            'FLUXCOM_rsonlyANN', \
                            'EPIC', \
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
      desired_legends=[\
                       "UNFCCC_F-F","UNFCCC_grass","UNFCCC_crops",\
                       "Spread of TRENDY_v7",\
                       "EFISCEN","ECOSSE_grass","EPIC",\
                       "EPIC/ECOSSE/EFISCEN","ORCHIDEE","FLUXCOM_rsonlyANN",\
                       ]

 
#      datasource='UNFCCC/IIASA/WEnR/UAbdn/MPI-BGC/LSCE/TRENDY'
      output_file_start="AllSectorBU_"
      output_file_end="_FCO2Nat_2019_v1.png" 

      plotmarker_master['EPIC']="P"

      facec_master['UNFCCC_F-F']="green"
      facec_master['UNFCCC_grass']="gold"
      facec_master['UNFCCC_crops']="brown"
      facec_master['EPIC']="brown"

      if lshow_productiondata:
         productiondata_master['ECOSSE_crops']=False
         productiondata_master['ECOSSE_grass']=False
      #endif

   elif graphname == "forestry_full":
      desired_simulations=[ \
                            'ORCHIDEE_F-F', \
                            'EFISCEN', \
#                            'EFISCEN-unscaled', \
                            'EFISCEN-Space', \
                            'CBM', \
                            'UNFCCC_F-F', \
                            'FLUXCOM_F-F_ANN', \
                            'FLUXCOM_F-F_RF', \
                            'FAOSTAT_F-F', \
                            'LUH2v2_FOREST', \
                         ]   
#      datasource='UNFCCC/MPI-BGC/JRC/WEnR/LSCE/FAOSTAT'
      printfakewarning=False
      output_file_start="ForestRemain_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      titleending=" - CO2 emissions from forests remaining forests"
      lplot_areas=True

      plotmarker_master['EFISCEN']="P"
      plotmarker_master['CBM']="X"
      plotmarker_master['FLUXCOM_F-F_RF']="s"
      plotmarker_master['FLUXCOM_F-F_ANN']="s"
      plotmarker_master['FAOSTAT_F-F']="d"

      edgec_master["ORCHIDEE_F-F"]="black"
      edgec_master["EFISCEN"]="black"
      edgec_master["CBM"]="black"
      edgec_master["FLUXCOM_F-F_RF"]="black"
      edgec_master["FLUXCOM_F-F_ANN"]="black"
      edgec_master["FAOSTAT_F-F"]="black"
      
      facec_master["ORCHIDEE_F-F"]="black"
      facec_master["EFISCEN-Space"]="blue"
      facec_master["EFISCEN"]="skyblue"
      facec_master["CBM"]="red"
      facec_master["FLUXCOM_F-F_RF"]="orange"
      facec_master["FLUXCOM_F-F_ANN"]="orangered"
      facec_master["FAOSTAT_F-F"]="yellow"


      #if lshow_productiondata:
      #   productiondata_master['FLUXCOM_F-F']=False
      #endif

   elif graphname == "grassland_full":
      desired_simulations=[ \
                            'ORCHIDEE_grass', \
                            'ECOSSE_grass', \
                            'UNFCCC_grass', \
                            'FLUXCOM_grass', \
                         ]   
#      datasource='UNFCCC/MPI-BGC/UAbdn/LSCE'
      output_file_start="grassland_full_"
      output_file_end="_2019_v1.png" 

      # Change some things from the above
      plotmarker_master['ECOSSE_grass']='o'

      if lshow_productiondata:
         productiondata_master['ECOSSE_grass']=False
         productiondata_master['FLUXCOM_grass']=False
      #endif

   elif graphname == "crops_full":
      desired_simulations=[ \
                            'ORCHIDEE_crops', \
                            'ECOSSE_crops', \
                            'UNFCCC_crops', \
                            'FLUXCOM_crops', \
                            'EPIC', \
                         ]   
#      datasource='UNFCCC/IIASA/MPI-BGC/UAbdn/LSCE'
      output_file_start="croplands_full_"
      output_file_end="_2019_v1.png" 
      titleending=" - CO2 emissions from croplands remaining croplands"

      # Change some things from the above
      plotmarker_master['ECOSSE_crops']='X'
      plotmarker_master['EPIC']='P'
      facec_master['EPIC']='chocolate'
      facec_master['ECOSSE_crops']='tan'
      displayname_master['EPIC']='EPIC_crops'

      plotmarker_master['FLUXCOM_crops']="s"

      if lshow_productiondata:
         productiondata_master['ECOSSE_crops']=False
         productiondata_master['FLUXCOM_crops']=False
      #endif

   elif graphname == "biofuels":
      desired_simulations=[ \
                            'UNFCCC_biofuels', \
                            'TNO_biofuels', \
                         ]   
#      datasource='UNFCCC/TNO'
      output_file_start="biofuels_"
      output_file_end="_2019_v1.png" 
      titleending=" - CO2 emissions from biofuel combustion"
      printfakewarning=False
      facec_master['UNFCCC_biofuels']='red'
      facec_master['TNO_biofuels']='blue'

   elif graphname == "inversions_combined":

      titleending=" - CO2 natural emissions from land use, land use change, and forestry"

      desired_simulations=[ \
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
                            'ULB_Inland_waters', \
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
                            'MS-NRT', \
                            #'ORCHIDEE-MICT', \
                            'FAOSTAT_LULUCF', \
                            'FAOSTAT_Crp', \
                            'FAOSTAT_Grs', \
                            'FAOSTAT_For', \
      ]   
      output_file_start="TopDownLULUCF_"
      output_file_end="_FCO2Nat_2019_v1.png" 
      edgec_master['MS-NRT']=facec_master['MS-NRT']

      # The legend is tricky.  You can use names not definied in the above
      # simulation list if they are defined later on.
      desired_legend=[ \
                            'UNFCCC_LULUCF', \
                            'MS-NRT', \
                            'ULB_Inland_waters', \
                            'Mean of CarboScopeReg (removing lakes/rivers)', \
                            'Mean of EUROCOM (removing lakes/rivers)',"Min/Max of EUROCOM",\
                            'Mean of GCP (removing lakes/rivers)',"Min/Max of GCP", \
                            'BLUE', \
                            'H&N', \
                            'MS-NRT', \
                            'FAOSTAT_LULUCF', \
      ]
  
      # These simulations will be combined together.
      overwrite_simulations["FAOSTAT_LULUCF"]=['FAOSTAT_Crp','FAOSTAT_Grs','FAOSTAT_For']
      # So I don't want to generally plot the components
      displaylegend_master['FAOSTAT_Crp']=False
      displaylegend_master['FAOSTAT_Grs']=False
      displaylegend_master['FAOSTAT_For']=False

      # Change some colors and symbols here
      facec_master['BLUE']='blue'
      facec_master['H&N']='green'
      facec_master['FAOSTAT_LULUCF']='orange'

      plotmarker_master['BLUE']='^'
      plotmarker_master['H&N']='^'
      plotmarker_master['ORCHIDEE-MICT']='X'

      uncert_color_master['UNFCCC_LUC']='darkseagreen'

      if lshow_productiondata:
         productiondata_master['ORCHIDEE-MICT']=False
      #endif

      # No more fake data in these plots!
      printfakewarning=False

   elif graphname == "inversions_verify":
      desired_simulations=[ \
                            'JENA-REG-100km', \
                            'JENA-REG-200km', \
                            'JENA-REG-Core100km', \
                            'JENA-REG-Valid100km', \
                         ]   
#      datasource='JENA'
      output_file_start="inversions_verify_"
      output_file_end="_2019_v1.png" 
      titleending=" - CO2 inversion from CarboScopeReg simulations in VERIFY"
      printfakewarning=False

   elif graphname in ( "inversions_test", "inversions_full"):
      
      if graphname == "inversions_test":
         titleending=" - net emissions from land use and land use change - TEST (not complete dataset)"
         desired_simulations=[ \
                               'UNFCCC_LULUCF', \
                               'MS-NRT', \
                               'ULB_Inland_waters', \
                               'JENA-REG-100km', \
                               'JENA-REG-200km', \
                               'EUROCOM_Carboscope', \
                               'EUROCOM_Flexinvert', \
                               'GCP_JENA', \
                               'GCP_CAMS', \
                            ]   
         output_file_start="inversions_test_"
      else:
         titleending=" - net emissions from land use and land use change"
         desired_simulations=[ \
                               'UNFCCC_LULUCF', \
                               'MS-NRT', \
                               'ULB_Inland_waters', \
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

#      datasource='UNFCCC/GCP/EUROCOM/MPI-Jena/ULB'
      output_file_end="_FCO2Nat_2019_v2.png" 
      edgec_master['MS-NRT']=facec_master['MS-NRT']

      # No more fake data in these plots!
      printfakewarning=False

   else:
      print("I do not understand which simulation this is:")
      print(graphname)
      sys.exit()
   #endif

#   return linclude_inventories,desired_inventories,desired_others,desired_verify,datasource,output_file_start,output_file_end
   return desired_simulations,files_master,simtype_master,plotmarker_master,variables_master,edgec_master,facec_master,uncert_color_master,markersize_master,productiondata_master,displayname_master,displaylegend_master,datasource,output_file_start,output_file_end,titleending,printfakewarning,lplot_areas,overwrite_simulations,desired_legend
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

def readfile(filename,variablename,ndesiredyears):
   # The goal of this routine is to read in a slice from 1990
   # until 2018.
   # The time axes for all these files starts as days from 1900-01-01,
   # the axis itself might start at a different year (1901, 1970).
   # We need to find the indices corresponding to the year 1990.
   FCO2=np.zeros((ndesiredyears,12,64))
   print("************************************************************")
   print("Reading in file: ",filename)
   print("************************************************************")
   ncfile=nc.Dataset(filename)
   FCO2_file=ncfile.variables[variablename][:]  #kg C yr-1

   # we only need to convert units if we are not dealing with uncertainties,
   # since uncertainties are given as a fraction
   if ncfile.variables[variablename].units == "kg C yr-1":
      print("Converting units from {0} to Tg C yr-1".format(ncfile.variables[variablename].units))
      FCO2_TOT=FCO2_file/1e+9   #kg CO2/yr -->  Tg C/ year
   else:
      print("Not changing units from file: ",ncfile.variables[variablename].units)
      FCO2_TOT=FCO2_file*1.0
      print("Shape of input array: ",FCO2_TOT.shape)
      print("Shape of input array: ",FCO2_TOT.mask)
   #endif
   timeperiod=ncfile.variables['time'][:]  ##days since 1900-01-01, middle of each month
   startday=np.float(timeperiod[0]);endday=np.float(timeperiod[-1])
   startyear,startmonth=find_date(startday)  ## to convert to date 
   endyear,endmonth=find_date(endday)
   print("Timeseries starts at: {0}/{1}".format(startmonth,startyear))
   print("Timeseries starts at: {0}/{1}".format(endmonth,endyear))
   
   # This is something I added to distinguish more clearly between the two sets of dates we have.
   desired_startdate=date(1990,1,15)-date(1900,1,1)
   desired_enddate=date(2018,12,15)-date(1900,1,1)
   data_startdate=date(startyear,startmonth,15)-date(1900,1,1)
   data_enddate=date(endyear,endmonth,15)-date(1900,1,1)

   # this is a slow way to do it, but it works.
   mm=1
   yy=1990
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
      sys.exit()
   #endif


   FCO2[istart:iend,:]=FCO2_TOT[indstart:indend,:]  # extract the slice we are interested in
   return FCO2
#enddef
#####################################################################


#####################################################################
# This subroutine aims to select the countries/regions that you wish to plot
# from the whole list of data available after reading in from the files
# I read in the uncertainties and the real data at the same time.
# If there is no uncertainty, no worries.
def group_input(inputvar,inputerr,desired_plots,luncert,ndesiredyears,numplot,countries65,desired_simulation):
   outputvar=np.zeros((ndesiredyears,numplot))*np.nan
   outputerr=np.zeros((ndesiredyears,numplot))*np.nan
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
         sys.exit()
      #endif
      for iindex in range(len(indices)):
         value=indices[iindex]
         # This is necessary because I initialize the arrays with nan
         if iindex == 0:
            outputvar[:,igroup]=inputvar[:,value]
            if luncert:
               outputerr[:,igroup]=(inputerr[:,value]*inputvar[:,value])**2
            #endif
         else:
            outputvar[:,igroup]=outputvar[:,igroup]+inputvar[:,value]
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
      #endif

   #endfor

   return outputvar,outputerr
#enddef
####################################################################




#####################################################################
# This subroutine combines a specificed list of existing simulations
# and puts the results into a specific simulation.
# I use this because sometimes I need to combine variables from
# a NetCDF file into a single simulation result.
# It overwrites the existing simulation_data and returns it.
def combine_simulations(overwrite_simulations,simulation_data,simulation_err,desired_simulations,graphname):

   if not overwrite_simulations:
      print("No simulations need to be combined.")
      return simulation_data,simulation_err
   #endif

# In the case of the UNFCCC LUC, this is a sum of six different timeseries.
# Those are all in different files, so I combine them here, propogate the
# error, and then only print out this in the actual plot.
   #temp_desired_sims=('UNFCCC_forest_convert','UNFCCC_grassland_convert','UNFCCC_cropland_convert','UNFCCC_wetland_convert','UNFCCC_settlement_convert','UNFCCC_other_convert')

   for osim,temp_sims in overwrite_simulations.items():

      ioverwrite=desired_simulations.index(osim)
      if ioverwrite < 0:
         print("******************************************************************")
         print("For the graph {0}, you need to be sure to include the simulation {}!".format(graphname,osim))
         print("******************************************************************")
         sys.exit()
      #endif

      simulation_data[ioverwrite,:,:]=0.0
      simulation_err[ioverwrite,:,:]=0.0
      for isim,csim in enumerate(temp_sims):
         simulation_data[ioverwrite,:,:]=simulation_data[ioverwrite,:,:]+simulation_data[desired_simulations.index(csim),:,:]
         # Do a simple propogation of error, as well
         simulation_err[ioverwrite,:,:]=simulation_err[ioverwrite,:,:]+(simulation_err[desired_simulations.index(csim),:,:]*simulation_data[desired_simulations.index(csim),:,:])**2
      #endfor

      # don't like doing this in a loop, but the sqrt function doesn't seem to work on arrays?
      for iplot in range(len(simulation_err[0,0,:])):
         for itime in range(len(simulation_err[0,:,0])):
            simulation_err[ioverwrite,itime,iplot]=math.sqrt(simulation_err[ioverwrite,itime,iplot])/simulation_data[ioverwrite,itime,iplot]
         #endfor
      #endfor
   
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
   
   return simulation_data,simulation_err
#enddef
####################################################################



