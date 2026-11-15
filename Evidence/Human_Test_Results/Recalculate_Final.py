from pathlib import Path
import json, hashlib, datetime
r=Path(__file__).resolve().parents[2];h=r/'Evidence/Human_Test_Results'
bank=json.JSONDecoder().raw_decode((r/'MVP/CyberLearn.html').read_text().split('const BANK=',1)[1])[0];b={q['id']:q for q in bank};rows=[];tot={s:{'actions':0,'classification':0,'threats_flagged':0,'false_alarms':0,'n':0} for s in ['pre','post']}
for p in sorted(h.glob('CyberLearn_*.json')):
 x=json.loads(p.read_text())['records'][0];out={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**{k:x[k] for k in ['id','code','role','lang','start','end']},'duration_seconds':(x['end']-x['start'])/1000,'start_utc':datetime.datetime.fromtimestamp(x['start']/1000,datetime.timezone.utc).isoformat(),'end_utc':datetime.datetime.fromtimestamp(x['end']/1000,datetime.timezone.utc).isoformat(),'followup_due_utc':datetime.datetime.fromtimestamp(x['end']/1000+7*86400,datetime.timezone.utc).isoformat(),'ratings':x['fb'],'stages':{}}
 for s in ['pre','prac','post']:
  a=[a for a in x['answers'] if a['stage']==s];m={'actions':sum(a['a']==b[a['id']]['key'] for a in a),'classification':sum(a['f']==b[a['id']]['risk'] for a in a),'threats_flagged':sum(a['f'] and b[a['id']]['risk'] for a in a),'false_alarms':sum(a['f'] and not b[a['id']]['risk'] for a in a),'n':len(a)};out['stages'][s]=m
  if s in tot:
   for k,v in m.items():tot[s][k]+=v
 rows.append(out)
assert tot['pre']['actions']==9 and tot['post']['actions']==6 and len({x['id'] for x in rows})==5
(h/'Analysis_Final.json').write_text(json.dumps({'method':'Independent recalculation from answer-level original files and unchanged item keys, 15 November 2026. No exclusion.','sessions':rows,'pooled':tot},indent=2,ensure_ascii=False))
print('5 original exports independently recalculated; totals',tot)
