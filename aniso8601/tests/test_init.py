# -*- coding: utf-8 -*-

# Copyright (c) 2014, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import unittest
import datetime
import aniso8601

class TestInitFunctions(unittest.TestCase):
    def test_import(self):
        #Just some tests repeated from other places to make sure the
        #imports work
        time = aniso8601.parse_time('01:23:45')
        self.assertEqual(time.hour, 1)
        self.assertEqual(time.minute, 23)
        self.assertEqual(time.second, 45)

        resultdatetime = aniso8601.parse_datetime('1981-04-05T23:21:28.512400Z')
        self.assertEqual(resultdatetime.year, 1981)
        self.assertEqual(resultdatetime.month, 4)
        self.assertEqual(resultdatetime.day, 5)
        self.assertEqual(resultdatetime.hour, 23)
        self.assertEqual(resultdatetime.minute, 21)
        self.assertEqual(resultdatetime.second, 28)
        self.assertEqual(resultdatetime.microsecond, 512400)
        tzinfoobject = resultdatetime.tzinfo
        self.assertEqual(tzinfoobject.utcoffset(None), datetime.timedelta(hours=0))
        self.assertEqual(tzinfoobject.tzname(None), 'UTC')

        date = aniso8601.parse_date('19810405')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        resultduration = aniso8601.parse_duration('P1Y2M3DT4H54M6S')
        self.assertEqual(resultduration.days, 428)
        self.assertEqual(resultduration.seconds, 17646)

        resultinterval = aniso8601.parse_interval('1980-03-05T01:01:00/1981-04-05T01:01:00')
        self.assertEqual(resultinterval[0], datetime.datetime(year=1980, month=3, day=5, hour=1, minute=1))
        self.assertEqual(resultinterval[1], datetime.datetime(year=1981, month=4, day=5, hour=1, minute=1))

        results = list(aniso8601.parse_repeating_interval('R3/1981-04-05/P1D'))
        self.assertEqual(results[0], datetime.date(year=1981, month=4, day=5))
        self.assertEqual(results[1], datetime.date(year=1981, month=4, day=6))
        self.assertEqual(results[2], datetime.date(year=1981, month=4, day=7))
