const mysql=require('mysql2/promise');
const {execFileSync}=require('node:child_process');
async function db(){const c=await mysql.createConnection({host:'127.0.0.1',port: +(process.env.DB_PORT||3308),user:'root',password:process.env.DB_PASSWORD||'SqeLocal2026',database:'bookflow_test',multipleStatements:true});await c.query("SET time_zone = '+05:00'");return c;}
async function seed(){const c=await db();
// Guard prevents reset of any database other than the dedicated synthetic test database.
const [[name]]=await c.query('SELECT DATABASE() AS name');if(name.name!=='bookflow_test')throw Error('Refusing non-test database');
const hash=execFileSync('python',['-c',"import bcrypt; print(bcrypt.hashpw(b'SqeTest123!',bcrypt.gensalt(4)).decode())"],{encoding:'utf8'}).trim();
await c.query('SET FOREIGN_KEY_CHECKS=0');
for(const t of ['fines','transactions','reservations','audit_log','password_reset_tokens','announcements','ai_cache','books','users'])await c.query('TRUNCATE TABLE '+t);
await c.query('SET FOREIGN_KEY_CHECKS=1');
for(const [id,role,status] of [['LIB000001LIB','LIB','ACTIVE'],['STU000001STU','STU','ACTIVE'],['LOCK000001STU','STU','LOCKED'],['ADM000001ADM','ADM','ACTIVE']])await c.query('INSERT INTO users(system_id,first_name,last_name,password_hash,role,email,phone,status,failed_login_attempts) VALUES (?,?,?,?,?,?,?,?,0)',[id,'Synthetic',role,hash,role,id+'@example.test','9876543210',status]);
for(let i=1;i<=5;i++)await c.query('INSERT INTO books(isbn,title,author,category,total_copies,available,status) VALUES (?,?,?,?,?,?,?)',['978000000000'+i,'SQE Book '+i,'Synthetic Author','TEXTBOOK',5,i===5?0:5,i===5?'ISSUED':'AVAILABLE']);
await c.query("INSERT INTO config(config_key,config_value) VALUES ('fine.rate.textbook','5.00'),('fine.rate.default','5.00') ON DUPLICATE KEY UPDATE config_value=VALUES(config_value)");
await c.end();}
module.exports={db,seed};
if(require.main===module)seed().then(()=>console.log('Synthetic database reset complete')).catch(e=>{console.error(e);process.exit(1)});
