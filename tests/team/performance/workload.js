import http from 'k6/http';
import {check,sleep} from 'k6';
import {Rate} from 'k6/metrics';
const unexpectedFailures=new Rate('unexpected_failures');
export const options={vus:Number(__ENV.VUS||1),duration:'65s',thresholds:{'http_req_duration{operation:precheck}':['p(95)<500'],'unexpected_failures':['rate<0.01']}};
const base=__ENV.BASE_URL||'http://host.docker.internal:8081/bookflow';
export function setup(){const page=http.get(base+'/auth/login');const token=page.html().find('input[name="_csrf"]').attr('value');http.post(base+'/auth/login',{systemId:'LIB000001LIB',password:'SqeTest123!',_csrf:token});return {cookie:http.cookieJar().cookiesForURL(base).JSESSIONID[0]};}
export default function(data){const r=http.get(base+'/librarian/issue/precheck?memberId=STU000001STU&isbn=9780000000001',{headers:{Cookie:'JSESSIONID='+data.cookie},tags:{operation:'precheck'},redirects:0});const valid=check(r,{'status 200':r=>r.status===200,'availability JSON':r=>r.body.includes('copiesLeft')});unexpectedFailures.add(!valid);sleep(0.2);}
