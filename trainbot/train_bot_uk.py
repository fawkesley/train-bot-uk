#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import logging
import re
import textwrap
import threading

import tweepy

from responders import JourneyResponder, PingResponder

_API = None
_MY_NAME = None

_PARSERS = [
    JourneyResponder(),
    PingResponder(),
]


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


def setup_bot(oauth_handler, my_name):
    global _MY_NAME
    _MY_NAME = my_name

    global _API
    _API = tweepy.API(oauth_handler)

    stream = tweepy.Stream(oauth_handler, CustomStreamListener(tweet_callback))
    logging.info("Now tracking Twitter for {}".format(_MY_NAME))
    stream.filter(track=[_MY_NAME])  # blocking function


def tweet_callback(status):
    pretty_print_tweet(status)

    if not addressed_to_me(status.text):
        logging.info("Ignoring '{}'".format(status.text))
        return

    handler_thread = ReplyHandlerThread(status)
    handler_thread.start()


_SCREEN_NAME_RE = re.compile(r'@[A-Za-z_]+[A-Za-z0-9_]+')


def strip_screen_names(message):
    return re.sub(_SCREEN_NAME_RE, '', message).strip()


def make_response_message(message):

    for parser in _PARSERS:
        logging.info("Trying {} against '{}'".format(parser, message))
        response_params = parser.match(message)
        if response_params is not None:
            return parser.reply(**response_params)
        else:
            logging.info("Parser didn't match.")

    logging.info("No parsers matched.")


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
