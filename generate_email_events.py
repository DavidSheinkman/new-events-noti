from datetime import datetime
from mongodb_helper import (
    new_events_collection,
    users_collection,
    emailevents_collection
)

def main():
    newevents = list(new_events_collection.find({}))
    users = list(users_collection.find({}))

    print(f"Found {len(newevents)} artist entries in newevents")
    print(f"Found {len(users)} users")

    for artist_doc in newevents:
        artist_name = artist_doc["artist"]
        events = artist_doc.get("events", [])

        for event in events:
            event_id = event["id"]
            matched_users = 0

            for user in users:
                if artist_name in user.get("artists", []):
                    emailevents_collection.insert_one({
                        "email": user["email"],
                        "artist": artist_name,
                        "event": event,
                        "createdAt": datetime.utcnow()
                    })
                    matched_users += 1
                    print(
                        f"Queued email → {user['email']} → "
                        f"{artist_name} → {event['title']}"
                    )

            # remove this event from newevents after processing
            new_events_collection.update_one(
                {"_id": artist_doc["_id"]},
                {"$pull": {"events": {"id": event_id}}}
            )

            print(
                f"Event processed and removed from newevents → "
                f"{artist_name} → {event['title']} "
                f"(matched {matched_users} users)"
            )

if __name__ == "__main__":
    main()
