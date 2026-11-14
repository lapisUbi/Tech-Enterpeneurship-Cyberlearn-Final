"""Reproduce the 600/700 KZT comparison without modifying the workbook."""
import contextlib,io,runpy,json
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):model=runpy.run_path(str(Path(__file__).with_name('Audit_Financial_Model.py')))
results={}
for price in (600,700):
 model['data']['Inputs']['B6']['v']=price
 model['calc'].cache_clear()
 results[str(price)]=model['calc']('Indicators','B11')
print(json.dumps({'NPV_KZT':results,'uplift_KZT':results['700']-results['600'],'scope':'Price only; acquisition, costs, seats and retention unchanged'},indent=2))
