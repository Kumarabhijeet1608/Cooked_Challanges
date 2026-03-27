# PasteBoard -- Team 2

A code-sharing web app built with Flask. Users create and share code snippets, search through pastes, upload files, and manage their profiles. Admins get a separate dashboard for managing users.

## Stack

- Python 3.12
- Flask 3.0.3, Flask-Login, Flask-SQLAlchemy
- SQLite (file-based, auto-created on first boot)
- Runs in Docker on port 80 (configurable in docker-compose.yml)

## Running It

```bash
cd flask
docker compose up -d --build
```

Go to http://localhost, register an account, and you're in.

## Accounts

The admin account is seeded on first boot:

- Username: `admin`
- Password: `supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog`
- Role: admin

Register a new account through `/register` for a regular user.

## Features

### Template Baseline
- Create, view, and delete code pastes
- Syntax language tagging (Python, JS, HTML, SQL, etc.)
- Private pastes that only the author can see
- User registration, login, logout

### Added Features

**1. Search**
Full-text search across paste titles. Results link back to the paste detail page. Located at `/search`.

**2. Comment System**
Any logged-in user can post comments on pastes. Comments show the author's username and are displayed below the paste body on the detail page.

**3. File Upload and Viewer**
Upload files through `/upload`. View uploaded file contents in-browser at `/uploads/<filename>`. HTML files get rendered as a preview; everything else shows as plaintext. There's also a download API at `/download?file=<name>`.

**4. User Profiles with Editable Bio**
Every user gets a profile page at `/profile/<username>` showing their avatar, username, and bio. Users can edit their bio from the profile page. A password reset form is available from the profile as well.

**5. Admin Dashboard with API**
Admin users can access `/admin` to see system stats (user count, paste count). The dashboard includes a user management API at `/admin/users` that returns user data as JSON. There's also a settings API at `/api/profile/settings` that accepts JSON updates for user preferences.

## File Structure

```
flask/
    Dockerfile
    docker-compose.yml
    requirements.txt
    entrypoint.sh
    seed_db.py
    app/
        __init__.py          # app factory, db init
        models.py            # User, Paste, Comment models
        routes.py            # all route handlers (main + auth blueprints)
        templates/
            base.html        # shared layout with nav
            index.html       # homepage with recent pastes
            login.html       # login form
            register.html    # registration form
            paste_form.html  # new paste form
            view_paste.html  # single paste view + comments
            search.html      # search form and results
            upload.html      # file upload form
            view_file.html   # uploaded file content display
            profile.html     # user profile page
            reset.html       # password reset form
            admin.html       # admin dashboard
```
