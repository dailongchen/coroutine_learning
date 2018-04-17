import asyncio
import aiohttp
import re


class Clawler:
    def __init__(self, max_redirect):
        self._crawl_id = 0

        self._max_redirect = max_redirect
        self._url_queue = None
        self._client_session = None

        self._seen_urls = set()

    async def _save(self, data):
        pass

    async def _load(self, url):
        if url in self._seen_urls:
            return

        print(url)
        self._seen_urls.add(url)

        async with self._client_session.request('GET', url) as response:
            data = await response.text()
        return data

    def _fetch_url(self, text):
        urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''',
                              text))
        for url in urls:
            if url.startswith('http'):
                self._url_queue.put_nowait(url)

    async def _crawl(self):
        self._crawl_id += 1
        this_crawl_id = self._crawl_id

        while True:
            try:
                url = await self._url_queue.get()
                self._fetch_url(await self._load(url))
            finally:
                try:
                    self._url_queue.task_done()
                except ValueError:
                    print('Clawler_{} is done'.format(this_crawl_id))
                    await self._client_session.close()

    async def run(self):
        self._url_queue = asyncio.Queue()

        tcp_connector = aiohttp.TCPConnector(verify_ssl=False)

        self._client_session = aiohttp.ClientSession(connector=tcp_connector)

        tasks = [asyncio.ensure_future(self._crawl()) for _ in range(5)]

        await self._url_queue.put('https://www.google.com')

        await self._url_queue.join()
        asyncio.gather(*tasks).cancel()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Clawler(5).run())
        loop.close()
    except KeyboardInterrupt:
        pass
