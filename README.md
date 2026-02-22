# Rex Phish Suite

<div align="center">

```
██████╗ ███████╗██╗  ██╗    ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗
██╔══██╗██╔════╝╚██╗██╔╝    ██╔══██╗██║  ██║██║██╔════╝██║  ██║
██████╔╝█████╗   ╚███╔╝     ██████╔╝███████║██║███████╗███████║
██╔══██╗██╔══╝   ██╔██╗     ██╔═══╝ ██╔══██║██║╚════██║██╔══██║
██║  ██║███████╗██╔╝ ██╗    ██║     ██║  ██║██║███████║██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
```

**A self-hosted phishing simulation & security awareness training platform**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square&logo=windows)

</div>

---

> ⚠️ **Authorized use only.** Never run this tool against systems or individuals without explicit written permission.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running the App](#running-the-app)
8. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
9. [Using the Dashboard](#using-the-dashboard)
10. [Creating a Campaign](#creating-a-campaign)
11. [Email Body Syntax](#email-body-syntax)
12. [Analytics](#analytics)
13. [Settings](#settings)
14. [URL Reference](#url-reference)
15. [Troubleshooting](#troubleshooting)

---

## Overview

Rex Phish Suite is a lightweight, self-hosted phishing simulation platform built with **Flask** and **SQLite**. It enables security professionals and red teams to:

- Send targeted phishing emails with embedded per-target tracking links
- Capture open, click, and credential submission events in real time
- View analytics across all campaigns from a single dashboard
- Export captured data as CSV

The UI uses a hacker/cyberpunk terminal aesthetic with a navy and neon color palette.

---

## Features

| Feature | Description |
|---|---|
| 📧 Campaign emails | Send HTML emails with a custom subject and body via Gmail SMTP |
| 🔗 Tracking links | Per-target UUID tracking for opens, clicks, and form submissions |
| 📊 Real-time analytics | Open rate, click rate, and credential capture rate per campaign |
| 📋 CSV export | Export all targets and captured credentials for any campaign |
| ⚙️ Settings panel | Admin credential management, system info, and database purge |
| 🔒 Localhost restriction | Admin panel accessible only from `127.0.0.1` by default |
| 🌐 Cloudflare tunnel | Public URL via `cloudflared` for internet-facing simulations |

---

## Project Structure

```
rexphish/
├── app.py                  # Main Flask application and all routes
├── config.py               # Config loader (reads from .env)
├── models.py               # SQLAlchemy database models
├── email_service.py        # SMTP email sending with tracking
├── requirements.txt        # Python dependencies
├── .env                    # 🔑 Secrets — never commit this file
├── .gitignore
├── run.bat                 # One-click start script (Windows)
├── start_tunnel.bat        # Cloudflare tunnel helper (Windows)
│
├── templates/
│   ├── admin_login.html       # Login page
│   ├── dashboard.html         # Campaign creation and listing
│   ├── campaign_details.html  # Per-campaign target table
│   ├── analytics.html         # Stats and event feed
│   ├── settings.html          # Admin credentials and preferences
│   └── landing.html           # Phishing landing page (credential capture)
│
└── static/
    └── rex_logo.svg        # App logo
```

---

## Requirements

- **Python 3.10+** — [python.org](https://python.org)
- **pip** (included with Python)
- **Gmail account** with an [App Password](https://myaccount.google.com/apppasswords) (requires 2FA)
- **cloudflared** *(optional, for a public URL)* — [Cloudflare Tunnel downloads](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/yourname/rexphish.git
cd rexphish
```

### 2. Create a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `flask-sqlalchemy` | ORM / database layer |
| `python-dotenv` | Loads `.env` config |

### 4. Configure `.env`

Create `rexphish/.env` using the template below:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password

SECRET_KEY=replace-this-with-a-long-random-string
DATABASE_URL=sqlite:///site.db

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Set this after starting your Cloudflare tunnel (see below)
PUBLIC_URL=https://your-tunnel.trycloudflare.com
```

> **Tip:** Generate a strong secret key with: `python -c "import secrets; print(secrets.token_hex(32))"`

### 5. Initialize the database

The database is created automatically on first run. To initialize it manually:

```bash
python -c "from app import app, db; app.app_context().__enter__(); db.create_all()"
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Admin panel login username |
| `ADMIN_PASSWORD` | `admin` | Admin panel login password |
| `SECRET_KEY` | *(hardcoded fallback)* | Flask session secret — **always change this in production** |
| `DATABASE_URL` | `sqlite:///site.db` | SQLAlchemy database URI |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | `587` | SMTP port (587 = STARTTLS) |
| `PUBLIC_URL` | *(empty)* | Public base URL used in tracking links |

Changes to `.env` take effect after restarting the app.

---

## Running the App

### Option A — One-click (Windows)

Double-click **`run.bat`** or run it from a terminal:

```bat
.\run.bat
```

This will automatically create the `venv` if needed, activate it, install dependencies, start the Flask server, and open `http://localhost:5000` in your browser.

### Option B — Manual

```bash
venv\Scripts\activate
python app.py
```

Then open: **http://localhost:5000/admin/login**

---

## Cloudflare Tunnel Setup

A public URL is required for tracking links in live campaigns. The easiest option is a free Cloudflare quick tunnel.

### 1. Download cloudflared

Download `cloudflared.exe` from the [Cloudflare downloads page](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) and place it in the `rexphish/` folder.

### 2. Start the tunnel

```bat
.\start_tunnel.bat
```

You'll see output similar to:

```
INF | Your quick Tunnel has been created! Visit it at:
https://warm-sunset-abc123.trycloudflare.com
```

### 3. Update `.env`

Copy the generated URL and set it in `.env`:

```env
PUBLIC_URL=https://warm-sunset-abc123.trycloudflare.com
```

Restart the app. Use the same URL in the **Public Base URL** field when creating a campaign.

> **Note:** Free quick tunnel URLs change every time you restart `start_tunnel.bat`. Update `.env` and any active campaigns accordingly.

---

## Using the Dashboard

Go to **http://localhost:5000** — you'll be redirected to the login page if not authenticated.

**Default credentials** are set in `.env` (`ADMIN_USERNAME` / `ADMIN_PASSWORD`).

### Sidebar Navigation

| Icon | Page | Description |
|---|---|---|
| ⬡ | Dashboard | Create campaigns and view the campaign list |
| ◈ | Analytics | Global stats, per-campaign rates, and event feed |
| ◇ | Settings | Change credentials, interface preferences, system info |
| ⏏ | Logout | End the admin session |

---

## Creating a Campaign

Fill in the **Launch Campaign** form on the Dashboard:

| Field | Description |
|---|---|
| **Sender Email** | Your Gmail address |
| **App Password** | Your Gmail App Password (not your regular password) |
| **Email Subject** | Subject line shown to targets |
| **Email Body** | HTML body — supports `{{link}}` syntax (see below) |
| **Target Emails** | One email address per line |
| **Public Base URL** | Your Cloudflare tunnel URL (e.g. `https://abc.trycloudflare.com`) |
| **Redirect URL** | Where targets land after submitting credentials (default: `microsoft.com`) |

Click **Launch Campaign** to create the campaign, then click **▶ Start Sending** on the details page to dispatch emails. Each target receives a unique tracking UUID.

---

## Email Body Syntax

The email body accepts standard HTML. Use the `{{link}}` token to embed a tracked click link.

**Default link text:**
```html
Please verify your account: {{link}}
```
Renders as: `Please verify your account: <a href="...">Click here to verify</a>`

**Custom anchor text:**
```html
Click {{link:here}} to complete your security check.
```
Renders as: `Click <a href="...">here</a> to complete your security check.`

A 1×1 invisible tracking pixel is automatically appended to every email to record open events.

---

## Analytics

Navigate to **http://localhost:5000/analytics**.

### Summary Cards

| Card | What it counts |
|---|---|
| Total Campaigns | All campaigns ever created |
| Emails Sent | Targets with status `Sent` |
| Total Clicks | `click` events across all campaigns |
| Credentials Captured | `submit` events (completed form submissions) |

### Campaign Breakdown

Per-campaign rate bars for open rate, click rate, and credential capture rate.

### Recent Events Feed

The last 50 events (open / click / submit), showing event type, target email, timestamp, and source IP. The page refreshes automatically every **30 seconds**.

---

## Settings

Navigate to **http://localhost:5000/settings**.

### Admin Credentials

Change the admin username and/or password. Your current password is required to authorize the change.

> ⚠️ Changes made here apply to the current session only. For permanent changes, update `.env` and restart the app.

### Interface Preferences

These are saved to browser `localStorage` and take effect immediately:

| Setting | Description |
|---|---|
| Auto-Reload on Campaign Page | Refresh every 5s to track live events |
| Confirm Before Delete | Show a confirmation dialog before deleting campaigns |
| Show Tracking IDs | Display UUID tracking IDs in tables |
| Default Redirect URL | Pre-filled in the redirect field for new campaigns |

### Purge All Data

Permanently deletes all campaigns, targets, events, and captured credentials from the database. A confirmation dialog is shown before execution.

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
| `/settings/clear_data` | POST | Purge all database data |
| `/send` | POST | Create a campaign and send emails |
| `/campaign/<id>` | GET | Campaign details page |
| `/export/<id>` | GET | Download campaign data as CSV |
| `/delete/<id>` | POST | Delete a campaign |
| `/api/send_target/<id>` | POST | Send email to a single target |
| `/track/open/<uuid>` | GET | Tracking pixel endpoint (open event) |
| `/account/verify?session=<uuid>` | GET | Click tracking and redirect |
| `/login/<uuid>` | GET | Phishing landing page |
| `/submit/<uuid>` | POST | Credential capture endpoint |

> 🔒 All `/admin/*` routes are restricted to `127.0.0.1`. Public tracking routes (`/track/`, `/account/`, `/login/`, `/submit/`) are accessible externally.

---

## Troubleshooting

**Gmail isn't sending emails**

Make sure 2-Step Verification is enabled on your Google account, then generate an [App Password](https://myaccount.google.com/apppasswords). Use the 16-character App Password in the campaign form — not your regular Gmail password.

**Tracking links point to localhost instead of the public URL**

Confirm you filled in the **Public Base URL** field when creating the campaign. It must exactly match your Cloudflare tunnel URL with no trailing slash. Also update `PUBLIC_URL` in `.env` and restart.

**`ModuleNotFoundError` on startup**

```bash
pip install -r requirements.txt
```

**Database errors or schema mismatch**

Delete the old database file and let the app recreate it:

```bash
del instance\site.db
python app.py
```

**Port 5000 is already in use**

Change the port in the last line of `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## License

MIT License — free to use for authorized security testing and educational purposes.

---

<div align="center">
Made with ◈ by Rex
</div>