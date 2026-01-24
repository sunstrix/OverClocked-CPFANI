# OverClocked Helpdesk

OverClocked Helpdesk is a FastAPI based helpdesk system built for hackathons and college events. It allows teams to raise queries, admins to manage mentors, and mentors to view and respond to assigned queries in real time. The system focuses on fast routing, clear visibility, and minimal manual coordination during events.

The project is designed to work as a central query handling platform where teams do not have to chase mentors, and mentors can see exactly what they need to handle.

---

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite (local development)
* Jinja2 Templates
* HTML, CSS
* Uvicorn

---

## Features

* Team helpdesk form to raise queries
* Admin dashboard to manage mentors and view queries
* Mentor dashboard to see assigned queries
* Automatic mentor assignment logic
* QR code based access for teams
* Email notification support
* Slack notification support
* Clean separation of admin, mentor, and team views

---

## Project Structure

```
OverClocked-Helpdesk/
│
├── overclocked_helpdesk/
│   ├── api/
│   │   ├── admin.py          # Admin routes and logic
│   │   ├── mentors.py        # Mentor related APIs
│   │   ├── queries.py        # Team query APIs
│   │   ├── qr.py             # QR code generation logic
│   │   └── __init__.py
│   │
│   ├── db/
│   │   ├── schema.py         # Database models setup
│   │   └── session.py        # Database session handling
│   │
│   ├── models/
│   │   ├── mentor.py         # Mentor table model
│   │   ├── query.py          # Query table model
│   │   └── team.py           # Team table model
│   │
│   ├── services/
│   │   ├── assigner.py       # Mentor assignment logic
│   │   ├── email_service.py  # Email notification logic
│   │   ├── slack_service.py  # Slack notification logic
│   │   └── notifier.py       # Unified notification handler
│   │
│   ├── utils/
│   │   └── qr.py             # QR utility helpers
│   │
│   ├── config.py             # App configuration and settings
│   ├── main.py               # FastAPI app entry point
│   └── __init__.py
│
├── templates/
│   ├── admin_dashboard.html  # Admin UI
│   ├── mentor_dashboard.html # Mentor UI
│   ├── helpdesk_form.html    # Team query form
│   ├── team_status.html      # Query status page
│   └── success.html          # Submission success page
│
├── scripts/
│   ├── seed_data.py          # Initial data seeding
│   ├── test_email.py         # Email testing script
│   └── test_notifier.py      # Notification testing
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Screenshots

Screenshots of the following pages will be added:

* Admin dashboard
* Mentor dashboard
* Team helpdesk form

---

## How to Run Locally

### 1. Clone the repository

```
git clone https://github.com/Ishitaaa26/OverClocked-Helpdesk.git
cd OverClocked-Helpdesk
```

### 2. Create and activate virtual environment

```
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run the FastAPI server

```
uvicorn overclocked_helpdesk.main:app --reload
```

### 5. Open in browser

* App: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Use Case

This project is ideal for:

* Hackathons
* College technical events
* Internal tech fests
* Any event where teams need quick access to mentors

---

## Future Scope

* Authentication for admins and mentors
* Real time updates using WebSockets
* Deployment support using Docker
* Analytics dashboard for admins

