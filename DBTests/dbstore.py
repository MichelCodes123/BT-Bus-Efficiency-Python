import json
import os
import psycopg2
from dotenv import load_dotenv
import re
import psycopg2.extras
import psycopg

load_dotenv()

with open("GTFSMappings/busTo_stops.json", "r") as fp:
    busTOstops = json.load(fp)

with open("GTFSMappings/stopsTo_stopname.json", "r") as fp:
    stopsTOstopName = json.load(fp)


# Dont push this, use env key
def getConnection():
    try:
        return psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("USER_NAME"),
            password=os.getenv("PASS"),
            host=os.getenv("HOST_NAME"),
            port=os.getenv("PORT_NUM"),
        )
    except:
        "Error"
        return False


conn = getConnection()
curr = conn.cursor()

vals = []
for bus_name in busTOstops:
    if "LOOP" in bus_name:
        continue
    stop_sequence = 1
    for stop_id in busTOstops.get(bus_name):
        stop_name = stopsTOstopName.get(stop_id)

        bus_name = " ".join(re.sub(r"[/\-\.]", " ", bus_name).split())

        vals.append((stop_id, bus_name, stop_sequence, stop_name))

        stop_sequence = stop_sequence + 1

with curr.copy(
    "COPY bus_stops (stop_id, bus_name, stop_sequence, stop_name) FROM STDIN"
) as copy:
    for val in vals:
        copy.write_row(val)

conn.commit()

curr.close()
conn.close()
