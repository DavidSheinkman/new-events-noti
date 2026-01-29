import requests
import json
from datetime import datetime, timedelta

URL = 'https://ra.co/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Referer': 'https://ra.co/events/uk/london',
    'User-Agent': 'Mozilla/5.0'
}
QUERY_TEMPLATE_PATH = "graphql_query_template.json"
DELAY = 1  # seconds

def fetch_all_berlin_events():
    """Fetch all events in Berlin for the next year"""
    events = []
    start_date = datetime.today()
    end_date = start_date + timedelta(days=60)  # for testing, limit to 1 week
    current_date = start_date

    while current_date <= end_date:
        gte = current_date.strftime("%Y-%m-%dT00:00:00.000Z")
        lte = current_date.strftime("%Y-%m-%dT23:59:59.999Z")

        with open(QUERY_TEMPLATE_PATH, "r") as f:
            payload = json.load(f)
        payload["variables"]["filters"]["areas"]["eq"] = 34  # Berlin
        payload["variables"]["filters"]["listingDate"]["gte"] = gte
        payload["variables"]["filters"]["listingDate"]["lte"] = lte

        response = requests.post(URL, headers=HEADERS, json=payload)
        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            data = {}

        events_on_day = data.get("data", {}).get("eventListings", {}).get("data", [])
        print(f"{current_date.strftime('%Y-%m-%d')} → fetched {len(events_on_day)} events")
        # Print first event for debugging
        if events_on_day:
            print("First event:", events_on_day[0])
        events.extend(events_on_day)
        current_date += timedelta(days=1)

    print(f"Total events fetched: {len(events)}")
    return events
