import logging
import logging.handlers
import pickle
import socketserver

logger = logging.getLogger(name="udp_server")
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(hdlr=handler)
logger.setLevel(level=logging.DEBUG)


class TestUDPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data, sock = self.request[0], self.request[1]
        data = data[4:]  # remove first 4 bytes
        obj = pickle.loads(data)
        logger.info(msg=str(obj))
        record = logging.makeLogRecord(obj)
        logger.info(msg=str(record))


if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", logging.handlers.DEFAULT_UDP_LOGGING_PORT

        with socketserver.UDPServer(server_address=(HOST, PORT), RequestHandlerClass=TestUDPHandler) as server:
            logger.info(msg=f"Starting UDP server at {HOST}:{PORT}. To close click: `Ctrl + C`.")
            server.serve_forever()
    except KeyboardInterrupt:
        logger.info(msg=f"\nClosing UDP server at {HOST}:{PORT}.")
        exit(code=1)
