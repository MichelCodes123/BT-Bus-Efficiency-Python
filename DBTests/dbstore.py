import json
import os
import psycopg2
from dotenv import load_dotenv
import re
import psycopg2.extras

load_dotenv()

with open("GTFSMappings/busTo_stops.json", "r") as fp:
    busTOstops = json.load(fp)

with open("GTFSMappings/stopsTo_stopname.json", "r") as fp:
    stopsTOstopName = json.load(fp)


# Dont push this, use env key
def getConnection():
    try:
        return psycopg2.connect(
            database=os.getenv("DB_NAME"),
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

curr.execute("DROP Table bus_stops;")
curr.execute(
    """CREATE TABLE bus_stops(
    stop_id varchar(10),
    bus_name varchar(50),
    stop_sequence smallint,
    stop_name varchar (100),
    PRIMARY KEY(stop_id, bus_name, stop_sequence)
);"""
)

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


psycopg2.extras.execute_batch(
    curr,
    "INSERT INTO bus_stops (stop_id, bus_name, stop_sequence, stop_name) VALUES (%s, %s, %s, %s);",
    tuple(vals),
)

curr.close()
conn.close()
