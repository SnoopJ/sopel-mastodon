# coding=utf-8
from collections import namedtuple
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
    status = get_status_parts(trigger)

    if not status:
        # silently fail
        # TODO: *maybe* log this? don't want IRC output
        return

    if status.num_attachments == 1:
        attach_msg = " [attachment] "
    elif status.num_attachments > 1:
        attach_msg = f" [{status.num_attachments} attachments] "
    else:
        attach_msg = " "

    if status.text:
        bot.say(f'@{status.user}:{attach_msg}«{status.text}', truncation='…', trailing='»')
    else:
        bot.say(f'@{status.user}{attach_msg}')


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
        if tag == "p" or tag == "br":
            self.text += " "

    def handle_data(self, data):
        self.text += data


ParsedToot = namedtuple('ParsedToot', ['user', 'text', 'num_attachments'])
"""Helper type that holds the fields of a parsed toot"""


def get_status_parts(trigger) -> namedtuple:
    host = trigger.group("host")
    toot_id = trigger.group("toot_id")
    url = trigger.group("mastodon_url")

    try:
        details = toot_details(host, toot_id)
    except:
        return ()

    user = details["account"]["acct"]

    fulltxt = details.get("content", "")

    attachments = details.get("media_attachments", [])

    parser = TootParser()
    parser.feed(fulltxt)
    txt = parser.text.rstrip()

    return ParsedToot(user=user, text=txt, num_attachments=len(attachments))
