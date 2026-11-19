# XMRig 6.26.0 — Linux

Статический x64-бинарник. Работает на большинстве дистрибутивов с glibc
(Ubuntu/Debian/CentOS/Fedora/Alma/Rocky и т.п.).

## Установка (одна команда)

```bash
sudo bash setup.sh
```

`setup.sh` ставит systemd-сервис `xmrig`, включает его при загрузке,
запускает и поднимает huge pages (если получается).

## Ручной запуск

```bash
bash start.sh
```

Имя воркера = `hostname`. Своё имя: `bash start.sh --rig-id=MYSERVER`.

## Управление

```bash
systemctl status xmrig
systemctl stop xmrig
systemctl restart xmrig
journalctl -u xmrig -f
```

## Проверка

- https://xmrpool.eu/ — введи адрес кошелька
- API: `curl -H "Authorization: Bearer ba0622fc2c0e614bd91cfcf8f3e5b94e" http://localhost:8080/1/summary`

## Разные дистрибутивы

| ОС | Что делать |
|---|---|
| Ubuntu 20.04/22.04/24.04, Debian, CentOS, Fedora | этот статический `xmrig` работает |
| Alpine / другие musl-дистрибутивы | статический бинарник может не запуститься — собери из исходников |
| ARM64 (Raspberry Pi, ARM-серверы) | в официальном релизе нет Linux ARM64 — собери из исходников |
| Без systemd (OpenWrt, старые дистро) | просто `bash start.sh` вручную |

## Важно

- `config.json` содержит адрес кошелька и токен API — репо публичное, не публикуй свой токен где-то ещё.
- Репо: https://github.com/Lolicks/xmrig-setup
