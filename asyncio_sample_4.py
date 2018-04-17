import asyncio


async def consumer(cond, name, second):
    await asyncio.sleep(second)
    with await cond:
        await cond.wait()
        print('{}: Resource is available to consumer'.format(name))


async def producer1(cond):
    print('run producer1')
    await asyncio.sleep(2)
    with await cond:
        n = 2
        print('notifying {} consumers'.format(n))
        cond.notify(n)


async def producer2(cond):
    print('run producer2')
    await asyncio.sleep(2)
    with await cond:
        print('notifying all consumers')
        cond.notify_all()


async def main(the_loop):
    condition = asyncio.Condition()

    task = the_loop.create_task(producer1(condition))
    consumers = [consumer(condition, name, index)
                 for index, name in enumerate(('c1', 'c2'))]
    await asyncio.wait(consumers)
    task.cancel()

    task = the_loop.create_task(producer2(condition))
    consumers = [consumer(condition, name, index)
                 for index, name in enumerate(('c1', 'c2'))]
    await asyncio.wait(consumers)
    task.cancel()


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
