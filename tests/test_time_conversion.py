from datetime import datetime
from unittest import TestCase

import astropy.time
from pytz import UTC


class TestTime(TestCase):
    def compare_times(self, utc, diff):
        """Take a utc localised datetime object, convert to TAI and
        check that the two datetime objects are offset by the correct
        number of seconds (depending on the date) specified by diff"""
        tai = astropy.time.Time(utc.timestamp(), scale="tai", format="unix")
        self.assertEqual(utc.second + diff, tai.datetime.second)

    def test_utc_to_tai(self):
        """Test conversion from a UTC datetime object to TAI"""
        # As of 31 Dec 2016 TAI is 37 seconds ahead of UTC
        self.compare_times(datetime(2017, 1, 1, 12, tzinfo=UTC), 37)
        # Before this the difference is only 36 seconds
        self.compare_times(datetime(2016, 12, 31, 12, tzinfo=UTC), 36)
        # At millenium difference should be 32 seconds
        self.compare_times(datetime(2000, 1, 1, 12, tzinfo=UTC), 32)
