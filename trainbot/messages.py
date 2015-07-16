from collections import namedtuple


class StopProcessing(object):
    pass


InboundMessage = namedtuple(
    'InboundMessage', 'channel,sender,content,extra')

OutboundMessage = namedtuple(
    'OutboundMessage', 'channel,recipient,content,inbound_message')
