# sopel-mastodon

A Mastodon plugin for [Sopel](https://sopel.chat/).

**NOTE:** this plugin currently uses a tiny hard-coded list of Mastodon
instance hostnames (just `mastodon.social` and `hachyderm.io`), so it needs
some customization to work with other instances. I plan to make the list of
hosts configurable the next time I work on this plugin

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
