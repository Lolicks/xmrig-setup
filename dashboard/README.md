# Единый дашборд XMRig

Один сервер хранит общий `config.json`. Агенты на машинах подтягивают его
(и перезапускают майнер при изменении) и шлют статистику.

## Архитектура

```
   Дашборд (server.py, порт 8081)
   ├─ GET  /api/config  → агенты берут конфиг
   ├─ POST /api/report  ← агенты шлют хешрейт/шары/аптайм
   └─ GET  /            → веб-страница со статистикой и редактором конфига
```

## 1. Сервер (одна машина, доступная остальным)

```bash
DASH_TOKEN=mysecret python3 server.py
```

Открой `http://IP_СЕРВЕРА:8081/?token=mysecret`.

На странице: таблица всех машин (хешрейт, шары, uptime, last seen) и поле с
общим `config.json`. Изменил → «Сохранить и разослать» → агенты подхватят
в течение минуты.

## 2. Агент (на каждой машине)

В папке `dashboard/` на каждой машине:

1. Открой `agent.json`, укажи:
   - `server` — `http://IP_СЕРВЕРА:8081`
   - `token` — тот же, что `DASH_TOKEN`
   - `config_path` — путь до конфига майнера
2. Запусти:
   ```bash
   python3 agent.py
   ```

Агент работает постоянно: раз в минуту сверяет конфиг и шлёт статистику.

### Автозапуск агента

**Windows** — Планировщик заданий, при загрузке:
```
schtasks /Create /TN "XMRig-Agent" /TR "pythonw.exe C:\майнер\dashboard\agent.py" /SC ONSTART /RU SYSTEM /F
```

**Linux** — systemd (`/etc/systemd/system/xmrig-agent.service`):
```
[Unit]
Description=XMRig config agent
After=network-online.target
[Service]
Type=simple
WorkingDirectory=/opt/xmrig/dashboard
ExecStart=/usr/bin/python3 /opt/xmrig/dashboard/agent.py
Restart=always
[Install]
WantedBy=multi-user.target
```
```
systemctl daemon-reload && systemctl enable --now xmrig-agent
```

## 3. Доступность машин в разных сетях

Агент стучится на сервер исходящими запросами — это работает, даже если у машин серые IP.
Главное, чтобы сервер был доступен по IP/домену. Если сервер в другой сети —
подними Tailscale/ZeroTier и укажи его IP из виртуальной сети.

## Безопасность

- Токен в URL и в `agent.json`. Не публикуй его.
- В репо уже есть пример `config.json` с адресом кошелька — это публично, норм.
- `agent.py` перезапускает майнер при смене конфига — убедись, что путь `config_path` правильный.

## Файлы

| Файл | Что |
|---|---|
| `server.py` | дашборд + API |
| `config.json` | эталонный конфиг, который раздаётся агентам |
| `agent.py` | агент (один для Windows и Linux) |
| `agent.json` | настройки агента (IP сервера, токен, путь) |
