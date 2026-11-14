"""In-process handler tests, no sockets and no real participant records.
Run: python Receiver_QA.py
"""
import importlib.util, pathlib, json, io, tempfile, copy, time, os
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('receiver',root/'01_Product/classroom.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Authored synthetic record matching the bank. Never counts as human testing.
r=dict(schema='CQ2',id='a'*24,parent=None,code='QA-ONLY',role='teaching',lang='en',start=int(time.time()*1000)-1000,end=int(time.time()*1000),answers=[],fb=dict(use=None,rate=None,comment='Synthetic QA',confidence=None,frequency=''))
used=set()
for phase in ['pre','prac','post']:
 for risk in [True,False]:
  pool='teaching' if phase=='prac' else 'shared'
  for k,v in [(k,v) for k,v in m.RULES.items() if v[0]==pool and v[1]==risk and k not in used][:2]:r['answers'].append(dict(id=k,stage=phase,f=risk,a=v[2]));used.add(k)
def call(route,obj=None,token=None,ip='127.0.0.1',method='POST'):
 h=m.Handler.__new__(m.Handler);h.path=route;h.client_address=(ip,1234);raw=json.dumps(obj).encode();h.rfile=io.BytesIO(raw);h.headers={'Content-Length':str(len(raw)),'Authorization':'Bearer '+(token or '')};h.reply=lambda status,data,*args:(status,data)
 return h.do_GET() if method=='GET' else h.do_POST()
checks={}
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks[name]='PASS'
with tempfile.TemporaryDirectory() as d:
 m.DATA=pathlib.Path(d)
 check('unauthorised submit',call('/api/submit',r)[0],403)
 check('valid submission',call('/api/submit',r,m.ROOM)[0],201)
 check('identical duplicate',call('/api/submit',r,m.ROOM)[1]['added'],False)
 bad=copy.deepcopy(r);bad['fb']['comment']='conflict'
 check('conflicting duplicate',call('/api/submit',bad,m.ROOM)[0],409)
 check('teacher inbox',len(call('/api/inbox',token=m.TEACHER,method='GET')[1]['records']),1)
 check('learner cannot read inbox',call('/api/inbox',token=m.ROOM,method='GET')[0],403)
 check('nonloopback reviewer denied',call('/api/inbox',token=m.TEACHER,ip='192.0.2.2',method='GET')[0],403)
 for name,change in [('invalid code',{'code':'!'}),('missing answer',{'answers':r['answers'][:-1]}),('invalid role',{'role':'other'}),('oversized comment',{'fb':{**r['fb'],'comment':'x'*401}})]:
  check(name,call('/api/submit',{**r,**change},m.ROOM)[0],400)
 follow={**r,'id':'b'*24,'parent':r['id'],'answers':[]}
 for risk in [True,False]:
  for k,v in [(k,v) for k,v in m.RULES.items() if v[0]=='follow' and v[1]==risk][:2]:follow['answers'].append(dict(id=k,stage='follow',f=risk,a=v[2]))
 check('early followup denied',call('/api/submit',follow,m.ROOM)[0],409)
 check('readable report produced',(m.DATA/(r['id']+'.html')).exists(),True)
 check('selective delete',call('/api/delete',{'ids':[r['id']]},m.TEACHER)[0],200)
 check('json and html removed',len(list(m.DATA.iterdir())),0)
print(json.dumps({'scope':'In-process request handlers, temporary storage; HTTP transport and browser NOT tested','checks':checks},indent=2))
