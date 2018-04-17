import selectors
import socket

import pprint


class Future:
    def __init__(self):
        self.result = None
        self._done_callback_fn = None

    def __iter__(self):
        yield self
        return self.result

    def set_result(self, result):
        self.result = result
        if self._done_callback_fn:
            self._done_callback_fn(self)

    def set_done_callback(self, fn):
        self._done_callback_fn = fn


class Task:
    def __init__(self, corn):
        self._corn = corn
        self.step(None)

    def step(self, future):
        result = None
        if future:
            result = future.result

        try:
            future = self._corn.send(result)
            future.set_done_callback(self.step)
        except StopIteration:
            pass


class Fetcher:
    def __init__(self, url):
        self.response = b''  # Empty array of bytes.
        self.url = url
        self.sock = None

    def fetch(self, selector):
        the_socket = socket.socket()
        self.sock = the_socket  # ssl_context.wrap_socket(s)
        self.sock.setblocking(False)
        try:
            self.sock.connect(('xkcd.org', 80))
        except BlockingIOError:
            pass

        connected_future = Future()

        # Register next callback.
        selector.register(self.sock.fileno(),
                          selectors.EVENT_WRITE,
                          lambda *args: connected_future.set_result(None))

        yield from connected_future

        print('connected!')
        selector.unregister(self.sock.fileno())

        yield from self.read_all(selector)

    def read_all(self, selector):
        request = 'GET {0} HTTP/1.0\r\nHost: xkcd.org\r\n\r\n'.format(self.url)
        self.sock.send(request.encode('ascii'))

        while True:
            read_response_future = Future()

            # Register the next callback.
            selector.register(self.sock.fileno(),
                              selectors.EVENT_READ,
                              lambda *args: read_response_future.set_result(self.sock.recv(4096)))

            chunk = yield from read_response_future

            selector.unregister(self.sock.fileno())  # Done reading.

            if chunk:
                self.response += chunk
            else:
                pprint.pprint(self.response)
                break


def loop(selector):
    while True:
        events = selector.select()
        if not events:
            break

        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)


def main():
    selector = selectors.DefaultSelector()

    urls = ['/353/', '/354/', '/355/', '/356/', '/357/', '/358/', '/359/', '/360/', '/361/']
    urls_todo = set(urls)

    # Begin fetching http://xkcd.com/353/
    for url in urls_todo:
        fetcher = Fetcher(url)
        Task(fetcher.fetch(selector))

    loop(selector)


if __name__ == '__main__':
    main()
