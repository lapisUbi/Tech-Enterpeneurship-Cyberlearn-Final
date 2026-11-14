#!/usr/bin/env python3
"""Read-only audit for the CyberLearn A6 workbook. Uses the Python standard library.
Run: python3 Audit_Financial_Model.py [optional/path/to/workbook.xlsx]
JSON is printed to stdout. This script does not modify the workbook.
The evaluator covers only the formula language actually used by this workbook;
it is not a general-purpose Excel calculation engine.
"""

import zipfile, xml.etree.ElementTree as E, json, re, math, functools, hashlib, sys
from pathlib import Path
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name("CyberLearn_A6_Model.xlsx")
ns={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
data={}
with zipfile.ZipFile(p) as z:
 ss=["".join(x.itertext()) for x in E.fromstring(z.read("xl/sharedStrings.xml"))] if "xl/sharedStrings.xml" in z.namelist() else []
 rel={r.attrib["Id"]:r.attrib["Target"] for r in E.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
 wb=E.fromstring(z.read("xl/workbook.xml"))
 for sh in wb.find("s:sheets",ns):
  target=rel[sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
  path=target.lstrip("/") if target.startswith("/") else "xl/"+target
  cells={}
  for c in E.fromstring(z.read(path)).findall(".//s:c",ns):
   v=c.find("s:v",ns); f=c.find("s:f",ns); inline=c.find("s:is",ns)
   value=v.text if v is not None else "".join(inline.itertext()) if inline is not None else None
   if c.attrib.get("t")=="s" and value is not None: value=ss[int(value)]
   elif c.attrib.get("t") not in ("str","inlineStr","e") and value is not None:
    try: value=float(value)
    except ValueError: pass
   if value is not None or f is not None: cells[c.attrib["r"]]={"v":value,"f":None if f is None else f.text}
  data[sh.attrib["name"]]=cells

tok_re=re.compile(r'\s*(?:((?:[A-Za-z_][A-Za-z0-9_]*!)?\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)|([0-9]+(?:\.[0-9]*)?(?:[Ee][+-]?[0-9]+)?)|("(?:""|[^"])*")|([A-Za-z_][A-Za-z0-9_]*)|(>=|<=|<>|[+*/^(),=<>-]))')
active=set()
def flatten(v):
 if isinstance(v,list):
  for x in v: yield from flatten(x)
 else: yield v
def colnum(c):
 n=0
 for x in c: n=n*26+ord(x)-64
 return n
def colstr(n):
 s=""
 while n: n,r=divmod(n-1,26); s=chr(65+r)+s
 return s
def refval(sheet,ref):
 if "!" in ref: sheet,ref=ref.split("!")
 ref=ref.replace("$","")
 if ":" not in ref: return calc(sheet,ref)
 a,b=ref.split(":"); ca,ra=re.match(r"([A-Z]+)(\d+)",a).groups(); cb,rb=re.match(r"([A-Z]+)(\d+)",b).groups()
 return [calc(sheet,colstr(c)+str(r)) for r in range(int(ra),int(rb)+1) for c in range(colnum(ca),colnum(cb)+1)]
def func(name,args):
 vals=list(flatten(args))
 nums=[v for v in vals if isinstance(v,(float,int))]
 if name=="SUM": return sum(nums)
 if name=="MIN": return min(nums)
 if name=="IF": return args[1] if args[0] else args[2]
 if name=="AND": return all(args)
 if name=="ROUND": return round(args[0],int(args[1]))
 if name=="ROUNDUP": return math.copysign(math.ceil(abs(args[0])*10**args[1])/10**args[1],args[0])
 if name=="SUMPRODUCT": return sum(math.prod(a) for a in zip(*args))
 raise ValueError(name)
class Parser:
 def __init__(self,s,sheet):
  self.t=[]; self.sheet=sheet; pos=0; self.i=0
  while pos<len(s):
   m=tok_re.match(s,pos)
   if not m: raise ValueError("Bad token "+s[pos:])
   self.t.append(next((k,x) for k,x in enumerate(m.groups()) if x is not None)); pos=m.end()
 def peek(self): return self.t[self.i][1] if self.i<len(self.t) else None
 def take(self): t=self.t[self.i]; self.i+=1; return t
 def expr(self,minp=0):
  kind,v=self.take()
  if v in ("+","-"): a=self.expr(4); a=a if v=="+" else -a
  elif v=="(": a=self.expr(); assert self.take()[1]==")"
  elif kind==0: a=refval(self.sheet,v)
  elif kind==1: a=float(v)
  elif kind==2: a=v[1:-1].replace('""','"')
  elif kind==3:
   assert self.take()[1]=="("; args=[]
   if self.peek()!=")":
    while True:
     args.append(self.expr())
     if self.peek()!=",": break
     self.take()
   assert self.take()[1]==")"; a=func(v,args)
  else: raise ValueError(v)
  prec={"=":1,"<>":1,">":1,"<":1,">=":1,"<=":1,"+":2,"-":2,"*":3,"/":3,"^":4}
  while self.peek() in prec and prec[self.peek()]>=minp:
   op=self.take()[1]; b=self.expr(prec[op]+(0 if op=="^" else 1))
   if op=="+": a=a+b
   elif op=="-": a=a-b
   elif op=="*": a=a*b
   elif op=="/": a=a/b
   elif op=="^": a=a**b
   elif op=="=": a=a==b
   elif op=="<>": a=a!=b
   elif op==">": a=a>b
   elif op=="<": a=a<b
   elif op==">=": a=a>=b
   elif op=="<=": a=a<=b
  return a
@functools.lru_cache(None)
def calc(sheet,ref):
 key=(sheet,ref)
 if key in active: raise ValueError("CYCLE "+str(key))
 c=data[sheet].get(ref,{"v":0,"f":None})
 if not c["f"]: return 0 if c["v"] is None else c["v"]
 active.add(key)
 try:
  p=Parser(c["f"],sheet); v=p.expr(); assert p.i==len(p.t); return v
 finally: active.remove(key)
mismatches=[]; problems=[]; count=0; maxdiff=0
for sh,cells in data.items():
 for ref,c in cells.items():
  if not c["f"]: continue
  count+=1
  try:
   v=calc(sh,ref); old=c["v"]
   if isinstance(v,(int,float)) and isinstance(old,(int,float)):
    diff=abs(v-old); maxdiff=max(maxdiff,diff)
    if diff>1e-6: mismatches.append([sh,ref,old,v,diff])
   elif old!=v: mismatches.append([sh,ref,old,v])
  except Exception as e: problems.append([sh,ref,c["f"],str(e)])
formula_result={"evaluated":count,"cache_mismatches_gt_0.000001":mismatches,"maximum_numeric_difference":maxdiff,"errors_or_cycles":problems}

def inp(r,c="B"): return calc("Inputs",c+str(r))
fixed=[]; base_new=[inp(33,c) for c in "BCDEF"]
for y,c in enumerate("BCDEF"):
 e=(1+inp(10))**y
 f=(inp(34,c)*inp(12)*12+inp(35,c)*inp(13)*12+inp(36,c)*inp(14)*12+inp(15)*12+inp(16)+inp(17)*12+inp(18)*12)*e
 fixed.append(f)
initial=sum(calc("Startup","B"+str(r))*calc("Startup","C"+str(r)) for r in range(5,11))
out=[]
for sr in range(5,12):
 acq,pr,ret,op,rate=[calc("Sensitivity",c+str(sr)) for c in "BCDEF"]
 close=0.; revenue=[]; costs=[]; cash=[]; monthly=[]; monthly_bal=[]; balance=-initial; annual_balance=-initial; annual_pb=None; monthly_pb=None
 for y in range(5):
  new=base_new[y]*acq; retained=close*ret; close=retained+new; bill=retained+new*inp(9); escal=(1+inp(10))**y
  r=bill*inp(5)*inp(6)*12*pr+new*inp(7)
  co=fixed[y]*op+(bill*(inp(19)+inp(20))+new*(inp(21)+inp(22)))*escal*op
  flow=r-co; revenue.append(r); costs.append(co); cash.append(flow)
  if annual_balance<0<=annual_balance+flow: annual_pb=y-annual_balance/flow
  annual_balance+=flow
  for m in range(1,13):
   active_customers=retained+(new if m>=inp(25) else 0)
   new_at_month=new if m==inp(25) else 0
   receipts=active_customers*inp(5)*inp(6)*pr+new_at_month*inp(7)
   paid=fixed[y]*op/12+active_customers*(inp(19)+inp(20))*escal*op/12+new*inp(22)*escal*op/12+new_at_month*inp(21)*escal*op
   cf=receipts-paid; monthno=y*12+m
   if balance<0<=balance+cf: monthly_pb=(monthno-1-balance/cf)/12
   balance+=cf; monthly.append(cf); monthly_bal.append(balance)
 npv=-initial+sum(v/(1+rate)**(i+1) for i,v in enumerate(cash))
 pvbenefits=sum(v/(1+rate)**(i+1) for i,v in enumerate(revenue)); pvcost=initial+sum(v/(1+rate)**(i+1) for i,v in enumerate(costs))
 roi=(sum(revenue)-sum(costs)-initial)/(sum(costs)+initial); gap=-min([-initial]+monthly_bal)
 checks={"NPV":npv-calc("Sensitivity","G"+str(sr)),"BCR":pvbenefits/pvcost-calc("Sensitivity","H"+str(sr)),"ROI":roi-calc("Sensitivity","I"+str(sr))}
 if annual_pb is not None: checks["annual_payback"]=annual_pb-calc("Sensitivity","J"+str(sr))
 rec={"scenario":data["Sensitivity"]["A"+str(sr)]["v"],"NPV":npv,"BCR":pvbenefits/pvcost,"ROI_pct":roi*100,"annual_payback":annual_pb,"independent_monthly_payback":monthly_pb,"independent_cash_gap":gap,"gap_month":monthly_bal.index(min(monthly_bal))+1,"funding_plus_15pct":gap*(1+inp(23)),"diff_from_workbook":checks}
 if sr==5:
  rec["annual_net_cash"]=cash
  rec["monthly_max_diff"]=max(abs(v-calc("Cash_Monthly","O"+str(i+5))) for i,v in enumerate(monthly))
  rec["monthly_balance_max_diff"]=max(abs(v-calc("Cash_Monthly","P"+str(i+5))) for i,v in enumerate(monthly_bal))
  rec["reconciliation_cells"]={str(r):calc("Indicators","B"+str(r)) for r in [30,31,32,33,34,36]}
 out.append(rec)

result={
 "method":"Read-only OOXML formula evaluation plus independent economic rebuild from input drivers. Not a native Excel or LibreOffice recalculation.",
 "workbook":p.name,
 "workbook_bytes":p.stat().st_size,
 "workbook_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
 "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 "currency":"KZT",
 "model_scope":"Five forecast operating years plus year-zero launch investment; pre-tax, unlevered, nominal, no terminal value.",
 "formula_verification":formula_result,
 "independent_economic_rebuild":out,
 "limitations":[
  "Forecast assumptions are not observed sales, signed contracts, vendor quotes, or customer-validation evidence.",
  "Scenario payback in the original workbook uses annual interpolation; the base headline monthly payback has a different timing basis.",
  "Independent monthly scenario payback and cash-gap figures are supplemental calculations, not outputs already stored in original workbook cells.",
  "Inputs B9 and B25 must remain coherent; the current timing and annual/monthly reconciliation checks equal zero.",
  "No native application recalculation, workbook editing, tax review, or market validation was performed."
 ]
}
print(json.dumps(result,indent=2))
if problems or mismatches: sys.exit(1)

