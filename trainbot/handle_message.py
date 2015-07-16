import logging
from .messages import OutboundMessage, StopProcessing
from .create_github_issue import create_github_issue
from .config import PARSERS

LOG = logging.getLogger(__name__)


def handle_message(message_queue, reply_queue):
    for message in iter(message_queue.get, StopProcessing):
        LOG.info('handle_message({})'.format(repr(message)))

        try:
            reply_content = make_reply(message.content)
        except Exception as e:  # Unhandled exception - bad.
            LOG.exception(e)
            issue_url = create_github_issue(message)
            reply_content = 'Oops! Fail. See {}'.format(issue_url)

        reply_queue.put(
            OutboundMessage(
                channel=message.channel,
                recipient=message.sender,
                content=reply_content,
                inbound_message=message))

    LOG.debug('handle_message process ending')


def make_reply(message_content):
    LOG.debug('Processing `{}`'.format(message_content))

    for parser in PARSERS:
        LOG.debug("Trying {} against '{}'".format(parser.__class__.__name__,
                                                  message_content))
        response_params = parser.match(message_content)
        if response_params is not None:
            LOG.debug('Parser responded with `{}`'.format(response_params))
            return parser.reply(**response_params)

    LOG.info("No parsers matched.")
    return "Sorry, I didn't understand that."
