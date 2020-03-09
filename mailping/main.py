#!/usr/bin/env python3
import uuid
from textwrap import dedent

from dynaconf import settings
import logging, imapclient
from pysigset import suspended_signals
from signal import SIGINT, SIGTERM
import smtplib
import email.utils


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)

class MailPinger:
    def __init__(self):
        self.imap_client = None

    def run(self):
        self.imap_client = imapclient.IMAPClient(settings.IMAP_HOSTNAME, port=settings.IMAP_PORT, ssl=settings.IMAP_SSL)
        self.imap_client.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)

        self.imap_client.debug = settings.IMAP_DEBUG

        known_mails = set()
        first_run = True

        while True:
            mail_info = set()
            select_info = self.imap_client.select_folder("INBOX")
            if select_info[b"EXISTS"]:
                messages = self.imap_client.search(["NOT", "DELETED", "NOT", "SEEN"])

                with suspended_signals(SIGINT, SIGTERM):
                    response = self.imap_client.fetch(messages, ["ENVELOPE"])

                    for msgid, data in response.items():
                        envelope = data[b"ENVELOPE"]

                        mail_info.add(
                            "{:%Y-%m-%d %H:%M:%S} - {}".format(
                                envelope.date,
                                envelope.subject[:30].decode("us-ascii", errors="replace")
                            )
                        )

                new_mails = mail_info.difference(known_mails)

                if new_mails and not first_run:

                    subject = "{0} neue Mail(s) eingegangen".format(len(new_mails))
                    message = "Folgende Mails sind dazugekommen\n\n" + (
                        "\n  * ".join(sorted(list(new_mails)))
                    ) + "\n"


                    if settings.SMTP_SSL:
                        smtpfactory = smtplib.SMTP_SSL
                    else:
                        smtpfactory = smtplib.SMTP
                    smtp_con = smtpfactory(host=settings.SMTP_HOSTNAME, port=settings.SMTP_PORT)
                    if settings.SMTP_STARTTLS:
                        smtp_con.starttls()

                    smtp_con.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

                    smtp_con.sendmail(
                        to_addrs=[settings.NOTIFICATION_TO],
                        from_addr=settings.NOTIFICATION_FROM,
                        msg=dedent("""\
                        From: {from_}
                        To: {to}
                        Date: {date}
                        Message-ID: {msgid}
                        Subject: {subject}
                        
                        {message}
                        """).format(
                            from_=settings.NOTIFICATION_FROM,
                            to=settings.NOTIFICATION_TO,
                            date=email.utils.formatdate(),
                            msgid=str(uuid.uuid4())+"."+settings.NOTIFICATION_FROM,
                            subject=subject,
                            message=message,
                        ),
                    )

                    smtp_con.quit()

                known_mails = mail_info
                first_run = False

            self.imap_client.idle()
            self.imap_client.idle_check(
                timeout=300
            )  # Do a normal poll every 5 minutes, just in case
            self.imap_client.idle_done()

    def cleanup(self):
        if self.imap_client:
            self.imap_client = None


def main():
    mp =MailPinger()
    try:
        mp.run()
    finally:
        mp.cleanup()


if __name__ == "__main__":
    main()
