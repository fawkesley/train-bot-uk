#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import datetime
import logging
import re
import HTMLParser

import uktrains

from .message_responder import MessageResponder


class JourneyResponder(MessageResponder):
    def match(self, message):
        match = re.match(r'(?P<from>.+) to (?P<to>.+)', message)
        if match:
            from_, to = match.group('from'), match.group('to')
            logging.info("Searching '{}' to '{}'".format(from_, to))

            return {'depart_station': _format_station(from_),
                    'arrive_station': _format_station(to)}

    def reply(self, depart_station, arrive_station):
        journeys = uktrains.search_trains(
            depart_station,
            arrive_station,
            when=datetime.datetime.now() + datetime.timedelta(minutes=5))
        if len(journeys) > 0:
            return describe_journey(journeys[0])


def _format_station(string):
    """
    Santise the station name before using it to search with.
    >>> _format_station('&amp;')
    u'&'
    >>> _format_station('x &amp; y ')
    u'x & y'
    """
    return HTMLParser.HTMLParser().unescape(string).strip()


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
                status='no info' if not journey.status else journey.status
            ))
