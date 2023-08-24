# Automated Next Day Block Google Calendar Event Creator
This Python script automates the creation of calendar events based on available time slots. It is designed to run on both macOS and Windows.

## Installation
Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/automated-calendar-block.git
cd automated-calendar-block
```
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Setup credentials
Here's how you can obtain the credentials.json file:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
1. Create a new project or select an existing project.
1. In the left sidebar, click on "APIs & Services" > "Credentials."
Click the "+ CREATE CREDENTIALS" button and select "OAuth client ID."
Choose "Desktop app" as the application type.
1. Give your OAuth 2.0 client ID a name (e.g., "Calendar Automation Script").
1. Click the "Create" button.
1. In the list of OAuth 2.0 Client IDs, find the one you just created and click on the download button to the right. This will download the credentials.json file.
1. Once you have the credentials.json file, place it in the same directory as your automation.py script. This file contains the information necessary for your script to authenticate with the Google Calendar API and access your calendar.

## Enable API

1. Visit the following link in your web browser: [Google Cloud Console - Calendar API Overview](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview)
1. If prompted, sign in with the Google Account associated with the project you're using.
1. On the Overview page, you'll see information about the Google Calendar API. If it's not enabled, click on the "Enable" button to enable the API for your project.
1. After enabling the API, wait a few minutes to ensure that the action propagates to Google's systems.

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

License
This project is licensed under the MIT License. See the LICENSE file for details.

Remember to replace placeholders like yourusername, /path/to/automated-calendar-event, and others with the actual values for your setup.