import asyncio
import pprint
import time


async def do_some_work(x):
    print('Waiting: ', x)

    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)


def main():
    coroutine_1 = do_some_work(1)
    coroutine_2 = do_some_work(2)
    coroutine_3 = do_some_work(2)

    tasks = [
        asyncio.ensure_future(coroutine_1),
        asyncio.ensure_future(coroutine_2),
        asyncio.ensure_future(coroutine_3)
    ]

    def now(): return time.time()
    start = now()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt as e:
        pprint.pprint(asyncio.Task.all_tasks())

        # # method_1, cancel tasks one by one
        # for task in asyncio.Task.all_tasks():
        #     if task.done():
        #         continue
        #     print(task.cancel())

        # method 2, gather tasks and cancel together
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())

        loop.stop()
        loop.run_forever()
    finally:
        loop.close()

    print('TIME: ', now() - start)


if __name__ == '__main__':
    main()
