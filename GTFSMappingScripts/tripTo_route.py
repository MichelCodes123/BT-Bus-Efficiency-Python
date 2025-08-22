import json


##Description
values = {}

with open("Google_Transit/trips.txt", "r") as f:
    f.readline()

    for line in f:
        b = line.strip().split(",")
        key = b[2]
        value = b[3].replace('"', "")
        values[key] = value


data = json.dumps(values, separators=(",", ":"))
with open("GTFSMappings/tripTo_route.json", "w") as f:
    f.write(data)

##json.dumps([1,2,3], separators=(","))
