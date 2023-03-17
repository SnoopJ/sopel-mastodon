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
    response = requests.get(f"https://{toot_instance}/api/v1/statuses/{toot_id}", headers={"Accept": 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'})
    response.raise_for_status()
    details = response.json()

    return details


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

    MAXLEN = (
        # maximum length of line sent to server, including command/etc.
        512 -
        # whatever it takes to send this PRIVMSG
        len(f"PRIVMSG {trigger.sender!s} :\r\n") -
        # allowance for this plugin's prefix
        len(MASTODON_PLUGIN_PREFIX) -
        # this calculation should be exact but doesn't seem to be, so here's some arbitrary additional margin
        42
    )

    fulltxt = details.get("content", "")

    attachments = details.get("media_attachments", [])
    N_attached = len(attachments)
    if N_attached == 1:
        attach_msg = "[attachment] "
    elif N_attached > 1:
        attach_msg = f"[{N_attached} attachments] "
    else:
        attach_msg = ""

    parser = TootParser()
    parser.feed(fulltxt)
    txt = parser.text.rstrip()

    msg = f"@{user}: {attach_msg}"
    if txt:
        msg += " «{txt}»"
    else:

    if len(msg) > MAXLEN:
        msg = msg[:MAXLEN-3] + "…»"

    bot.say(msg)
