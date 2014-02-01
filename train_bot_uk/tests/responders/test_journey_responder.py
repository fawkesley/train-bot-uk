
from mock import patch, call
from nose.tools import assert_equal

from train_bot_uk import make_response_message
from train_bot_uk.responders.journey_responder import (
    describe_journey, JourneyResponder)


from uktrains import Journey, Station


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
        ('17:35 => 19:53 plat 3: Liverpool Lime Street LIV to '
         'London Euston EUS | 2 chg | on time'),
        description)


def test_no_changes_says_direct():
    description = describe_journey(
        Journey(
            depart_station=Station('Liverpool Lime Street', 'LIV'),
            arrive_station=Station('London Euston', 'EUS'),
            depart_time='17:35',
            arrive_time='19:53',
            platform=3,
            changes=0,
            status='on time'))

    assert_equal(
        ('17:35 => 19:53 plat 3: Liverpool Lime Street LIV to '
         'London Euston EUS | direct | on time'),
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


def test_station_names_decoded_correctly():
    test_cases = [
        ('liverpool to euston', 'liverpool', 'euston'),
        #('foo to bar ', 'foo', 'bar'),                        # trailing space
        ('dore &amp; totley to foo', 'dore & totley', 'foo'),  # encoded
    ]

    for text, dep, arr in test_cases:
        yield _test_text_parsed_as_stations, text, dep, arr


def _test_text_parsed_as_stations(text, dep, arr):
    expected = {'depart_station': dep,
                'arrive_station': arr}
    actual = JourneyResponder().match(text)

    assert_equal(expected, actual)
