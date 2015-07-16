import logging

from .messages import StopProcessing
from .config import SENDERS

LOG = logging.getLogger(__name__)


def send_reply(outbound_message_queue):
    for message in iter(outbound_message_queue.get, StopProcessing):
        LOG.info('Sending via channel `{}` to `{}`: {}'.format(
            message.channel, message.recipient, message.content))

        try:
            SENDERS[message.channel](message)
        except Exception as e:
            LOG.exception(e, message)

    LOG.debug('send_reply process ending')
