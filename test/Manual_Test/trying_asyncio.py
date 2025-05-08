# This was used to investigate using asyncio and how that would look
# before implementing it, and is meant to be run directly.

import asyncio

##############################################################################################
##                                                                                          ##
## The following code is based heavily on the following article:                            ##
## https://www.geeksforgeeks.org/asyncio-in-python/                                         ##
##                                                                                          ##
##############################################################################################

# async def fn():
    
#     print("one")
#     await asyncio.sleep(1)
#     await fn2()
#     print('four')
#     await asyncio.sleep(1)
#     print('five')
#     await asyncio.sleep(1)

# async def fn2():
#     await asyncio.sleep(1)
#     print("two")
#     await asyncio.sleep(1)
#     print("three")
# asyncio.run(fn())
# print("delay")
# asyncio.run(fn())

############### Use these functions for the next section ###############
async def print_time(num_sec:int):
    for time in range(num_sec+1):
        print(f"--> Time: {time} sec")
        await asyncio.sleep(1)

async def print_short_time(num_time_sec:int):
    num_time_sec *= 10
    for time in range(num_time_sec):
        print(f"> ShortTime: {time*0.1} sec")
        await asyncio.sleep(0.1)
########################################################################

#asyncio.run( asyncio.gather(*tasks) ) # I added asyncio.run to make sure that the async experiements were run at this point
#            # Maybe figure out task groups. See https://docs.python.org/3/library/asyncio-task.html#coroutines-and-tasks

# async def messing_with_time_1():
#     #Because of await these are evaluated in the exact order they are written in.
#     await print_time(3)
#     await print_short_time(1)
#     print("calls finished")
#     await print_time(3)

# asyncio.run(messing_with_time_1())


# async def messing_with_time_2():
#     #Because create tasks, all calls are performed asyncronously, but since we don't await they don't finish execution and exit prematurely.
#     task1=asyncio.create_task(print_time(3))
#     task2=asyncio.create_task(print_short_time(1))
#     print("calls finished")
#     task3=asyncio.create_task(print_time(3))

# asyncio.run(messing_with_time_2())


# async def messing_with_time_3():
#     #Because create tasks, all calls are performed asyncronously, but now we awaited ensuring that they finish execution before we leave the function.
#     task1=asyncio.create_task(print_time(3))
#     task2=asyncio.create_task(print_short_time(1))
#     print("calls finished")
#     task3=asyncio.create_task(print_time(3))
#     await task1
#     await task2
#     await task3

# asyncio.run(messing_with_time_3())


# async def messing_with_time_4():
#     #Same functionality as *_3, except using gather.
#     print("calls started")
#     await asyncio.gather(
#         print_time(3),
#         print_short_time(1),
#         print_time(3)
#     )
#     print("calls finished")

# asyncio.run(messing_with_time_4())

##############################################################################################################
##                                                                                                          ##
## The following code is based heavily on the following article:                                            ##
## https://www.dataleadsfuture.com/combining-multiprocessing-and-asyncio-in-python-for-performance-boosts/  ##
## https://pypi.org/project/aioprocessing/   (NOT THIS ONE- Interesting Alternative)                        ##
## https://pypi.org/project/aiomultiprocess/                                                                ##
## A good CLI progressbar implementation:                                                                   ##
## https://pypi.org/project/tqdm/                                                                           ##
## https://github.com/tqdm/tqdm                                                                             ##
##                                                                                                          ##
##############################################################################################################

async def messing_with_time_5():
    #Same functionality, another syntax, using tasks with gather.
    tasks = []
    tasks.append(asyncio.create_task(print_time(3)))
    tasks.append(asyncio.create_task(print_short_time(1)))
    print("calls finished")
    tasks.append(asyncio.create_task(print_time(3)))
    await asyncio.gather(*tasks)

asyncio.run(messing_with_time_5())