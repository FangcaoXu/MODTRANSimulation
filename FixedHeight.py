#### Please enter into the folder you want to write the data
### Fix the elevation of the sensor, research azimuths as well

import json
import os
import pandas as pd
import numpy as np
from ctypes import cdll

# Check the LD_LIBRARY_PATH
# LD_LIBRARY_PATH = '/amethyst/s0/fbx5002/modtran/software/MODTRAN6.0/bin/linux/'
# If it's not, please add your MODTRAN path to .bashrc file
# If it prompts the key error, please open the Pycharm from the command line to inherit the system setting
os.environ['LD_LIBRARY_PATH']
# Load Library and Initiallize the environment
rtlib = cdll.LoadLibrary('libmod6rt.so')


def readjsonintoMODTRAN(args):
    jsonfile =args.jsonfile
    sensorfile = args.sensorfile
    df = pd.read_csv(sensorfile, index_col=0)
    n = len(df.index)
    index = np.r_[0, 73:n]
    zeniths = df.loc[:, 'theta']
    azimuths = df.loc[:, 'phi']

    with open(jsonfile, 'r') as f:
        jsonObj = json.load(f)
    # load json to modtran cases
    if jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['IPARM'] in [10, 11, 12]:  # the target is selected as the reference point
        for i in index:
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s' % i
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = i
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s%s' % (i, '.csv')
            # delete "BCKZEN" column when it is 0
            if zeniths.iloc[i] == 0 and 'BCKZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN'] = zeniths.iloc[i]
            # delete "TRUEAZ" column when it is 0
            if azimuths.iloc[i] == 0 and 'TRUEAZ' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['TRUEAZ']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']["TRUEAZ"] = azimuths.iloc[i]
            # overwrite changed json to original file
            with open(filename, 'w') as f:
                json.dump(jsonObj, f, indent=2)
            rtlib.modInputJsonFile(filename, -1)  # -1 to initialize the case template
    else:  # the sensor is selected as reference point, the azimuth is from sensor to target
        latitudes = df.loc[:, 'latitude']
        longitudes = -df.loc[:, 'longitude']
        zeniths = 180 - df.loc[:, 'theta']  # the zenith is calculated from the tangent line of observer to the target
        azimuths = [(x + 180) if x < 180 else (x - 180) for x in df.loc[:, 'phi']]
        for i in index:
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s' % i
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = i
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s%s' % (i, '.csv')
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['PARM1'] = latitudes.iloc[i]
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['PARM2'] = longitudes.iloc[i]
            # Make sure the "LENN" of "Geometry" is set as 0 to indicate the short transmission path
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['LENN'] = 0
            if zeniths.iloc[i] == 180 and 'OBSZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['OBSZEN']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['OBSZEN'] = int(zeniths.iloc[i])
            # delete "TRUEAZ" column when it is 0
            if azimuths.iloc[i] == 0 and 'TRUEAZ' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['TRUEAZ']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']["TRUEAZ"] = int(azimuths.iloc[i])
            # overwrite changed json to original file
            with open(jsonfile, 'w') as f:
                json.dump(jsonObj, f, indent=2)
            rtlib.modInputJsonFile(jsonfile, -1)  # -1 to initialize the case template

# function to validate and run all cases
def runcases():
    n = rtlib.modCaseCount()
    print(n)
    if n > 0:
        for x in range(n):
            rtlib.modCaseValidate(x)
            if rtlib.modExecuteCase(x):
                rtlib.modCaseMessage(x)
                rtlib.modCaseOutputWrite(x)
                print('Run successfully')
            else:
                print('Failed')
        # after running all cases, clean up and initialize the environment
        rtlib.modCleanup()
        rtlib.modInit()
    else:
        print('No case to be executed')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="read json file")
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/LWIRRadiance.json')
    parser.add_argument('--sensorfile', type=str, default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorLocation.csv')

    # read the argument of jsonfile from the command line
    readjsonintoMODTRAN(parser.parse_args())
    runcases()


