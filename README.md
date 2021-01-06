# caldav-infer-freebusy
A Python script to generate a free/busy iCalendar from a server that doesn't support free/busy requests

## usage
> python main.py --url https://mydav.server.example --user username --pass $(pass mydav.server.example) --ahead 60

Will return a .ics to standard out.
