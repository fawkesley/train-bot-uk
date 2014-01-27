#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import datetime
import logging
import sys
import textwrap
import os
import re

import tweepy

import uktrains


_MY_NAME = os.environ.get('MY_NAME', '@TestAccount')

_API = None


def main():
    logging.basicConfig(level=logging.INFO)
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
    message = strip_screen_names(status.text)

    response = make_response_message(message)

    if response is not None:
        logging.info("Responding: '{}'".format(response))
        send_tweet(status.author.screen_name, response)

_SCREEN_NAME_RE = re.compile(r'@[A-Za-z_]+[A-Za-z0-9_]+')


def strip_screen_names(message):
    return re.sub(_SCREEN_NAME_RE, '', message).strip()


def make_response_message(message):
    match = re.match(r'(?P<from>.+) to (?P<to>.+)', message)
    if match:
        journeys = list(uktrains.search_trains(match.group('from'),
                                               match.group('to')))
        return describe_journey(journeys[0])
    return None


def describe_journey(journey):
    return ('{dep_name} {dep_code} to {arr_name} {arr_code}: {time} '
            'plat {platform} [{changes}] {status}'
            .format(
                dep_code=journey.depart_station.code,
                arr_code=journey.arrive_station.code,
                dep_name=journey.depart_station.name,
                arr_name=journey.arrive_station.name,
                time=journey.depart_time,
                platform=journey.platform if journey.platform else '??',
                changes=('direct' if journey.changes == 0
                         else '{} chg'.format(journey.changes)),
                status=journey.status
            ))


def send_tweet(screen_name, message):
    global _API
    _API.update_status('@{screen_name} {message}'.format(
        screen_name=screen_name,
        message=message))


def pretty_print_tweet(status):
    #print('%s:  "%s" (%s via %s)\n' % (status.author.screen_name,
    #                                   status.text,
    #                                   status.created_at,
    #                                   status.source))
    for line in textwrap.wrap('{}'.format(status.text)):
        logging.info(line)
    logging.info('    - @{}\n'.format(status.author.screen_name))


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
