"use strict";

const TOKEN = document.querySelector('meta[name="session-token"]').content;
const $$ = selector => [...document.querySelectorAll(selector)];
const $ = selector => document.querySelector(selector);
const state = { stats: {}, policy: {}, tunnels: [], api: "", busy: false };
const CATEGORY_NAMES = {api_key:"API keys and tokens",email:"Email addresses",phone:"Phone numbers",payment_card:"Payment card numbers",korean_rrn:"Korean resident numbers",us_ssn:"US social security numbers"};
const CATEGORY_HELP = {api_key:"Recognized GitHub, OpenAI-style and AWS access-key patterns",email:"Common email address syntax",phone:"Common Korean and North American phone formats",payment_card:"Luhn-valid candidate card numbers",korean_rrn:"Korean 13-digit resident-number patterns",us_ssn:"Formatted US SSN candidates"};
const CATEGORY_SEVERITY = {api_key:"Critical",email:"Moderate",phone:"Moderate",payment_card:"High",korean_rrn:"High",us_ssn:"High"};

function escapeHTML(value){return String(value).replace(/[&<>"']/g, s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));}
async function api(path, options={}){
  const headers={"X-SparkPrivacy-Token":TOKEN,...options.headers};
  if(options.body && typeof options.body!=="string"){options.body=JSON.stringify(options.body);headers["Content-Type"]="application/json";}
  const response = await fetch(path,{...options,headers,cache:"no-store"});
  let payload;
  try{payload=await response.json();}catch{payload={detail:`HTTP ${response.status}`};}
  if(!response.ok){const detail=typeof payload.detail === "string"?payload.detail:`HTTP ${response.status}`;throw Error(detail);}
  return payload;
}
function toast(message,error=false){const el=$("#toast");el.textContent=message;el.classList.toggle("error",error);el.classList.add("show");clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.remove("show"),4000);}
async function action(fn){try{await fn();}catch(e){toast(e.message || "Request failed",true);}}
function setPage(page){
  const view=document.getElementById(`page-${page}`);if(!view)return;
  $$(".page").forEach(p=>p.classList.toggle("current",p===view));
  $$("[data-page]").forEach(link=>link.classList.toggle("active",link.dataset.page===page));
  const title=page==='gateway'?'AI Gateway':page==='connections'?'DGX Connections':page[0].toUpperCase()+page.slice(1);
  $("#page-name").textContent=title;$("#sidebar").classList.remove("open");window.location.hash=page;
  if(page==="audit")action(loadAudit);if(page==="connections")action(loadConnections);
  if(page==="overview")action(loadStatus);
}
function time(date){try{return new Date(date).toLocaleString(undefined,{dateStyle:"short",timeStyle:"short"});}catch{return date;}}
function buildMetric(label,value,sub,icon){return `<div class="metric"><span class="metric-icon" aria-hidden="true">${icon}</span><div class="metric-title">${escapeHTML(label)}</div><div class="metric-value">${Number(value).toLocaleString()}</div><div class="metric-change">${escapeHTML(sub)}</div></div>`;}
function renderMetrics(stats){
 $("#metric-cards").innerHTML=[buildMetric("Total policy events",stats.total||0,"All locally logged decisions","▤"),buildMetric("Blocked operations",stats.blocked||0,"Policy enforcement","⊘"),buildMetric("Redacted operations",stats.redacted||0,"Sensitive values masked","◇"),buildMetric("Observed operations",stats.observed||0,"Monitoring only","◉")].join("");
}
function renderPolicySummary(actions){
 const tally={block:0,redact:0,monitor:0};Object.values(actions).forEach(x=>{if(tally[x]!==undefined)tally[x]++;});
 const total=Math.max(Object.keys(actions).length,1);
 $("#policy-summary").innerHTML=[['Blocked categories',tally.block],['Redacted categories',tally.redact],['Monitor-only categories',tally.monitor]].map(([name,num])=>`<div><div class="policy-brief"><span>${name}</span><strong>${num} / ${total}</strong></div><div class="bar-track"><span style="width:${Math.round(num/total*100)}%"></span></div></div>`).join("");
}
function renderEvents(rows,target,limit){
 const el=document.querySelector(target);
 if(!rows.length){el.innerHTML='<div class="empty-small">No activity yet. Run a sample inspection to create your first local security event.</div>';return;}
 el.innerHTML=rows.slice(0,limit).map(e=>`<div class="event"><span class="event-icon" aria-hidden="true">◇</span><span class="event-detail"><strong>${escapeHTML(e.channel.replace(/_/g," "))}</strong><small>${escapeHTML(time(e.at))} · ${Number(e.count)} finding(s)</small></span><span class="pill ${escapeHTML(e.disposition)}">${escapeHTML(e.disposition)}</span></div>`).join("");
}
async function loadStatus(){
 const result=await api('/api/status');state.stats=result.stats;state.policy=result.policies;
 $("#version").textContent=`v${result.version}`;renderMetrics(result.stats);renderPolicySummary(result.policies);
 $("#gateway-url").value=result.endpoint;$("#gateway-model").value=result.model;
 const events=await api('/api/audit?limit=6');renderEvents(events.events,'#recent-events',6);
 renderPolicyEditor();
}
function renderPolicyEditor(){
 $("#policy-editor").innerHTML=Object.keys(CATEGORY_NAMES).map(cat=>{
   const current=state.policy[cat]||"redact";
   return `<div class="policy-row"><div><strong>${escapeHTML(CATEGORY_NAMES[cat])}</strong><small>${CATEGORY_SEVERITY[cat]} detection category</small></div><p>${escapeHTML(CATEGORY_HELP[cat])}</p><select class="policy-select" data-category="${cat}" aria-label="Action for ${escapeHTML(CATEGORY_NAMES[cat])}">${["block","redact","monitor"].map(x=>`<option value="${x}" ${x===current?'selected':''}>${x==='block'?'Block':x==='redact'?'Redact':'Monitor only'}</option>`).join("")}</select></div>`;
 }).join("");
}
async function loadAudit(){
 const rows=(await api('/api/audit?limit=250')).events;
 $("#audit-rows").innerHTML=rows.length?rows.map(e=>`<tr><td>${escapeHTML(time(e.at))}</td><td>${escapeHTML(e.channel)}</td><td><span class="pill ${escapeHTML(e.disposition)}">${escapeHTML(e.disposition)}</span></td><td>${Number(e.count)}</td><td>${escapeHTML(Object.keys(e.categories).join(', ')||'—')}</td></tr>`).join(""):'<tr><td colspan="5">No events recorded.</td></tr>';
}
async function loadConnections(){
 const result=await api('/api/connections');state.tunnels=result.tunnels;
 $("#ssh-hosts").innerHTML=result.aliases.map(host=>`<option value="${escapeHTML(host)}"></option>`).join("");
 $("#ssh-tunnels").innerHTML=result.tunnels.length?result.tunnels.map(row=>`<div class="event"><div class="event-detail"><strong>127.0.0.1:${row.local_port}</strong><small>${row.active?'SSH process active':'Process stopped'}</small></div><button type="button" class="btn btn-muted" data-stop-port="${row.local_port}">Stop</button></div>`).join(""):'<div class="empty-small">No managed tunnels.</div>';
}
function renderScan(result){
 const categories=Object.entries(result.categories);
 $("#scan-state").textContent=result.disposition.toUpperCase();
 const box=$("#scan-result");box.className="";
 box.innerHTML=`<div class="scan-stats"><div class="scan-stat"><b>${result.finding_count}</b><span>Detected elements</span></div><div class="scan-stat"><b class="decision-tag">${escapeHTML(result.disposition.toUpperCase())}</b><span>Final policy decision</span></div></div><div class="mini-title">Detected categories</div><div class="event-list">${categories.length?categories.map(([name,count])=>`<div class="event"><span class="event-icon">◎</span><span class="event-detail"><strong>${escapeHTML(CATEGORY_NAMES[name]||name)}</strong><small>${Number(count)} finding(s)</small></span></div>`).join(""):'<div class="empty-small">No configured detector matched the input.</div>'}</div><div class="mini-title">${result.sanitized===null?'Protected output':'Sanitized preview'}</div><pre class="sanitized" id="sanitized-output"></pre>`;
 $("#sanitized-output").textContent=result.sanitized===null?'The content was blocked. The unredacted input is not returned by the service.':result.sanitized;
}
async function saveReport(){
 const response=await fetch('/api/report.pdf',{headers:{'X-SparkPrivacy-Token':TOKEN},cache:'no-store'});
 if(!response.ok)throw Error('Could not generate the report');
 const file=await response.blob();const url=URL.createObjectURL(file);const a=document.createElement('a');a.href=url;a.download='SparkPrivacy-Assessment.pdf';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
 toast('PDF assessment generated locally.');
}
function listeners(){
 $$('[data-page]').forEach(item=>item.addEventListener('click',()=>setPage(item.dataset.page)));
 $$('[data-page-jump]').forEach(item=>item.addEventListener('click',()=>setPage(item.dataset.pageJump)));
 $('#mobile-menu').addEventListener('click',()=>$('#sidebar').classList.toggle('open'));
 $('#date').textContent=new Date().toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'});
 $('#scan-text').addEventListener('input',e=>$('#text-counter').textContent=`${e.target.value.length.toLocaleString()} / 100,000`);
 $('#load-sample').addEventListener('click',()=>{$('#scan-text').value='Please contact example.user@sample.test or call +1 415-555-0132 about the documentation. This is synthetic test data.';$('#scan-text').dispatchEvent(new Event('input'));});
 $('#scan-action').addEventListener('click',()=>action(async()=>{const r=await api('/api/inspect',{method:'POST',body:{text:$('#scan-text').value}});renderScan(r);await loadStatus();toast('Inspection completed. Audit metadata recorded locally.');}));
 $('#save-policies').addEventListener('click',()=>action(async()=>{const actions={};$$('.policy-select').forEach(input=>actions[input.dataset.category]=input.value);const r=await api('/api/policies',{method:'PUT',body:{actions}});state.policy=r.actions;renderPolicySummary(r.actions);toast('Protection policy saved.');}));
 $('#save-gateway').addEventListener('click',()=>action(async()=>{const r=await api('/api/gateway/config',{method:'POST',body:{endpoint:$('#gateway-url').value.trim(),model:$('#gateway-model').value.trim(),upstream_token:$('#gateway-key').value||null}});$('#gateway-key').value='';toast('Local model connection configured for this session.');}));
 $('#gateway-send').addEventListener('click',()=>action(async()=>{$('#gateway-output').textContent='Sending through local protection gateway…';const r=await api('/api/gateway/test',{method:'POST',body:{prompt:$('#gateway-prompt').value}});$('#gateway-output').textContent=JSON.stringify(r,null,2).slice(0,8500);await loadStatus();toast('Protected completion completed.');}));
 $('#copy-session').addEventListener('click',()=>action(async()=>{await navigator.clipboard.writeText(TOKEN);toast('Ephemeral local gateway token copied. Treat it like a password.');}));
 $('#refresh-hosts').addEventListener('click',()=>action(loadConnections));
 $('#inspect-ssh').addEventListener('click',()=>action(async()=>{$('#ssh-output').textContent='Running read-only OpenSSH diagnostics…';const r=await api('/api/connections/inspect',{method:'POST',body:{alias:$('#ssh-alias').value.trim()}});$('#ssh-output').textContent=r.ok?r.result:r.message;toast(r.message,!r.ok);}));
 $('#start-ssh').addEventListener('click',()=>action(async()=>{const r=await api('/api/connections/tunnel',{method:'POST',body:{alias:$('#ssh-alias').value.trim(),remote_port:Number($('#ssh-remote-port').value),local_port:Number($('#ssh-local-port').value)}});if(!r.ok)throw Error(r.message);await loadConnections();toast(`Private forwarding process started on localhost:${r.local_port}. Check model readiness before use.`);}));
 $('#ssh-tunnels').addEventListener('click',e=>{const btn=e.target.closest('[data-stop-port]');if(!btn)return;action(async()=>{await api(`/api/connections/tunnel/${Number(btn.dataset.stopPort)}`,{method:'DELETE'});await loadConnections();toast('Tunnel stopped.');});});
 $('#refresh-audit').addEventListener('click',()=>action(loadAudit));
 $('#export-pdf').addEventListener('click',()=>action(saveReport));
 $('#purge-audit').addEventListener('click',()=>action(async()=>{const days=Number($('#retention-days').value);if(days===0&&!window.confirm('Permanently delete ALL audit metadata? This cannot be undone.'))return;const r=await api('/api/audit/purge',{method:'POST',body:{days}});toast(`${r.deleted} event(s) deleted.`);await loadStatus();}));
 window.addEventListener('hashchange',()=>{const hash=location.hash.slice(1);if(hash && document.getElementById(`page-${hash}`))setPage(hash);});
}
async function init(){
 listeners();const hash=window.location.hash.slice(1);if(hash)setPage(hash);
 try{await loadStatus();}catch(e){toast(`Local controller unavailable: ${e.message}`,true);}
}
init();
