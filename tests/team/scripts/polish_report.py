from pathlib import Path
r=Path(__file__).resolve().parents[3];p=r/'tests/team/scripts/build_report.py';s=p.read_text()
s=s.replace("('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)","('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)")
s=s.replace("lat=m.get('http_req_duration{operation:precheck}',{}).get('values',{});rate=m.get('http_reqs',{}).get('values',{});fail=m.get('unexpected_failures',{}).get('values',{})","lat=m.get('http_req_duration{operation:precheck}',{});lat=lat.get('values',lat);rate=m.get('http_reqs',{});rate=rate.get('values',rate);fail=m.get('unexpected_failures',{});fail=fail.get('values',fail)")
s=s.replace("100*fail.get('rate',0)","100*fail.get('rate',fail.get('value',0))")
needle="page('21. Monitoring, residual risks and completion')"
insert='''page('20b. Fishbone diagrams')
def fishbone(title,causes):
 h(title)
 d=Drawing(500,190);d.add(Line(20,90,390,90,strokeColor=colors.HexColor('#147d92'),strokeWidth=2));d.add(Polygon([390,90,380,95,380,85],fillColor=colors.HexColor('#147d92')))
 d.add(Rect(390,68,110,44,fillColor=colors.HexColor('#e0edf4'),strokeColor=colors.HexColor('#147d92')))
 d.add(String(400,94,'Observed failure',fontSize=9));d.add(String(400,79,title.split(':')[0],fontSize=9))
 for i,(category,cause) in enumerate(causes):
  x=65+(i%3)*115;up=i<3;end=160 if up else 20
  d.add(Line(x+40,90,x,end,strokeColor=colors.HexColor('#147d92')))
  d.add(String(x-35,end+8,category,fontName='Helvetica-Bold',fontSize=8))
  for j,line in enumerate(cause.split('|')):d.add(String(x-35,end-5-j*10,line,fontSize=7))
 story.append(d)
fishbone('D01: duplicate active loan',[('Requirements','Retry invariant|not specified'),('Code','No member/ISBN|active-loan guard'),('Tests','No retry|assertion'),('Data','Extra stock permits|second issue'),('Process','Missing state|review checklist')])
fishbone('D03: populated dashboard crash',[('Requirements','No date|view contract'),('Code','LocalDate sent to|legacy formatter'),('Tests','No populated|browser scenario'),('Data','Empty demo hides|date-bearing loop'),('Process','No rendered|evidence review')])
para('Effects are supported by baseline failures. Corrective and preventive actions appear in the preceding 5 Whys analyses; the diagrams organise contributing factors, not independently proven historical intent.')
'''
s=s.replace(needle,insert+needle)
s=s.replace("'See performance table. Repaired dashboard axe violations '+str(len(after['violations']))+'. Evaluate all workload thresholds from raw reports.'", "'Four workload runs: '+('MET' if len(load(e/'k6-run-status.json',[]))==4 and all(x['exitCode']==0 for x in load(e/'k6-run-status.json',[])) else 'NOT YET MET')+'; repaired dashboard axe violations '+str(len(after['violations']))+'. See exact p95/failure values in section 18.'")
p.write_text(s,encoding='utf-8')
