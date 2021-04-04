#### Please enter into the folder you want to write the data
import os
import json
import pandas as pd
import FixedRange as bprange

# the defaut json file: Day 107; time GMT 18:00; IPARM 11, the target is the reference point
def writeReflec2Json(reflecfile, jsonObj, outputpath, reflec=True):
    df = pd.read_csv(reflecfile, index_col=0)
    # whether the second column of reflecfile is the reflectivity or absorptance
    if reflec:
        wv = df.iloc[:, 0].tolist()
        reflect = df.iloc[:, 1].tolist()
    else:
        wv = df.iloc[:, 0].tolist()
        reflect = [1 - x for x in df.iloc[:, 1].tolist()]
    # modify the standard MODTRAN jsonObj
    jsonObj["MODTRAN"][0]['MODTRANINPUT']['SURFACE']['SURFP']['WVSURF'] = wv
    jsonObj["MODTRAN"][0]['MODTRANINPUT']['SURFACE']['SURFP']['UDSALB'] = reflect
    # write the modified jsonObj into output json file
    with open(outputpath, 'w') as f:
        json.dump(jsonObj, f, indent=2)

# get all user defined reflectivity files
reflecinfofolder = '/home/graduate/fbx5002/disk10TB/DARPA/MatrixCSV/Stage1_7.5_12um/DifferentMaterials/exoscan/exoscan_info'
reflecinfos= [os.path.join(reflecinfofolder, f) for f in os.listdir(reflecinfofolder) if f.endswith('.csv')]
# create all folders for storing the simulated files of different materials
ouputdirectory = '/home/graduate/fbx5002/disk10TB/DARPA/MODTRANSimulated/Stage1_7.5_12um/DifferentMaterials/exoscan'
outputfolders = [os.path.splitext(os.path.join(ouputdirectory, os.path.basename(f)))[0] for f in reflecinfos]
for outputfolder in outputfolders:
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="read json file")
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/standardJson/LWIRRadianceUserDefined.json')

    filename = parser.parse_args().jsonfile
    with open(filename, 'r') as f:
        jsonObj = json.load(f)

    # write each reflectivity file into the json and run the MODTRAN
    for i in range(0, len(reflecinfos)):
        file = reflecinfos[i]
        jsonoutput = '/home/graduate/fbx5002/MODTRAN6/LWIRRadiance.json'
        # write the user defined reflectivity into the json file
        writeReflec2Json(file, jsonObj, jsonoutput)
        # simulate files in different working directory with MODTRAN
        outputfolder = outputfolders[i]
        os.chdir(outputfolder)
        bprange.readjsonintoMODTRAN(parser.parse_args())
        bprange.runcases()

