#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This script uses apt; please run with sudo." >&2
  echo "Example: sudo ./scripts/install_docker.sh" >&2
  exit 1
fi

apt-get update

apt-get remove -y docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc || true

apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list >/dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

if ! getent group docker >/dev/null 2>&1; then
  groupadd docker
fi

target_user="${SUDO_USER:-}"
if [ -z "${target_user}" ] || [ "${target_user}" = "root" ]; then
  target_user="$(logname 2>/dev/null || true)"
fi
if [ -z "${target_user}" ] || [ "${target_user}" = "root" ]; then
  target_user="$(id -un 2>/dev/null || true)"
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
echo "Or run: newgrp docker"
