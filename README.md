[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/S4IEeO3Z)
# ENPM634 Midterm — Team 2: PasteBoard

A deliberately vulnerable code-sharing web application for the Build-It Break-It Fix-It midterm exercise.

## Template Chosen: Flask (Python)

All source code lives in the `flask/` directory. Other template directories have been removed.

## Quickstart

```bash
cd flask
docker compose up -d --build
```

Open [http://localhost](http://localhost) and register an account to get started.

## Documentation

- **[flask/README.md](flask/README.md)** — Features, file structure, default credentials
- **[VULNERABILITY_DISCLOSURE.md](VULNERABILITY_DISCLOSURE.md)** — Detailed disclosure of all 5 intentional vulnerabilities
- **[solves/](solves/)** — Exploit scripts and expected flags

## Features Built (5 beyond baseline)

1. **Search** — Full-text search across paste titles
2. **Comment system** — Post and view comments on pastes
3. **File upload/viewer** — Upload and read files in-browser
4. **User profiles with bio** — Editable bio with preview rendering
5. **Admin dashboard** — User management with stats and API
