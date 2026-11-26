from pathlib import Path
r=Path(__file__).resolve().parents[3]
p=r/'tests/team/scripts/timezone_evidence.cjs';s=p.read_text();s=s.replace('jdbc_connection_init_sql:"SET time_zone = \'+05:00\'"','jdbc_timezone_options:"connectionTimeZone=%2B05:00&forceConnectionTimeZoneToSession=true"');p.write_text(s)
p=r/'tests/team/scripts/build_report.py';s=p.read_text(encoding='utf-8');needle="evidence('k6-1-1/1-2/5-1/5-2.json and logs; final-build.log; RecoveryIntegrationTest.java; environment.json')"
addition="""para('Continuation on 26 Nov exposed a test-environment midnight mismatch: MySQL CURRENT_DATE was still 25 Nov UTC while Java used 26 Nov Karachi. The failed browser run is preserved. Fixture SQL sessions and JDBC sessions now use +05:00; Java is explicitly Asia/Karachi. A database/date contract integration test prevents silent drift. Retained k6 measurements precede this explicit timezone configuration; the measured stock lookup does not use dates.')
evidence('timezone-policy.json; playwright-timezone-failure.json; browser-expanded-final.log; unit-expanded.log')
"""
s=s.replace(needle,needle+'\n'+addition);p.write_text(s,encoding='utf-8')
p=r/'README-SQE.txt';s=p.read_text();s+='\nTIMEZONE REPRODUCIBILITY\nThe start script pins Java to Asia/Karachi and JDBC connectionTimeZone=+05:00 with\nforceConnectionTimeZoneToSession=true. The SQL fixture connections also set time_zone=+05:00.\nThis prevents UTC/local midnight drift in CURRENT_DATE test fixtures.\nConnector/J documentation: https://dev.mysql.com/doc/connector-j/en/connector-j-time-instants.html\n';p.write_text(s)
