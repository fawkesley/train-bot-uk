import os
import re
import time
import logging

import tweepy

from ..messages import InboundMessage

LOG = logging.getLogger(__name__)

_CONSUMER_KEY = os.environ['CONSUMER_KEY']
_CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
_ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
_ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
_MY_NAME = os.environ['MY_NAME']


_AUTH = tweepy.auth.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
_AUTH.set_access_token(_ACCESS_TOKEN, _ACCESS_TOKEN_SECRET)
_API = tweepy.API(_AUTH)

_SCREEN_NAME_RE = re.compile(r'@[A-Za-z_]+[A-Za-z0-9_]+')


__all__ = ['receive_messages', 'send_message']


def receive_messages(inbound_message_queue, channel_name):
    while True:
        try:
            stream = tweepy.Stream(
                _AUTH,
                CustomStreamListener(inbound_message_queue, channel_name)
            )
            stream.filter(track=[_MY_NAME])  # blocking function
            logging.info("Now tracking Twitter for {}".format(_MY_NAME))

        except Exception as e:
            LOG.exception(e)

        LOG.info('Pausing then restarting Twitter receiver.')
        time.sleep(2)


def send_message(outbound_message):
    original_tweet_id = outbound_message.inbound_message.extra['tweet_id']

    status = '@{screen_name} {message}'.format(
            screen_name=outbound_message.recipient,
            message=outbound_message.content)

    LOG.info('Replying to {} with: `{}`'.format(original_tweet_id, status))
    _API.update_status(status=status, in_reply_to_status_id=original_tweet_id)


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, inbound_message_queue, channel_name):
        self.inbound_message_queue = inbound_message_queue
        self.channel_name = channel_name
        super(CustomStreamListener, self).__init__()

    def on_status(self, tweet):
        if not addressed_to_me(tweet.text):
            LOG.info("Tweet not for me, ignoring: `{}`".format(tweet.text))
            return

        self.inbound_message_queue.put(
            InboundMessage(
                channel=self.channel_name,
                sender=tweet.author.screen_name,
                content=strip_screen_names(tweet.text),
                extra={'tweet_id': int(tweet.id)}
            )
        )


def addressed_to_me(text):
    return text.lower().startswith(_MY_NAME.lower())


def strip_screen_names(message):
    return re.sub(_SCREEN_NAME_RE, '', message).strip()
