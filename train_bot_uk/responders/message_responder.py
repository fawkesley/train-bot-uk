#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals


class MessageResponder(object):
    def match(self, message):
        pass

    def reply(self, **args):
        return None  # no reply
