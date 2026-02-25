# RA Artist Event Notifier

A full-stack system that monitors Berlin events from RA.co and sends email notifications to users when their favorite artists have new events.

## Features

- Fetches Berlin events from RA (GraphQL API)
- Tracks favorite artists per user
- Detects new events automatically
- Queues notifications
- Sends email alerts
- Runs daily via GitHub Actions

## Architecture

RA.co → update_events.py  
          ↓
      newevents (MongoDB)
          ↓
generate_email_events.py
          ↓
      emailevents (MongoDB)
          ↓
send_email_events.py
          ↓
        Email → User


---

# 3️⃣ Database Schema

Very important for clarity.

```markdown
## Database Collections

### users
{
  email: string,
  artists: string[]
}

### artists
{
  name: string,
  events: Event[]
}

### newevents
{
  artist: string,
  events: Event[]
}

### emailevents
{
  email: string,
  artist: string,
  event: Event,
  createdAt: Date
}

## Daily Pipeline

### 1. update_events.py
Fetches Berlin events and updates the `artists` and `newevents` collections.

### 2. generate_email_events.py
Matches users to new events and creates email jobs in `emailevents`.

### 3. send_email_events.py
Sends emails and deletes processed email jobs.

## Local Setup

1. Install Python 3.11+
2. Install dependencies:
   pip install -r requirements.txt

3. Create `.env` file:

MONGODB_URI=...
EMAIL_USER=...
EMAIL_PASS=...

4. Run manually:
   python update_events.py
   python generate_email_events.py
   python send_email_events.py

## Automated Daily Run

The pipeline runs daily at 07:00 UTC via GitHub Actions.

Workflow file:
.github/workflows/pipeline.yml

Secrets required:
- MONGODB_URI
- EMAIL_USER
- EMAIL_PASSWORD

## Future Improvements

- HTML email templates
- Daily digest mode
- Rate limiting
- Email retry logic
- Admin dashboard
- Logging and monitoring
- Deploy Next.js frontend to Vercel

