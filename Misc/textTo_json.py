import json

##Converts text file to JSON and writes to a specified file.

myFile = []
x = 0

with open("Google_Transit/stop_times.txt", "r") as f:
    titles = f.readline().strip().split(",")

    for line in f:
        b = line.strip().split(",")
        values = {}
        for i in range(len(titles)):
            values[titles[i]] = b[i]

        myFile.append(values)

data = json.dumps(myFile, separators=(",", ":"))
with open("GTFSMappings/stop_times.json", "w") as f:
    f.write(data)

##json.dumps([1,2,3], separators=(","))
