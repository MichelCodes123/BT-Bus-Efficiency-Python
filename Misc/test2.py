import asyncio
import time


async def my_task(delay, count):
    print("code executed")

    await asyncio.sleep(1)


async def main():

    for i in range(20):
        print(i)
        await asyncio.create_task(my_task(i, i))
        print("wow")


asyncio.run(main())
