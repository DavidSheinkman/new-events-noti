# RA Artist Event Notifier — Backend

A Python pipeline that monitors Berlin events from RA.co and sends email notifications to users when their followed artists have new upcoming events.

---

## Why This Exists

Keeping up with your favourite DJs shouldn't be a daily chore. This notifier solves three real problems:

- **Buy tickets while they're cheap.** New events often go on sale at their lowest price. Being notified on release day means you can grab tickets before demand drives prices up — or before they sell out entirely.
- **Plan ahead with confidence.** Knowing about an event weeks or months in advance gives you time to coordinate with friends, book time off work, and actually make it happen — instead of finding out three days before and scrambling.
- **No more manual checking.** Instead of visiting RA every day across a dozen artists, you get a single email the moment something new is announced. Your inbox becomes your event radar.

---

## Example Notification

Here's what a notification email looks like when one of your followed artists announces a new event:

![Email notification example](https://i.imgur.com/v2NIySf.png)

---

## How It Works

```
RA.co GraphQL API
       ↓
update_events.py        — fetches Berlin events, detects new ones
       ↓
  MongoDB (artists, newevents)
       ↓
generate_email_events.py — matches new events to subscribed users
       ↓
  MongoDB (emailevents)
       ↓
send_email_events.py    — sends emails and clears processed jobs
       ↓
     User Inbox
```

The pipeline runs daily at **07:00 UTC** via GitHub Actions.

---

## Pipeline Steps

### 1. `update_events.py`

Calls `fetch_events.py` to pull all Berlin events from the RA.co GraphQL API for the next 360 days (one day at a time to avoid pagination limits).

For each artist in the `artists` collection it checks whether any of the fetched events feature that artist. New events — ones not already stored in the artist's record — are added to both:
- `artists` collection (permanent history)
- `newevents` collection (pending notifications queue)

---

### 2. `generate_email_events.py`

Reads all documents from `newevents` and matches them against the `users` collection. For every user who follows a given artist, an email job is inserted into the `emailevents` collection. Once all users have been matched for a given event, that event is removed from `newevents`.

---

### 3. `send_email_events.py`

Reads all documents from `emailevents`, sends each one as a plain-text email via Gmail SMTP, and deletes the document on success. Failed sends are logged but not deleted, so they can be retried on the next run.

---

## Database Schema

### `users`
```json
{
  "email": "string",
  "artists": ["string"]
}
```

### `artists`
```json
{
  "name": "string",
  "events": ["Event"]
}
```

### `newevents`
```json
{
  "artist": "string",
  "events": ["Event"]
}
```

### `emailevents`
```json
{
  "email": "string",
  "artist": "string",
  "event": "Event",
  "createdAt": "Date"
}
```

---

## Local Setup

1. Install Python 3.11+

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```env
   MONGODB_URI=your_mongodb_connection_string
   EMAIL_USER=your_gmail_address
   EMAIL_PASS=your_gmail_app_password
   ```

4. Run the pipeline manually:
   ```bash
   python update_events.py
   python generate_email_events.py
   python send_email_events.py
   ```

---

## Automated Daily Run

The pipeline is triggered every day at 07:00 UTC by a GitHub Actions workflow.

**Workflow file:** `.github/workflows/pipeline.yml`

**Required secrets:**

| Secret | Description |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `EMAIL_USER` | Gmail address used to send emails |
| `EMAIL_PASSWORD` | Gmail App Password (not your account password) |

---

## Roadmap

### Frontend
- Redesign UI with modern layout and mobile responsiveness
- User authentication — login, signup, password reset
- Better loading states and artist search experience

### Backend
- Replace Gmail SMTP with a transactional email provider (SendGrid, Mailgun, or Resend) to avoid account suspension and improve deliverability
- Scheduled cleanup job to remove artists from the global `artists` collection when no users follow them and they have no upcoming events
- HTML email templates for richer notifications
- Daily digest mode — batch all new events into a single email per user per day
- Email retry logic for failed sends
- Structured logging and monitoring (e.g. Sentry, Datadog)

### Infrastructure
- Deploy Next.js frontend to Vercel
- Rate limiting on RA.co API requests
- Admin dashboard for monitoring pipeline runs
