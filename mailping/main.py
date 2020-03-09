#!/usr/bin/env python3
from dynaconf import settings
import logging, imapclient
from pysigset import suspended_signals
from signal import SIGINT, SIGTERM


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

        while True:
            select_info = self.imap_client.select_folder("INBOX")
            if select_info[b"EXISTS"]:
                messages = self.imap_client.search(["NOT", "DELETED", "NOT", "SEEN"])

                with suspended_signals(SIGINT, SIGTERM):
                    response = self.imap_client.fetch(messages, ["ENVELOPE"])

                    for msgid, data in response.items():
                        envelope = data[b"ENVELOPE"]
                        print(envelope)

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
