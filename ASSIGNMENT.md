# ENPM634 Midterm: Build-It Break-It Fix-It

## Overview

This midterm is a team-based, two-phase security exercise. Teams of four will first **build** a web application, then **attack** another team's application and document what they find. The goal is hands-on experience with the full software security lifecycle: building features, finding vulnerabilities, and writing actionable remediations.

---

## Teams

Teams of four have been pre-assigned. All team members are expected to contribute to both phases. Each submission must include a contribution statement indicating what each member worked on.

---

## Phase 1: Build It (2 weeks)

### Objective

Build a functional, deployable web application using one of the provided Docker starter templates. You will extend the template with **3 to 5 new features** and intentionally introduce **3 to 5 vulnerabilities** into your application. Keep scope tight — this is not a semester-long project. Focus on features that involve user input, data storage, and retrieval, as these naturally create interesting attack surface.

### Requirements

Your application must include:

- **User authentication** — registration, login, and logout (provided in the template)
- **3 to 5 additional features** beyond the template baseline. Examples:
  - A search function
  - File upload or download
  - User profiles or a settings page
  - An admin dashboard with elevated privileges
  - A comment or post system
  - A password reset or account management flow
- **3 to 5 intentional vulnerabilities** woven into your features. These should be real, exploitable weaknesses — not trivial issues like a missing field label. Each vulnerability must include a **flag** — a secret string in the format `ENPM634{descriptive_text}` (e.g., `ENPM634{sql_injection_login_bypass}`) that is revealed when the vulnerability is successfully exploited. Store flags as environment variables in your `docker-compose.yml` and wire them into your vulnerable code. See `solves/README.md` for details. Examples of vulnerabilities:
  - A SQL injection in a search or login query
  - A stored XSS in a comment or profile field
  - A missing authorization check that lets a regular user access admin functionality
  - An IDOR that allows a user to view or modify another user's data
  - A file upload that accepts and serves dangerous file types
- **A database** storing user data and feature data
- **Must run via `docker compose up --build`** from your repository root with no manual setup steps
- **Code quality standards** (see below)

Do not over-build. Three solid, working features are better than five broken ones. The vulnerabilities should feel natural — embedded in real features, not tacked on.

### Code Quality Standards

Your code will be evaluated for readability and documentation. These are professional expectations, not just grading criteria.

**Code Comments**

- Comment the *why*, not the *what*. A comment that says `// increment i` is useless. A comment that says `// skip admin users — they bypass rate limiting` adds real value.
- Every function or route handler should have a short comment explaining its purpose, its inputs, and any non-obvious behavior.
- Mark intentional vulnerabilities with a `TODO: vulnerable` comment so the grader can identify them — but make the comment vague enough that it is not an obvious cheat sheet (e.g., `// TODO: vulnerable — input handling` rather than `// TODO: SQL injection here`).

**Git Practices**

- Use **meaningful commit messages**. `fix bug` is not acceptable. `fix login redirect failing when session cookie is missing` is.
- Commit frequently — small, focused commits are better than one large commit at the end.
- Use **branches** for features and merge into `main` via pull requests. Each team member should have commits in the repository.
- Do not commit secrets, `.env` files, or credentials. Use `.env.example` for defaults (already provided in the templates).
- Tag your Phase 1 submission commit: `git tag phase1-submission`

**Clean Code**

- Use consistent indentation and formatting throughout. Pick a style and stick to it.
- Name variables and functions descriptively. `u` is not a variable name; `currentUser` is.
- Keep functions short and focused — a function that does one thing is easier to read and easier to attack.
- Remove dead code and commented-out blocks before submitting.

### Deliverables

Submit to Canvas by the Phase 1 deadline:

1. **GitHub repository - Provided by Github Classroom** — Must contain all of your source code (with documentation and code comments). 
2. **Docker Hub image** — your application must be pushed to Docker Hub so the instructor can pull and host it for Phase 2. See the [Docker Hub Submission Guide](#docker-hub-submission-guide) at the bottom of this document for step-by-step instructions.
3. **README** — instructions to run the app, default credentials (if any), and a brief description of each feature you built
4. **Vulnerability disclosure document** — a separate document (PDF or Markdown) listing each vulnerability you intentionally introduced. For each one, include:
   - The vulnerability type (e.g., Stored XSS)
   - Where it is in the code (file name and line number)
   - The flag associated with the vulnerability (e.g., `ENPM634{sql_injection_login_bypass}`) or defined indicator of success. This must be very obvious so the team in part 2 receiving your vulnerable app knows they successfully exploited. 
      - Becareful if the indicator of success is destructive like dropping SQL Tables. Highly recommend sticking with information and/or flag disclosure, authentication bypass (can use flag to show successfully authenticated), or remote code exxecution. 
   - A brief explanation of how it works

   This document will be used by the Instructor and TA to ensure everything works as intended. 
5. **Solve scripts (recommended)** — a `solves/` directory containing one exploit script per vulnerability and a `flags.txt` file with expected flags. Each script demonstrates that the vulnerability is real and exploitable by outputting a flag in the format `ENPM634{descriptive_text}`. The autograder runs these automatically when you push. This is a useful way to prove your vulnerabilities work and is strongly encouraged. See `solves/README.md` for full instructions.
6. **Contribution statement** — a short paragraph describing what each team member contributed

### Rules

- You may use AI tools (ChatGPT, Claude, Copilot, etc.) to assist with building your application. However, **we strongly recommend writing your intentional vulnerabilities by hand.** Understanding how a vulnerability works at the code level — how a query is constructed, why an input isn't sanitized, where an authorization check is missing — is the core learning objective of this exercise. If an AI writes your vulnerabilities for you, you will struggle in Phase 2 when you need to find and exploit similar issues in another team's code without AI assistance.
- You may use any libraries or frameworks available for your chosen stack.
- You may not submit pre-built vulnerable application frameworks (DVWA, WebGoat, Juice Shop, etc.).
- Your application must be original work — do not copy another team's code.

---

## Phase 2: Break It + Fix It (3 weeks)

After Phase 1 submissions are collected, each team will be assigned another team's application to attack. You will receive:
- A **URL** pointing to the live hosted application
- **Read access to their GitHub repository** so you can review the source code alongside your testing

### Objective

Find **3 to 5 vulnerabilities** in the assigned application. For each one, document what it is, show that it works, and explain how to fix it. The goal is not to find every bug — it is to practice the finding → exploiting → remediating cycle with a small number of well-documented issues.

### What to Test

You are expected to test for, but are not limited to:

- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Broken Access Control / Insecure Direct Object References (IDOR)
- Authentication weaknesses (weak passwords, missing session expiry, insecure logout)
- Sensitive data exposure (credentials in source code, verbose error messages)
- File upload vulnerabilities
- Any other OWASP Top 10 category

### Penetration Testing Report Requirements

Your report must be **concise and professional**. It does not need to be long — clear writing and solid evidence matter more than length. Use the following structure:

**1. Scope and Methodology**

A short section (half a page or less) covering:
- What application you tested and what features you focused on
- What tools you used (e.g., Burp Suite, curl, browser DevTools, sqlmap)
- Your general approach (manual testing, fuzzing, source code review, etc.)

**2. Findings**

Document **3 to 5 vulnerabilities**. For each finding, include:

- **Title** — A short descriptive name (e.g., "Stored XSS in Comment Field")
- **Severity** — Critical / High / Medium / Low
- **Description** — What the vulnerability is and where it exists in the application
- **Steps to Reproduce** — A numbered, step-by-step proof-of-concept that someone else can follow
- **Impact** — What an attacker could accomplish by exploiting this
- **Remediation** — A specific, actionable fix. Where possible, show the corrected code or configuration.

**3. Conclusion**

One short paragraph summarizing the overall security posture of the application and the most important fix the team should make.

### Scope and Rules of Engagement

- Your target is the **URL or Docker Image provided by the instructor**. That URL and its subpaths are in scope. Nothing else is.
- You may use any standard penetration testing tools (Burp Suite, OWASP ZAP, sqlmap, curl, browser DevTools, etc.).
- If provided a URL - you may **not** attack the server infrastructure itself (SSH, the Docker host, cloud provider console, etc.) — only the web application over HTTP/HTTPS.
- Demonstrate destructive attacks (e.g., dropping a table, deleting all users) with screenshots **before** you execute them — do not leave the application broken for your entire test window. If you cause data loss, document it and move on.
- Do not attempt denial-of-service attacks or send traffic at a rate that would affect the hosted server.
- Be professional. This is a simulated engagement, not a competition.

### Deliverables

Submit to Canvas by the Phase 2 deadline:

1. **Penetration testing report** (PDF) — Following the structure above
2. **Evidence** — Screenshots, HTTP request/response captures, or tool output for each finding. May be embedded in the PDF or submitted as a separate ZIP.
3. **Contribution statement** — What each team member worked on during Phase 2

---

## Grading Rubric (100 points)

### Phase 1: Build It (50 points)

| Criterion | Points |
|---|---|
| Application runs via `docker compose up --build` with no errors | 10 |
| 3 to 5 working features built beyond the template baseline | 15 |
| 3 to 5 intentional vulnerabilities are real and exploitable | 10 |
| Vulnerability disclosure document is complete and accurate | 5 |
| Code comments are meaningful and functions are documented | 5 |
| Git history shows frequent, well-described commits from all team members | 5 |
| Code is original | 0 (violation = zero for Phase 1) |

### Phase 2: Penetration Testing Report (50 points)

| Criterion | Points |
|---|---|
| Scope and methodology clearly describe what was tested and how | 10 |
| Each finding has a clear description and accurate severity rating | 10 |
| Each finding includes a working, reproducible proof-of-concept | 20 |
| Each finding includes a specific, actionable remediation | 5 |
| Conclusion is concise and identifies the most critical issue | 5 |

**Grading note:** Quality over quantity. A report with three findings that are fully documented — clear PoC, correct severity, and a concrete remediation — will score higher than a report with five vague findings with no evidence. Severity ratings that are significantly miscalibrated (e.g., marking a stored XSS as Low) will lose points.

---

## Deadlines

| Milestone | Date |
|---|---|
| Phase 1 — Application submission | TBD |
| Phase 2 — Penetration testing report submission | TBD (3 weeks after Phase 1) |

---

## Resources

### Security

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Starter templates repository](https://github.com/your-org/enpm634-midterm-template) *(update this link)*

### Code Comments and Documentation

- [Google Engineering Practices — Comments](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) (Python-focused but principles apply to any language)
- [Refactoring Guru — Comments (Code Smells)](https://refactoring.guru/smells/comments) — explains when comments help vs. hurt readability
- *Clean Code* by Robert C. Martin, Chapter 4 — the canonical reference on writing useful comments

### Git Best Practices

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — a widely used standard for commit message formatting
- [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) — Atlassian's guide to branch-based collaboration
- [How to Write a Git Commit Message](https://cbea.ms/git-commit/) — the classic blog post on the seven rules of a great commit message
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) — GitHub's recommended lightweight branching model

### Clean Code

- [Google Style Guides](https://google.github.io/styleguide/) — language-specific style guides for Python, JavaScript, and more
- [Refactoring Guru — Clean Code](https://refactoring.guru/refactoring) — interactive examples of clean vs. messy code
- [The Art of Readable Code](https://www.oreilly.com/library/view/the-art-of/9781449318482/) (O'Reilly) — practical, short book on writing code others can read

### Working in a Team

If this is your first time collaborating on code with a team, the tools and habits below will prevent most of the common pain points.

**Git and GitHub Collaboration**

- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) — the simplest branching model: one branch per feature, merge via pull request
- [How to Write a Git Commit Message](https://cbea.ms/git-commit/) — seven rules for commit messages your teammates can actually understand
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — a structured format for commit messages (`feat:`, `fix:`, `docs:`, etc.)
- [Resolving Merge Conflicts](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line) — merge conflicts will happen; this is how to resolve them cleanly
- [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) — Atlassian's step-by-step guide to branch-based teamwork
- [About Pull Requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) — how to use PRs for code review before merging

**Dividing Work**

- Assign each feature to one or two people — avoid everyone editing the same file at once
- Use GitHub Issues to track who is working on what (one issue per feature or task)
- Open a pull request early, even before the feature is done, and mark it as a Draft — this lets teammates see what you are working on and give feedback before you finish
- Review each other's code before merging — catching a bug in review is easier than debugging it later

**Communication and Process**

- Agree on a code style before you start writing (indentation, naming, file structure) — changing this midway causes noisy diffs and conflicts
- When you are blocked, say so early — a short message to your team is better than losing two days silently
- Treat code review comments as feedback on the code, not on the person who wrote it
- [The Joel Test](https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/) — a classic checklist for healthy software team practices; worth reading even if you only follow a few items

---

## Docker Hub Submission Guide

The instructor will pull your Docker image to host it for Phase 2. Follow these steps to push your application to Docker Hub.

### 1. Create a Docker Hub Account

If you don't already have one, sign up at [https://hub.docker.com](https://hub.docker.com). One account per team is sufficient.

### 2. Create a Repository on Docker Hub

1. Log in to Docker Hub
2. Click **Create Repository**
3. Name it something identifiable, e.g., `enpm634-team01`
4. Set the visibility to **Public** (so the instructor can pull it without credentials)

### 3. Build Your Image

From your project root (the directory containing `docker-compose.yml`):

```bash
docker compose build
```

### 4. Tag Your Image

Find the image name that was built (it's usually `<folder>-app`):

```bash
docker images
```

Tag it with your Docker Hub username and repository name:

```bash
docker tag <local-image-name> <dockerhub-username>/enpm634-team01:phase1
```

For example, if your local image is `flask-app` and your Docker Hub username is `student123`:

```bash
docker tag flask-app student123/enpm634-team01:phase1
```

### 5. Log In to Docker Hub from the CLI

```bash
docker login
```

Enter your Docker Hub username and password (or access token) when prompted.

### 6. Push the Image

```bash
docker push <dockerhub-username>/enpm634-team01:phase1
```

### 7. Verify the Push

Go to your Docker Hub repository page and confirm the `phase1` tag appears. You can also test pulling it on a clean machine:

```bash
docker pull <dockerhub-username>/enpm634-team01:phase1
```

### 8. Submit the Image Reference

Include the full image reference in your Canvas submission, e.g.:

```
student123/enpm634-team01:phase1
```

### Important Notes

- **Push early.** Do not wait until the last hour before the deadline — upload issues and network errors happen.
- If your application uses multiple containers (e.g., app + database), you only need to push the **application image**. The instructor will provide the database container. Make sure your app can connect to a database via environment variables (`DB_HOST`, `DB_USER`, etc.) so it works in the hosted environment.
- If you update your image before the deadline, push again with the same tag — it will overwrite the previous version.
- **Do not include secrets or `.env` files in your Docker image.** Use environment variables that can be set at runtime.

---

## Academic Integrity

All work must comply with the University of Maryland Academic Integrity Policy. Copying code from another team or attacking infrastructure outside the defined scope will result in a zero for the assignment and may be referred for academic integrity review.
