#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This script uses apt; please run with sudo." >&2
  echo "Example: sudo ./scripts/install_prereqs.sh" >&2
  exit 1
fi

apt-get update
apt-get install -y python3-venv python3-pip

echo "Prerequisites installed: python3-venv, python3-pip"
