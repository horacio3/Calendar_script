# Automated Next Day Block Google Calendar Event Creator
This Python script automates the creation of calendar events based on available time slots for the next workday. It creates "focus time" events in your Google Calendar to block off open time slots, helping you manage your schedule more effectively.

## Features
- Automatically identifies the next workday
- Respects existing calendar events
- Creates "focus time" events in open time slots
- Configurable work hours and company holidays

## Requirements
- Python 3.7 or higher
- Google account with Calendar access

## Installation
Clone this repository to your local machine:

```bash
git clone git@github.com:horacio3/Calendar_script.git
cd automated-calendar-block
```
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Setup credentials
To use this script, you need to obtain a credentials.json file from Google:

1. Go to the Google Cloud Console.
1. Create a new project or select an existing project.
1. In the left sidebar, click on "APIs & Services" > "Credentials."
1. Click the "+ CREATE CREDENTIALS" button and select "OAuth client ID."
1. Choose "Desktop app" as the application type.
1. Give your OAuth 2.0 client ID a name (e.g., "Calendar Automation Script").
1. Click the "Create" button.
1. In the list of OAuth 2.0 Client IDs, find the one you just created and click on the download button to the right. This will download the credentials.json file.
1. Place the credentials.json file in the same directory as your automation.py script.

## Enable API

1. Visit the following link in your web browser: [Google Cloud Console - Calendar API Overview](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview)
1. If prompted, sign in with the Google Account associated with the project you're using.
1. On the Overview page, you'll see information about the Google Calendar API. If it's not enabled, click on the "Enable" button to enable the API for your project.
1. After enabling the API, wait a few minutes to ensure that the action propagates to Google's systems.

## Configuration

Open the automation.py file and modify the following variables as needed:

- WORK_START_TIME: Set your workday start time (default is "07:30:00")
- WORK_END_TIME: Set your workday end time (default is "19:00:00")
- TIME_ZONE: Set your time zone (default is "America/Chicago")
- COMPANY_HOLIDAYS: Update the list with your company's holiday dates

## Usage
### Run the script manually using the following command:

```bash
python automation.py
```

Edit your crontab file by running:

Copy code
crontab -e
Add the following line to run the script every weekday at 4:45 PM:

```
45 16 * * 1-5 /usr/local/bin/python3 /path/to/automated-calendar-event/automation.py >> ~/calendar_logfile.log 2>&1
```

Schedule on Windows using Task Scheduler
Open Task Scheduler from the Start menu.
Click on "Create Basic Task" and follow the prompts.
Choose "Start a program" as the action and browse to select the Python executable (usually python.exe or python3.exe).
In the "Add arguments" field, enter the path to your script: C:\path\to\automated-calendar-event\automation.py.
Set the trigger to run the task daily at 5:00 PM.


## Troubleshooting

- If you encounter authentication errors, delete the token.pickle file and run the script again to re-authenticate.
- Ensure that your credentials.json file is in the same directory as the script.
- Check that the Google Calendar API is enabled for your project in the Google Cloud Console.

## Security and Privacy

This script requires access to your Google Calendar. It only creates events and does not read or modify existing events. Always review the permissions you grant to scripts and applications. The credentials.json file and token.pickle file contain sensitive information - keep them secure and do not share them.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

Remember to replace placeholders like yourusername, /path/to/automated-calendar-event, and others with the actual values for your setup.