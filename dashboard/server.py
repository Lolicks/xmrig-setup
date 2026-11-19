#!/usr/bin/env python3
# Единый дашборд для парка XMRig.
# Запуск: python3 server.py   (порт 8081, токен задаётся переменной DASH_TOKEN)
import json, os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("DASH_PORT", "8081"))
TOKEN = os.environ.get("DASH_TOKEN", "changeme")
BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE, "state.json")
CONFIG_FILE = os.path.join(BASE, "config.json")


def load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


state = load(STATE_FILE, {"machines": {}})
config = load(CONFIG_FILE, {})

HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<title>XMRig fleet</title>
<style>
body{font-family:system-ui;background:#141821;color:#e8eaf0;margin:24px}
table{border-collapse:collapse;width:100%;background:#1c2230}
th,td{padding:8px 10px;border:1px solid #2a3346;text-align:left}
th{background:#263049}
.ok{color:#5ee08a}.bad{color:#ff6b6b}
textarea{width:100%;height:320px;background:#0e1118;color:#8fe3a4;border:1px solid #2a3346;font-family:monospace;font-size:12px;padding:10px}
button{padding:8px 16px;background:#3b6ef5;color:#fff;border:0;cursor:pointer}
h1,h2{margin-top:24px}
</style></head><body>
<h1>XMRig fleet — __N__ машин</h1>
<table id="t"><thead><tr><th>Машина</th><th>kH/s</th><th>Shares</th><th>Uptime</th><th>Пул</th><th>Last seen</th></tr></thead><tbody></tbody></table>
<h2>Общий config.json</h2>
<textarea id="cfg"></textarea><br><br>
<button onclick="saveCfg()">Сохранить и разослать</button> <span id="msg"></span>
<script>
const T="__TOKEN__";
function api(p,o){return fetch(p+(p.includes('?')?'&':'?')+'token='+T,o).then(r=>r.json())}
function draw(d){
  const tb=document.querySelector('#t tbody');tb.innerHTML='';
  for(const [id,m] of Object.entries(d.machines||{})){
    const age=(Date.now()-new Date(m.last_seen.replace(' ','T')).getTime())/1000;
    const st=age<300?'<span class="ok">online</span>':'<span class="bad">offline</span>';
    tb.innerHTML+=`<tr><td>${id} ${st}</td><td>${((m.hashrate||0)/1000).toFixed(2)}</td><td>${m.shares_good||0}/${m.shares_total||0}</td><td>${Math.round((m.uptime||0)/60)}m</td><td>${m.pool||''}</td><td>${m.last_seen||''}</td></tr>`;
  }
}
function refresh(){api('/api/state').then(d=>{draw(d);if(!document.querySelector('#cfg').value)document.querySelector('#cfg').value=JSON.stringify(d.config,null,2)})}
function saveCfg(){
  const txt=document.querySelector('#cfg').value;let obj;
  try{obj=JSON.parse(txt)}catch(e){document.querySelector('#msg').textContent='Ошибка JSON';return}
  api('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({config:obj})})
   .then(()=>{document.querySelector('#msg').textContent='Сохранено — агенты подхватят в течение минуты'});
}
refresh();setInterval(refresh,15000);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if not isinstance(body, str):
            body = json.dumps(body, ensure_ascii=False)
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _auth(self, q):
        return q.get("token", [None])[0] == TOKEN or self.headers.get("X-Auth-Token") == TOKEN

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if not self._auth(q):
            return self._send(401, "unauthorized", "text/plain")
        if u.path == "/":
            html = HTML.replace("__TOKEN__", TOKEN).replace("__N__", str(len(state.get("machines", {}))))
            return self._send(200, html, "text/html")
        if u.path == "/api/state":
            d = dict(state)
            d["config"] = config
            return self._send(200, d)
        if u.path == "/api/config":
            return self._send(200, config)
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        global config
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if not self._auth(q):
            return self._send(401, "unauthorized", "text/plain")
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n).decode("utf-8", "replace")
        try:
            data = json.loads(raw)
        except Exception:
            return self._send(400, "bad json", "text/plain")
        if u.path == "/api/report":
            mid = str(data.get("id", "unknown"))
            m = dict(data)
            m["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            state.setdefault("machines", {})[mid] = m
            save(STATE_FILE, state)
            return self._send(200, {"ok": True})
        if u.path == "/api/config":
            config = data.get("config", data)
            save(CONFIG_FILE, config)
            return self._send(200, {"ok": True})
        return self._send(404, "not found", "text/plain")


if __name__ == "__main__":
    print("Dashboard: http://0.0.0.0:%d/?token=%s" % (PORT, TOKEN))
    print("Agents:    %s/api/config?token=%s" % ("http://HOST:%d" % PORT, TOKEN))
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
