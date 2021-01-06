#!/usr/bin/env python
#Requirements: pytz, caldav, tzlocal, icalendar (all available with pip)

import caldav
import pytz
import time
import os.path
import pickle
from icalendar import Calendar, Event, FreeBusy, Timezone, TimezoneDaylight, TimezoneStandard
from datetime import datetime, timedelta
import tzlocal
import argparse
import urllib

def main():
    parser = argparse.ArgumentParser("A stupid Free/Busy generator")
    parser.add_argument('--user', dest='user', nargs=1, help='CalDav username')
    parser.add_argument('--pass', dest='password', nargs=1, help='CalDav password')
    parser.add_argument('--url', dest='url', nargs=1, help='CalDav url')
    args = parser.parse_args()

    client = caldav.DAVClient(args.url[0], username=args.user[0], password=args.password[0])
    principal = client.principal()
    calendars = principal.calendars()
    #Get a list of events (i.e raw data) and make it into calendars (icalender objects).
    eventlist = list()
    callist = list()
    free_busy_cal = Calendar()
    timezones = list()
    def convert_to_free_busy(vcal):
        for i in vcal.subcomponents:
            if isinstance(i, Event) and i['uid'] not in eventlist:
                e = Event()
                e['uid'] = i['uid']
                e['dtstamp'] = i['dtstamp']
                e['dtstart'] = i['dtstart']
                e['dtend'] = i['dtend']
                #e['rstatus'] = event['rstatus']
                e['freebusy'] = "BUSY" # should be read from event, but KDE doesn't support
                e['summary'] = "BUSY"
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
        for event in calendar.date_search((datetime.today() - timedelta(7)), (datetime.today() + timedelta(12))):
            c = Calendar.from_ical(event.data)
            convert_to_free_busy(c)
    print(free_busy_cal.to_ical().decode())
    return

main()
