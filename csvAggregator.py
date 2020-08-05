from glob import glob               # https://github.com/python/cpython/blob/2.7/Lib/glob.py
import pandas as pd
import numpy as np
import re
import json

# get json filenames from dir
annotatedJsonRoutes = sorted(glob("data/processed/*"))
routesForRaw = []
for route in annotatedJsonRoutes:
    route1 = route.strip('data/processed/')
    route2 = route1.strip('.json')
    routesForRaw.append(route2)


# get correlated openFace json from new_raw
openFaceDir = "data/new_raw/"
openFaceJsonRoutes = []
for route in routesForRaw:
    dirRoute = openFaceDir + route + "/*.json"
    globRoutes = glob(dirRoute)
    openFaceJsonRoutes.append(sorted(globRoutes))

annotatedJson = []
# import annotatedJsons
for route in annotatedJsonRoutes:
    data = pd.read_json(route)
    del data['annotator']
    del data['framesDirectory']
    annotatedJson.append(data)

npAnnotated = np.asarray(annotatedJson)
openFaceJson = []
# import openFaceJsons
for file in openFaceJsonRoutes:
    files = []
    for route in file:
        data = pd.read_json(route)
        del data['version']
        dataString = data.to_string(header=None, index=None)
        dataString1 = dataString.strip("{'person_id': [-1], 'pose_keypoints_2d':")
        dataString2 = dataString1.strip("], 'face_keypoints_2d': [], 'hand_left_keypoints_2d': [], 'hand_right_keypoints_2d': [], 'pose_keypoints_3d': [], 'face_keypoints_3d': [], 'hand_left_keypoints_3d': [], 'hand_right_keypoints_3d': []}")
        stringArray = re.sub("[^\w]", " ",  dataString2).split()
        files.append(stringArray)
    openFaceJson.append(files)

npOpenFace = np.asarray(openFaceJson)

# combine the array
combinedArray = []
for file in range(len(npAnnotated)):
    array = []
    for frame in range(len(npAnnotated[file])-1):
        joinedRow = npAnnotated[file][frame].tolist() + npOpenFace[file][frame]
        array.append(joinedRow)
    combinedArray.append(array)

# for row in range(len(combinedArray[0])):
#     print(combinedArray[0][row])

# export to json
for i in range(len(combinedArray)):
    route = "data/combinedJsons/" + routesForRaw[i] + ".json"
    print(route)
    with open(route, 'w') as f:
        json.dump(combinedArray, f)


