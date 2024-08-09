from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os.path
import argparse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

# Get the Slack token from the environment variable
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Define color categories to filter out
EXCLUDED_COLOR_IDS = ['1','3','4','5','6','7','8','9','11','12','13','14']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_events(service, calendar_id, start_date, end_date):
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_date,
                                          timeMax=end_date, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])

def filter_events(events):
    return [
        event for event in events 
        if event.get('colorId') not in EXCLUDED_COLOR_IDS
        # if event.get('colorId') in INCLUDED_COLOR_IDS
        and 'dateTime' in event['start']  # This ensures the event has a specific time
    ]

def get_conference_type(event):
    if 'conferenceData' in event:
        conf_type = check_conference_solution(event['conferenceData'])
        if conf_type:
            return conf_type
        
        conf_type = check_entry_points(event['conferenceData'])
        if conf_type:
            return conf_type

    conf_type = check_location_and_description(event)
    if conf_type:
        return conf_type

    if 'hangoutLink' in event:
        return 'Google Meet'

    return ''  # Return empty string if no conference type found

def format_events(events, timezone, for_slack=False):
    formatted_data = []
    current_date = None

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        summary = event.get('summary', 'No title')

        start_dt = datetime.fromisoformat(start).astimezone(timezone)
        end_dt = datetime.fromisoformat(end).astimezone(timezone)

        event_date = start_dt.date()
        
        if event_date != current_date:
            if for_slack and formatted_data:
                formatted_data.append({"type": "divider"})
            current_date = event_date
            day_of_week = event_date.strftime('%A')
            date_str = f"{day_of_week} - {event_date.strftime('%m/%d/%Y')}"
            
            if for_slack:
                formatted_data.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": date_str,
                        "emoji": True
                    }
                })
            else:
                if formatted_data:
                    formatted_data.append("")
                formatted_data.append(f"# {date_str}")

        start_time = start_dt.strftime('%I:%M %p')
        end_time = end_dt.strftime('%I:%M %p')
        conference_type = get_conference_type(event)
        conference_info = f" ({conference_type})" if conference_type else ""
        
        event_text = f"*{start_time} to {end_time}:* {summary}{conference_info}" if for_slack else f"  - {start_time} to {end_time}: {summary}{conference_info}"
        
        if for_slack:
            formatted_data.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": event_text
                }
            })
        else:
            formatted_data.append(event_text)

    return formatted_data

# def get_user_email(service):
#     profile = service.calendarList().get(calendarId='primary').execute()
#     return profile['id']

def check_conference_solution(conference_data):
    if 'conferenceSolution' in conference_data:
        solution_name = conference_data['conferenceSolution']['name'].lower()
        if 'zoom' in solution_name:
            return 'Zoom'
        elif 'meet' in solution_name:
            return 'Google Meet'
        elif 'teams' in solution_name:
            return 'Teams'
        else:
            return solution_name.capitalize()
    return None

def check_entry_points(conference_data):
    if 'entryPoints' in conference_data:
        for entry_point in conference_data['entryPoints']:
            if entry_point.get('entryPointType') == 'video':
                uri = entry_point.get('uri', '').lower()
                if 'zoom.us' in uri:
                    return 'Zoom'
                elif 'meet.google.com' in uri:
                    return 'Google Meet'
                elif 'teams.microsoft.com' in uri:
                    return 'Teams'
                else:
                    return 'Video Conference'
    return None

def check_location_and_description(event):
    location = event.get('location', '').lower()
    description = event.get('description', '').lower()
    
    if 'chime' in location or 'chime' in description or 'https://chime.aws' in description:
        return 'Chime :vomit:'
    elif 'zoom' in location or 'zoom.us' in description:
        return 'Zoom'
    elif 'meet.google.com' in location or 'meet.google.com' in description:
        return 'Google Meet'
    elif 'teams.microsoft.com' in location or 'teams.microsoft.com' in description:
        return 'Teams'
    
    return None

def get_week_range(target_date):
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week, end_of_week

def send_to_slack(formatted_data, channel_id):
    client = WebClient(token=SLACK_TOKEN)
    
    try:
        # Start with the header
        current_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Weekly Calendar for Client Calls",
                    "emoji": True
                }
            },
            {"type": "divider"}
        ]

        for block in formatted_data:
            if len(current_blocks) >= 45:  # Leave some room for the header and divider
                # Send the current set of blocks
                result = client.chat_postMessage(
                    channel=channel_id,
                    blocks=current_blocks,
                    text="Your weekly calendar information (Part)"
                )
                print(f"Partial message sent to Slack: {result['ts']}")
                
                # Start a new set of blocks
                current_blocks = [{"type": "divider"}]
            
            current_blocks.append(block)

        # Send any remaining blocks
        if current_blocks:
            result = client.chat_postMessage(
                channel=channel_id,
                blocks=current_blocks,
                text="Your weekly calendar information (Final Part)"
            )
            print(f"Final message sent to Slack: {result['ts']}")

    except SlackApiError as e:
        print(f"Error sending message to Slack: {e}")

def main():
    parser = argparse.ArgumentParser(description='Get calendar events for a week.')
    parser.add_argument('--date', type=str, help='Date to use for the week (YYYY-MM-DD format)', default=None)
    parser.add_argument('--email', type=str, help='Email address of the calendar to view', default=None)
    parser.add_argument('--slack', type=str, help='Slack channel or user ID to send the message to', default=None)
    args = parser.parse_args()

    timezone = ZoneInfo("America/Chicago")

    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').replace(tzinfo=timezone).date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        target_date = datetime.now(timezone).date()

    service = get_calendar_service()
    calendar_id = args.email if args.email else 'primary'
    
    start_of_week, end_of_week = get_week_range(target_date)
    
    start_date = datetime.combine(start_of_week, datetime.min.time()).replace(tzinfo=timezone).isoformat()
    end_date = datetime.combine(end_of_week, datetime.max.time()).replace(tzinfo=timezone).isoformat()

    try:
        events = get_events(service, calendar_id, start_date, end_date)
        filtered_events = filter_events(events)
        
        if args.slack:
            formatted_data = format_events(filtered_events, timezone, for_slack=True)
            send_to_slack(formatted_data, args.slack)
        else:
            formatted_data = format_events(filtered_events, timezone, for_slack=False)
            print("\n".join(formatted_data) if isinstance(formatted_data[0], str) else formatted_data)
        
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()