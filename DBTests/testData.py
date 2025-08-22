import json
import os
import random
import psycopg2
from dotenv import load_dotenv
import re

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

curr.execute(f"DELETE FROM daily_penalty_records;")
conn.commit()


for x in busTOstops:
    if "LOOP" in x:
        continue
    for y in busTOstops.get(x):
        for i in range(1, 9):

            x = " ".join(re.sub(r"[/\-\.]", " ", x).split())
            curr.execute(
                """INSERT into daily_penalty_records (stop_id, bus_name, record_date, penalty) VALUES (%s,%s,%s,%s);""",
                (y, x, f"2025-02-{i}", f"{random.random() * 5:.2f}"),
            )
            conn.commit()

curr.close()
conn.close()
