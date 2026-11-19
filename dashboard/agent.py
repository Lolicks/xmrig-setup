#!/usr/bin/env python3
# Агент для каждой машины: тянет общий конфиг с дашборда и шлёт статистику.
# Настройки в agent.json рядом с файлом. Запуск: python3 agent.py
import json, os, time, hashlib, subprocess, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.join(BASE, "agent.json")

default = {
    "server": "http://SERVER_IP:8081",
    "token": "changeme",
    "config_path": os.path.join(BASE, "config.json"),
    "interval": 60
}
try:
    with open(SET, encoding="utf-8") as f:
        s = json.load(f)
except Exception:
    s = default
    with open(SET, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)

server = s["server"].rstrip("/")
token = s["token"]
cfg_path = s["config_path"]
interval = int(s.get("interval", 60))
mid = os.environ.get("COMPUTERNAME") or os.uname().nodename


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    return urllib.request.urlopen(req, timeout=8).read().decode("utf-8")


def post(url, obj):
    req = urllib.request.Request(
        url, data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=8).read()


def restart_miner():
    if os.name == "nt":
        subprocess.run(["taskkill", "/IM", "xmrig.exe", "/F"], capture_output=True)
        subprocess.Popen(["start-miner.cmd"], cwd=os.path.dirname(cfg_path), shell=True)
    else:
        subprocess.run(["systemctl", "restart", "xmrig"], capture_output=True)


last_hash = None
while True:
    try:
        raw = get(server + "/api/config?token=" + token)
        h = hashlib.md5(raw.encode("utf-8")).hexdigest()
        if h != last_hash:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(raw)
            restart_miner()
            last_hash = h

        cfg = json.loads(raw)
        api_tok = cfg.get("http", {}).get("access-token", "")
        st = get("http://127.0.0.1:8080/1/summary",
                 {"Authorization": "Bearer " + api_tok})
        d = json.loads(st)
        rep = {
            "id": mid,
            "hashrate": d["hashrate"]["total"][1],
            "shares_good": d["results"]["shares_good"],
            "shares_total": d["results"]["shares_total"],
            "uptime": d["connection"]["uptime"],
            "pool": d["connection"]["pool"]
        }
        post(server + "/api/report?token=" + token, rep)
        print(mid, "OK", round(rep["hashrate"]), "H/s")
    except Exception as e:
        print(mid, "ERR", e)
    time.sleep(interval)
