### Fix Range, Change zenith angle from 0 to 60.
### For a specfic dat and reflectance
import json
import os
import sys
import pandas as pd
from ctypes import cdll

# Check the LD_LIBRARY_PATH
# LD_LIBRARY_PATH = '/amethyst/s0/fbx5002/modtran/software/MODTRAN6.0/bin/linux/'
# If it's not, please add your MODTRAN path to .bashrc file
# If it prompts the key error, please open the Pycharm from the command line to inherit the system setting
os.environ['LD_LIBRARY_PATH']
# Load Library and Initiallize the environment
rtlib = cdll.LoadLibrary('libmod6rt.so')

### Fix Range between the sensor and target
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
    if jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['IPARM'] in [10, 11, 12]:
        casenum = 0

        for i in range(0, n):
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['H1ALT'] = elevations.iloc[i] / 1000 + 0.035
            # delete "BCKZEN" column when it is 0
            if zeniths.iloc[i] == 0 and 'BCKZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN']
            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN'] = zeniths.iloc[i]

            if args.fullyear:
                for day in range(1,366):
                    jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']["IDAY"] = day
                    # change the atomospheric and aerosol models for summer or winter
                    if 79 <= day < 266:
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] = "SEASN_SPRING_SUMMER"
                        if "MODEL" in jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]:
                            del jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]["MODEL"]
                    else:
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']["ATMOSPHERE"]["MODEL"] = "ATM_MIDLAT_WINTER"
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']["AEROSOLS"]["ISEASN"] = "SEASN_FALL_WINTER"

                    for t in args.GMTtime:
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['GMTIME'] = t
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s_%s_%s' % (i, day, t)
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s_%s_%s%s' % (i, day, t, '.csv')
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = casenum
                        casenum += 1
                        # overwrite changed json to original file
                        with open(jsonfile, 'w') as f:
                            json.dump(jsonObj, f, indent=2)
                        rtlib.modInputJsonFile(jsonfile, -1)  # -1 to initialize the case template

            else:
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s' % i
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = casenum
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s%s' % (i, '.csv')
                casenum += 1
                # overwrite changed json to original file
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
    parser.add_argument('--sensorfile', type=str,default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorElevation.csv')
    parser.add_argument('--fullyear', default=False, action="store_true", help='switch to True if this argument is in cmd')
    parser.add_argument('--GMTtime', required='--fullyear' in sys.argv, type=int, nargs='*', help='provide time of the day')


    # read the argument of jsonfile from the command line
    readjsonintoMODTRAN(parser.parse_args())
    runcases()