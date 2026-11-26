import requests,json,time
from pathlib import Path
e=Path(__file__).resolve().parents[1]/'evidence';url='http://127.0.0.1:8090'
for _ in range(60):
 n=int(requests.get(url+'/JSON/pscan/view/recordsToScan/',timeout=10).json()['recordsToScan'])
 if n==0:break
 time.sleep(2)
data=requests.get(url+'/JSON/core/view/alerts/',params={'baseurl':'http://host.docker.internal:8081','count':1000},timeout=30).json()
(e/'zap-passive.json').write_text(json.dumps(data,indent=2))
(e/'zap-passive.html').write_text(requests.get(url+'/OTHER/core/other/htmlreport/',timeout=30).text,encoding='utf-8')
(e/'zap-mode.json').write_text(json.dumps(requests.get(url+'/JSON/core/view/mode/',timeout=10).json()))
print(len(data.get('alerts',[])),'passive alerts saved')
