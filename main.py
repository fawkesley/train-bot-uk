#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import logging
import sys
import textwrap
import os

import tweepy

_CONSUMER_KEY = os.environ['CONSUMER_KEY']
_CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
_ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
_ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


def main():
    logging.basicConfig(level=logging.INFO)
    auth = tweepy.auth.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
    auth.set_access_token(_ACCESS_TOKEN, _ACCESS_TOKEN_SECRET)

    stream = tweepy.Stream(auth, CustomStreamListener(tweet_callback))
    stream.filter(track=KEYWORDS)  # blocking function


def tweet_callback(status):
    #print('%s:  "%s" (%s via %s)\n' % (status.author.screen_name,
    #                                   status.text,
    #                                   status.created_at,
    #                                   status.source))
    for i, hashtag in enumerate(KEYWORDS):
        if hashtag.lower() in status.text.lower():
            for line in textwrap.wrap('{}'.format(status.text)):
                print(line)
            print('    - @{}\n'.format(status.author.screen_name))
            #print("'{}' in @{}: {}".format(
            #    hashtag, status.author.screen_name, status.text))


class CustomStreamListener(tweepy.StreamListener):

    def __init__(self, callback=None):
        self.callback = callback
        super(CustomStreamListener, self).__init__()

    # Alternatively, override on_data instead (then on_status won't be called)

    def on_status(self, status):
        if self.callback is not None:
            self.callback(status)

    def on_error(self, status_code):
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
