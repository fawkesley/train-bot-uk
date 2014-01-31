#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import logging
import os
import sys

import tweepy

import train_bot_uk


def main():
    logging.basicConfig(
        filename='output.log',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    _CONSUMER_KEY = os.environ['CONSUMER_KEY']
    _CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    _ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    _ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

    auth = tweepy.auth.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
    auth.set_access_token(_ACCESS_TOKEN, _ACCESS_TOKEN_SECRET)

    train_bot_uk.setup_bot(auth, os.environ.get('MY_NAME', '@TestAccount'))


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
