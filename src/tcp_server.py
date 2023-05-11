import logging
import logging.handlers
import pickle
import socketserver
import struct

logger = logging.getLogger(name="tcp_server")
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(hdlr=handler)
logger.setLevel(level=logging.DEBUG)


class TestTCPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            full_len = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(full_len)
            while len(chunk) < full_len:
                chunk = chunk + self.connection.recv(full_len - len(chunk))
            obj = pickle.loads(chunk)
            logger.info(msg=str(obj))
            record = logging.makeLogRecord(obj)
            logger.info(msg=str(record))


class TestTCPServer(socketserver.ThreadingTCPServer):
    ...


if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", logging.handlers.DEFAULT_TCP_LOGGING_PORT

        with TestTCPServer(server_address=(HOST, PORT), RequestHandlerClass=TestTCPHandler) as server:
            logger.info(msg=f"Starting TCP server at {HOST}:{PORT}. To close click: `Ctrl + C`.")
            server.serve_forever()
    except KeyboardInterrupt:
        logger.info(msg=f"\nClosing TCP server at {HOST}:{PORT}.")
        exit(code=1)
