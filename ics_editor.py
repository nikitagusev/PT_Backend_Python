from icalendar import Calendar, Event
from icalevents import icalevents
from datetime import date, timedelta, datetime
from pytz import timezone
import pytz

def parseEvents(icsFile):
    start = date(2020,11,2)
    end = date(2020,11,9)
    evs = icalevents.events(url=None, file = icsFile, start = start, end = end)
    
    for events in evs:
        start = events.start
        end = events.end

        localStart = start.astimezone(pytz.timezone('America/Toronto'))
        localEnd = end.astimezone(pytz.timezone('America/Toronto'))

        localStartString = localStart.strftime("%Y-%m-%d %H:%M:%S")
        localEndString = localEnd.strftime("%Y-%m-%d %H:%M:%S")
        title = events.summary.split(':')
        venueName = title[0].strip()
        eventName = title[1].strip()
        venueAddress = (events.location).replace('\n',' ')
        print(venueName)
        print(eventName)
        print(venueAddress)


def main():
    if(1==1):
        parseEvents('TestICS.ics')
if __name__ == "__main__":
	main()
