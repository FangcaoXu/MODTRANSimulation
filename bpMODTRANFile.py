import os
import json
import copy
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


filename = '/home/graduate/fbx5002/MODTRAN6/LWIRRadiance.json'

# https://www.tutorialspoint.com/python/python_dictionary.htm
# dict_keys(['NAME', 'DESCRIPTION', 'CASE', 'RTOPTIONS', 'ATMOSPHERE', 'AEROSOLS', 'GEOMETRY', 'SURFACE', 'SPECTRAL', 'FILEOPTIONS'])
# "SPECTRAL": {"BMNAME": "15_2013"} 15 indicates 15 cm-1 resolution, 05_2013 means 5 cm-1. If it's 1 cm-1 resolution, delete this row

# load(),dump() with loads(), dumps()
with open(filename, 'r') as f:
    jsonObj = json.load(f)

# Read the simulated sensor locations
df = pd.read_csv('/amethyst/s0/fbx5002/PythonWorkingDir/sensorLocation/sensorLocation.csv', index_col=0)
latitudes = df.loc[:,'latitude']
longitudes = -df.loc[:,'longitude']
zeniths = 180 - df.loc[:,'theta']  # the zenith is calculated from the tangent line of observer to the target
azimuths =  df.loc[:,'phi'] + 180  # the observer is selected as the reference point


# append new cases starting from 1 to the json file
n = len(df.index)

# make sure the first case input indicates where the observer is at the head of the target with zenith and azimuth 0
jsonObj["MODTRAN"][0]['MODTRANINPUT']['SPECTRAL']['BMNAME'] = '15_2013'
jsonObj["MODTRAN"][0]['MODTRANINPUT']['NAME'] = 'Radiance%s' % 0
jsonObj["MODTRAN"][0]['MODTRANINPUT']['CASE'] = 0
jsonObj["MODTRAN"][0]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s%s' % (0, '.csv')
jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['PARM1'] = latitudes.iloc[0]
jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['PARM2'] = longitudes.iloc[0]
# delete "OBSZEN" column when it is 180.0
if zeniths.iloc[0] == 180 and 'OBSZEN' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
    del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['OBSZEN']
else:
    jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['OBSZEN'] = zeniths.iloc[0]
if azimuths.iloc[0] == 0 and 'TRUEAZ' in jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']:
    del jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']['TRUEAZ']
else:
    jsonObj["MODTRAN"][0]['MODTRANINPUT']['GEOMETRY']["TRUEAZ"] = azimuths.iloc[0]

# append other modified cases to the same json file
for i in range(1, n):
    jsonObj["MODTRAN"].append(copy.deepcopy(jsonObj["MODTRAN"][0]))
    jsonObj["MODTRAN"][i]['MODTRANINPUT']['NAME'] = 'Radiance%s' % i
    jsonObj["MODTRAN"][i]['MODTRANINPUT']['CASE'] = i
    jsonObj["MODTRAN"][i]['MODTRANINPUT']['FILEOPTIONS']['CSVPRNT'] = 'Radiance%s%s' % (i, '.csv')
    jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']['PARM1'] = latitudes.iloc[i]
    jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']['PARM2'] = longitudes.iloc[i]
    # delete "OBSZEN" column when it is 180.0
    if zeniths.iloc[i] == 180 and 'OBSZEN' in jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']:
        del jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']['OBSZEN']
    else:
        jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']['OBSZEN'] = zeniths.iloc[i]
    if azimuths.iloc[i] == 0 and 'TRUEAZ' in jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']:
        del jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']['TRUEAZ']
    else:
        jsonObj["MODTRAN"][i]['MODTRANINPUT']['GEOMETRY']["TRUEAZ"] = azimuths.iloc[i]
    # write new files to json
    with open(filename, 'w') as f:
        json.dump(jsonObj, f, indent=2) # this is a single json file

rtlib.modInputJsonFile(filename, -1)


# Two way to generate JSON string
def jsonstrgenerator(args1, args2):
    if args1 == 'filename':
        with open(args2, 'r') as f:
            jsonStr = f.read()
        return jsonStr
    elif args1 == 'jsonObj':
        jsonStr = json.dumps(args2, indent=2)
        return jsonStr
    else:
        print('false')

jsonStr1= jsonstrgenerator('filename', filename)
jsonStr2 = jsonstrgenerator('jsonObj', jsonObj)
