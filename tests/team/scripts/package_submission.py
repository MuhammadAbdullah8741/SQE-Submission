from pathlib import Path
import zipfile,subprocess,json,hashlib
r=Path(__file__).resolve().parents[3];out=r.parent/'output';out.mkdir(exist_ok=True);dest=out/'Project_24i-3068_24i-3132_24i-3050_C.zip';pdf=out/'pdf/Project_24i-3068_24i-3132_24i-3050_C.pdf'
excluded={'.sonar','node_modules','test-results','logs','uploads','__pycache__'}
files=[]
for p in r.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(r)
 if any(part in excluded for part in rel.parts):continue
 if rel.parts[0]=='target' and not (rel.as_posix()=='target/bookflow.war' or rel.parts[1] in ['site','pit-reports','surefire-reports']):continue
 if rel.as_posix().startswith('tests/team/evidence/app') and p.suffix=='.log':continue
 files.append((p,'BookFlow-SQE/'+rel.as_posix()))
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,arc in files:z.write(p,arc)
with zipfile.ZipFile(dest) as z:
 assert 'BookFlow-SQE/.git/HEAD' in z.namelist()
 assert 'BookFlow-SQE/tests/team/browser/workflows.spec.cjs' in z.namelist()
 assert z.testzip() is None
manifest={'repository_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'baseline':'4312c97ba3767b7bb8ba19687a49368b49133390','archive_files':len(files),'contains_git':True,'remote_publication':'not performed','pending':['registration evidence','team GitHub URL and genuine Issues/PRs','individual member contributions','full application coverage if examiner interprets business-logic scope broadly'],'artifacts':{}}
for p in [dest,pdf]:manifest['artifacts'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(out/'submission-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
