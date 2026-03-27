[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/S4IEeO3Z)
# ENPM634 Midterm -- Team 2: PasteBoard

A code-sharing web application built for the Build-It Break-It Fix-It midterm. Users can share code snippets, search pastes, upload files, manage their profiles, and admins get a dashboard for user management.

## Template: Flask (Python)

Everything lives in `flask/`. The other template directories have been removed.

## How to Run

```bash
cd flask
docker compose up -d --build
```

The app starts on port 80 by default. Open http://localhost and register a new account to start using it.

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | `supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog` | admin |

A regular user account can be created through the registration page.

## Features (5 beyond template baseline)

1. **Search** -- full-text search across paste titles with result linking
2. **Comments** -- post and view comments on any paste
3. **File upload and viewer** -- upload files to the server and preview them in-browser
4. **User profiles with editable bio** -- profile page with avatar, bio editing, password reset
5. **Admin dashboard with API** -- admin panel showing stats, user management, and a REST API endpoint for user data

## Documentation

- [flask/README.md](flask/README.md) -- features, file structure, default credentials
- [VULNERABILITY_DISCLOSURE.md](VULNERABILITY_DISCLOSURE.md) -- all 5 intentional vulnerabilities with code locations and flags
- [CONTRIBUTION.md](CONTRIBUTION.md) -- what each team member worked on
- [solves/](solves/) -- exploit scripts and expected flags
- [solves/flags.txt](solves/flags.txt) -- one flag per line, matching vuln1 through vuln5

## Solve Scripts

Each vulnerability has a corresponding solve script in `solves/`. They take the app URL as the first argument and print the flag to stdout.

```bash
bash solves/vuln1_stored_xss_html_upload.sh http://localhost
bash solves/vuln2_ssti_username.sh http://localhost
bash solves/vuln3_sqli_search.sh http://localhost
bash solves/vuln4_path_traversal.sh http://localhost
bash solves/vuln5_broken_access_control.sh http://localhost
```

The autograder runs these automatically:

```bash
bash .github/scripts/run-test.sh smoke     # build check
bash .github/scripts/run-test.sh vuln 1    # runs vuln1 script, checks flag
```
