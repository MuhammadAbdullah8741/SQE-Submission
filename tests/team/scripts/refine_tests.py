from pathlib import Path
r=Path(__file__).resolve().parents[3];p=r/'tests/team/browser/workflows.spec.cjs';s=p.read_text();s=s.replace("const token=await page.locator('input[name=_csrf]').first().getAttribute('value');", "const tokenHtml=await (await page.request.get(base+'/auth/login')).text();const token=tokenHtml.match(/name=\"_csrf\"[^>]*value=\"([^\"]+)\"/)[1];")
p.write_text(s)
