#!/bin/sh
set -eu

mkdir -p /run/clamav /var/log/clamav /var/lib/clamav
chown -R clamav:clamav /run/clamav /var/log/clamav /var/lib/clamav

# Prime signatures, then keep the updater running. The API stays unavailable until clamd answers PING.
if [ ! -f /var/lib/clamav/main.cvd ] && [ ! -f /var/lib/clamav/main.cld ]; then
  su -s /bin/sh clamav -c "freshclam --stdout" || true
fi
su -s /bin/sh clamav -c "freshclam --daemon --checks=12" &

su -s /bin/sh clamav -c "clamd --foreground --config-file=/etc/clamav/clamd.conf" &
CLAMD_PID=$!

shutdown() {
  kill "$CLAMD_PID" 2>/dev/null || true
}
trap shutdown TERM INT

exec uvicorn scanner:app --host 0.0.0.0 --port 8080
