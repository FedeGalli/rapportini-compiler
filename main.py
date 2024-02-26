import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

def get_hours(max_date:str, min_date:str):
    diff_in_seconds = int((datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%S%z") - datetime.strptime(min_date, "%Y-%m-%dT%H:%M:%S%z")).total_seconds()) / 60 / 60

    return diff_in_seconds


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

time_max = datetime.utcnow()
time_min = time_max - timedelta(days=datetime.utcnow().weekday())
time_min = time_min.replace(hour=9, minute=0, second=0, microsecond=0)

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="c_1ed1b2639e4c48be816d0b0fcddc393e68c7eb94b694aadfc8f8b712282006d4@group.calendar.google.com",
            timeMin=time_min.isoformat() + "Z",
            timeMax=time_max.isoformat() + "Z",
            maxResults=200,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events

    print(events)

    for event in events:
        date = datetime.strptime(event["start"].get("dateTime", event["start"].get("date")), "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m/%Y")
        hours = get_hours(event["end"].get("dateTime", event["end"].get("date")), event["start"].get("dateTime", event["start"].get("date")))
        ticket, wp = str.split(event["summary"], '-')
        wp = wp.strip().lower()
        desc = event["description"]

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()