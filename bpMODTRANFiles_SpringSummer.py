#### Please enter into the folder you want to write the data
import json
import os
import pandas as pd
from ctypes import cdll

# Check the LD_LIBRARY_PATH
# LD_LIBRARY_PATH = '/amethyst/s0/fbx5002/modtran/software/MODTRAN6.0/bin/linux/'
# If it's not, please add your MODTRAN path to .bashrc file
# If it prompts the key error, please open the Pycharm from the command line to inherit the system setting
os.environ['LD_LIBRARY_PATH']
# Load Library and Initiallize the environment
rtlib = cdll.LoadLibrary('libmod6rt.so')

# Spring 2019 in Northern Hemisphere began on Wednesday, March 20 (79)
# Fall 2019 in Northern Hemisphere began on Monday, September 23 (266)
days = range(79,266)
GMTtimes = range(2,24,4)  # 2, 6, 10, 14, 18, 22 for the same day
reflectances = [0,5,10,30,50,80,100]

# Read the first json file
# in each loop the values of keys "NAME", "CASE", "CSVPRNT" and "GEOMETRY" are rewritten for the original JSON File
# dict_keys(['NAME', 'DESCRIPTION', 'CASE', 'RTOPTIONS', 'ATMOSPHERE', 'AEROSOLS', 'GEOMETRY', 'SURFACE', 'SPECTRAL', 'FILEOPTIONS'])
# "SPECTRAL": {"BMNAME": "15_2013"} 15 indicates 15 cm-1 resolution, 05_2013 means 5 cm-1. If it's 1 cm-1 resolution, delete this row
# "IMULT": "RT_DISORT_AT_OBS", "RT_DISORT", "RT_ISAACS_2STREAM"   "DISALB": false,
# "SOLCON": 0. No scaling of TOA (Top-Of-Atmosphere) solar irradiance.
def readjsonintoMODTRAN(args):
    jsonfile = args.jsonfile
    sensorfile = args.sensorfile
    df = pd.read_csv(sensorfile, index_col=0)
    n = len(df.index)
    zeniths = df.loc[:, 'theta']
    elevations = df.loc[:, 'elevation']

    with open(jsonfile, 'r') as f:
        jsonObj = json.load(f)
    # load json to modtran cases
    if jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['IPARM'] in [10, 11, 12]:  # the target is selected as the reference point
        casenum = 0

        # set the atmosphere and aerosols model
        jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] = "SEASN_SPRING_SUMMER"
        if "MODEL" in jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]:
            del jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]["MODEL"]

        for i in range(0, n):
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['H1ALT'] = elevations.iloc[i] / 1000 + 0.035
            # delete "BCKZEN" column when it is 0
            if zeniths.iloc[i] == 0 and 'BCKZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN'] = zeniths.iloc[i]

            for day in days:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']["IDAY"] = day

                for t in GMTtimes:
                    jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['GMTIME'] = t

                    for reflec in reflectances:
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']["SURFACE"]["SURFP"]["CSALB"] = "LAMB_CONST_%s_PCT" % (
                            reflec)
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']["SURFACE"]["SURFA"]["CSALB"] = "LAMB_CONST_%s_PCT" % (
                            reflec)
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s_%s_%s_%s' % (i, day, t, reflec)
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = casenum
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS'][
                            'CSVPRNT'] = 'Radiance%s_%s_%s_%s%s' % (i, day, t, reflec, '.csv')
                        # overwrite changed json to original file
                        casenum += 1
                        with open(jsonfile, 'w') as f:
                            json.dump(jsonObj, f, indent=2)
                        rtlib.modInputJsonFile(jsonfile, -1)  # -1 to initialize the case template
    else:
        print("the sensor is selected as the reference point")

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
    parser.add_argument('--sensorfile', type=str,
                        default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorElevation.csv')

    # read the argument of jsonfile from the command line
    readjsonintoMODTRAN(parser.parse_args())
    runcases()
