import asyncio
import selectors
import socket
import ssl


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.check_hostname = False
ssl_context.load_default_certs()

selector = selectors.DefaultSelector()

# urls = ['/353/', '/354/', '/355/']
urls = ['/']
urls_todo = set(urls)

stopped = False


class Fetcher:
    def __init__(self, url):
        self.response = b''  # Empty array of bytes.
        self.url = url
        self.sock = None

    def fetch(self):
        s = socket.socket()
        self.sock = s  # ssl_context.wrap_socket(s)
        self.sock.setblocking(False)
        try:
            self.sock.connect(('www.baidu.org', 80))
        except BlockingIOError:
            pass

        connected_future = asyncio.Future()

        def connected(key, mask):
            connected_future.set_result(None)

        # Register next callback.
        selector.register(self.sock.fileno(),
                          selectors.EVENT_WRITE,
                          connected)

        yield connected_future

        print('connected!')
        selector.unregister(self.sock.fileno())

        request = 'GET {0} HTTP/1.0\r\nHost: www.baidu.org\r\n\r\n'.format(self.url)
        self.sock.send(request.encode('ascii'))

        the_sock = self.sock
        global stopped

        while True:
            read_response_future = asyncio.Future()

            def read_response(key, mask):
                read_response_future.set_result(the_sock.recv(4096))  # 4k chunk size.

            # Register the next callback.
            selector.register(self.sock.fileno(),
                              selectors.EVENT_READ,
                              read_response)

            chunk = yield read_response_future
            if chunk:
                self.response += chunk
            else:
                selector.unregister(self.sock.fileno())  # Done reading.

                print(self.response)

                urls_todo.remove(self.url)
                if not urls_todo:
                    stopped = True

                break


def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)


# Begin fetching http://xkcd.com/353/
for url in urls_todo:
    fetcher = Fetcher(url)
    next(fetcher.fetch())

loop()
