#### Please enter into the folder you want to write the data
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
    zeniths = df['theta']
    elevations = df['elevation']
    ranges = df['range']
    # df.index[(df['theta'] == 45) & (df['range'] == 5000)] #561

    # load json to modtran cases
    with open(jsonfile, 'r') as f:
        jsonObj = json.load(f)

    if jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['IPARM'] in [10, 11, 12]:
        casenum = 0

        for i in range(0, n):
            # python 2:  / will round the number if both are interger. Python 3: / will be float calculator
            jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['H1ALT'] = elevations[i]/1000.0 + 0.035
            # delete "BCKZEN" column when it is 0
            if zeniths.iloc[i] == 0 and 'BCKZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
                del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN']
            else: # BCKZEN: target zenith angle: defines the zenith angle for the reverse path from the target back to the sensor
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['BCKZEN'] = zeniths[i]
                jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['HRANGE'] = ranges[i]/1000.0

            # whether cover one year or specific days
            days = range(1,366) if args.fullyear else args.days
            for day in days:
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

                    for temp in args.Temp:
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['SURFACE']['TPTEMP'] = temp
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s_%s_%s_%s' % (i, day, t, temp)
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s_%s_%s_%s%s' % (i, day, t, temp, '.csv')
                        jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = casenum
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
    parser.add_argument('--jsonfile', type=str, default='/home/graduate/fbx5002/MODTRAN6/RadianceBuiltinMaterials.json')
    parser.add_argument('--sensorfile', type=str, default='/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorAngleEle.csv')
    parser.add_argument('--fullyear', default=False, action="store_true", help='switch to True if this argument is in cmd')
    parser.add_argument('--days', required='--fullyear' not in sys.argv, type=int, nargs='*', help='provide days of the year')
    parser.add_argument('--GMTtime', type=int, nargs='*', help='provide time of the day')
    parser.add_argument('--Temp', type=int, nargs='*', help='provide target temperature')

    # read the argument of jsonfile from the command line
    readjsonintoMODTRAN(parser.parse_args())
    runcases()


'''
python '/amethyst/s0/fbx5002/PythonWorkingDir/runMODTRAN/VaryingRangeEle.py' --days 107 --GMTtime 14 --Temp 295
'''