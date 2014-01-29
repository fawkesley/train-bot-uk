#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import datetime
import logging
import os
import re
import sys
import textwrap
import threading
import HTMLParser

import tweepy

import uktrains


_MY_NAME = os.environ.get('MY_NAME', '@TestAccount')

_API = None


class ReplyHandlerThread(threading.Thread):
    def __init__(self, tweet):
        threading.Thread.__init__(self)
        self.tweet = tweet

    def run(self):
        try:
            message = strip_screen_names(self.tweet.text)
            response = make_response_message(message)

            if response is not None:
                logging.info("Responding: '{}'".format(response))
                send_tweet(
                    self.tweet.author.screen_name,
                    response,
                    self.tweet.id)

        except Exception as e:
            logging.exception(e)


def main():
    logging.basicConfig(
        filename='output.log',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    _CONSUMER_KEY = os.environ['CONSUMER_KEY']
    _CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    _ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    _ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

    logging.basicConfig(level=logging.DEBUG)
    auth = tweepy.auth.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
    auth.set_access_token(_ACCESS_TOKEN, _ACCESS_TOKEN_SECRET)

    global _API
    _API = tweepy.API(auth)

    stream = tweepy.Stream(auth, CustomStreamListener(tweet_callback))
    logging.info("Now tracking Twitter for {}".format(_MY_NAME))
    stream.filter(track=[_MY_NAME])  # blocking function


def tweet_callback(status):
    global _API

    pretty_print_tweet(status)

    if not addressed_to_me(status.text):
        logging.debug("Ignoring '{}'".format(status.text))
        return

    handler_thread = ReplyHandlerThread(status)
    handler_thread.start()


_SCREEN_NAME_RE = re.compile(r'@[A-Za-z_]+[A-Za-z0-9_]+')


def strip_screen_names(message):
    return re.sub(_SCREEN_NAME_RE, '', message).strip()


def make_response_message(message):
    match = re.match(r'(?P<from>.+) to (?P<to>.+)', message)
    if match:
        from_, to = match.group('from'), match.group('to')
        logging.info("Searching '{}' to '{}'".format(from_, to))

        journeys = uktrains.search_trains(
            _unescape(from_),
            _unescape(to))
        if len(journeys) > 0:
            return describe_journey(journeys[0])

    if 'ping' in message.lower():
        return 'pong ' + datetime.datetime.now().isoformat()

    return None

def _unescape(string):
    """
    >>> _unescape('&amp;')
    u'&'
    """
    return HTMLParser.HTMLParser().unescape(string)


def describe_journey(journey):
    return ('{dep_time} => {arr_time} plat {platform}: {dep_name} {dep_code} '
            'to {arr_name} {arr_code} | {changes} | {status}'
            .format(
                dep_code=journey.depart_station.code,
                arr_code=journey.arrive_station.code,
                dep_name=journey.depart_station.name,
                arr_name=journey.arrive_station.name,
                dep_time=journey.depart_time,
                arr_time=journey.arrive_time,
                platform=journey.platform if journey.platform else '??',
                changes=('direct' if journey.changes == 0
                         else '{} chg'.format(journey.changes)),
                status=journey.status
            ))


def send_tweet(screen_name, message, tweet_id=None):
    global _API
    _API.update_status(
        '@{screen_name} {message}'.format(
            screen_name=screen_name,
            message=message),
        in_reply_to_status_id=tweet_id)


def pretty_print_tweet(status):
    #print('%s:  "%s" (%s via %s)\n' % (status.author.screen_name,
    #                                   status.text,
    #                                   status.created_at,
    #                                   status.source))
    for line in textwrap.wrap('{}'.format(status.text)):
        logging.info(line)
    logging.info('    - @{}'.format(status.author.screen_name))


def addressed_to_me(text):
    return text.lower().startswith(_MY_NAME.lower())


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
