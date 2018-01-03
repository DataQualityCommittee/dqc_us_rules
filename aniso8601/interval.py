# -*- coding: utf-8 -*-

# Copyright (c) 2014, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

from datetime import datetime
from aniso8601.duration import parse_duration
from aniso8601.time import parse_datetime
from aniso8601.date import parse_date

def parse_interval(isointervalstr, intervaldelimiter='/', datetimedelimiter='T'):
    #Given a string representing an ISO8601 interval, return a
    #tuple of datetime.date or date.datetime objects representing the beginning
    #and end of the specified interval. Valid formats are:
    #
    #<start>/<end>
    #<start>/<duration>
    #<duration>/<end>
    #
    #The <start> and <end> values can represent dates, or datetimes,
    #not times.
    #
    #The format:
    #
    #<duration>
    #
    #Is expressly not supported as there is no way to provide the addtional
    #required context.

    firstpart, secondpart = isointervalstr.split(intervaldelimiter)

    if firstpart[0] == 'P':
        #<duration>/<end>
        #Notice that these are not returned 'in order' (earlier to later), this
        #is to maintain consistency with parsing <start>/<end> durations, as
        #well as making repeating interval code cleaner. Users who desire
        #durations to be in order can use the 'sorted' operator.

        #We need to figure out if <end> is a date, or a datetime
        if secondpart.find(datetimedelimiter) != -1:
            #<end> is a datetime
            duration = parse_duration(firstpart)
            enddatetime = parse_datetime(secondpart, delimiter=datetimedelimiter)

            return (enddatetime, enddatetime - duration)
        else:
            #<end> must just be a date
            duration = parse_duration(firstpart)
            enddate = parse_date(secondpart)

            #See if we need to upconvert to datetime to preserve resolution
            if firstpart.find(datetimedelimiter) != -1:
                return (enddate, datetime.combine(enddate, datetime.min.time()) - duration)
            else:
                return (enddate, enddate - duration)
    elif secondpart[0] == 'P':
        #<start>/<duration>
        #We need to figure out if <start> is a date, or a datetime
        if firstpart.find(datetimedelimiter) != -1:
            #<end> is a datetime
            duration = parse_duration(secondpart)
            startdatetime = parse_datetime(firstpart, delimiter=datetimedelimiter)

            return (startdatetime, startdatetime + duration)
        else:
            #<start> must just be a date
            duration = parse_duration(secondpart)
            startdate = parse_date(firstpart)

            #See if we need to upconvert to datetime to preserve resolution
            if secondpart.find(datetimedelimiter) != -1:
                return (startdate, datetime.combine(startdate, datetime.min.time()) + duration)
            else:
                return (startdate, startdate + duration)
    else:
        #<start>/<end>
        if firstpart.find(datetimedelimiter) != -1 and secondpart.find(datetimedelimiter) != -1:
            #Both parts are datetimes
            return (parse_datetime(firstpart, delimiter=datetimedelimiter), parse_datetime(secondpart, delimiter=datetimedelimiter))
        elif firstpart.find(datetimedelimiter) != -1 and secondpart.find(datetimedelimiter) == -1:
            #First part is a datetime, second part is a date
            return (parse_datetime(firstpart, delimiter=datetimedelimiter), parse_date(secondpart))
        elif firstpart.find(datetimedelimiter) == -1 and secondpart.find(datetimedelimiter) != -1:
            #First part is a date, second part is a datetime
            return (parse_date(firstpart), parse_datetime(secondpart, delimiter=datetimedelimiter))
        else:
            #Both parts are dates
            return (parse_date(firstpart), parse_date(secondpart))

def parse_repeating_interval(isointervalstr, intervaldelimiter='/', datetimedelimiter='T'):
    #Given a string representing an ISO8601 interval repating, return a
    #generator of datetime.date or date.datetime objects representing the
    #dates specified by the repeating interval. Valid formats are:
    #
    #Rnn/<interval>
    #R/<interval>

    if isointervalstr[0] != 'R':
        raise ValueError('String is not a valid ISO8601 repeating interval.')

    #Parse the number of iterations
    iterationpart, intervalpart = isointervalstr.split(intervaldelimiter, 1)

    if len(iterationpart) > 1:
        iterations = int(iterationpart[1:])
    else:
        iterations = None

    interval = parse_interval(intervalpart, intervaldelimiter, datetimedelimiter)

    intervaltimedelta = interval[1] - interval[0]

    #Now, build and return the generator
    if iterations != None:
        return _date_generator(interval[0], intervaltimedelta, iterations)
    else:
        return _date_generator_unbounded(interval[0], intervaltimedelta)

def _date_generator(startdate, timedelta, iterations):
    currentdate = startdate
    currentiteration = 0

    while currentiteration < iterations:
        yield currentdate

        #Update the values
        currentdate += timedelta
        currentiteration += 1

def _date_generator_unbounded(startdate, timedelta):
    currentdate = startdate

    while True:
        yield currentdate

        #Update the value
        currentdate += timedelta
