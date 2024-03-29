#!/usr/bin/env python
#Requirements: pytz, caldav, tzlocal, icalendar (all available with pip)

import caldav
import uuid
import pytz
import time
import os.path
import pickle
from icalendar import Calendar, Event, FreeBusy, Timezone, TimezoneDaylight, TimezoneStandard
from datetime import datetime, timedelta, date
import tzlocal
import argparse
import urllib

def datetime_trunc(d, ahead):
    tz = getattr(d, 'tzinfo', None)
    begin_dt = datetime.now(tz)
    end_dt = datetime.now(tz) + timedelta(ahead)
    if not isinstance(d, datetime):
        d = datetime.combine(d, datetime.now().time(), tz)
    if d < begin_dt:
        return datetime.combine(begin_dt.date(), d.time(), tz)
    elif d > end_dt:
        return datetime.combine(end_dt.date(), d.time(), tz)
    else:
        return d

def create_free_busy(url, ahead, user, password, exceptions, compliant=False):
    client = caldav.DAVClient(url, username=user, password=password, auth=(user, password))
    principal = client.principal()
    calendars = principal.calendars()
    #Get a list of events (i.e raw data) and make it into calendars (icalender objects).
    eventlist = list()
    callist = list()
    free_busy_cal = Calendar()
    timezones = list()

    seen = list()
    def convert_to_free_busy(vcal):
        for i in vcal.subcomponents:
            if isinstance(i, Event) and \
               (not i['uid'] in seen) and \
               (not 'transp' in i or
                i.decoded('transp').decode() == 'OPAQUE') and \
               (not 'class' in i or
                i.decoded('class').decode() != 'CONFIDENTIAL'):
                e = Event()
                #e['x-old-uid'] = i['uid']
                #e['uid'] = uuid.uuid4()
                e['uid'] = i['uid']
                seen.append(i['uid'])
                e['dtstamp'] = i['dtstamp']
                #e.add('dtstart', datetime_trunc(i.decoded('dtstart')))
                #e.add('dtend', datetime_trunc(i.decoded('dtend')))
                e['dtstart'] = i['dtstart']
                e['dtend'] = i['dtend']
                #e['rstatus'] = event['rstatus']
                e['freebusy'] = 'BUSY' # should be read from event, but KDE doesn't support
                if compliant:
                    e['summary'] = i['summary']
                if 'class' in i:
                    e['class'] = i['class']
                    if i.decoded('class').decode() == 'PRIVATE':
                        e['summary'] = "Busy"
                    if i.decoded('class').decode() == 'PUBLIC':
                        e['summary'] = i['summary']
                if not compliant:
                    e['summary'] = "Busy"
                if 'rrule' in i:
                    e['rrule'] = i['rrule']
                free_busy_cal.add_component(e)
                eventlist.append(i['uid'])
            elif isinstance(i, Timezone) \
                 or isinstance(i, TimezoneDaylight) \
                 or isinstance(i, TimezoneStandard):
                if not i['tzid'] in timezones:
                    free_busy_cal.add_component(i)
                    timezones.append(i['tzid'])
    free_busy_cal.add('prodid', '-//FreeBusy//williamjbowman.com')
    free_busy_cal.add('version', '2.0')
    for calendar in calendars:
        if not calendar.name in exceptions:
            for event in calendar.date_search(datetime.now(), datetime.now() + timedelta(ahead)):
                c = Calendar.from_ical(event.data)
                convert_to_free_busy(c)
    return free_busy_cal

def main():
    parser = argparse.ArgumentParser("A stupid Free/Busy generator")
    parser.add_argument('--user', dest='user', default=None, help='CalDav username')
    parser.add_argument('--pass', dest='password', default=None, help='CalDav password')
    parser.add_argument('--url', dest='url', help='CalDav url')
    parser.add_argument('--ahead', dest='ahead', default=7, type=int,
                        help='How many days of events to look ahead, starting from today. Defaults to 1 week.')
    parser.add_argument('--compliant', dest='compliant', action='store_true',
                        help='Set privacy of events by being compliant with CalDAV; this meaning events are PUBLIC BY DEFAULT. Defaults to False to preserve privacy.')
    parser.add_argument('--except', dest='exceptions', nargs="*", type=str,
                        help="A list of calendar names to not include in the free/bsuy calendar.")
    args = parser.parse_args()

    print(create_free_busy(args.url, args.ahead, args.user, args.password, args.exceptions, args.compliant).to_ical().decode())
    return

if __name__=='__main__':
    main()
