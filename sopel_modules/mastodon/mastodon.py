# coding=utf-8
from html.parser import HTMLParser
import re

import requests

from sopel import plugin


STATUS_REGEX = r"/(?P<user>@(?P<handle>[^@]+)(@(?P<toot_host>[^/]+))?)/(?P<toot_id>\d+)"
MASTODON_REGEX = f"(?P<mastodon_url>https://(?P<host>.*){STATUS_REGEX})"
MASTODON_PLUGIN_PREFIX = "[mastodon] "


@plugin.url(MASTODON_REGEX)
@plugin.output_prefix(MASTODON_PLUGIN_PREFIX)
def url_status(bot, trigger):
    output_status(bot, trigger)


def toot_details(toot_instance: str, toot_id: int) -> dict:
    # TODO: maybe we should send a request with `Accept: application/ld+json; profile="https://www.w3.org/ns/activitystreams"`
    # instead and pull the relevant data out of the response? The Mastodon API is working fine for now and provides some more
    # rich information
    response = requests.get(f"https://{toot_instance}/api/v1/statuses/{toot_id}", headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return response.json()


class TootParser(HTMLParser):
    """
    Helper class that drops HTML tags from toots
    """
    def __init__(self):
        super().__init__()

        self.text = ""

    def handle_endtag(self, tag):
        # toots include plenty of <p> tags, notably to separate URLs from the rest of the text
        # a simple way to make this look nice on IRC is to stick a space in at the end of a 'paragraph'
        if tag == "p":
            self.text += " "

    def handle_data(self, data):
        self.text += data


def output_status(bot, trigger):
    host = trigger.group("host")
    toot_id = trigger.group("toot_id")
    url = trigger.group("mastodon_url")

    try:
        details = toot_details(host, toot_id)
    except:
        return False
    user = details["account"]["acct"]

    MAXLEN = 200 - len(url)

    # strip tags out of toot text
    fulltxt = details["content"]
    url = details["url"]

    parser = TootParser()
    parser.feed(fulltxt)
    txt = parser.text.rstrip()

    summary = txt[:MAXLEN] + ("…" if len(txt) > MAXLEN else "")

    bot.say(f'@{user}: "{summary}" — {url}')
