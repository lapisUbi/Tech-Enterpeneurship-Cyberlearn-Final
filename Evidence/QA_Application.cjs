// Reproducible synthetic test of the complete distributed script using host DOM stubs.
// No browser engine, layout, physical keyboard or human usability claims.
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'MVP/CyberLearn.html'),'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const checks=[],downloads=[];let blocked=false;
const memory=new Map(),events={},nodes=new Map();
function node(k){if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',dataset:{},value:'',attrs:{},setAttribute(a,v){this.attrs[a]=v},focus(){this.focused=true},scrollIntoView(){},setSelectionRange(){},appendChild(x){this.child=x},querySelector(){return this.child||null},closest(){return node('form')},remove(){},click(){},append(){}});return nodes.get(k)}
const document={querySelector:node,querySelectorAll:()=>[],createElement:()=>node('new-'+Math.random()),addEventListener:(t,fn)=>events[t]=fn,documentElement:{lang:'en'},body:node('body')};
const window={addEventListener(){},scrollTo(){},print(){}};
const context={document,window,crypto:crypto.webcrypto,Uint8Array,URLSearchParams,URL,Blob,location:{protocol:'file:',hash:''},localStorage:{getItem:k=>memory.get(k)||null,setItem:(k,v)=>{if(blocked)throw Error('storage unavailable');memory.set(k,v)}},setTimeout:()=>0,clearTimeout(){},Intl,confirm:()=>true,assert,downloads};
const ctx=vm.createContext(context),run=s=>vm.runInContext(s,ctx);
vm.runInContext(script,ctx);run('filedownload=(name,content,type)=>downloads.push({name,content,type})');
const yes=(name,test)=>{assert(test,name);checks.push({name,result:'PASS'})};
const event=async(t,target)=>events[t]({target,preventDefault(){}});
const click=async(a,v='')=>event('click',{closest:()=>({dataset:{a,v}})});
(async()=>{
 yes('bank contains 60 complete trilingual items',run(`BANK.length===60&&BANK.every(q=>LANG.every(l=>{const c=q.text[l];return c&&c.subject&&c.body&&c.explanation&&c.options.length===3}))`));
 yes('all UI entries have three nonempty translations',run('Object.values(UI).every(v=>Array.isArray(v)&&v.length===3&&v.every(x=>typeof x===\'string\'&&x.length))'));
 for(const lang of ['en','kk','ru'])for(const role of ['teaching','admissions','finance']){
  run(`st=defaults();st.lang='${lang}';st.role='${role}';st.alias='QA-${role}';view='home';render(false)`);
  node('#alias').value='!';await event('submit',{id:'launch'});yes(`${lang}/${role}: invalid code rejected and focused`,run('st.draft===null')&&node('#alias').attrs['aria-invalid']==='true'&&node('#alias').focused);
  node('#alias').value='QA-ONLY';await event('submit',{id:'launch'});
  const ids=run('st.draft.items.map(x=>x.id).join()');yes(`${lang}/${role}: 12 unique balanced items`,run('st.draft.items.length===12&&new Set(st.draft.items.map(x=>x.id)).size===12'));
  await event('submit',{id:'answer'});yes(`${lang}/${role}: missing choices rejected`,run('st.draft.answers.length===0')&&node('[name=f]').focused);
  await event('change',{id:'lang',value:lang==='en'?'kk':'en',dataset:{}});yes(`${lang}/${role}: language switch preserves route`,run('st.draft.items.map(x=>x.id).join()')===ids);await event('change',{id:'lang',value:lang,dataset:{}});
  for(let i=0;i<12;i++){
   if(run("st.draft.screen==='lesson'"))await click('enter');
   const answer=run('({f:dict[st.draft.items[st.draft.pos].id].risk,a:dict[st.draft.items[st.draft.pos].id].key})');
   await event('change',{name:'f',value:answer.f?'1':'0',dataset:{}});await event('change',{name:'a',value:String(answer.a),dataset:{}});await event('submit',{id:'answer'});
   if(i===4)yes(`${lang}/${role}: practice explanation rendered`,node('#main').innerHTML.includes(run('E(txt(st.draft.items[st.draft.pos].id).explanation)')));
   yes(`${lang}/${role}: progress ${i+1}/12`,node('#main').innerHTML.includes(`value="${i+1}" max="12"`));
   await click('next');
  }
  yes(`${lang}/${role}: finish guidance rendered`,node('#main').innerHTML.includes(run("t('progressFeedback')")));await click('finish');
  yes(`${lang}/${role}: completion, separate scores and handoff rendered`,['score-guide','handoff-guide'].every(x=>node('#main').innerHTML.includes(x))&&node('#main').innerHTML.includes(run("t('completeSaved')")));
  yes(`${lang}/${role}: correct scoring, 80 XP and build identifier`,run("safeRecord(st.own[0])&&metrics(get(st.own[0],'pre')).actions===4&&metrics(get(st.own[0],'post')).ok===4&&xp(st.own[0])===80&&st.own[0].build==='2.2.0'"));
  yes(`${lang}/${role}: saved state and JSON export`,JSON.parse(memory.get('CyberLearnCampusQuest2')).own.length===1&&JSON.parse(downloads.at(-1).content).records[0].build==='2.2.0');
 }
 run("var sample=JSON.parse(JSON.stringify(st.own[0]));var wrong=JSON.parse(JSON.stringify(sample));wrong.answers=wrong.answers.map(a=>({...a,f:!dict[a.id].risk,a:(dict[a.id].key+1)%3}));");
 yes('wrong-answer scoring remains zero',run("metrics(get(wrong,'post')).actions===0&&metrics(get(wrong,'post')).ok===0&&metrics(get(wrong,'post')).fp===2&&xp(wrong)===0"));
 yes('optional build validated; old records accepted',run("!safeRecord({...sample,build:'bad'})&&safeRecord((({build,...r})=>r)(sample))"));
 await click('nav','teach');const file=r=>({size:1000,text:async()=>JSON.stringify({format:'CyberLearn.CampusQuest/2',records:[r]})});ctx.file=file(JSON.parse(run('JSON.stringify(sample)')));await run('ingest([file])');yes('reviewer import',run('st.imports.length===1'));await run('ingest([file])');yes('identical duplicate skipped',run('st.imports.length===1&&importMsg.includes(t(\'dup\')+\': 1\')'));
 ctx.file=file({...JSON.parse(run('JSON.stringify(sample)')),build:'9.9.9'});await run('ingest([file])');yes('conflicting duplicate rejected',run('st.imports.length===1&&importMsg.includes(t(\'invalid\')+\': 1\')'));
 ctx.file={size:3000000,text:async()=>''};await run('ingest([file])');yes('oversized import rejected',run('st.imports.length===1&&importMsg.includes(t(\'invalid\')+\': 1\')'));
 run("chosen.add(st.imports[0].id)");await click('delete');yes('reviewer selected record deleted',run('st.imports.length===0'));
 run("st.draft=null;start(st.own[0].id)");yes('day-seven early start denied',run('st.draft===null'));
 run("st.own[0].end=now()-8*D;st.own[0].start=st.own[0].end-1000;start(st.own[0].id)");yes('eligible followup uses four held-out items',run("st.draft.items.length===4&&st.draft.items.every(x=>dict[x.id].pool==='follow')"));
 run('save()');const reload=vm.createContext({...context,document:{...document,addEventListener(){}}});vm.runInContext(script,reload);yes('reload restores in-progress followup',vm.runInContext('st.draft.items.length===4',reload));
 blocked=true;run('save();render(false)');yes('storage failure warning rendered',run('storageOK===false')&&node('#main').innerHTML.includes(run("t('storage')")));blocked=false;
 run("st.draft=null;view='hist';chosen.add(st.own[0].id)");await click('delete');yes('own selected record deleted',run('st.own.length===0'));
 yes('basic accessibility hooks in distributed HTML',html.includes('class="skip"')&&html.includes('tabindex="-1"')&&html.includes('aria-live="polite"')&&html.includes('<fieldset')&&html.includes('<legend'));
 console.log(JSON.stringify({version:'2.2.0',generated_utc:new Date().toISOString(),scope:'Complete distributed JavaScript executed with a minimal host DOM adapter; callbacks, state and generated markup checked. Not browser rendering, physical keyboard, OS download, or human usability testing.',html_sha256:crypto.createHash('sha256').update(html).digest('hex'),checks,passed:checks.length,limitations:['No browser engine or visual layout','No actual OS download or browser localStorage quota','Kazakh linguistic quality needs human review','No real users retested build 2.2.0']},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
