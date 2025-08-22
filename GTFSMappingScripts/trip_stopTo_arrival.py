import json


##This script takes the GTFS stop_times.txt file and converts it to a JSON file that matches a tripID and StopID key to a specified time of scheduled arrival.
## If I know the trip, and where it should stop next, then I know the time that it should get there.
myFile = []

values = {}
with open("Google_Transit/stop_times.txt", "r") as f:
    f.readline()

    for line in f:
        b = line.strip().split(",")
        key = b[0] + "," + b[3]
        value = b[1]
        values[key] = value


data = json.dumps(values, separators=(",", ":"))
with open("GTFSMappings/stop_times.json", "w") as f:
    f.write(data)

##json.dumps([1,2,3], separators=(","))
