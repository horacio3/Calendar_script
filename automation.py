import datetime
import os
import pickle
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file_path = '/Users/Horacio3/Scripts/credentials.json'  # Replace with the correct path
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Calculate the date for the next workday
    today = datetime.date.today()
    # today = datetime.date(2023, 8, 17)
    next_workday = today + datetime.timedelta(days=1)
    while next_workday.weekday() >= 5:  # Skip weekends
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
    # TODO: Fix issue with an event at 8AM and start time at 8AM this code will create event at same time
    start_time = f'{next_workday}T07:30:00'  # Adjust the start time as needed
    end_time = f'{next_workday}T19:00:00'    # Adjust the end time as needed

    for event in events:
        if 'dateTime' in event['start']:
            event_start = event['start']['dateTime']
            event_end = event['end']['dateTime']
            if start_time < event_start:
                open_slots.append({'start': start_time, 'end': event_start})
            if event_end > start_time:  # Update start_time only if event_end is greater
                start_time = event_end

    if start_time < end_time:
        open_slots.append({'start': start_time, 'end': end_time})

    # Create open time slot events
    for slot in open_slots:
        event = {
            'eventType':'focusTime', # focusTime is only available via UI not API https://developers.google.com/calendar/api/v3/reference/events
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
