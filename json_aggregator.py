from glob import glob               # https://github.com/python/cpython/blob/2.7/Lib/glob.py
import pandas as pd
import numpy as np
import json

# get json filenames from dir
annotatedJsonRoutes = sorted(glob("data/processed/*"))
routesForRaw = []
for route in annotatedJsonRoutes:
    route1 = route.strip('data/processed/')
    route2 = route1.strip('.json')
    routesForRaw.append(route2)

# remove files that have already been combined
previouslyCombinedJson = glob("data/combined_jsons/*")
routesToRemove = []
for route in previouslyCombinedJson:
    route1 = route.strip('data/combined_jsons/')
    route2 = route1.strip('_combined.json')
    routesToRemove.append(route2)

routesToPop = []
for i in range(len(routesForRaw)):
    for route in routesToRemove:
        if routesForRaw[i] == route:
            routesToPop.append(i)

for i in sorted(routesToPop, reverse=True):
    # print(i, routesForRaw[i])
    routesForRaw.pop(i)
    annotatedJsonRoutes.pop(i)

# get correlated openPose json from new_raw
openPoseDir = "data/new_raw/"
openPoseJsonRoutes = []
indecesToPop = []
for index in range(len(routesForRaw)):
    route = routesForRaw[index]
    dirRoute = openPoseDir + route + "/*.json"
    globRoutes = glob(dirRoute)
    if globRoutes == []:
        indecesToPop.append(index)
    else:
        openPoseJsonRoutes.append(sorted(globRoutes))

# print(indecesToPop)
for i in sorted(indecesToPop, reverse=True):
    # print(i, routesForRaw[i])
    routesForRaw.pop(i)
    annotatedJsonRoutes.pop(i)



print("openPoseJsonRoutes len is: ", len(openPoseJsonRoutes))
annotatedJson = []
# import annotatedJsons
for route in annotatedJsonRoutes:
    data = pd.read_json(route)
    del data['annotator']
    del data['framesDirectory']
    dataString = data.to_string(header=None, index=None)
    dataString1 = dataString.strip("labels")
    stringArray = dataString1.split()
    array = []
    for string in stringArray:
        if string == "none":
            array.append(0)
        elif string == "not confused":
            array.append(1)
        elif string == "uncertain":
            array.append(2)
        elif string == "confused":
            array.append(3)
    annotatedJson.append(array)


npAnnotated = np.asarray(annotatedJson, dtype=object)
openPoseJson = []
# import openPoseJsons
for file in openPoseJsonRoutes:
    files = []
    for route in file:
        data = pd.read_json(route)
        del data['version']
        dataString = data.to_string(header=None, index=None)
        dataString1 = dataString.strip("{'person_id': [-1], 'pose_keypoints_2d':")
        stringArray = dataString1.split(']')[0]
        stringArraySplit = stringArray.replace(",", "")
        # print(stringArraySplit)
        stringArraySplit1 = stringArraySplit.split()
        # print(stringArraySplit1)
        npStringArray = np.array(stringArraySplit1)
        # print(npStringArray)
        if npStringArray[0] == 'Empty':
            files.append(np.empty([]))
            break
        floatArray = npStringArray.astype(np.float)
        # print(floatArray)
        files.append(floatArray)
    openPoseJson.append(files)


npOpenPose = np.asarray(openPoseJson, dtype=object)
# print("routesForRaw shape is: ", len(routesForRaw))
# print("npOpenPose shape is: ", npOpenPose.shape)
# print("npAnnotated shape is: ", npAnnotated.shape)
# print("npAnnotated type is: ", type(npAnnotated))

# combine the array
combinedArray = []

for file in range(len(npAnnotated)):
    array = []

    print("file number is: ", file)
    # print(routesForRaw[file])
    # print("npOpenPose[file] is: ", npOpenPose[file])
    # print("npOpenPose[file].length is: ", len(npOpenPose[file]))
    # print("npAnnotated[file] is: ", npAnnotated[file])
    # print("npAnnotated[file].length is: ", len(npAnnotated[file]))

    if len(npOpenPose[file]) != 0 and len(npAnnotated[file]) != 0:
        frameMaxLen = min(len(npAnnotated[file]) - 1, len(npOpenPose[file]))
        for frame in range(frameMaxLen):
            # print("npAnnotated[file][frame]", npAnnotated[file][frame])
            # print("npOpenPose[file][frame]", npOpenPose[file][frame])
            # annotatedRow = [npAnnotated[file][frame]]
            newRow = npOpenPose[file][frame].tolist()
            if isinstance(newRow, list):
                newRow.insert(0, npAnnotated[file][frame])
                array.append(newRow)
            else:
                array.append([npAnnotated[file][frame]])
        combinedArray.append(array)

# for row in range(len(combinedArray[0])):
#     print(combinedArray[0][row])

# print("combinedArray shape is: ", len(combinedArray))
# export to json
for i in range(len(combinedArray)):
    route = "data/combined_jsons/" + routesForRaw[i] + "_combined.json"
    print(route)
    with open(route, 'w') as f:
        json.dump(combinedArray[i], f)
