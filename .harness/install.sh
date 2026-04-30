#!/usr/bin/env bash
# Schedule the Sentinel Health autonomous worker on macOS (launchd) or Linux (cron).
#
# Usage:
#   ./install.sh                # default 30 min interval
#   INTERVAL_SECONDS=900 ./install.sh   # custom interval (clamped to >=600)
#
# Adapted from pillowtalk's install.sh.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS_DIR="${REPO_ROOT}/.harness"
HEARTBEAT="${HARNESS_DIR}/heartbeat.sh"

INTERVAL_SECONDS="${INTERVAL_SECONDS:-1800}"
if (( INTERVAL_SECONDS < 600 )); then
  echo "INTERVAL_SECONDS must be >= 600 (10 min). Got: $INTERVAL_SECONDS"
  exit 1
fi

# Prerequisites
for cmd in git uv claude; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Missing prerequisite: $cmd"
    exit 1
  }
done

[[ -f "$HARNESS_DIR/CLAUDE.md" ]] || { echo "Missing $HARNESS_DIR/CLAUDE.md"; exit 1; }
[[ -f "$HARNESS_DIR/TODO.md"   ]] || { echo "Missing $HARNESS_DIR/TODO.md"; exit 1; }
[[ -x "$HEARTBEAT"             ]] || chmod +x "$HEARTBEAT"

OS="$(uname -s)"
case "$OS" in
  Darwin)
    PLIST_LABEL="com.sankar.sentinelhealth.harness"
    PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
    mkdir -p "$HOME/Library/LaunchAgents"
    cat >"$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>          <string>${PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${HEARTBEAT}</string>
  </array>
  <key>StartInterval</key>  <integer>${INTERVAL_SECONDS}</integer>
  <key>RunAtLoad</key>      <false/>
  <key>StandardOutPath</key><string>/tmp/sentinel-harness.out.log</string>
  <key>StandardErrorPath</key><string>/tmp/sentinel-harness.err.log</string>
  <key>WorkingDirectory</key><string>${REPO_ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH}</string>
  </dict>
</dict>
</plist>
PLIST
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load   "$PLIST_PATH"
    echo "Installed launchd agent: $PLIST_LABEL"
    echo "Interval: ${INTERVAL_SECONDS}s"
    echo "Logs:     /tmp/sentinel-harness-*.log"
    echo "Stop:     ./uninstall.sh"
    ;;
  Linux)
    MINUTES=$(( INTERVAL_SECONDS / 60 ))
    CRON_LINE="*/${MINUTES} * * * * ${HEARTBEAT}"
    ( crontab -l 2>/dev/null | grep -v "$HEARTBEAT" ; echo "$CRON_LINE" ) | crontab -
    echo "Installed cron entry: $CRON_LINE"
    echo "Interval: every ${MINUTES} min"
    echo "Logs:     /tmp/sentinel-harness-*.log"
    echo "Stop:     ./uninstall.sh"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac
