
from mock import patch, call
from nose.tools import assert_equal

from main import strip_screen_names, make_response_message, describe_journey
from uktrains import Journey, Station


def test_strip_screen_names():
    yield _strip_screen_names, '@someone foo', 'foo'
    yield _strip_screen_names, '.@someone foo', '. foo'
    yield _strip_screen_names, '@someone foo @someone_else', 'foo'


def _strip_screen_names(message, expected):
    assert_equal(expected, strip_screen_names(message))


def test_describe_journey():
    description = describe_journey(
        Journey(
            depart_station=Station('Liverpool Lime Street', 'LIV'),
            arrive_station=Station('London Euston', 'EUS'),
            depart_time='17:35',
            arrive_time='19:53',
            platform=3,
            changes=2,
            status='on time'))

    assert_equal(
        'LIV to EUS: 17:35 plat 3 [2 chg] on time',
        description)


def _test_make_response_message():

    with patch('uktrains.search_trains') as mock:
        mock.return_value = [
        ]
        result = make_response_message('liverpool to euston')
        assert_equal(
            [call('liverpool', 'euston')],
            mock.call_args_list)
        assert_equal('x y z', result)
