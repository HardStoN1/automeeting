from datetime import datetime, date
import dateutil.parser

class Event:
    def __init__(self, summary, color, times, date):
        self.summary = summary
        self.color = color
        self.times = times
        self.date = date

    def get_event_length(self):
        #["12:00:00", "13:00:00"] -> "1:00:00"
        #["13:00:00"], ["12:00:00"] -> "-1 day, 23:00:00"

        tS = self.times[0]
        tE = self.times[1]

        tS = dateutil.parser.parse(tS).time()
        tE = dateutil.parser.parse(tE).time()

        length = datetime.combine(date.today(), tE) - datetime.combine(date.today(), tS)
        return length