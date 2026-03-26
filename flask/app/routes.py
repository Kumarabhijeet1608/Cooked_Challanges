"""
URL route handlers for PasteBoard.

Split into two blueprints:
- main: homepage, paste CRUD, search, comments, file upload, profiles, admin
- auth: registration, login, logout, password reset

Features beyond the template baseline:
1. Search pastes with full-text lookup
2. Comment system on individual pastes
3. File upload and viewer with download API
4. User profiles with editable biography
5. Admin dashboard with API key-protected user management
"""

import os
import hmac
import hashlib
import re as regex
import urllib.parse
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import User, Paste, Comment

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

# ---------------------------------------------------------------------------
# Internal constants for admin API key verification (vuln 5 chain)
# The key is derived from SECRET_KEY at runtime — not hardcoded
# ---------------------------------------------------------------------------
def _derive_api_key():
    """Derive admin API key from SECRET_KEY using HMAC-SHA256."""
    secret = os.environ.get("SECRET_KEY", "dev-secret-key")
    return hmac.new(
        secret.encode(), b"pasteboard-admin-api-v1", hashlib.sha256
    ).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Homepage — shows public pastes (excludes private pastes from other users)
# ---------------------------------------------------------------------------

@main.route("/")
def index():
    """Homepage — show public pastes."""
    pastes = Paste.query.filter_by(is_private=False).order_by(Paste.id.desc()).all()
    return render_template("index.html", pastes=pastes)


# ---------------------------------------------------------------------------
# View single paste — displays paste content and its comments
# ---------------------------------------------------------------------------

@main.route("/pastes/<int:paste_id>")
@login_required
def view_paste(paste_id):
    """View a single paste + its comments."""
    paste = Paste.query.get_or_404(paste_id)
    if paste.is_private and current_user.id != paste.user_id:
        abort(403)
    comments = Comment.query.filter_by(paste_id=paste_id).all()
    return render_template("view_paste.html", paste=paste, comments=comments)


# ---------------------------------------------------------------------------
# Search — full-text search across paste titles
# VULNERABILITY 3 (SQLi): raw SQL with user input via f-string
# TODO: vulnerable — input handling needs parameterization
# ---------------------------------------------------------------------------

@main.route("/search")
@login_required
def search():
    """Search pastes by title. Uses raw SQL for flexible LIKE matching."""
    query = request.args.get("q", "")
    results = []
    if query:
        # Build a raw SQL query for flexible LIKE matching
        # Using string formatting to support wildcard patterns in search
        raw = f"SELECT * FROM paste WHERE title LIKE '%{query}%' AND (is_private = 0 OR user_id = {current_user.id})"
        results = db.session.execute(db.text(raw)).fetchall()
    return render_template("search.html", results=results, query=query)


# ---------------------------------------------------------------------------
# Comments — add a comment to a paste
# ---------------------------------------------------------------------------

@main.route("/pastes/<int:paste_id>/comment", methods=["POST"])
@login_required
def add_comment(paste_id):
    """Add a comment to a paste."""
    text = request.form.get("body", "")
    if not text.strip():
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("main.view_paste", paste_id=paste_id))
    comment = Comment(content=text, posted_by=current_user.username, paste_id=paste_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("main.view_paste", paste_id=paste_id))


# ---------------------------------------------------------------------------
# File upload and viewer
# VULNERABILITY 1 (Stored XSS): HTML uploads rendered with |safe filter
# TODO: vulnerable — uploaded content rendering needs sanitization
# ---------------------------------------------------------------------------

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    """Upload a file. Filename is sanitized but extension is not restricted."""
    if request.method == "POST":
        f = request.files.get("file")
        if f and f.filename:
            # Sanitize stored name only; extension is not restricted (e.g. .html allowed)
            filename = secure_filename(f.filename)
            upload_folder = "/app/data/uploads"
            os.makedirs(upload_folder, exist_ok=True)
            f.save(os.path.join(upload_folder, filename))
            flash(f"{filename} uploaded.", "success")
            return redirect(url_for("main.index"))
    return render_template("upload.html")


@main.route("/uploads/<path:filename>")
@login_required
def view_file(filename):
    """Serve uploaded file contents for preview.

    Resolved paths must stay under the upload directory. For .html/.htm,
    view_file.html renders content with |safe (intentional stored XSS) and
    exposes FLAG_UPLOAD in a hidden span for grading.
    """
    upload_folder = os.path.normpath("/app/data/uploads")
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.normpath(os.path.join(upload_folder, filename))
    # Path traversal mitigation — keep reads inside uploads dir
    if not filepath.startswith(upload_folder + os.sep):
        abort(404)
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError:
        abort(404)
    # Read from file written at boot (not from env — env is scrubbed)
    upload_flag = ""
    try:
        with open("/tmp/.flag_upload") as f:
            upload_flag = f.read().strip()
    except OSError:
        pass
    return render_template(
        "view_file.html",
        filename=filename,
        content=content,
        upload_flag=upload_flag,
    )


# ---------------------------------------------------------------------------
# Download API v2 — file download with encoding support and security filters
# VULNERABILITY 4 (Path Traversal): URL-decode bypass on traversal filter
#
# Security measures present:
#   - Blocks literal "../" sequences (regex WAF)
#   - Blocks absolute paths starting with "/"
#   - Blocks null bytes
#   - Blocks ".db" extension reads
#   - Allowlist: only /app/data/ tree and /app/.secrets/ readable
#
# The bypass:
#   The WAF strips "../" ONCE before checking but the path parameter is
#   URL-decoded by Flask BEFORE reaching the route handler. If an attacker
#   sends a DOUBLE-URL-ENCODED path (e.g. %252e%252e%252f), Flask decodes
#   it to "%2e%2e%2f" (which passes the WAF), then os.path.join +
#   urllib.parse.unquote decodes it again to "../" during file resolution.
#
# The flag is NOT at the obvious /app/flag.txt (that's a decoy).
# Real flag: /app/.secrets/pt_flag.txt  (requires ../.secrets/pt_flag.txt
# from /app/data/uploads/)
#
# Inspired by CVE-2024-23334 (aiohttp static path traversal) and
# CVE-2023-24322 (Werkzeug path traversal via encoding confusion)
# TODO: vulnerable — path filter can be bypassed with encoded sequences
# ---------------------------------------------------------------------------

@main.route("/download")
@login_required
def download_file():
    """Download a file by name (?file=). Reads from uploads dir.

    Applies a security WAF to block directory traversal attempts.
    Supports optional format parameter (raw, hex) for developer tooling.
    """
    filename = request.args.get("file", "")
    if not filename:
        abort(400)

    # ---- WAF Layer 1: Block absolute paths ----
    if filename.startswith("/"):
        abort(403)

    # ---- WAF Layer 2: Block null bytes ----
    if "\x00" in filename:
        abort(403)

    # ---- WAF Layer 3: Regex filter for traversal sequences ----
    # Block literal dot-dot-slash in all common forms
    traversal_pattern = regex.compile(
        r'(\.\./|\.\.\\)',   # only catches literal ../ and ..\
        regex.IGNORECASE
    )
    if traversal_pattern.search(filename):
        abort(403)

    # ---- Resolve path (with secondary URL decode for API compat) ----
    # The download API accepts URL-encoded filenames for interoperability
    # with frontend JavaScript that may double-encode special characters.
    # We decode once here because Flask already decoded the query string once.
    resolved_name = urllib.parse.unquote(filename)

    upload_folder = "/app/data/uploads"
    filepath = os.path.join(upload_folder, resolved_name)

    # Resolve to absolute path
    resolved = os.path.realpath(filepath)

    # ---- WAF Layer 4: Allowlist — only /app/data/ and /app/.secrets/ ----
    allowed = (
        resolved.startswith("/app/data/")
        or resolved.startswith("/app/.secrets/")
    )
    if not allowed:
        abort(403)

    # ---- WAF Layer 5: Block database files ----
    if resolved.endswith((".db", ".sqlite", ".sqlite3")):
        abort(403)

    try:
        with open(filepath, "r") as fh:
            content = fh.read()
    except FileNotFoundError:
        abort(404)
    except (PermissionError, IsADirectoryError, OSError):
        abort(403)

    # Optional hex format for binary file inspection
    fmt = request.args.get("format", "raw")
    if fmt == "hex":
        content = content.encode().hex()

    return render_template("view_file.html", filename=filename, content=content,
                           upload_flag="")


# ---------------------------------------------------------------------------
# Paste CRUD — create, delete
# ---------------------------------------------------------------------------

@main.route("/pastes/new", methods=["GET", "POST"])
@login_required
def new_paste():
    """Create a new paste (title, body, language, private toggle)."""
    if request.method == "POST":
        title = request.form.get("title", "")
        body = request.form.get("body", "")
        language = request.form.get("language", "text")
        is_private = True if request.form.get("is_private") else False
        paste = Paste(
            title=title, body=body, language=language,
            user_id=current_user.id, is_private=is_private,
        )
        db.session.add(paste)
        db.session.commit()
        flash("Paste created.", "success")
        return redirect(url_for("main.index"))
    return render_template("paste_form.html")


@main.route("/pastes/<int:paste_id>/delete", methods=["POST"])
@login_required
def delete_paste(paste_id):
    """Delete a paste (author only)."""
    paste = Paste.query.get_or_404(paste_id)
    if paste.user_id != current_user.id:
        flash("You can only delete your own pastes.", "danger")
        return redirect(url_for("main.index"))
    db.session.delete(paste)
    db.session.commit()
    flash("Paste deleted.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# User profile — view and edit bio/settings
# VULNERABILITY 2 (SSTI): render_template_string on user-controlled username
# TODO: vulnerable — template rendering with user data needs sandboxing
# ---------------------------------------------------------------------------

@main.route("/profile/<username>")
@login_required
def profile(username):
    """Show a user's profile; greeting uses render_template_string."""
    user = User.query.filter_by(username=username).first_or_404()

    # VULNERABILITY (SSTI): user.username is embedded then evaluated as Jinja
    # Malicious usernames containing template syntax will be executed
    greeting_html = f"<h1>Welcome to {user.username}'s Board!</h1>"
    rendered_greeting = render_template_string(greeting_html)

    display_bio = None
    if current_user.is_authenticated and current_user.id == user.id:
        pastes = Paste.query.filter_by(user_id=user.id).all()
        display_bio = user.bio
    else:
        pastes = []

    return render_template(
        "profile.html", user=user, pastes=pastes,
        greeting=rendered_greeting, bio=display_bio,
    )


@main.route("/profile/edit_bio", methods=["POST"])
@login_required
def edit_bio():
    """Update current user's bio."""
    new_bio = request.form.get("bio", "")
    current_user.bio = new_bio
    db.session.commit()
    flash("Bio updated successfully!", "success")
    return redirect(url_for("main.profile", username=current_user.username))


# ---------------------------------------------------------------------------
# Profile settings API — update user preferences via JSON
# VULNERABILITY 5 (Broken Access Control): Mass assignment + IDOR chain
#
# The intended exploit chain (3 steps):
#
#   Step 1 — Mass Assignment (CVE-2024-29400 pattern):
#     POST /api/profile/settings with JSON body {"bio": "...", "role": "admin"}
#     The endpoint blindly applies ALL JSON keys to the User model, including
#     the "role" field which should be immutable. An attacker can self-promote
#     to admin by including "role": "admin" in the request body.
#
#   Step 2 — Discover the admin API key:
#     GET /admin → the dashboard HTML contains the API key in an HTML comment
#     (only visible if you have admin role from Step 1). The API key is
#     HMAC-derived from the SECRET_KEY.
#
#   Step 3 — Access the protected endpoint:
#     GET /admin/users?api_key=<key> → returns user list + flag
#     This endpoint validates the API key AND checks role == "admin".
#
# TODO: vulnerable — user settings endpoint accepts unvalidated fields
# ---------------------------------------------------------------------------

@main.route("/api/profile/settings", methods=["POST"])
@login_required
def profile_settings_api():
    """Update user settings via JSON. Accepts bio, display_name, etc."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Apply all provided fields to the user model
    # Intended fields: bio, display_name
    # BUG: also accepts "role" and any other User column — mass assignment!
    allowed_display = ("bio",)  # documented fields
    updated = []
    for key, value in data.items():
        if hasattr(current_user, key) and key not in ("id", "password_hash"):
            setattr(current_user, key, value)
            updated.append(key)

    db.session.commit()
    return jsonify({
        "status": "ok",
        "updated_fields": updated,
        "note": "Settings saved successfully.",
    })


# ---------------------------------------------------------------------------
# Admin dashboard — requires admin role
# ---------------------------------------------------------------------------

@main.route("/admin")
@login_required
def admin_dashboard():
    """Admin panel — role-gated. Contains the API key in page source."""
    if current_user.role != "admin":
        abort(403)

    user_count = User.query.count()
    paste_count = Paste.query.count()
    # Derive the API key to embed in the dashboard for frontend JS
    api_key = _derive_api_key()

    return render_template(
        "admin.html",
        user_count=user_count,
        paste_count=paste_count,
        api_key=api_key,
    )


# ---------------------------------------------------------------------------
# Admin flag endpoint — requires admin session (forged via SSTI SECRET_KEY leak)
# This is the final step in the SSTI exploit chain
# ---------------------------------------------------------------------------

@main.route("/admin/flag")
@login_required
def admin_flag():
    """Admin-only endpoint that reveals the SSTI flag."""
    if current_user.id != 1:
        abort(403)
    ssti_flag = ""
    try:
        with open("/tmp/.flag_ssti") as f:
            ssti_flag = f.read().strip()
    except OSError:
        pass
    return jsonify({"flag": ssti_flag})


# ---------------------------------------------------------------------------
# Admin users API — requires valid API key + admin role
# VULNERABILITY 5 final step: flag is returned when both gates pass
# TODO: vulnerable — endpoint accessible with leaked API key
# ---------------------------------------------------------------------------

@main.route("/admin/users")
@login_required
def admin_users_api():
    """User list API. Requires admin role AND valid api_key parameter."""
    # Gate 1: role check
    if current_user.role != "admin":
        return jsonify({"error": "Admin role required"}), 403

    # Gate 2: API key validation
    provided_key = request.args.get("api_key", "")
    expected_key = _derive_api_key()
    if not hmac.compare_digest(provided_key, expected_key):
        return jsonify({"error": "Invalid API key"}), 401

    users = User.query.all()
    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "paste_count": len(u.pastes),
        })
    # Flag gated behind both role + API key
    bac_flag = ""
    try:
        with open("/tmp/.flag_bac") as f:
            bac_flag = f.read().strip()
    except OSError:
        pass
    return jsonify({"users": user_list, "admin_token": bac_flag})


# ---------------------------------------------------------------------------
# Auth routes — registration, login, logout, password reset
# ---------------------------------------------------------------------------

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("auth.register"))
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        flash("Registered! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Log in with username and password."""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("main.index"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    """Log out and redirect to homepage."""
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/reset", methods=["GET", "POST"])
@login_required
def reset_password():
    """Change current user's password."""
    if request.method == "POST":
        current_password = request.form.get("password")
        new_password = request.form.get("new password")
        confirm_password = request.form.get("confirm password")

        if not check_password_hash(current_user.password_hash, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.reset_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password"))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Your password has been updated!", "success")
    return render_template("reset.html")
