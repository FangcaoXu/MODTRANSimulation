import os
import sys
import json
import FixedRange as bprange

# # get all user defined reflectivity files
# materials_MODTRAN = ['LAMB_SNOW_COVER', 'LAMB_FOREST', 'LAMB_FARM', 'LAMB_DESERT', 'LAMB_OCEAN', 'LAMB_CLOUD_DECK', 'LAMB_OLD_GRASS', 'LAMB_DECAYED_GRASS',
#                      'LAMB_MAPLE_LEAF', 'LAMB_BURNT_GRASS', 'LAMB_SEA_ICE_CCM3', 'LAMB_CONIFER', 'LAMB_OLIVE_GLOSS_PAINT', 'LAMB_DECIDUOUS_TREE', 'LAMB_SANDY_LOAM',
#                      'LAMB_GRANITE', 'LAMB_GALVANIZED_STEEL', 'LAMB_GRASS', 'LAMB_BLACK_PLASTIC', 'LAMB_ALUMINUM', 'LAMB_EVERGREEN_NEEDLE_FOREST',
#                      'LAMB_EVERGREEN_BROADLEAF_FOREST', 'LAMB_DECIDUOUS_NEEDLE_FOREST', 'LAMB_DECIDUOUS_BROADLEAF_FOREST', 'LAMB_FOREST_MIXED', 'LAMB_SHRUBS_CLOSED',
#                      'LAMB_SHRUBS_OPEN', 'LAMB_SAVANNA_WOODY', 'LAMB_SAVANNA', 'LAMB_GRASSLAND', 'LAMB_WETLAND', 'LAMB_CROPLAND', 'LAMB_URBAN', 'LAMB_CROP_MOSAIC',
#                      'LAMB_SNOW_ANTARCTIC', 'LAMB_DESERT_BARREN', 'LAMB_OCEAN_WATER', 'LAMB_TUNDRA', 'LAMB_SNOW_FRESH', 'LAMB_SEA_ICE', 'LAMB_SPECTRALON', 'LAMB_SAND_DRY']

# get all user defined reflectivity files
materials_MODTRAN = ['LAMB_SNOW_FRESH', 'LAMB_SEA_ICE', 'LAMB_SPECTRALON', 'LAMB_SAND_DRY']
#
# create all folders for storing the simulated files of different materials
ouputdirectory = '/home/graduate/fbx5002/disk10TB/DARPA/MODTRANSimulated/Stage2_BHData/DifferentMaterials'
outputfolders = [os.path.join(ouputdirectory, m) for m in materials_MODTRAN]
for outputfolder in outputfolders:
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="read json file")
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/RadianceBuiltinMaterials.json')
    parser.add_argument('--sensorfile', type=str, default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorElevation.csv')
    parser.add_argument('--fullyear', default=False, action="store_true", help='switch to True if this argument is in cmd')
    parser.add_argument('--GMTtime', required='--fullyear' in sys.argv, type=int, nargs='*', help='provide time of the day')

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
            # try:
            #     input("Press enter to continue for simulations {}".format(materials_MODTRAN[i+1]))
            # except SyntaxError:
            #     pass
        else:
            print("All Simulations are done")


'''
python '/amethyst/s0/fbx5002/PythonWorkingDir/runMODTRAN/differentMaterialsMODTRAN.py' --fullyear --GMTtime 10 12 14 16 18 20 22 24
'''