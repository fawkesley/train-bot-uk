#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import sys
import threading
import os

import tweepy

HASHTAGS = ['#IoT', 'python']


_CONSUMER_KEY = os.environ['CONSUMER_KEY']
_CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
_ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
_ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


TIMERS = {}


def main():
    auth = tweepy.auth.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
    auth.set_access_token(_ACCESS_TOKEN, _ACCESS_TOKEN_SECRET)
    #api = tweepy.API(auth)

    stream = tweepy.Stream(auth, CustomStreamListener(tweet_callback))
    stream.filter(None, HASHTAGS)  # blocking function


def tweet_callback(status):
    #print('%s:  "%s" (%s via %s)\n' % (status.author.screen_name,
    #                                   status.text,
    #                                   status.created_at,
    #                                   status.source))
    for i, hashtag in enumerate(HASHTAGS):
        if hashtag.lower() in status.text.lower():
            print("'{}' in tweet".format(hashtag))
            turn_on_five_seconds(i)
        else:
            print("'{}' NOT in: {}".format(hashtag, status.text))


def turn_on_five_seconds(i):
    existing_timer = TIMERS.get(i)
    if existing_timer:
        existing_timer.cancel()

    turn_on_now(i)
    TIMERS[i] = threading.Timer(5, turn_off_now, [i])
    TIMERS[i].start()


def turn_on_now(i):
    print("ON: {}".format(i))


def turn_off_now(i):
    print("OFF: {}".format(i))


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
