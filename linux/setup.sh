#!/usr/bin/env bash
# Одноразовая настройка: systemd-сервис с автозапуском и перезапуском при падении.
# Запуск: sudo bash setup.sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$DIR/xmrig" "$DIR/start.sh"

echo "[1/4] Устанавливаем systemd-сервис..."
cat > /etc/systemd/system/xmrig.service <<EOF
[Unit]
Description=XMRig Monero Miner
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=$DIR/start.sh
Restart=always
RestartSec=10
User=root
Nice=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable xmrig >/dev/null 2>&1 || true

echo "[2/4] Отключаем донат разработчику..."
if ! grep -qi 'donate.v2.xmrig.com' /etc/hosts; then
    echo "127.0.0.1 donate.v2.xmrig.com"  >> /etc/hosts
    echo "127.0.0.1 donate.ssl.xmrig.com" >> /etc/hosts
    echo "      OK"
else
    echo "      уже отключён"
fi

echo "[3/4] Пробуем включить huge pages (опционально)..."
if [ -w /proc/sys/vm/nr_hugepages ]; then
    echo 256 > /proc/sys/vm/nr_hugepages 2>/dev/null || true
    echo "      nr_hugepages=256"
else
    echo "      пропущено (нет прав) - не критично"
fi

echo "[4/4] Запускаем..."
systemctl start xmrig
sleep 2
systemctl --no-pager status xmrig | head -12

echo
echo "Готово. Проверка: https://xmrpool.eu/ + адрес кошелька"
echo "Логи: journalctl -u xmrig -f"
