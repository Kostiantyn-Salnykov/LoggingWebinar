import json
import logging.handlers

from loggers import format_time


class SlackHandler(logging.handlers.HTTPHandler):
    def emit(self, record: logging.LogRecord) -> None:
        self.format(record=record)
        json_data = json.dumps(
            {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"⏰{format_time(record=record)}❗", "emoji": True},
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"\n📶Level: *{record.levelname}*;\n 📝Message: {record.message}.",
                        },
                    },
                ]
            }
        )
        try:
            https_connection = self.getConnection(host=self.host, secure=self.secure)
            https_connection.putrequest(method=self.method, url=self.url)
            if self.method == "POST":
                https_connection.putheader("Content-Type", "application/json")
                https_connection.putheader("Content-Length", str(len(json_data)))
                https_connection.endheaders()
                https_connection.send(data=json_data.encode(encoding="utf-8"))
            https_connection.getresponse()
        except Exception:
            self.handleError(record=record)
