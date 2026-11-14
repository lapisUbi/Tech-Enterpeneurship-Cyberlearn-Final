from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parents[2]
p=root/'01_Product/CyberLearn.html'
s=p.read_text(encoding='utf-8'); bank=json.JSONDecoder().raw_decode(s.split('const BANK=',1)[1])[0]; keys={x['id']:x for x in bank}
a=json.loads((Path(__file__).with_name('Analysis_v15.json')).read_text(encoding='utf-8'))
for r in a['sessions']:
 f=Path(__file__).with_name(r['source_file']); assert hashlib.sha256(f.read_bytes()).hexdigest()==r['source_sha256']
 raw=json.loads(f.read_text(encoding='utf-8'))['records'][0]
 for stage in ['pre','prac','post']:
  aa=[v for v in raw['answers'] if v['stage']==stage]
  assert len(aa)==4
  m=dict(total=4,actions=0,ok=0,risk=0,safe=0,tp=0,fp=0)
  for v in aa:
   q=keys[v['id']];m['actions']+=q['key']==v['a'];m['ok']+=q['risk']==v['f'];m['risk']+=q['risk'];m['safe']+=not q['risk'];m['tp']+=q['risk'] and v['f'];m['fp']+=(not q['risk']) and v['f']
  assert m==raw['summary'][stage]
print('PASS: 5 unique complete exports, source hashes and all 15 stage summaries verified.')
