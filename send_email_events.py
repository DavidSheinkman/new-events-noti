import os
import smtplib
from email.message import EmailMessage
from mongodb_helper import emailevents_collection


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")


def send_email(to_email, artist, event):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = f"New {artist} event in Berlin 🎶"

    body = f"""
New event found!

Artist: {artist}
Event: {event['title']}
Date: {event['date']}
Start: {event['startTime']}
Venue: {event['venue']['name']}

Link:
https://ra.co{event['contentUrl']}
"""

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    email_events = list(emailevents_collection.find({}))
    print(f"Found {len(email_events)} email events to send")

    for email_event in email_events:
        try:
            send_email(
                to_email=email_event["email"],
                artist=email_event["artist"],
                event=email_event["event"]
            )

            emailevents_collection.delete_one(
                {"_id": email_event["_id"]}
            )

            print(
                f"Email sent → "
                f"{email_event['email']} → "
                f"{email_event['event']['title']}"
            )

        except Exception as e:
            print(
                f"FAILED to send email to {email_event['email']} "
                f"for {email_event['event']['title']}: {e}"
            )

if __name__ == "__main__":
    main()
