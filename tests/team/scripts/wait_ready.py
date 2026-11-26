import requests,time
for i in range(90):
 try:
  if requests.get('http://127.0.0.1:8081/bookflow/auth/login',timeout=2).status_code==200:break
 except requests.RequestException:pass
 time.sleep(2)
else:raise SystemExit('Application did not become ready')
