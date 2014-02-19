
####################################################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: Trying to figure out how to run async non blocking tasks with asyncio
#  Author: Aidan Fowler
#  Assumes:
#  Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Wednesday February 19th
#####################################################################################################

import asyncio

loop = asyncio.get_event_loop()

chunk = [5,4,3,2,1,6]

global future
future = None

def sort_me(chunk, future):
    future.set_result(sorted(chunk))

def create_future(chunk):
    f = asyncio.Future()
    loop.call_soon(sort_me, chunk, f)
    global future
    future = f
    return f

@asyncio.coroutine
def run():
    global future
    yield from create_future(chunk)
    print("future:",future)

def run2():
    global future
    yield from create_future(chunk)
    print("future:",future)

def main():
    print("TRY 1:")
    loop.run_until_complete(run())
    print("TRY 2:")
    run2()
    print("TRY 3:")
    loop.run_until_complete(run2())

main()