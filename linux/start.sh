#!/usr/bin/env bash
# Запуск XMRig на Linux. Имя воркера = hostname.
cd "$(dirname "$0")"
chmod +x ./xmrig 2>/dev/null || true
RIG="$(hostname)"
exec ./xmrig --rig-id="$RIG" --api-worker-id="$RIG" "$@"
