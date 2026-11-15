"""CyberLearn classroom receiver. Python 3.9+; standard library only. Never expose to public internet."""
import html,datetime
import argparse,hmac,ipaddress,json,os,re,secrets,socket,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent; RULES=json.loads((ROOT/'bank_rules.json').read_text()); LOCK=threading.RLock(); ROOM=secrets.token_urlsafe(24); TEACHER=secrets.token_urlsafe(32); ID=re.compile('[0-9a-f]{24}'); DAY=86400000

def valid(r):
    if not isinstance(r,dict) or r['schema']!='CQ2' or not ID.fullmatch(r['id']) or not re.fullmatch('[a-zA-Z0-9-]{2,20}',r['code']) or r['role'] not in ('teaching','admissions','finance') or r['lang'] not in ('ru','kk','en'):raise ValueError()
    parent=r['parent']; stages=['follow'] if parent else ['pre','prac','post']
    if parent is not None and (not ID.fullmatch(parent) or parent==r['id']):raise ValueError()
    if not all(type(r[k])==int and 946684800000<=r[k]<=4102444800000 for k in ('start','end')) or r['end']<r['start']:raise ValueError()
    ans=r['answers']; fb=r['fb']; out=[]; summary={}
    if len(ans)!=len(stages)*4 or len({a['id'] for a in ans})!=len(ans):raise ValueError()
    for p in stages:
        g=[a for a in ans if a['stage']==p]; pool=r['role'] if p=='prac' else 'follow' if p=='follow' else 'shared'
        if len(g)!=4 or sum(RULES[a['id']][1] for a in g)!=2:raise ValueError()
        for a in g:
            if RULES[a['id']][0]!=pool or type(a['a'])!=int or not 0<=a['a']<3 or type(a['f'])!=bool:raise ValueError()
            out.append({k:a[k] for k in ('id','stage','f','a')})
        summary[p]={'correct_actions':sum(a['a']==RULES[a['id']][2] for a in g),'correct_triage':sum(a['f']==RULES[a['id']][1] for a in g),'threats_flagged':sum(a['f'] and RULES[a['id']][1] for a in g),'false_alarms':sum(a['f'] and not RULES[a['id']][1] for a in g),'total':4,'threats':2,'routine':2}
    if not isinstance(fb['comment'],str) or len(fb['comment'])>400 or not all(fb[k] is None or type(fb[k])==int and 1<=fb[k]<=5 for k in ('use','rate')):raise ValueError()
    if fb.get('confidence') is not None and (type(fb['confidence']) is not int or not 1<=fb['confidence']<=5):raise ValueError()
    if fb.get('frequency','') not in ('','weekly','twice','monthly','onboard','unsure'):raise ValueError()
    if 'build' in r and (not isinstance(r['build'],str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',r['build'])):raise ValueError()
    result=dict({k:r[k] for k in ('schema','id','code','role','lang','parent','start','end')},answers=out,fb={k:fb.get(k) for k in ('use','rate','comment','confidence','frequency')},summary=summary)
    if 'build' in r:result['build']=r['build']
    return result
BANK={q['id']:q for q in json.loads((ROOT/'CyberLearn.html').read_text('utf-8').split('const BANK=',1)[1].split(';const UI=',1)[0])}
def readable(r):
    e=lambda v:html.escape(str(v),quote=True)
    L=r['lang']; j={'en':0,'ru':1,'kk':2}[L]; w=lambda a,b,c:(a,b,c)[j]
    phase={'pre':w('Before the lesson','До урока','Сабаққа дейін'),'prac':w('Practice','Практика','Жаттығу'),'post':w('Final check','Итоговая проверка','Қорытынды тексеру'),'follow':w('Day-seven check','Повторная проверка','Жеті күннен кейінгі тексеру')}
    title=w('Reviewer report','Ведомость проверяющего','Тексеруші есебі');role={'finance':w('Finance','Бухгалтерия','Бухгалтерия'),'teaching':w('Teaching staff','Преподаватели','Оқытушылар'),'admissions':w('Admissions','Приёмная комиссия','Қабылдау комиссиясы')}[r['role']]
    bits=[f'<!doctype html><html lang="{L}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;;style-src &#39;unsafe-inline&#39;"><title>CyberLearn · {title}</title><style>body{{font:16px/1.5 system-ui;color:#132d3b;max-width:850px;margin:2em auto;padding:0 1em}}article{{break-inside:avoid;border-top:1px solid #ccc}}td,th{{padding:.4em;text-align:left}}.scroll{{overflow:auto}}</style><h1>CyberLearn · {title}</h1><p>{e(r["code"])} · {role} · {L.upper()} · {datetime.datetime.fromtimestamp(r["end"]/1000,datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p><small>ID: {e(r["id"])}</small>']
    if r['parent']: bits.append('<p>'+w('Original ID','Исходная попытка','Бастапқы әрекет')+': '+e(r['parent'])+'</p>')
    heads=[w('Stage','Этап','Кезең'),w('Safe actions','Верные действия','Қауіпсіз әрекеттер'),w('Correct classifications','Верная оценка','Дұрыс жіктеу'),w('Threats flagged','Обнаружено угроз','Анықталған қауіптер'),w('False alarms','Ложные тревоги','Жалған дабылдар')];bits.append('<div class="scroll"><table><tr>'+''.join('<th>'+h+'</th>' for h in heads)+'</tr>')
    for k,v in r['summary'].items():bits.append('<tr>'+''.join('<td>'+e(c)+'</td>' for c in [phase[k],str(v['correct_actions'])+'/4',str(v['correct_triage'])+'/4',str(v['threats_flagged'])+'/2',str(v['false_alarms'])+'/2'])+'</tr>')
    bits.append('</table></div><p>'+w('These scores describe this attempt only.','Баллы относятся только к этой попытке.','Ұпайлар тек осы әрекеттің нәтижесін көрсетеді.')+'</p>')
    for stage in r['summary']:
        bits.append('<h2>'+phase[stage]+'</h2>')
        for a in (a for a in r['answers'] if a['stage']==stage):
            q=BANK[a['id']];c=q['text'][L];yn=lambda x:w('Yes','Да','Иә') if x else w('No','Нет','Жоқ');bits.append('<article><h3>'+e(c['subject'])+'</h3><p>'+e(c['body'])+'</p><p>'+w('Flagged / expected','Сообщили / ожидалось','Белгіленді / дұрыс жауап')+': '+yn(a['f'])+' / '+yn(q['risk'])+'</p><p><b>'+w('Selected','Выбрано','Таңдалған жауап')+':</b> '+e(c['options'][a['a']])+'<br><b>'+w('Best action','Лучшее действие','Дұрыс әрекет')+':</b> '+e(c['options'][q['key']])+'</p><p>'+e(c['explanation'])+'</p></article>')
    f=r['fb'];bits.append('<h2>'+w('Optional feedback','Необязательный отзыв','Ерікті пікір')+'</h2><p>'+w('Relevance / usefulness / confidence','Соответствие работе / полезность / уверенность','Жұмысқа сәйкестік / пайдалылық / сенімділік')+': '+' / '.join(e(f.get(x) or '—') for x in ['rate','use','confidence'])+'</p><p>'+e(f.get('comment') or '—')+'</p></html>');return ''.join(bits)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def reply(self,status,data,typ='application/json; charset=utf-8'):
        b=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY');self.end_headers();self.wfile.write(b)
    def auth(self,teacher):return (not teacher or ipaddress.ip_address(self.client_address[0]).is_loopback) and hmac.compare_digest(self.headers.get('Authorization','').encode(),('Bearer '+(TEACHER if teacher else ROOM)).encode())
    def vals(self):return [json.loads(x.read_text('utf-8'))['records'][0] for x in sorted(DATA.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True)]
    def do_GET(self):
        p=urlsplit(self.path).path
        if p in ('/','/CyberLearn.html'):return self.reply(200,(ROOT/'CyberLearn.html').read_bytes(),'text/html; charset=utf-8')
        if p=='/api/mode':return self.reply(200,{'mode':'classroom'})
        if p=='/favicon.ico':return self.reply(204,b'')
        if p=='/api/inbox' and self.auth(True):
            with LOCK:return self.reply(200,{'records':self.vals()})
        return self.reply(403 if p=='/api/inbox' else 404,{})
    def do_POST(self):
        p=urlsplit(self.path).path
        if p not in ('/api/submit','/api/import','/api/delete'):return self.reply(404,{})
        if not self.auth(p!='/api/submit'):return self.reply(403,{})
        try:
            n=int(self.headers.get('Content-Length',0));
            if not 0<n<=32000:return self.reply(413,{})
            r=json.loads(self.rfile.read(n));
            with LOCK:
                if p=='/api/delete':
                    ids=r['ids'];
                    if not isinstance(ids,list) or len(ids)>1000 or not all(ID.fullmatch(i) for i in ids):raise ValueError()
                    for i in ids:
                        for suffix in ('.json','.html'):(DATA/(i+suffix)).unlink(missing_ok=True)
                    return self.reply(200,{'deleted':len(ids)})
                r=valid(r);path=DATA/(r['id']+'.json');obj={'format':'CyberLearn.CampusQuest/2','records':[r]}
                if path.exists():
                    if json.loads(path.read_text('utf-8'))!=obj:return self.reply(409,{'error':'conflicting record'})
                    return self.reply(200,{'receipt':r['id'],'added':False})
                if p=='/api/submit' and r['parent']:
                    parent=DATA/(r['parent']+'.json');
                    if not parent.exists():return self.reply(409,{'error':'original missing'})
                    par=json.loads(parent.read_text('utf-8'))['records'][0]
                    if par['parent'] or par['code']!=r['code'] or par['role']!=r['role'] or min(time.time()*1000-parent.stat().st_mtime*1000,r['start']-par['end'])<7*DAY or any(x['parent']==r['parent'] for x in self.vals()):return self.reply(409,{'error':'follow-up not due'})
                if sum(1 for _ in DATA.glob('*.json'))>=5000:return self.reply(507,{})
                tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False),'utf-8');rh=path.with_suffix('.html');ht=rh.with_suffix('.html.tmp');ht.write_text(readable(r),'utf-8');os.replace(ht,rh);os.replace(tmp,path);return self.reply(201,{'receipt':r['id'],'added':True})
        except (ValueError,TypeError,KeyError,IndexError,AttributeError):return self.reply(400,{'error':'invalid input'})
        except OSError:return self.reply(500,{'error':'storage error'})
def lanip():
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:s.connect(('192.0.2.1',9));return s.getsockname()[0]
    except OSError:return socket.gethostbyname(socket.gethostname())
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--port',type=int,default=8765);ap.add_argument('--lan',action='store_true');ap.add_argument('--data',type=Path,default=ROOT/'Reviewer_Inbox');args=ap.parse_args();DATA=args.data.resolve();DATA.mkdir(parents=True,exist_ok=True)
    try:srv=ThreadingHTTPServer(('0.0.0.0' if args.lan else '127.0.0.1',args.port),Handler)
    except OSError as e:raise SystemExit(f'Cannot start: {e}. Try another --port.')
    print(f'Private reviewer (this computer): http://127.0.0.1:{args.port}/#review={TEACHER}',flush=True); print(f'Learner invitation: http://{lanip() if args.lan else "127.0.0.1"}:{args.port}/#room={ROOM}',flush=True);print('Result files:',DATA,'\nOnly for trusted classroom networks. Press Ctrl+C to stop.',flush=True)
    try:srv.serve_forever()
    except KeyboardInterrupt:pass
    finally:srv.server_close()
