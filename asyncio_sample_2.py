import asyncio


async def work(q):
    while True:
        i = await q.get()
        try:
            print(i, 'q.qsize(): ', q.qsize())
        finally:
            q.task_done()


async def run():
    q = asyncio.Queue()

    # can be simplified to: [q.put(i) for i in range(10)]
    put_futures = []
    for i in range(10):
        put_futures.append(q.put(i))  # put is a coroutine, so cannot promise the put sequence

    await asyncio.wait(put_futures)

    tasks = [asyncio.ensure_future(work(q))]
    print('wait join')
    await q.join()
    print('end join')

    asyncio.gather(*tasks).cancel()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
