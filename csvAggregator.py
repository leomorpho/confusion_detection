from glob import glob               # https://github.com/python/cpython/blob/2.7/Lib/glob.py
import pandas as pd

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


openFaceJson = []
# import openFaceJsons
for file in openFaceJsonRoutes:
    files = []
    for route in file:
        files.append(pd.read_json(route))

    openFaceJson.append(files)

print(openFaceJson[0])

annotatedJson = []
# import annotatedJsons
for route in annotatedJsonRoutes:
    # print(route)
    annotatedJson.append(pd.read_json(route))

# print(annotatedJsonParsed)

