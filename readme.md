# Automated Calendar Block Creator

This Python script automates the creation of focus time blocks in your Google Calendar. It finds open time slots for a given workday and fills them with "DO NOT BOOK" focus time events, helping protect your schedule from unwanted meetings.

## Features

- Automatically identifies the next workday (skips weekends and company holidays)
- Respects existing calendar events when calculating open slots
- Skips declined meetings — their time is treated as available
- Idempotent — running the script multiple times on the same day won't create duplicate blocks
- Accepts an optional date argument to target a specific day
- Configurable work hours, timezone, and company holidays

## Requirements

- Python 3.9 or higher
- Google account with Calendar access

## Installation

Clone this repository:

```bash
git clone git@github.com:horacio3/Calendar_script.git
cd Calendar_script
```

Install dependencies using `uv`:

```bash
uv sync
```

## Setup credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Go to **APIs & Services → Credentials**.
4. Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
5. Choose **Desktop app** as the application type and give it a name.
6. Download the JSON file and place it in the same directory as `automation.py`.
7. Update the `credentials_file_path` variable in `automation.py` to point to your downloaded file.

## Enable the API

1. Visit the [Google Calendar API overview](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview).
2. Sign in with the Google account associated with your project.
3. Click **Enable** if the API is not already enabled.

## Configuration

Edit `automation.py` to adjust these values as needed:

| Setting | Location | Default |
|---|---|---|
| Work start time | `start_time` in `main()` | 7:30 AM |
| Work end time | `end_time` in `main()` | 7:00 PM |
| Timezone | `CHICAGO_TZ` | America/Chicago |
| Company holidays | `company_holidays` list | See file |

## Usage

Block open slots for the next workday:

```bash
python automation.py
```

Target a specific date:

```bash
python automation.py 2026-04-23
```

### Automate with cron (macOS/Linux)

Run `crontab -e` and add a line to run the script every weekday at 4:45 PM:

```
45 16 * * 1-5 /usr/local/bin/python3 /path/to/Calendar_script/automation.py >> ~/calendar_logfile.log 2>&1
```

### Automate with Task Scheduler (Windows)

1. Open Task Scheduler and click **Create Basic Task**.
2. Set the action to **Start a program** and select your Python executable.
3. In **Add arguments**, enter the path to `automation.py`.
4. Set the trigger to run daily at your preferred time on weekdays.

## Troubleshooting

- **Authentication errors** — delete `token.pickle` and re-run to re-authenticate.
- **Wrong credentials file** — ensure `credentials_file_path` in `automation.py` points to your `client_secret_*.json` file.
- **API not enabled** — confirm the Google Calendar API is enabled in Google Cloud Console.

## Security and Privacy

This script reads your Google Calendar to find open slots and creates new focus time events. It does not modify or delete existing events. The `client_secret_*.json` and `token.pickle` files contain sensitive credentials — keep them secure and do not commit them to version control (both are covered by `.gitignore`).

## License

This project is licensed under the MIT License. See the LICENSE file for details.
