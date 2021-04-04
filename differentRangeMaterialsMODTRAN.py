import os
import sys
import json
import VaryingRangeEle as bprange

# BH Data alt.gmb: [3411.706 3447.039]; range: [3613.563 6134.737]; angle: [30, 60]
# # get all user defined reflectivity files
# materials_MODTRAN = ['LAMB_SNOW_COVER', 'LAMB_FOREST', 'LAMB_FARM', 'LAMB_DESERT', 'LAMB_OCEAN', 'LAMB_CLOUD_DECK', 'LAMB_OLD_GRASS', 'LAMB_DECAYED_GRASS',
#                      'LAMB_MAPLE_LEAF', 'LAMB_BURNT_GRASS', 'LAMB_SEA_ICE_CCM3', 'LAMB_CONIFER', 'LAMB_OLIVE_GLOSS_PAINT', 'LAMB_DECIDUOUS_TREE', 'LAMB_SANDY_LOAM',
#                      'LAMB_GRANITE', 'LAMB_GALVANIZED_STEEL', 'LAMB_GRASS', 'LAMB_BLACK_PLASTIC', 'LAMB_ALUMINUM', 'LAMB_EVERGREEN_NEEDLE_FOREST',
#                      'LAMB_EVERGREEN_BROADLEAF_FOREST', 'LAMB_DECIDUOUS_NEEDLE_FOREST', 'LAMB_DECIDUOUS_BROADLEAF_FOREST', 'LAMB_FOREST_MIXED', 'LAMB_SHRUBS_CLOSED',
#                      'LAMB_SHRUBS_OPEN', 'LAMB_SAVANNA_WOODY', 'LAMB_SAVANNA', 'LAMB_GRASSLAND', 'LAMB_WETLAND', 'LAMB_CROPLAND', 'LAMB_URBAN', 'LAMB_CROP_MOSAIC',
#                      'LAMB_SNOW_ANTARCTIC', 'LAMB_DESERT_BARREN', 'LAMB_OCEAN_WATER', 'LAMB_TUNDRA', 'LAMB_SNOW_FRESH', 'LAMB_SEA_ICE', 'LAMB_SPECTRALON', 'LAMB_SAND_DRY']


materials_MODTRAN = ['LAMB_FOREST', 'LAMB_FARM', 'LAMB_DESERT', 'LAMB_CLOUD_DECK', 'LAMB_GRASS', 'LAMB_BLACK_PLASTIC', 'LAMB_ALUMINUM', 'LAMB_EVERGREEN_NEEDLE_FOREST',
                     'LAMB_EVERGREEN_BROADLEAF_FOREST', 'LAMB_SHRUBS_CLOSED', 'LAMB_GRASSLAND', 'LAMB_OLD_GRASS', 'LAMB_DECAYED_GRASS', 'LAMB_BURNT_GRASS', 'LAMB_MAPLE_LEAF',
                     'LAMB_CONIFER', 'LAMB_OLIVE_GLOSS_PAINT', 'LAMB_DECIDUOUS_TREE', 'LAMB_GRANITE', 'LAMB_GALVANIZED_STEEL','LAMB_SHRUBS_OPEN', 'LAMB_CROPLAND', 'LAMB_URBAN',
                     'LAMB_OCEAN_WATER', 'LAMB_TUNDRA', 'LAMB_SNOW_FRESH', 'LAMB_SPECTRALON', 'LAMB_SANDY_LOAM', 'LAMB_SAND_DRY']

# create all folders for storing the simulated files of different materials
ouputdirectory = '/home/graduate/fbx5002/disk10TB/DARPA/MODTRANSimulated/Stage2_BHData/DifferentMaterials/TemperatureChecking'
outputfolders = [os.path.join(ouputdirectory, m) for m in materials_MODTRAN]
for outputfolder in outputfolders:
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="read json file")
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/RadianceBuiltinMaterials.json')
    parser.add_argument('--sensorfile', type=str, default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorAngleEle.csv')
    parser.add_argument('--fullyear', default=False, action="store_true", help='switch to True if this argument is in cmd')
    parser.add_argument('--days', required='--fullyear' not in sys.argv, type=int, nargs='*', help='provide days of the year')
    parser.add_argument('--GMTtime', type=int, nargs='*', help='provide time of the day')
    parser.add_argument('--Temp', type=int, nargs='*', help='provide target temperature')

    jsonfile = parser.parse_args().jsonfile
    with open(jsonfile, 'r') as f:
        jsonObj = json.load(f)

    # write each reflectivity file into the json and run the MODTRAN
    for i in range(0, len(materials_MODTRAN)):
        material_MODTRAN = materials_MODTRAN[i]
        jsonObj["MODTRAN"][0]['MODTRANINPUT']["SURFACE"]["SURFP"]["CSALB"] = material_MODTRAN
        jsonObj["MODTRAN"][0]['MODTRANINPUT']["SURFACE"]["SURFA"]["CSALB"] = material_MODTRAN

        with open(jsonfile, 'w') as f:
            json.dump(jsonObj, f, indent=2)

        # simulate files in different working directory with MODTRAN
        outputfolder = outputfolders[i]
        os.chdir(outputfolder)
        bprange.readjsonintoMODTRAN(parser.parse_args())
        bprange.runcases()
        if i < len(materials_MODTRAN)-1:
            print("Simulations for {} is done".format(material_MODTRAN))
        else:
            print("All Simulations are done")


'''
python '/amethyst/s0/fbx5002/PythonWorkingDir/runMODTRAN/differentRangeMaterialsMODTRAN.py' --fullyear --GMTtime 14 16 18 20
python '/amethyst/s0/fbx5002/PythonWorkingDir/runMODTRAN/differentRangeMaterialsMODTRAN.py' --days 107 --GMTtime 14 16 18 20 --Temp 295 300 305 310 315 320

python '/amethyst/s0/fbx5002/PythonWorkingDir/runMODTRAN/differentRangeMaterialsMODTRAN.py' --days 107 --GMTtime 16 --Temp 270 271 272 273 274 275 276 277 278 279 280 281 282 283 284 285 \
 286 287 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320
'''