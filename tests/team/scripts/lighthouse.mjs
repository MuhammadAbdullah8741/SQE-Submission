import {chromium} from '@playwright/test';
import lighthouse from 'lighthouse';
import fs from 'node:fs';
const phase=process.argv[2]||'before';
const browser=await chromium.launch({headless:true,args:['--remote-debugging-port=9223']});
const context=await browser.newContext();const page=await context.newPage();
await page.goto('http://127.0.0.1:8081/bookflow/auth/login');await page.locator('[name=systemId]').fill('LIB000001LIB');await page.locator('[name=password]').fill('SqeTest123!');await page.locator('button[type=submit]').click();await page.waitForURL(/dashboard/);
const cookie=(await context.cookies()).map(c=>c.name+'='+c.value).join('; ');
for(const screen of ['issue','return']){
 const result=await lighthouse('http://127.0.0.1:8081/bookflow/librarian/dashboard#'+screen+'-section',{port:9223,output:['html','json'],logLevel:'error',onlyCategories:['accessibility','best-practices','seo'],disableStorageReset:true,extraHeaders:{Cookie:cookie},formFactor:'desktop',screenEmulation:{mobile:false,width:1440,height:1000,deviceScaleFactor:1,disabled:false}});
 fs.writeFileSync(`tests/team/evidence/lighthouse-${screen}-${phase}.html`,result.report[0]);fs.writeFileSync(`tests/team/evidence/lighthouse-${screen}-${phase}.json`,result.report[1]);
}
await browser.close();
