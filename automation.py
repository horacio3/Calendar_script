import datetime
import os
import pickle
import sys
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CHICAGO_TZ = ZoneInfo('America/Chicago')

def parse_dt(dt_str):
    dt = datetime.datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CHICAGO_TZ)
    return dt

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# List of company holidays (date format: YYYY-MM-DD)
company_holidays = ['2024-07-04','2024-09-02','2024-11-28','2024-11-29','2024-12-24',
                    '2024-12-25','2025-01-01','2025-01-20','2025-05-26','2025-06-19',
                    '2025-07-04','2025-09-01','2025-11-27','2025-11-28','2025-12-24',
                    '2025-12-25','2025-12-31']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    token_path = '/Users/horacio/forks/Calendar_script/token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file_path = '/Users/horacio/forks/Calendar_script/client_secret_295637899002-e3dejutnrc3cj6o1b7j22mmcfg5h5lbn.apps.googleusercontent.com.json'
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Calculate the date for the next workday
    if len(sys.argv) > 1:
        next_workday = datetime.date.fromisoformat(sys.argv[1])
    else:
        today = datetime.date.today()
        next_workday = today + datetime.timedelta(days=1)
    while next_workday.weekday() >= 5 or next_workday.strftime('%Y-%m-%d') in company_holidays:  # Skip weekends
        next_workday += datetime.timedelta(days=1)

    # Get the list of events for the next workday
    events_result = service.events().list(
        calendarId='primary',
        timeMin=f'{next_workday}T00:00:00Z',
        timeMax=f'{next_workday}T23:59:59Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    # Calculate open time slots
    open_slots = []
    start_time = datetime.datetime(next_workday.year, next_workday.month, next_workday.day, 7, 30, tzinfo=CHICAGO_TZ)
    end_time = datetime.datetime(next_workday.year, next_workday.month, next_workday.day, 19, 0, tzinfo=CHICAGO_TZ)

    for event in events:
        if 'dateTime' in event['start']:
            if any(a.get('self') and a.get('responseStatus') == 'declined'
                   for a in event.get('attendees', [])):
                continue
            event_start = parse_dt(event['start']['dateTime'])
            event_end = parse_dt(event['end']['dateTime'])
            if start_time < event_start:
                open_slots.append({'start': start_time.isoformat(), 'end': event_start.isoformat()})
            if event_end > start_time:
                start_time = event_end

    if start_time < end_time:
        open_slots.append({'start': start_time.isoformat(), 'end': end_time.isoformat()})

    # Create open time slot events
    for slot in open_slots:
        event = {
            'eventType':'focusTime', # focusTime API https://developers.google.com/calendar/api/v3/reference/events
	    'focusTimeProperties': {
    		'autoDeclineMode': 'declineOnlyNewConflictingInvitations',
	    },
            'summary': 'DO NOT BOOK. For INTERNAL use',
            'start': {
                'dateTime': slot['start'],
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': slot['end'],
                'timeZone': 'America/Chicago',
            },
            'transparency': 'opaque',
            'visibility': 'default',
            'conferenceData': {
                'createRequest': {
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    },
                    'requestId': 'random-request-id'
                }
            },
            'guestsCanInviteOthers': False,
            'guestsCanModify': False,
            'guestsCanSeeOtherGuests': False,
            'colorId': '3',  # Color ID for "Internal"
            'reminders': {
                'useDefault': False,
                'overrides': []
            }
        }
        service.events().insert(calendarId='primary', body=event).execute()
        print('Event created:', event.get('start')['dateTime'], '-', event.get('end')['dateTime'])

if __name__ == '__main__':
    main()
