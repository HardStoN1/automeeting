from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from event import Event 
from datetime import datetime, timedelta, date
import dateutil.parser
import arrow

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
events_arr = []
edge_times = []


def print_calender(cal, color, isA):
    for c in cal:
        if isA:
            print(color + str(c[0]) + " -> " + str(c[1]) + " - AVAILABLE!")
        else:
            print(color + str(c[0]) + " -> " + str(c[1]))
    
def substract_times(timeE, timeS):
    timeS = dateutil.parser.parse(timeS).time()
    timeE = dateutil.parser.parse(timeE).time()

    meeting_length = datetime.combine(date.today(), timeE) - datetime.combine(date.today(), timeS)
    return meeting_length

def get_avail_times(time_range, e_times):
    global events_arr
    edge_times = e_times

    if type(time_range) is list:
        tS = time_range[0]
        tE = time_range[1]

        tS = dateutil.parser.parse(tS).time()
        tE = dateutil.parser.parse(tE).time()

        meeting_length = datetime.combine(date.today(), tE) - datetime.combine(date.today(), tS)
        print("Meeting length -> " + str(meeting_length))
    else:
        mlength = time_range
        mlength = dateutil.parser.parse(mlength).time()
        stam = dateutil.parser.parse("00:00:00").time()

        meeting_length = datetime.combine(date.today(), mlength) - datetime.combine(date.today(), stam)
        print("Meeting length -> " + str(meeting_length))

    times = []
    for event in events_arr:
        times.append(event.times)
    
    counter = 0

    available_times = []

    for time in times:

        if counter == 0:
            current_start_time = times[1][0]
            old_end_time = times[0][1]

            subs = substract_times(current_start_time, old_end_time)
        
            if subs >= meeting_length:
                available_times.append([old_end_time, current_start_time])
        
        elif counter == len(times) - 1:
            old_end_time = time[1]
            current_start_time = edge_times[1]

            subs = substract_times(current_start_time, old_end_time)
        
            if subs >= meeting_length:
                available_times.append([old_end_time, current_start_time])

        else:
            current_start_time = times[counter + 1][0]
            old_end_time = time[1]
            
            subs = substract_times(current_start_time, old_end_time)
            
            if subs >= meeting_length:
                available_times.append([old_end_time, current_start_time])

        
        counter += 1
      
    os.system("cls")
    print("The available times for that calender")
    print_calender(times, bcolors.OKBLUE, False)
    print(bcolors.WARNING + "\n")
    return available_times     

def setup(t_range, isRange, etimes):
    global events_arr
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
       
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    yesterday = date.today() - timedelta(days=1)
    yesterday = arrow.get(yesterday).to('UTC')
    yesterday = yesterday.isoformat() + 'Z'
    
    tomo = date.today() + timedelta(days=1)
    tomo = arrow.get(tomo).to('UTC')
    tomo = tomo.isoformat() + 'Z'
    
    events_result = service.events().list(calendarId='primary', timeMin=now, #timeMax=tomo,
                                        maxResults=3, singleEvents=True,
                                        orderBy='startTime').execute()
                                        
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = str(event['start'].get('dateTime', event['start'].get('date')))
        end = str(event['end'].get('dateTime', event['end'].get('date')))
        nsT = datetime.fromisoformat(start)
        neT = datetime.fromisoformat(end)
        desc = str(event["summary"])
        color = "None"
        temp = Event(desc, color, [str(nsT.time()), str(neT.time())], str(nsT.date()))
        events_arr.append(temp)
    
    if '-' in t_range:
        avail_t = get_avail_times(t_range.split('-'), etimes)
    else:
        avail_t = get_avail_times(t_range, etimes)

    if not avail_t:
        print("You are not available in those times spans!")
    else:
        print_calender(avail_t, bcolors.OKGREEN, True)


if __name__ == '__main__':
    
    edgemin = input("Enter your minimum time (hh:mm:ss): ")
    edgemax = input("Enter your maximum time (hh:mm:ss): ")

    edge_times.append(edgemin)
    edge_times.append(edgemax)

    uDesc = input("Would you like to check for a specific time or check for total availabilities? (Y - specific /N - else)")
    if uDesc.capitalize() == "Y":
        time_range = input("Please make the input like that (hh:mm:ss-hh:mm:ss): ")
        os.system("cls")
        setup(time_range, True, [edgemin, edgemax])
    elif uDesc.capitalize() == "N":
        meeting_time = input("Please enter meeting time: ")
        os.system("cls")
        setup(meeting_time, False, [edgemin, edgemax])
    else:
        print("Oops! Invalid decision!")
