import json

with open("GTFSMappings/tripTo_route.json", "r") as fp:
    data = json.load(fp)


values = {}
stops = []
current_bus = ""
with open("Google_Transit/stop_times.txt", "r") as f:
    # Skip header
    f.readline()

    # Store first line
    firstLine = f.readline().strip().split(",")
    current_bus = data.get(firstLine[0])
    stops.append(firstLine[3])

    # Start reading from second entry
    # May need to optimize the script, right now I could potentially be setting the same bus multiple times.
    for line in f:
        b = line.strip().split(",")

        if b[4] == "1":
            values[current_bus] = stops
            current_bus = data.get(b[0])
            stops = []

        stops.append(b[3])

    # Captures last entry in the file
    values[current_bus] = stops

data2 = json.dumps(values, separators=(",", ":"))
with open("GTFSMappings/busTo_stops.json", "w") as f:
    f.write(data2)
