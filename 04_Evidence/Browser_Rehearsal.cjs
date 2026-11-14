const { chromium }=require('playwright');const fs=require('fs');const path=require('path');const assert=require('assert');
(async()=>{const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),headless:true,args:['--no-sandbox']});const results=[];let sample;
for(const lang of ['en','ru','kk'])for(const role of ['teaching','admissions','finance']){
 const context=await browser.newContext({acceptDownloads:true});const p=await context.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('file://'+path.resolve(__dirname,'../01_Product/CyberLearn.html'));
 await p.selectOption('#lang',lang);await p.check(`[name=role][value=${role}]`);await p.fill('#alias','!');await p.locator('#launch button[type=submit],#launch button:not([type])').click();assert.equal(await p.locator('#answer').count(),0);
 await p.fill('#alias','QA-'+lang+'-'+role);await p.locator('#launch button[type=submit],#launch button:not([type])').click();
 await p.locator('#answer button:not([type])').click();assert.equal(await p.evaluate(()=>st.draft.answers.length),0);
 for(let i=0;i<12;i++){
  if(i===4)await p.locator('[data-a=enter]').click();
  const q=await p.evaluate(()=>{const q=dict[st.draft.items[st.draft.pos].id];return {f:q.risk,a:q.key}});
  await p.check(`[name=f][value=${q.f?1:0}]`);await p.check(`[name=a][value=${q.a}]`);
  if(i===1){await p.reload();await p.locator('[data-a=resume]').click();assert.equal(await p.locator(`[name=a][value=${q.a}]`).isChecked(),true);}
  if(i===2){await p.selectOption('#lang',lang==='en'?'kk':'en');await p.selectOption('#lang',lang);}
  await p.locator('#answer button:not([type])').click();await p.locator('[data-a=next]').click();
 }
 await p.selectOption('#rate','4');await p.fill('#comment','Synthetic technical QA only');const download=p.waitForEvent('download');await p.locator('[data-a=finish]').click();const file=await download;const record=JSON.parse(fs.readFileSync(await file.path(),'utf8'));assert.equal(record.records[0].answers.length,12);sample=record;
 assert.equal(await p.evaluate(()=>metrics(get(st.own[0],'post')).actions),4);assert.equal(await p.locator('[data-a=follow]:not([disabled])').count(),0);
 await p.reload();assert.equal(await p.evaluate(()=>st.own.length),1);
 await p.locator('[data-a=nav][data-v=teach]').click();await p.locator('#import').setInputFiles({name:'qa.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(record))});await p.waitForFunction(()=>st.imports.length===1);
 await p.locator('#import').setInputFiles({name:'qa.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(record))});await p.waitForTimeout(100);assert.equal(await p.evaluate(()=>st.imports.length),1);
 await p.locator('input[data-id]').check();p.once('dialog',d=>d.accept());await p.locator('[data-a=delete]').click();assert.equal(await p.evaluate(()=>st.imports.length),0);assert.equal(await p.evaluate(()=>st.own.length),1);
 if(lang==='en'&&role==='teaching'){await p.locator('[data-a=nav][data-v=home]').click();await p.screenshot({path:path.join(__dirname,'QA_home.png'),fullPage:true});await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(__dirname,'QA_mobile.png'),fullPage:true});}
 assert.deepEqual(errors,[]);results.push({lang,role,status:'PASS',checks:'invalid code, missing answer, 12 UI answers, lesson, reload/resume, language switch, feedback, actual JSON download, persisted record, locked early follow-up, reviewer import/deduplication/selective delete'});await context.close();
}
fs.writeFileSync(path.join(__dirname,'QA_synthetic_sample.json'),JSON.stringify(sample));fs.writeFileSync(path.join(__dirname,'QA_browser_results.json'),JSON.stringify({browser:await browser.version(),synthetic:true,flows:results},null,2));await browser.close();console.log(JSON.stringify(results));})().catch(e=>{console.error(e);process.exit(1)});
