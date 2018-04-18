import asyncio
import aiohttp
import re
import sys
import urllib


class RequestItem:
    _item_id = 0

    def __init__(self, url, max_redirect=10, chunk_size=4096):
        RequestItem._item_id += 1
        self.id = RequestItem._item_id

        self.url = url
        self.chunk_size = chunk_size

        self._max_redirect = max_redirect
        self.redirect_history = []

        self._body_cache = b''

    def __lt__(self, other):
        return self.id < other.id

    def received(self, chunk):
        self._body_cache += chunk

    def text(self, encoding='utf-8'):
        return self._body_cache.decode(encoding=encoding, errors='ignore')

    def to_redirect(self, location):
        self.redirect_history.append(location)
        self.url = location
        return len(self.redirect_history) <= self._max_redirect

    def done(self, crawler: object) -> object:
        pass


class Crawler:
    def __init__(self):
        self._crawl_id = 0

        self._semaphore = asyncio.Semaphore(10)

        self._request_queue = None
        self._client_session = None

        self._seen_urls = set()

    async def _load(self, request_item):
        with await self._semaphore:
            url = request_item.url
            if url in self._seen_urls:
                return

            print(url)
            self._seen_urls.add(url)

            try:
                async with self._client_session.request('GET', url, allow_redirects=False, timeout=60) as response:
                    if 'location' in response.headers:
                        next_url = response.headers['location']

                        if not next_url.startswith('http'):
                            next_url = urllib.parse.urljoin(url, next_url)
                            urllib.parse.quote(next_url)

                        if request_item.to_redirect(next_url):
                            self.add_request(request_item)
                    elif response.status == 200:
                        while True:
                            chunk = await response.content.read(request_item.chunk_size)
                            if not chunk:
                                break
                            request_item.received(chunk)
                        request_item.done(self)
            except asyncio.TimeoutError:
                print('error: timeout. {}'.format(url))
            except [aiohttp.client_exceptions.ClientResponseError,
                    aiohttp.client_exceptions.ClientOSError] as exc:
                print('error: {0}. {1}'.format(exc, url))
            except:
                exc_tuple = sys.exc_info()
                print('error: {0}, {1}. {2}'.format(exc_tuple[0], exc_tuple[1], url))
                raise

    async def _crawl(self):
        self._crawl_id += 1
        this_crawl_id = self._crawl_id

        while True:
            try:
                request = await self._request_queue.get()
                await self._load(request)
            finally:
                try:
                    self._request_queue.task_done()
                except ValueError:
                    print('Clawler_{} is done'.format(this_crawl_id))

    async def close(self):
        await self._client_session.close()

    def add_request(self, request_item):
        self._request_queue.put_nowait(request_item)

    async def run(self, request_item):
        self._request_queue = asyncio.PriorityQueue()

        tcp_connector = aiohttp.TCPConnector(verify_ssl=False)
        self._client_session = aiohttp.ClientSession(connector=tcp_connector)

        tasks = [asyncio.ensure_future(self._crawl()) for _ in range(5)]

        await self._request_queue.put(request_item)

        await self._request_queue.join()
        asyncio.gather(*tasks).cancel()

        await self.close()


class MyRequest(RequestItem):
    def __init__(self, url):
        RequestItem.__init__(self, url)

    def _fetch_url(self):
        urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''',
                              self.text()))
        for url in urls:
            if url.startswith('http'):
                yield url

    def done(self, crawler: object) -> object:
        for url in self._fetch_url():
            crawler.add_request(MyRequest(url))


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Crawler().run(MyRequest('http://xkcd.org')))
        loop.close()
    except KeyboardInterrupt:
        pass
