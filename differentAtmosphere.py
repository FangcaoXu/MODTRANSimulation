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
rtlib.modCleanup()
rtlib.modInit()

# Spring 2019 in Northern Hemisphere began on Wednesday, March 20 (79)
# Fall 2019 in Northern Hemisphere began on Monday, September 23 (266)
# The ATM_SUBARC_SUMMER, ATM_SUBARC_WINTER should change the days of the year
# ATM_TROPICAL and ATM_US_STANDARD_1976 cover the whole year for which the ["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] should be deleted
days = range(1,366)
#days = range(79,266)  #days = list(range(1,79))+ list(range(266, 366))
GMTtimes = range(2,24,4)
reflectances = [0,5,10,30,50,80,100]
models = ["ATM_MIDLAT_SUMMER", "ATM_MIDLAT_WINTER", "ATM_SUBARC_SUMMER", "ATM_SUBARC_WINTER", "ATM_TROPICAL", "ATM_US_STANDARD_1976"] #(default, SEASN_SPRING_SUMMER)

df = pd.read_csv('/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorElevation.csv', index_col=0)
n = len(df.index)
zeniths = df.loc[:, 'theta']
elevations = df.loc[:, 'elevation']

def readjsonintoMODTRAN(args):
    filename =args.jsonfile
    atmosphere = args.atmosphere

    with open(filename, 'r') as f:
        jsonObj = json.load(f)

    if jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['IPARM'] in [10, 11, 12]:  # the target is selected as the reference point
        casenum = 0

        # set the atmosphere and aerosols model
        jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]["MODEL"] = atmosphere
        if atmosphere in ["ATM_TROPICAL", "ATM_US_STANDARD_1976"]:
            if 'ISEASN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"]
        elif atmosphere in ["ATM_MIDLAT_WINTER", "ATM_SUBARC_WINTER"]:
            jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] = "SEASN_FALL_WINTER"
        else:
            jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] = "SEASN_SPRING_SUMMER"

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
                        with open(filename, 'w') as f:
                            json.dump(jsonObj, f, indent=2)
                        rtlib.modInputJsonFile(filename, -1)  # -1 to initialize the case template
    else:
        print("the sensor is selected as the reference point")

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
    else:
        print('No case to be executed')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="read json file")
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/standardJson/DifferentAtmosphere.json')
    parser.add_argument('--atmosphere', type=str, default='ATM_US_STANDARD_1976')

    # read the argument of jsonfile from the command line
    readjsonintoMODTRAN(parser.parse_args())
    runcases()