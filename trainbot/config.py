from .apis.twitter_tweepy import (
    receive_messages as twitter_receive,
    send_message as twitter_send
)

from .apis.console import write_to_console
from .responders import JourneyResponder, PingResponder

MESSAGE_RECEIVERS = [
    ('twitter', twitter_receive, 1),  # only 1 listener process required
]

SENDERS = {
    'twitter': twitter_send,
    'console': write_to_console,
}

PARSERS = [
    JourneyResponder(),
    PingResponder(),
]

REPORT_ERRORS_TO_GITHUB = True
