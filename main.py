import requests
import json, datetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os
import asyncio
import time
import psycopg
import re
import logging
from pprint import pformat

load_dotenv()


def setup_logger(name, log_file, level):

    handler = logging.FileHandler(log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


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


def delay_calc(current_time: str, scheduled_arrival: str) -> int:
    hour_current = int(current_time[0:2])
    hour_sched = int(scheduled_arrival[0:2])

    if hour_current - hour_sched < 0:
        return -1

    ## Bus may be delayed or exactly on time.
    delay = (
        ((hour_current - hour_sched) * 60 * 60)
        + (int(current_time[3:5]) - int(scheduled_arrival[3:5])) * 60
        + (int(current_time[6:8]) - int(scheduled_arrival[6:8]))
    )

    if delay > 0:
        return delay

    return -1


def convert_time_past_twelve(time: str) -> str:
    """
    Brampton Transit's GTFS data recognizes 24, 25,26, and 27, as scheduled arrival times at 12,1,2 and 3am.

    Ex. If the current time is 3am, and a bus is scheduled for this time, then the scheduled arrival time would be 27:00:00. This function converts the current time to match that format so I can still compare the times, and calculate a delay.

    """

    if int(time[0:2]) < 4:
        return str(int(time[0:2]) + 24) + ":" + time[3:5] + ":" + time[6:8]
    return time


def get_current_time() -> str:
    """
    Returns the current time in Toronto (same as Brampton). Wherever this script will run, it will always give accurate times.
    Unsure about how daylight savings works with this method though... find out

    """

    Toronto = ZoneInfo("America/Toronto")
    time = datetime.now(Toronto)
    currTime = f"{time.hour:02d}:{time.minute:02d}:{time.second:2d}"
    return currTime


def get_yesterday_date() -> str:
    Toronto = ZoneInfo("America/Toronto")
    time = datetime.now(Toronto)
    return (time - timedelta(1)).strftime("%Y-%m-%d")


def calculate_penalty(minutes_delayed: int) -> int:
    if minutes_delayed > 30:
        return 0
    elif minutes_delayed > 20:
        return 1
    elif minutes_delayed > 15:
        return 2
    elif minutes_delayed > 10:
        return 3
    elif minutes_delayed > 3:
        return 4
    else:
        return 5


def print_delay(x, totalDelay: int, scheduled_time: str, bus: str, penalty):
    if totalDelay > 0:
        print(
            "This bus is delayed by "
            + str(int(totalDelay / 60))
            + " minutes and "
            + str(totalDelay % 60)
            + " seconds. Penalty is "
            + str(penalty)
        )
        print(
            "The bus "
            + bus
            + ", corresponding to trip "
            + x["vehicle"]["trip"]["trip_id"]
            + " should arrive at "
            + scheduled_time
        )
        print("\n")


def remove_earliest_record(stop_id, bus_name, curr, conn):
    """
    No need to continuously store more than 8 records for a given stop. Remove the earliest
    """
    curr.execute(
        "SELECT from daily_penalty_records WHERE stop_id = %s and bus_name = %s;" "",
        (stop_id, bus_name),
    )
    numrows = curr.rowcount
    if numrows > 7:
        curr.execute(
            """WITH get_recent AS (SELECT * FROM daily_penalty_records Where stop_id = %s and bus_name = %s order by record_date ASC limit 1) DELETE FROM daily_penalty_records as x USING get_recent as y WHERE x.stop_id = y.stop_id and x.bus_name = y.bus_name and x.record_date = y.record_date;""",
            (stop_id, bus_name),
        )
        conn.commit()


# Create function to make sure the api query is the correct trip id


## Remove special characters for bus names
def calculate_daily_penalty(penalty_log: dict, elog):
    """
    Penalty log format: Bus name : {stop : {arrival: penalty }}

    """

    Toronto = ZoneInfo("America/Toronto")
    time = datetime.now(Toronto)

    conn = getConnection()
    if conn != False:
        curr = conn.cursor()
        vals = []

        # Record Log
        dlog = setup_logger("dlog", "records.log", 20)
        dlog.info(time.strftime("%Y-%m-%d") + " " + time.strftime("%H-%M-%S"))
        dlog.info(pformat(penalty_log))

        for bus_name in penalty_log:
            for stop_id in penalty_log.get(bus_name):
                sum = 0

                for penalty in penalty_log.get(bus_name).get(stop_id).values():
                    sum += penalty

                stop_daily_avg = sum / len(
                    penalty_log.get(bus_name).get(stop_id).values()
                )
                record_date = get_yesterday_date()

                remove_earliest_record(stop_id, bus_name, curr, conn)
                vals.append(
                    (
                        stop_id,
                        " ".join(re.sub(r"[/\-\.]", " ", bus_name).split()),
                        record_date,
                        stop_daily_avg,
                    )
                )

        try:
            with curr.copy(
                "COPY daily_penalty_records (stop_id, bus_name, record_date, penalty) FROM STDIN"
            ) as copy:
                for val in vals:
                    copy.write_row(val)
            conn.commit()

            curr.close()
            conn.close()
        except Exception as e:
            elog.error("Issue writing to database")
            elog.error(e)
    else:
        dblog = setup_logger("dblog", "error.log", 40)
        dblog.error("Database connection not found")


def update_delay(data2, tripTORoute, penalty_system, elog):

    Toronto = ZoneInfo("America/Toronto")
    time = datetime.now(Toronto)

    elog.error(time.strftime("%Y-%m-%d") + " " + time.strftime("%H-%M-%S"))
    print(time.strftime("%Y-%m-%d") + " " + time.strftime("%H-%M-%S"))
    url = os.getenv("BT_API")

    try:
        response = requests.get(url)
        data = response.json()
        resp = data.get("entity")

    except Exception as e:
        elog.error("Issue parsing response")
        elog.error(e)
        resp = None

    if resp != None and isinstance(resp, list):
        for x in resp:
            try:
                trip_id = x.get("vehicle").get("trip").get("trip_id")
                bus_key = tripTORoute.get(trip_id)
                stop_id = x.get("vehicle").get("stop_id")
                transit_status = x.get("vehicle").get("current_status")
                stop_sequence = x.get("vehicle").get("current_stop_sequence")

                # Key -> TripID,StopID
                if bus_key == None or trip_id == None or stop_id == None:
                    elog.error("The bus key or trip id or stop id is invalid:")
                    elog.error(pformat(x))
                    elog.info("\n")
                    continue

                key = trip_id + "," + stop_id
                scheduled_time = data2.get(key)

                if scheduled_time == None:
                    continue

                if "LOOP" in bus_key:
                    continue

                currentTime = get_current_time()
                # If the sheduled times are into the next day
                if int(scheduled_time[0:2]) > 23:
                    currentTime = convert_time_past_twelve(currentTime)

                totalDelay = -1

                # Current status field may be missing in place of "current_stop_sequence". Assume presence of "current_stop_sequence" still implies vehicle is in transit.
                if transit_status == "IN_TRANSIT_TO" or stop_sequence != None:
                    totalDelay = delay_calc(currentTime, scheduled_time)

                penalty = calculate_penalty(int(totalDelay / 60))

                # Bus name : {stop : {arrival: penalty }}
                stop_key = stop_id

                if penalty_system.get(bus_key) == None:
                    penalty_system[bus_key] = {stop_key: {scheduled_time: penalty}}
                else:
                    if (penalty_system.get(bus_key).get(stop_key)) == None:
                        penalty_system[bus_key][stop_key] = {scheduled_time: penalty}
                    else:
                        penalty_system[bus_key][stop_key][scheduled_time] = penalty

            except Exception as e:
                elog.info(e)
                elog.info(pformat(x))
                elog.info("\n")


# JSON Format -> TripID,StopID : scheduluedArrivalTime
with open("GTFSMappings/stop_times.json", "r") as fp:
    data2 = json.load(fp)

# JSON Format -> TripID : Bus Route Name
with open("GTFSMappings/tripTo_route.json", "r") as fp:
    tripTORoute = json.load(fp)

penalty_system = {}


elog = setup_logger("elog", "error.log", 40)


async def my_task(data2, tripTORoute, penalty_system, elog):
    delay = 0
    totalRunning = 0

    startTime = time.perf_counter()

    update_delay(data2, tripTORoute, penalty_system, elog)

    totalRunning = time.perf_counter() - startTime

    if totalRunning > 60:
        delay = 0
    else:
        delay = 60 - int(totalRunning)

    await asyncio.sleep(delay)


##Run every minute for 24 hours
async def main(data2, tripTORoute, penalty_system, elog):
    for i in range(1440):
        await my_task(data2, tripTORoute, penalty_system, elog)

    calculate_daily_penalty(penalty_system, elog)


asyncio.run(main(data2, tripTORoute, penalty_system, elog))
