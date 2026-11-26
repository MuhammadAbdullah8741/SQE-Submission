const {request}=require('@playwright/test');const {db,seed}=require('../scripts/seed.cjs');const fs=require('fs');
const base='http://127.0.0.1:8081/bookflow';
async function sql(q){const c=await db();try{return (await c.query(q))[0]}finally{await c.end()}}
async function run(){let results=[];
for(const tc of JSON.parse(fs.readFileSync('tests/team/api/generated.json'))){await seed();await sql("INSERT INTO transactions(member_id,isbn,issue_date,due_date,status) VALUES ('STU000001STU','9780000000002',CURRENT_DATE,CURRENT_DATE,'ISSUED')");const api=await request.newContext();const login=await api.get(base+'/auth/login');const html=await login.text();const token=(html.match(/name="_csrf"[^>]*value="([^"]+)"/)||[])[1];await api.post(base+'/auth/login',{form:{systemId:'LIB000001LIB',password:'SqeTest123!',_csrf:token},maxRedirects:0});const dash=await api.get(base+'/librarian/dashboard');const csrf=((await dash.text()).match(/name="_csrf"[^>]*value="([^"]+)"/)||[])[1];
const before=await sql('SELECT txn_id,status FROM transactions ORDER BY txn_id');const stock=await sql('SELECT isbn,available FROM books ORDER BY isbn');const data=Object.fromEntries(Object.entries(tc.data).map(([k,v])=>[k,String(v)]));
let res=tc.method==='post'?await api.post(base+tc.path,{form:{...data,_csrf:csrf},maxRedirects:0}):await api.get(base+tc.path,{params:data,maxRedirects:0});const after=await sql('SELECT txn_id,status FROM transactions ORDER BY txn_id');const stockAfter=await sql('SELECT isbn,available FROM books ORDER BY isbn');const body=(await res.text()).slice(0,1200);const valid=tc.path.endsWith('/issue')?(data.memberId==='STU000001STU'&&data.isbn==='9780000000001'):data.txnId==='1';let pass;
if(tc.path.endsWith('/issue')&&valid)pass=res.status()===302&&after.length===before.length+1&&stockAfter[0].available===stock[0].available-1;
else if(tc.path.endsWith('/return')&&valid)pass=res.status()===302&&after[0].status==='RETURNED';
else if(tc.method==='post')pass=JSON.stringify(before)===JSON.stringify(after)&&JSON.stringify(stock)===JSON.stringify(stockAfter)&&res.status()<500;
else {pass=res.status()<500;if(tc.path.endsWith('/precheck')&&data.memberId!=='STU000001STU')pass=pass&&body.includes('error');}
results.push({...tc,status:res.status(),pass,before,after,stock,stockAfter,body});await api.dispose();}
fs.writeFileSync('tests/team/evidence/api-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify({total:results.length,passed:results.filter(r=>r.pass).length,failed:results.filter(r=>!r.pass).length}));if(results.some(r=>!r.pass))process.exitCode=1;}
run().catch(e=>{console.error(e);process.exitCode=1});
