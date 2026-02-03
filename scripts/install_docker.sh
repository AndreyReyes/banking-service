#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This script uses apt; please run with sudo." >&2
  echo "Example: sudo ./scripts/install_docker.sh" >&2
  exit 1
fi

apt-get update
apt-get install -y docker.io

if ! apt-get install -y docker-compose-plugin; then
  echo "docker-compose-plugin not found; installing docker-compose." >&2
  apt-get install -y docker-compose
fi

target_user="${SUDO_USER:-}"
if [ -z "${target_user}" ] || [ "${target_user}" = "root" ]; then
  if id ubuntu >/dev/null 2>&1; then
    target_user="ubuntu"
  fi
fi

if [ -n "${target_user}" ]; then
  usermod -aG docker "${target_user}"
  echo "Added user '${target_user}' to the docker group."
else
  echo "Add your user to the docker group to run without sudo:"
  echo "  sudo usermod -aG docker <your-user>"
fi

systemctl enable --now docker

echo "Docker installed. You may need to log out and back in for group changes."
