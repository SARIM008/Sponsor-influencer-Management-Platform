# Influencer–Sponsor Management Platform

A web app where sponsors run advertising campaigns and influencers find and join them, with an admin who moderates both sides.

🏆 **Best Course Project, Modern Application Development I, IIT Madras.**

## What it does

- **Three roles: admin, sponsor, influencer.** Sponsors and influencers register with their own profile details (company, industry and budget for sponsors; platform, followers and niche for influencers).
- **Campaigns:** sponsors create, edit and delete campaigns with a budget, dates, goal, products and **public or private** visibility.
- **Two-way ad requests:**
  - Sponsors search influencers by name or niche and send them requests for a campaign.
  - Influencers browse active public campaigns and request to join.
  - The receiving side accepts or rejects; pending requests can be edited or withdrawn.
  - When a campaign is completed, its budget is added to the influencer's earnings.
- **Admin moderation:** an overview of campaigns by status and flagged/unflagged counts; admins can edit, delete, flag or unflag users, and delete, flag or unflag campaigns. Flagged items are hidden, and flagged users cannot log in.

## My role

Solo project: I designed and built the data model, routes and templates.

## Stack

Python, Flask, Flask-SQLAlchemy (SQLite), Jinja2 templates, HTML/CSS, Werkzeug password hashing

## Project structure

```
app.py         # entry point
init.py        # Flask app and SQLAlchemy setup
Config.py      # reads settings from .env
models.py      # User, Influencer, Sponsor, Campaign, Request; creates tables and the admin user
routes.py      # all pages and actions (auth, dashboards, campaigns, requests, admin)
templates/     # Jinja2 pages for each role
static/        # CSS
```

## How to run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit SECRET_KEY
python app.py               # http://localhost:5000
```

On first start the app creates the SQLite database and a local admin account (`admin` / `admin123`, for local testing only). Sponsors and influencers sign up through the registration pages.

## Known limitations

- Built as a course project for local use, not production.
- Admin pages do not check for an admin session, and the admin password is stored and compared in plain text. Sponsor and influencer passwords are hashed.
