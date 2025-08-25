import json
import os
import psycopg2
from dotenv import load_dotenv
import re
import psycopg2.extras
import psycopg
import time
import asyncio
import random

load_dotenv()

with open("GTFSMappings/busTo_stops.json", "r") as fp:
    busTOstops = json.load(fp)

with open("GTFSMappings/stopsTo_stopname.json", "r") as fp:
    stopsTOstopName = json.load(fp)


def getConnection2():
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


async def cleanup(curr):
    curr.execute(f"DELETE FROM bus_stops")
    conn.commit()

async def cleanup2(curr, conn):
    curr.execute(f"DELETE FROM daily_penalty_records;")
    conn.commit()


async def task1(busTOstops, stopsTOstopName, curr, conn):
    for bus_name in busTOstops:
        if "LOOP" in bus_name:
            continue
        stop_sequence = 1
        for stop_id in busTOstops.get(bus_name):
            stop_name = stopsTOstopName.get(stop_id)

            bus_name = " ".join(re.sub(r"[/\-\.]", " ", bus_name).split())

            curr.execute(
                """INSERT INTO bus_stops (stop_id, bus_name, stop_sequence, stop_name) VALUES (%s, %s, %s, %s);""",
                (stop_id, bus_name, stop_sequence, stop_name),
            )
            conn.commit()
            stop_sequence = stop_sequence + 1


async def taskO(busTOstops, stopsTOstopName, curr):
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


async def taskO_1(busTOstops, stopsTOstopName):

    conn2 = getConnection2()
    curr2 = conn2.cursor()
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

    with curr2.copy(
        "COPY bus_stops (stop_id, bus_name, stop_sequence, stop_name) FROM STDIN"
    ) as copy:
        for val in vals:
            copy.write_row(val)
    conn2.commit()


async def task2(busTOstops, curr, conn):

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


async def task2O(busTOstops, curr, conn):
    vals = []
    for x in busTOstops:
        if "LOOP" in x:
            continue
        for y in busTOstops.get(x):
            for i in range(1, 9):

                x = " ".join(re.sub(r"[/\-\.]", " ", x).split())

                vals.append((y, x, f"2025-02-{i}", f"{random.random() * 5:.2f}"))

    psycopg2.extras.execute_batch(
        curr,
        "INSERT into daily_penalty_records (stop_id, bus_name, record_date, penalty) VALUES (%s,%s,%s,%s);",
        vals,
    )
    conn.commit()


async def task2_1(busTOstops):

    conn2 = getConnection2()
    curr2 = conn2.cursor()

    vals = []
    for x in busTOstops:
        if "LOOP" in x:
            continue
        for y in busTOstops.get(x):
            for i in range(1, 9):

                x = " ".join(re.sub(r"[/\-\.]", " ", x).split())

                vals.append((y, x, f"2025-02-{i}", f"{random.random() * 5:.2f}"))

    with curr2.copy(
        "COPY daily_penalty_records (stop_id, bus_name, record_date, penalty) FROM STDIN"
    ) as copy:
        for val in vals:
            copy.write_row(val)
    conn2.commit()


async def main(busTOstops, stopsTOstopName, curr, conn):
    for i in range(3):
        await cleanup(curr)

        startTime = time.perf_counter()
        await task1(busTOstops, stopsTOstopName, curr, conn)
        totalRunning = time.perf_counter() - startTime
        print("Original Query Time: " + str(totalRunning))

        await cleanup(curr)

        startTime = time.perf_counter()
        await taskO(busTOstops, stopsTOstopName, curr)
        totalRunning = time.perf_counter() - startTime
        print("Optimized Query Time: " + str(totalRunning))

        await cleanup(curr)

        startTime = time.perf_counter()
        await taskO_1(busTOstops, stopsTOstopName)
        totalRunning = time.perf_counter() - startTime
        print("Optimized Query2 Time: " + str(totalRunning))
        print("\n")


async def main2(busTOstops, curr, conn):
    for i in range(3):

        await cleanup2(curr, conn)

        startTime = time.perf_counter()
        await task2(busTOstops, curr, conn)
        totalRunning = time.perf_counter() - startTime
        print("Original Query2 Time: " + str(totalRunning))

        await cleanup2(curr, conn)

        startTime = time.perf_counter()
        await task2O(busTOstops, curr, conn)
        totalRunning = time.perf_counter() - startTime
        print("Optimized Query2 Time: " + str(totalRunning))

        await cleanup2(curr, conn)

        startTime = time.perf_counter()
        await task2_1(busTOstops)
        totalRunning = time.perf_counter() - startTime
        print("Optimized Query2.1 Time: " + str(totalRunning))
        print("\n")


asyncio.run(main(busTOstops, stopsTOstopName, curr, conn))
# asyncio.run(main2(busTOstops, curr, conn))
curr.close()
conn.close()
