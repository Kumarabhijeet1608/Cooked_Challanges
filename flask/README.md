# PasteBoard — Team 2

A code-sharing web application built with Flask. Users can create, search, and comment on code pastes, upload files, manage their profiles, and admins can manage users from a dashboard.

## Stack

- **Language**: Python 3.12
- **Framework**: Flask 3 + Flask-Login + Flask-SQLAlchemy
- **Database**: SQLite (default)
- **Port**: 80

## Quickstart

```bash
cd flask
docker compose up -d --build
```

Open [http://localhost](http://localhost) in your browser, register an account, and start sharing code.

## Accounts

The admin account is seeded on first boot with a **random password** (no default creds). Register a new account via the registration page to use the app.

## Features

### 1. Paste Management (Template Baseline)
- Create, view, and delete code pastes
- Syntax language tagging (Python, JavaScript, HTML, SQL, etc.)
- **Private pastes** — toggle visibility so only the author can see them
- Public pastes appear on the homepage for all users

### 2. Search
- Full-text search across paste titles
- Results link directly to the paste detail page

### 3. Comment System
- Post comments on any paste
- Comments display the author's username and content
- Supports rich text formatting in comments

### 4. File Upload & Viewer
- Upload files to the server
- View uploaded file contents directly in the browser
- Supports text-based files (code, configs, notes, etc.)

### 5. User Profiles with Editable Bio
- Profile page shows avatar, username, role, and bio
- Edit bio from the profile settings page
- Bio preview renders dynamic content with template variables
- Password reset from the profile page

### 6. Admin Dashboard
- User management panel (view all users, delete accounts)
- System statistics (user count, paste count, comment count)
- REST API for dashboard data (`/admin/users`)
- Restricted to admin-role users via the navigation menu

## File Structure

```
flask/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── app/
    ├── __init__.py           # App factory, DB init, seed data
    ├── models.py             # SQLAlchemy models (User, Paste, Comment, Secret)
    ├── routes.py             # All URL handlers (main + auth blueprints)
    └── templates/
        ├── base.html         # Shared layout with nav bar
        ├── index.html        # Homepage with recent pastes
        ├── login.html        # Login form
        ├── register.html     # Registration form
        ├── paste_form.html   # New paste form with privacy toggle
        ├── view_paste.html   # Single paste view + comment section
        ├── search.html       # Search form and results
        ├── upload.html       # File upload form
        ├── view_file.html    # Uploaded file content display
        ├── profile.html      # User profile page
        ├── edit_profile.html # Bio editor form
        ├── reset.html        # Password reset form
        └── admin.html        # Admin dashboard with user table
```

## Contribution Statement

- **Priyanka**: Built the initial features — paste viewing, search, comments, file upload/download. Set up the Flask template structure and tested all features.
- **Shakthi**: Added user profile page, password reset functionality, private paste toggle feature. Tested and integrated on top of Priyanka's work.
- **Abhijeet**: Designed and implemented the 5 intentional vulnerabilities (SQLi, XSS, SSTI, path traversal, broken access control). Built the admin dashboard, secret table seeding, solve scripts, disclosure document, and README. Code review and Docker testing.
- **Nishki**: Assisted with vulnerability design discussions, testing, and documentation review.
