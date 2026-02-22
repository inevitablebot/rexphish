# Rex Phish Suite

A self-hosted phishing simulation & awareness training platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python) ![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square) ![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square&logo=windows)

---
> ⚠️ **For authorized security testing and awareness training only.**  
> Never use this tool against systems or individuals without explicit written permission.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Configuration (.env)](#configuration-env)
7. [Running the App](#running-the-app)
8. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
9. [Using the Dashboard](#using-the-dashboard)
10. [Creating a Campaign](#creating-a-campaign)
11. [Email Body Syntax](#email-body-syntax)
12. [Analytics Page](#analytics-page)
13. [Settings Page](#settings-page)
14. [URL Reference](#url-reference)
15. [Troubleshooting](#troubleshooting)

---

## Overview

Rex Phish Suite is a lightweight, self-hosted phishing simulation tool built with **Flask** and **SQLite**. It lets security professionals and red teams:

- Send targeted phishing emails with embedded tracking links
- Capture open / click / credential submission events per target
- View real-time analytics across all campaigns
- Export captured data as CSV

The UI follows a hacker/cyberpunk terminal aesthetic with a navy + neon palette.

---

## Quick Start (short)

1. Clone the repository and change directory:

```bash
git clone https://github.com/inevitablebot/rexphish.git
cd rexphish
```

2. Create and activate a Python virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a minimal `.env` file (see `Run scripts & .env` below for details) and start the app:

```powershell
# Windows one-click
.\run.bat

# Or manual
venv\Scripts\activate
python app.py
```

---

## Run scripts & .env (examples)

- `run.bat`: Windows helper that creates/activates the venv, installs dependencies, and launches the dev server. Use this for quick local runs.
- `start_tunnel.bat`: Starts a Cloudflare quick tunnel (if you placed `cloudflared.exe` in the repo).

Minimal `.env` example (DO NOT commit your real secrets):

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
SECRET_KEY=replace-with-strong-secret
DATABASE_URL=sqlite:///site.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
PUBLIC_URL=
```

Tips:
- Use a strong `SECRET_KEY` (generate with Python: `python -c "import secrets; print(secrets.token_hex(32))"`).
- For sending email via Gmail, create an App Password and put it in the campaign form (not in `.env`).
---

## Features

| Feature | Description |
|---|---|
| 📧 Campaign emails | Send HTML emails with custom subject & body via Gmail SMTP |
| 🔗 Tracking links | Per-target UUID tracking for opens, clicks, and form submissions |
| 📊 Analytics | Real-time stats: open rate, click rate, credential capture rate |
| 📋 Data export | CSV export of all targets + captured credentials per campaign |
| ⚙️ Settings | Admin credential management, system info, DB purge |
| 🔒 Localhost restriction | Admin panel only accessible from `127.0.0.1` by default |
| 🌐 Cloudflare tunnel | Public URL via `cloudflared` for remote phishing simulations |

---

## Project Structure

```
rexphish/
├── app.py                  # Main Flask application & all routes
├── config.py               # Config loader (reads from .env)
├── models.py               # SQLAlchemy DB models
├── email_service.py        # SMTP email sending with tracking
├── requirements.txt        # Python dependencies
├── .env                    # 🔑 Your secrets (never commit this)
├── .gitignore
├── run.bat                 # One-click start script (Windows)
├── start_tunnel.bat        # Cloudflare tunnel helper (Windows)
│
├── templates/
│   ├── admin_login.html    # Login page
│   ├── dashboard.html      # Campaign creation & listing
│   ├── campaign_details.html  # Per-campaign target table
│   ├── analytics.html      # Stats & event feed
│   ├── settings.html       # Admin credentials & preferences
│   └── landing.html        # Phishing landing page (credential capture)
│
└── static/
    └── rex_logo.svg        # App logo
```

---

## Requirements

- **Python 3.10+** — [python.org](https://python.org)
- **pip** (comes with Python)
- **Gmail account** with an [App Password](https://myaccount.google.com/apppasswords) (2FA must be enabled)
- **cloudflared** *(optional, for public URL)* — [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

---

## Installation

### Step 1 — Clone or download the project

```bash
git clone https://github.com/inevitablebot/rexphish.git
cd rexphish
```

Or just unzip the folder and open a terminal inside it.

---

### Step 2 — Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `flask-sqlalchemy` | ORM / database layer |
| `python-dotenv` | Loads `.env` config file |

---

### Step 4 — Configure `.env`

Copy the example below and edit `rexphish/.env`:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password

SECRET_KEY=replace-this-with-a-long-random-string
DATABASE_URL=sqlite:///site.db

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Your Cloudflare / ngrok public URL (set after running the tunnel)
PUBLIC_URL=https://your-tunnel.trycloudflare.com
```

> **Secret key tip:** Generate a strong key with Python:
> ```python
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### Step 5 — Initialize the database

The database is created automatically on first run. You can also run:

```bash
python -c "from app import app, db; app.app_context().__enter__(); db.create_all()"
```

---

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Login username for the admin panel |
| `ADMIN_PASSWORD` | `admin` | Login password for the admin panel |
| `SECRET_KEY` | *(hardcoded fallback)* | Flask session secret — **change this in production** |
| `DATABASE_URL` | `sqlite:///site.db` | SQLAlchemy DB URI. Use `sqlite:///site.db` for local |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | `587` | SMTP port (587 = STARTTLS) |
| `PUBLIC_URL` | *(empty)* | Public base URL used in tracking links (Cloudflare tunnel URL) |

> Changes to `.env` take effect after restarting `run.bat`.

---

## Running the App

### Option A — One-click (Windows)

Double-click **`run.bat`** or run from terminal:

```bat
.\run.bat
```

This will:
1. Create the `venv` if it doesn't exist
2. Activate the virtual environment
3. Install/update dependencies from `requirements.txt`
4. Open `http://localhost:5000` in your browser
5. Start the Flask dev server

---

### Option B — Manual

```bash
# Activate venv first
venv\Scripts\activate

# Start the server
python app.py
```

Then open: **http://localhost:5000/admin/login**

---

## Cloudflare Tunnel Setup

To make the phishing landing page reachable from the internet (required for sending real emails), you need a public URL.

### Step 1 — Download cloudflared

Download `cloudflared.exe` from:  
https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

Place `cloudflared.exe` in the `rexphish/` folder.

### Step 2 — Start the tunnel

Double-click **`start_tunnel.bat`** or run:

```bat
.\start_tunnel.bat
```

You'll see output like:

```
INF | Thank you for trying Cloudflare Tunnel...
INF | Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://warm-sunset-abc123.trycloudflare.com
```

### Step 3 — Add the URL to `.env`

Copy the `https://...trycloudflare.com` URL and set it in `.env`:

```env
PUBLIC_URL=https://warm-sunset-abc123.trycloudflare.com
```

Restart `run.bat`. Now paste the same URL into the **Public Base URL** field when creating a campaign.

> **Note:** The free Cloudflare quick tunnel URL changes each time you restart `start_tunnel.bat`. Update `.env` and the campaign accordingly.

---

## Using the Dashboard

Navigate to: **http://localhost:5000** (redirects to login if not authenticated)

### Login
- Default credentials are set in `.env` (`ADMIN_USERNAME` / `ADMIN_PASSWORD`)
- After login, you land on the Dashboard

### Navigation (sidebar)
| Icon | Page | Description |
|---|---|---|
| ⬡ | Dashboard | Create campaigns, view campaign list |
| ◈ | Analytics | Global stats, per-campaign rates, event feed |
| ◇ | Settings | Change credentials, interface prefs, system info |
| ⏏ | Logout | End the admin session |

---

## Creating a Campaign

On the **Dashboard**, fill in the **Launch Campaign** form:

| Field | Description |
|---|---|
| **Sender Email** | Your Gmail address used to send emails |
| **App Password** | Gmail App Password (not your regular Gmail password) |
| **Email Subject** | Subject line shown to targets |
| **Email Body** | HTML body. Supports `{{link}}` syntax (see below) |
| **Target Emails** | One email address per line |
| **Public Base URL** | Your Cloudflare tunnel URL (e.g. `https://abc.trycloudflare.com`) |
| **Redirect URL** | Where to send targets after they submit credentials (defaults to `microsoft.com`) |

Click **Launch Campaign** to create the campaign and go to the details page.

### Sending Emails

On the **Campaign Details** page, click **▶ Start Sending** to dispatch emails to all pending targets one by one. Each target gets its own unique tracking UUID.

---

## Email Body Syntax

The email body supports plain HTML. Use the special `{{link}}` token to embed a tracked click link.

### Auto link (default text)
```html
Please verify your account: {{link}}
```
Renders as: `Please verify your account: <a href="...">Click here to verify</a>`

### Custom anchor text
```html
Click {{link:here}} to complete your security check.
```
Renders as: `Click <a href="...">here</a> to complete your security check.`

### Tracking pixel
A 1×1 invisible tracking pixel is automatically appended to every email to detect **opens**.

---

## Analytics Page

Navigate to: **http://localhost:5000/analytics**

### Stat Cards
| Card | What it counts |
|---|---|
| Total Campaigns | All campaigns ever created |
| Emails Sent | Targets with status = `Sent` |
| Total Clicks | `click` events across all targets |
| Credentials Captured | `submit` events (form completions) |

### Campaign Breakdown Table
Per-campaign rate bars showing:
- **Open rate** — % of targets who opened the email
- **Click rate** — % of targets who clicked the link
- **Capture rate** — % of targets who submitted credentials

### Recent Events Feed
Live feed of the last 50 events (open / click / submit) showing:
- Event type + target email
- Timestamp
- Source IP address

> The page auto-refreshes every **30 seconds**.

---

## Settings Page

Navigate to: **http://localhost:5000/settings**

### Admin Credentials
Change the admin username and/or password. The current password is required to authorize the change.

> ⚠️ Credential changes apply **for the current session only** (config is in memory).  
> For permanent changes, update `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env` and restart.

### Interface Preferences
Saved to browser `localStorage` (no server restart needed):

| Setting | Description |
|---|---|
| Auto-Reload on Campaign Page | Refresh every 5s to track live events |
| Confirm Before Delete | Show dialog before deleting campaigns |
| Show Tracking IDs | Display UUID tracking IDs in tables |
| Default Redirect URL | Pre-filled in new campaigns |

### Purge All Data
Permanently deletes **all campaigns, targets, events, and captured data** from the database. A confirmation dialog is shown before execution.

---

## URL Reference

| URL | Method | Description |
|---|---|---|
| `/admin/login` | GET / POST | Admin login page |
| `/admin/logout` | GET | End session |
| `/` | GET | Dashboard |
| `/analytics` | GET | Analytics overview |
| `/settings` | GET | Settings page |
| `/settings/credentials` | POST | Update admin credentials |
| `/settings/clear_data` | POST | Purge all DB data |
| `/send` | POST | Create campaign + send emails |
| `/campaign/<id>` | GET | Campaign details |
| `/export/<id>` | GET | Download CSV of campaign data |
| `/delete/<id>` | POST | Delete a campaign |
| `/api/send_target/<id>` | POST | Send email to a single target |
| `/track/open/<uuid>` | GET | Tracking pixel endpoint (open event) |
| `/account/verify?session=<uuid>` | GET | Click tracking + redirect |
| `/login/<uuid>` | GET | Phishing landing page |
| `/submit/<uuid>` | POST | Credential capture endpoint |

> 🔒 All `/admin/*` and internal routes are restricted to `127.0.0.1` only.  
> Public tracking routes (`/track/`, `/account/`, `/login/`, `/submit/`) are accessible externally.

---

## Troubleshooting

### Gmail not sending emails?
1. Ensure **2-Step Verification** is enabled on your Google account
2. Generate an **App Password** at: https://myaccount.google.com/apppasswords
3. Use the App Password (16 characters, no spaces) in the **App Password** field — not your regular Gmail password

### Tracking links go to localhost instead of the public URL?
- Make sure you filled in the **Public Base URL** field when creating the campaign
- It must match your Cloudflare tunnel URL exactly (no trailing slash)
- Update `.env` → `PUBLIC_URL` and restart

### `ModuleNotFoundError` on startup?
```bash
pip install -r requirements.txt
```

### Database errors / schema mismatch?
Delete the old database and let it recreate:
```bash
del instance\site.db
python app.py
```

### Port 5000 already in use?
Change the port in `app.py` (last line):
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## License

MIT License — use freely for authorized testing and educational purposes.

---

<div align="center">
Made with ◈ by Rex
</div>
#   r e x p h i s h 
 
 