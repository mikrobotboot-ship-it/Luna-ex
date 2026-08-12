from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import sqlite3, hashlib, json, time, re, platform

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'luna_memory.db'
app=FastAPI(title='MikroBot LUNA NEXUS', version='1.0.0')

class TextIn(BaseModel):
    text:str
    context:dict|None=None
class MemoryIn(BaseModel):
    key:str
    value:str
    kind:str='lesson'

BLOCKED = re.compile(r'(^|\s)(format|diskpart|shutdown|reboot|poweroff|rm\s+-rf|del\s+/s|reg\s+delete|sc\s+delete)(\s|$)', re.I)
ALLOWED_PREFIXES=('ipconfig','ping ','tracert ','nslookup ','route print','arp -a','hostname','whoami','systeminfo','ssh -V','python --version','node --version')

def db():
    c=sqlite3.connect(DB); c.execute('CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY, key TEXT, value TEXT, kind TEXT, created REAL)'); c.commit(); return c

def fingerprint(text): return hashlib.sha256(text.encode()).hexdigest()[:16]

def classify(text):
    t=text.lower(); tags=[]
    for k in ('routeros','mikrotik','l2tp','ipsec','wireguard','vlan','dhcp','nat','dns','vpn','ethernet','windows','linux','ssh'):
        if k in t: tags.append(k)
    return tags

@app.get('/')
def home(): return FileResponse(ROOT/'frontend.html')
@app.get('/api/health')
def health(): return {'ok':True,'name':'MikroBot LUNA NEXUS','version':'1.0.0','python':platform.python_version(),'system':platform.system(),'time':time.time()}

@app.post('/api/analyze')
def analyze(x:TextIn):
    text=x.text.strip(); tags=classify(text)
    findings=[]
    if 'l2tp' in tags and 'ipsec' in tags: findings.append({'level':'info','title':'L2TP/IPsec detectado','detail':'Separar autenticação PPP, transporte IPsec, rota e estabilidade do link antes de alterar a configuração.'})
    if 'nat' in tags: findings.append({'level':'info','title':'NAT detectado','detail':'Verificar cadeia, interface de saída, ordem das regras e conflito com VPN/roteamento.'})
    if 'dns' in tags: findings.append({'level':'info','title':'DNS detectado','detail':'Distinguir falha de resolução de nomes de falha de conectividade IP.'})
    if not findings: findings.append({'level':'info','title':'Análise inicial','detail':'Nenhuma regra automática suficiente para concluir causa. Solicite evidência real do equipamento.'})
    return {'ok':True,'fingerprint':fingerprint(text),'tags':tags,'findings':findings,'evidence_policy':'Não marcar teste físico como concluído sem evidência do agente.'}

@app.post('/api/memory')
def save_memory(x:MemoryIn):
    if not x.key.strip() or not x.value.strip(): return JSONResponse({'ok':False,'error':'key/value obrigatórios'},400)
    c=db(); c.execute('INSERT INTO memory(key,value,kind,created) VALUES(?,?,?,?)',(x.key,x.value,x.kind,time.time())); c.commit(); c.close(); return {'ok':True}
@app.get('/api/memory')
def memories():
    c=db(); rows=c.execute('SELECT key,value,kind,created FROM memory ORDER BY id DESC LIMIT 100').fetchall(); c.close(); return {'items':[dict(zip(('key','value','kind','created'),r)) for r in rows]}

@app.post('/api/agent/command')
def agent_command(x:TextIn):
    cmd=x.text.strip()
    if BLOCKED.search(cmd): return JSONResponse({'ok':False,'error':'Comando bloqueado pelo modo seguro.'},403)
    if not any(cmd.lower()==p.strip() or cmd.lower().startswith(p) for p in ALLOWED_PREFIXES):
        return JSONResponse({'ok':False,'error':'Comando fora da política segura. Use um agente local configurado para ampliar a política.'},403)
    return {'ok':True,'accepted':True,'command':cmd,'note':'Este endpoint é um controlador; a execução no PC deve ocorrer pelo agente local.'}

@app.websocket('/ws')
async def ws(socket:WebSocket):
    await socket.accept()
    await socket.send_json({'type':'hello','name':'LUNA NEXUS','policy':'safe'})
    try:
        while True:
            msg=await socket.receive_json()
            if msg.get('type')=='ping': await socket.send_json({'type':'pong','ts':time.time()})
            elif msg.get('type')=='context': await socket.send_json({'type':'context_ack','tags':classify(json.dumps(msg))})
    except WebSocketDisconnect: pass
