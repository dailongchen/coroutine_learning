import asyncio
import random
import aiohttp


async def fetch_async(a):
    url = 'http://httpbin.org/get?a={}'
    async with aiohttp.request('GET', url.format(a)) as r:
        data = await r.json()
    return data['args']['a']


async def collect_result(a):
    return await fetch_async(a)


async def produce(queue):
    for num in random.sample(range(100), 7):
        print('producing {}'.format(num))
        item = (num, num)
        await queue.put(item)
        # await asyncio.sleep(0.3)


async def consume(queue):
    while 1:
        item = await queue.get()
        num = item[0]
        rs = await collect_result(num)
        print('consuming {}...'.format(rs))
        queue.task_done()


async def run():
    queue = asyncio.PriorityQueue()
    consumers = asyncio.ensure_future(consume(queue))

    # queue = asyncio.Queue()
    # consumers = asyncio.ensure_future(asyncio.gather(consume(queue),
    #                                                  consume(queue),
    #                                                  consume(queue)))
    await produce(queue)
    await queue.join()
    consumers.cancel()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
loop.close()
