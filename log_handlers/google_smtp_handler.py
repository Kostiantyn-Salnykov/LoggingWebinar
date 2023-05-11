import email.policy
import logging.handlers
import smtplib
from email.message import EmailMessage
from email.utils import formatdate


class TLS_SMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_SSL_PORT

            with smtplib.SMTP(host=self.mailhost, port=port) as smtp:
                msg = self.format(record=record)
                email_message = EmailMessage()
                email_message["Subject"] = self.subject
                email_message["From"] = self.fromaddr
                to = ", ".join(self.toaddrs) if isinstance(self.toaddrs, list) else self.toaddrs
                email_message["To"] = to
                email_message["Date"] = formatdate()
                email_message.set_content(msg)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(user=self.username, password=self.password)
                smtp.sendmail(
                    from_addr=self.fromaddr,
                    to_addrs=self.toaddrs,
                    msg=email_message.as_bytes(policy=email.policy.SMTP),
                )
        except (KeyboardInterrupt, SystemExit) as error:
            logging.warning(msg=str(error))
            raise
        except Exception as error:
            self.handleError(record=record)
            logging.warning(msg=str(error))
