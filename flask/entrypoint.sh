#!/bin/bash
# PasteBoard entrypoint — writes flags to temp files, scrubs env, starts Flask.
# No flag values remain in environment variables after boot, so
# os.popen('env'), /proc/self/environ, and os.environ can't leak them.

set -e

# Write each flag to a separate file with tight permissions
echo "$FLAG_UPLOAD"        > /tmp/.flag_upload   && chmod 600 /tmp/.flag_upload
echo "$FLAG_SSTI"          > /tmp/.flag_ssti     && chmod 600 /tmp/.flag_ssti
echo "$FLAG_SQLI"          > /tmp/.flag_sqli     && chmod 600 /tmp/.flag_sqli
echo "$FLAG_BAC"           > /tmp/.flag_bac      && chmod 600 /tmp/.flag_bac

# Path traversal flag — stored in /app/.secrets/ (not the obvious /app/flag.txt)
mkdir -p /app/.secrets && chmod 755 /app/.secrets
echo "$FLAG_PATHTRAVERSAL" > /app/.secrets/pt_flag.txt && chmod 644 /app/.secrets/pt_flag.txt

# Decoy flags — attackers who try the obvious paths get trolled
echo "ENPM634{nice_try_but_the_flag_moved_check_deeper}" > /app/flag.txt
chmod 644 /app/flag.txt
echo "ENPM634{lol_this_is_a_decoy_look_harder}" > /app/data/flag.txt
chmod 644 /app/data/flag.txt

# Seed the database (needs env vars for seed_db.py)
python3 seed_db.py

# Self-destruct this script so source can't be read
rm -f /app/entrypoint.sh

# Launch Flask with a CLEAN environment — NO flag values in env
# Only pass through the variables Flask needs to run
exec env -i \
  PATH="/usr/local/bin:/usr/bin:/bin" \
  HOME="/root" \
  FLASK_APP=app \
  FLASK_RUN_HOST=0.0.0.0 \
  FLASK_ENV="${FLASK_ENV:-development}" \
  SECRET_KEY="${SECRET_KEY:-dev-secret-key}" \
  DATABASE_URL="${DATABASE_URL:-sqlite:////app/data/app.db}" \
  flask run
