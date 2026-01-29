from mongodb_helper import artists_collection, new_events_collection
from fetch_events import fetch_all_berlin_events

def main():
    events = fetch_all_berlin_events()  # fetch events from RA.co
    artists = list(artists_collection.find({}))  # all artists in DB

    for artist_doc in artists:
        artist_name = artist_doc["name"]
        artist_events_db = artist_doc.get("events", [])
        artist_event_ids = {e["id"] for e in artist_events_db}

        # Find events in 'events' list that include this artist
        new_artist_events = []
        for e in events:
            ev = e.get("event")
            if not ev:
                continue  # skip broken events
            
            artists_list = ev.get("artists")
            if not artists_list:
                continue  # skip events missing artist list
            
            artist_names_lower = [a["name"].lower() for a in artists_list if a.get("name")]
            
            if artist_name.lower() in artist_names_lower:
                new_artist_events.append(e)
        print(f"Artist {artist_name} → found {len(new_artist_events)} events in fetched data")


        # Deduplicate by event ID
        unique_events_dict = {}
        for e in new_artist_events:
            event_id = e["event"]["id"]
            if event_id not in unique_events_dict:
                unique_events_dict[event_id] = e
        new_artist_events = list(unique_events_dict.values())



        for event in new_artist_events:
            event_id = event["event"]["id"]
            if event_id not in artist_event_ids:
                # Add to artist DB
                print(f"New event for {artist_name}: {event['event']['title']}")
                artists_collection.update_one(
                    {"_id": artist_doc["_id"]},
                    {"$push": {"events": event["event"]}}
                )
                # Add to newevents DB
                new_events_collection.update_one(
                    {"artist": artist_name},
                    {"$addToSet": {"events": event["event"]}},
                    upsert=True
                )
                print(f"New event for {artist_name}: {event['event']['title']}")

if __name__ == "__main__":
    main()
