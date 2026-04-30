#!/usr/bin/env bash
# Tear down the Sentinel Health autonomous worker schedule.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HEARTBEAT="${REPO_ROOT}/.harness/heartbeat.sh"

OS="$(uname -s)"
case "$OS" in
  Darwin)
    PLIST_LABEL="com.sankar.sentinelhealth.harness"
    PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
    if [[ -f "$PLIST_PATH" ]]; then
      launchctl unload "$PLIST_PATH" 2>/dev/null || true
      rm -f "$PLIST_PATH"
      echo "Removed launchd agent: $PLIST_LABEL"
    else
      echo "No launchd agent found at $PLIST_PATH"
    fi
    ;;
  Linux)
    if crontab -l 2>/dev/null | grep -q "$HEARTBEAT"; then
      crontab -l 2>/dev/null | grep -v "$HEARTBEAT" | crontab -
      echo "Removed cron entry for $HEARTBEAT"
    else
      echo "No cron entry found for $HEARTBEAT"
    fi
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac
