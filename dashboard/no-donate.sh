#!/usr/bin/env bash
# Отключает донат разработчику без пересборки XMRig.
# Запуск: sudo bash no-donate.sh
set -e
if grep -qi 'donate.v2.xmrig.com' /etc/hosts; then
  echo "Already disabled."
else
  echo "127.0.0.1 donate.v2.xmrig.com"  >> /etc/hosts
  echo "127.0.0.1 donate.ssl.xmrig.com" >> /etc/hosts
  echo "Added: donate hosts -> 127.0.0.1"
fi
echo
echo "Проверка:"
grep -i 'xmrig.com' /etc/hosts || true
