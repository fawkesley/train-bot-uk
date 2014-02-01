
from mock import patch, call
from nose.tools import assert_equal

from train_bot_uk import strip_screen_names, make_response_message


def test_strip_screen_names():
    yield _strip_screen_names, '@someone foo', 'foo'
    yield _strip_screen_names, '.@someone foo', '. foo'
    yield _strip_screen_names, '@someone foo @someone_else', 'foo'


def _strip_screen_names(message, expected):
    assert_equal(expected, strip_screen_names(message))
