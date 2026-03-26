"""Seed the database with admin user and flag data on first run."""

import os
from app import create_app, db
from app.models import User, Paste
from werkzeug.security import generate_password_hash

app = create_app()

ADMIN_PASS = "supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog"

with app.app_context():
    db.create_all()

    # Create admin user with admin role
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        print("[seed] Creating admin user...")
        admin = User(
            username="admin",
            password_hash=generate_password_hash(ADMIN_PASS),
            role="admin",
            bio="System administrator. Do not delete this account.",
        )
        db.session.add(admin)

    # Create sql_user with a private paste holding the SQLi flag (vuln 3)
    sql_user = User.query.filter_by(username="sql_user").first()
    if not sql_user:
        sql_user = User(
            username="sql_user",
            password_hash=generate_password_hash("sql_password_internal"),
            role="user",
            bio="",
        )
        db.session.add(sql_user)
        db.session.flush()

    sqli_paste = Paste.query.filter_by(title="Private Paste - SQL").first()
    if not sqli_paste:
        print("[seed] Creating SQLi flag paste...")
        sqli_paste = Paste(
            title="Private Paste - SQL",
            body=os.environ.get("FLAG_SQLI", "ENPM634{sql_injection_search_bypass}"),
            language="text",
            user_id=sql_user.id,
            is_private=True,
        )
        db.session.add(sqli_paste)

    db.session.commit()
    print("[seed] Database seeded successfully.")
