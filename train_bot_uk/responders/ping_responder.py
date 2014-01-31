#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import datetime
import HTMLParser


from .message_responder import MessageResponder


class PingResponder(MessageResponder):
    def match(self, message):
        if 'ping' in message.lower():
            return {}

    def reply(self):
        return 'pong ' + datetime.datetime.now().isoformat()
