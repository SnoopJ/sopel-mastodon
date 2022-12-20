# coding=utf-8
from html.parser import HTMLParser
import re

import requests

from sopel import plugin


# TODO: this should be configurable
MASTODON_HOSTS = [
    "mastodon.social",
    "hachyderm.io",
]
STATUS_REGEX = r"/(?P<user>@(?P<handle>[^@]+)(@(?P<toot_host>[^/]+))?)/(?P<toot_id>\d+)"
MASTODON_REGEXES = [f"(?P<mastodon_url>https://(?P<host>{host}){STATUS_REGEX})" for host in MASTODON_HOSTS]


@plugin.url(*MASTODON_REGEXES)
def url_status(bot, trigger):
    output_status(bot, trigger)


def toot_details(toot_instance: str, toot_id: int) -> dict:
    response = requests.get(f"https://{toot_instance}/api/v1/statuses/{toot_id}", headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return response.json()


class TootParser(HTMLParser):
    """
    Helper class that drops HTML tags from toots
    """
    def __init__(self):
        super().__init__()

        self.stripped = ""

    def handle_endtag(self, tag):
        # toots include plenty of <p> tags, notably to separate URLs from the rest of the text
        # a simple way to make this look nice on IRC is to stick a space in at the end of a 'paragraph'
        if tag == "p":
            self.stripped += " "

    def handle_data(self, data):
        self.stripped += data


def output_status(bot, trigger):
    host = trigger.group("host")
    toot_id = trigger.group("toot_id")
    url = trigger.group("mastodon_url")

    details = toot_details(host, toot_id)
    user = details["account"]["acct"]

    MAXLEN = 200 - len(url)

    # strip tags out of toot text
    fulltxt = details["content"]
    uri = details["uri"]

    parser = TootParser()
    parser.feed(fulltxt)
    txt = parser.stripped

    summary = txt[:MAXLEN] + ("…" if len(txt) > MAXLEN else "")

    bot.say(f'[Mastodon] @{user}: "{summary}" — {uri}')
