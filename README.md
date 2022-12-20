# sopel-mastodon

A Mastodon plugin for [Sopel](https://sopel.chat/).

This plugin looks for urls of the form `https://host/@user/12345` or `https://host/@user@homehost/12345`
and then tries to query a Mastodon API at `host` for details about the toot in question.

## Installation

```bash
$ pip install git+https://github.com/SnoopJ/sopel-mastodon
```

## Usage

Just send a link to a toot!

```irc
<SnoopJ> check out this toot: https://mastodon.social/@Gargron/1
<terribot> [Mastodon] @Gargron: "Hello world " — https://mastodon.social/users/Gargron/statuses/1
```
