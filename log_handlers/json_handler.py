import json
import logging.handlers


class JSONHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord):
        try:
            msg = json.dumps(record.__dict__)  # dumps LogRecord to JSON
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
