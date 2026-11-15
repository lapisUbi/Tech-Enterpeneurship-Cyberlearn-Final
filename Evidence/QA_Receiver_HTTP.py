"""Synthetic receiver HTTP checks on an ephemeral loopback port; no browser or real participants."""
import importlib.util, pathlib, tempfile, threading, json, time, urllib.request, urllib.error, copy, os, hashlib
root=pathlib.Path(__file__).resolve().parents[1];p=root/'MVP/classroom.py';spec=importlib.util.spec_from_file_location('receiver',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'name':name,'result':'PASS'})
def record():
 r=dict(schema='CQ2',build='2.2.0',id='a'*24,parent=None,code='QA-ONLY',role='finance',lang='kk',start=int(time.time()*1000)-1000,end=int(time.time()*1000),answers=[],fb=dict(use=None,rate=None,comment='<script>QA only</script>',confidence=None,frequency=''))
 used=set()
 for phase in ['pre','prac','post']:
  for risk in [True,False]:
   for k,v in [(k,v) for k,v in m.RULES.items() if v[0]==('finance' if phase=='prac' else 'shared') and v[1]==risk and k not in used][:2]:
    r['answers'].append(dict(id=k,stage=phase,f=risk,a=v[2]));used.add(k)
 return r
with tempfile.TemporaryDirectory() as d:
 m.DATA=pathlib.Path(d);srv=m.ThreadingHTTPServer(('127.0.0.1',0),m.Handler);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
 def call(route,obj=None,token=None,raw=None):
  body=raw if raw is not None else json.dumps(obj).encode() if obj is not None else None
  req=urllib.request.Request('http://127.0.0.1:'+str(srv.server_port)+route,data=body,headers={'Authorization':'Bearer '+(token or ''),'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=3) as res:return res.status,json.loads(res.read())
  except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
 try:
  r=record();check('mode API',call('/api/mode')[1]['mode']=='classroom')
  check('missing token denied',call('/api/submit',r)[0]==403)
  check('learner token cannot read reviewer inbox',call('/api/inbox',token=m.ROOM)[0]==403)
  check('submit yields matching receipt',call('/api/submit',r,m.ROOM)==(201,{'receipt':r['id'],'added':True}))
  check('identical duplicate is idempotent',call('/api/submit',r,m.ROOM)[1]['added'] is False)
  bad=copy.deepcopy(r);bad['fb']['comment']='changed';check('conflicting duplicate rejected',call('/api/submit',bad,m.ROOM)[0]==409)
  check('reviewer sees saved optional build',call('/api/inbox',token=m.TEACHER)[1]['records'][0]['build']=='2.2.0')
  report=(m.DATA/(r['id']+'.html')).read_text();check('report escapes user content and sets restrictive CSP','&lt;script&gt;QA only&lt;/script&gt;' in report and 'default-src' in report)
  for name,bad in [('invalid code',{**r,'code':'!'}),('invalid build',{**r,'build':'bad'}),('missing answer',{**r,'answers':r['answers'][:-1]}),('invalid rating',{**r,'fb':{**r['fb'],'rate':9}})]:check(name,call('/api/submit',bad,m.ROOM)[0]==400)
  check('oversized body rejected',call('/api/submit',token=m.ROOM,raw=b' '*32001)[0]==413)
  check('malformed JSON rejected',call('/api/submit',token=m.ROOM,raw=b'{')[0]==400)
  check('learner token cannot import',call('/api/import',r,m.ROOM)[0]==403)
  f={**r,'id':'b'*24,'parent':r['id'],'answers':[]}
  for risk in [True,False]:
   for k,v in [(k,v) for k,v in m.RULES.items() if v[0]=='follow' and v[1]==risk][:2]:f['answers'].append(dict(id=k,stage='follow',f=risk,a=v[2]))
  check('early followup denied',call('/api/submit',f,m.ROOM)[0]==409)
  pp=m.DATA/(r['id']+'.json');parent=json.loads(pp.read_text());parent['records'][0]['start']-=8*m.DAY;parent['records'][0]['end']-=8*m.DAY;pp.write_text(json.dumps(parent));os.utime(pp,(time.time()-8*86400,)*2)
  check('eligible followup accepted',call('/api/submit',f,m.ROOM)[0]==201)
  check('second followup denied',call('/api/submit',{**f,'id':'c'*24},m.ROOM)[0]==409)
  check('learner token cannot delete',call('/api/delete',{'ids':[r['id']]},m.ROOM)[0]==403)
  check('reviewer deletion succeeds',call('/api/delete',{'ids':[r['id'],f['id']]},m.TEACHER)[0]==200)
  check('all JSON and HTML copies removed',not list(m.DATA.iterdir()))
 finally:srv.shutdown();srv.server_close();thread.join()
print(json.dumps({'version':'2.2.0','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Actual loopback HTTP API with synthetic records and temporary storage. No browser, LAN device, Windows launcher or production hosting tested.','receiver_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'passed':len(checks),'checks':checks},indent=2))
