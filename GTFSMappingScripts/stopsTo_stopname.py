import json


values = {}

with open("Google_Transit/stops.txt", "r") as f:
    f.readline()

    for line in f:
        b = line.strip().split(",")
        key = b[0]
        value = b[2].replace('"', "")
        values[key] = value


data = json.dumps(values, separators=(",", ":"))
with open("GTFSMappings/stopsTo_stopname.json", "w") as f:
    f.write(data)

##json.dumps([1,2,3], separators=(","))
