# Contribution Statement -- Team 2

## Piyer (Priyanka)
Built the SQL injection vulnerability in the search feature. Set up the raw SQL query in the search route that allows UNION-based injection. Created the initial search page and wired up the query handling.

## Shakthi
Implemented the SSTI vulnerability in the user profile feature. Added the `render_template_string` call on the username in the profile greeting. Set up the profile page with bio editing and the password reset flow.

## Abhijeet
Took everyone's individual vulnerability work, merged it into a single working codebase, and got the whole thing running together. Fixed flag formats, wrote all the solve scripts, and made sure the autograder passes for all 5 vulnerabilities.

Built the two advanced vulnerabilities from scratch:
- **Path traversal (Vuln 4):** Designed the double-URL-encoding WAF bypass with the decoy flag misdirection. Based the approach on CVE-2024-23334 and CVE-2023-24322 patterns.
- **Broken access control (Vuln 5):** Built the three-step chain with mass assignment for privilege escalation, API key leak through HTML comments, and the dual-gated admin endpoint. Modeled after CVE-2024-29400 mass assignment patterns.

Also handled the security hardening to make sure each vulnerability can only reach its own flag (env scrubbing at boot, allowlist on file reads, stripping sensitive fields from API responses). Set up the Docker deployment, entrypoint script, database seeding, nginx reverse proxy on the server, and wrote all the documentation.

## Nishki
Stored XSS vulnerability in the file upload feature. Set up the HTML file upload handling and the `|safe` filter in the view template that allows uploaded HTML to execute in the browser. Worked on the upload and file viewer pages.
