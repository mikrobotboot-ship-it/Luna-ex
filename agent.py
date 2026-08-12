from http.server import BaseHTTPRequestHandler, HTTPServer
import json, subprocess, platform, re
HOST='127.0.0.1'; PORT=8765
BLOCKED=re.compile(r'(^|\s)(format|diskpart|shutdown|reboot|poweroff|rm\s+-rf|del\s+/s|reg\s+delete|sc\s+delete)(\s|$)',re.I)
ALLOWED=('ipconfig','ping ','tracert ','nslookup ','route print','arp -a','hostname','whoami','systeminfo','ssh -V','python --version','node --version')
def allowed(c):
    x=c.strip().lower()
    return not BLOCKED.search(x) and any(x==p.strip() or x.startswith(p) for p in ALLOWED)
class H(BaseHTTPRequestHandler):
    def _json(self,code,obj):
        b=json.dumps(obj).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=='/health': self._json(200,{'ok':True,'agent':'MikroBot LUNA Agent','system':platform.system(),'release':platform.release()})
        else: self._json(404,{'ok':False})
    def do_POST(self):
        if self.path!='/exec': return self._json(404,{'ok':False})
        n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(n) or '{}'); c=str(data.get('command','')).strip()
        if not allowed(c): return self._json(403,{'ok':False,'error':'Comando bloqueado ou não permitido'})
        try:
            p=subprocess.run(c,shell=True,capture_output=True,text=True,timeout=30)
            self._json(200,{'ok':True,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        except Exception as e: self._json(500,{'ok':False,'error':str(e)})
    def log_message(self,*args): pass
if __name__=='__main__':
    print(f'MikroBot LUNA Agent em http://{HOST}:{PORT}')
    HTTPServer((HOST,PORT),H).serve_forever()
