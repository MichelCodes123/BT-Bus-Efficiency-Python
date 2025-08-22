import asyncio
import time



async def my_task():
    delay = 0
    totalRunning = 5


    startTime = time.perf_counter()
    ##Code
    totalRunning = time.perf_counter() - startTime
    if totalRunning > 60:
        delay = 0
    else:
        delay = int(totalRunning)

    await asyncio.sleep(delay)


async def main(dict):
    for i in range(1440):
        await my_task()



asyncio.run(main(dict))
