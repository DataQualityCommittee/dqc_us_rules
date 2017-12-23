# -*- coding: utf-8 -*-

# Copyright (c) 2014, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import unittest

from aniso8601.date import parse_date, _parse_year, _parse_calendar_day, _parse_calendar_month, _parse_week_day, _parse_week, _parse_ordinal_date, get_date_resolution
from aniso8601.resolution import DateResolution

class TestDateFunctions(unittest.TestCase):
    def test_get_date_resolution(self):
        self.assertEqual(get_date_resolution('2013'), DateResolution.Year)
        self.assertEqual(get_date_resolution('0001'), DateResolution.Year)
        self.assertEqual(get_date_resolution('19'), DateResolution.Year)
        self.assertEqual(get_date_resolution('1981-04-05'), DateResolution.Day)
        self.assertEqual(get_date_resolution('19810405'), DateResolution.Day)
        self.assertEqual(get_date_resolution('1981-04'), DateResolution.Month)
        self.assertEqual(get_date_resolution('2004-W53'), DateResolution.Week)
        self.assertEqual(get_date_resolution('2009-W01'), DateResolution.Week)
        self.assertEqual(get_date_resolution('2004-W53-6'), DateResolution.Weekday)
        self.assertEqual(get_date_resolution('2004W53'), DateResolution.Week)
        self.assertEqual(get_date_resolution('2004W536'), DateResolution.Weekday)
        self.assertEqual(get_date_resolution('1981-095'), DateResolution.Ordinal)
        self.assertEqual(get_date_resolution('1981095'), DateResolution.Ordinal)

    def test_parse_date(self):
        date = parse_date('2013')
        self.assertEqual(date.year, 2013)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = parse_date('0001')
        self.assertEqual(date.year, 1)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = parse_date('19')
        self.assertEqual(date.year, 1900)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = parse_date('1981-04-05')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        date = parse_date('19810405')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        date = parse_date('1981-04')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 1)

        date = parse_date('2004-W53')
        self.assertEqual(date.year, 2004)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = parse_date('2009-W01')
        self.assertEqual(date.year, 2008)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = parse_date('2004-W53-6')
        self.assertEqual(date.year, 2005)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = parse_date('2004W53')
        self.assertEqual(date.year, 2004)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = parse_date('2004W536')
        self.assertEqual(date.year, 2005)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = parse_date('1981-095')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        date = parse_date('1981095')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

    def test_parse_year(self):
        date = _parse_year('2013')
        self.assertEqual(date.year, 2013)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = _parse_year('0001')
        self.assertEqual(date.year, 1)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = _parse_year('19')
        self.assertEqual(date.year, 1900)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        with self.assertRaises(ValueError):
            _parse_year('0')

    def test_parse_calendar_day(self):
        date = _parse_calendar_day('1981-04-05')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        date = _parse_calendar_day('19810405')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

    def test_parse_calendar_month(self):
        date = _parse_calendar_month('1981-04')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 1)

        with self.assertRaises(ValueError):
            _parse_calendar_month('198104')

    def test_parse_week_day(self):
        date = _parse_week_day('2004-W53-6')
        self.assertEqual(date.year, 2005)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = _parse_week_day('2009-W01-1')
        self.assertEqual(date.year, 2008)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.day, 29)

        date = _parse_week_day('2009-W53-7')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 3)

        date = _parse_week_day('2010-W01-1')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 4)

        date = _parse_week_day('2004W536')
        self.assertEqual(date.year, 2005)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = _parse_week_day('2009W011')
        self.assertEqual(date.year, 2008)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.day, 29)

        date = _parse_week_day('2009W537')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 3)

        date = _parse_week_day('2010W011')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 4)

    def test_parse_week(self):
        date = _parse_week('2004-W53')
        self.assertEqual(date.year, 2004)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2009-W01')
        self.assertEqual(date.year, 2008)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2009-W53')
        self.assertEqual(date.year, 2009)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2010-W01')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2004W53')
        self.assertEqual(date.year, 2004)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2009W01')
        self.assertEqual(date.year, 2008)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2009W53')
        self.assertEqual(date.year, 2009)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.weekday(), 0)

        date = _parse_week('2010W01')
        self.assertEqual(date.year, 2010)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.weekday(), 0)

    def test_parse_ordinal_date(self):
        date = _parse_ordinal_date('1981-095')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)

        date = _parse_ordinal_date('1981095')
        self.assertEqual(date.year, 1981)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 5)
