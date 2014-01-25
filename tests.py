
from mock import patch, call
from nose.tools import assert_equal

from main import strip_screen_names, make_response_message


def test_strip_screen_names():
    yield _strip_screen_names, '@someone foo', 'foo'
    yield _strip_screen_names, '.@someone foo', '. foo'
    yield _strip_screen_names, '@someone foo @someone_else', 'foo'


def _strip_screen_names(message, expected):
    assert_equal(expected, strip_screen_names(message))


def test_make_response_message():

    with patch('uktrains.search_trains') as mock:
        mock.return_value = [('x', 'y', 'z')]
        result = make_response_message('liverpool to euston')
        assert_equal(
            [call('liverpool', 'euston')],
            mock.call_args_list)
        assert_equal('x y z', result)
