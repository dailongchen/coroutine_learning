import pprint
import selectors
import socket


class Fetcher:
    def __init__(self, url, selector):
        self.response = b''  # Empty array of bytes.
        self.url = url
        self.selector = selector

    def fetch(self):
        sock = socket.socket()
        sock.setblocking(False)
        try:
            sock.connect(('xkcd.org', 80))
        except BlockingIOError:
            pass

        # Register next callback.
        self.selector.register(sock,
                               selectors.EVENT_WRITE,
                               self.connected)

    def connected(self, sock, mask):
        print('connected!')
        self.selector.unregister(sock)
        request = 'GET {} HTTP/1.0\r\nHost: xkcd.org\r\n\r\n'.format(self.url)
        sock.send(request.encode('ascii'))

        # Register the next callback.
        self.selector.register(sock,
                               selectors.EVENT_READ,
                               self.read_response)

    def read_response(self, sock, mask):
        global stopped

        chunk = sock.recv(4096)  # 4k chunk size.
        if chunk:
            self.response += chunk
        else:
            self.selector.unregister(sock)  # Done reading.

            pprint.pprint(self.response)


def loop(selector):
    while True:
        events = selector.select()
        if not events:
            break

        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key.fileobj, event_mask)


def main():
    selector = selectors.DefaultSelector()
    urls_todo = set(['/353/', '/354/', '/355/', '/356/', '/357/', '/358/', '/359/', '/360/', '/361/'])

    for url in urls_todo:
        fetcher = Fetcher(url, selector)
        fetcher.fetch()

    loop(selector)


if __name__ == '__main__':
    main()

