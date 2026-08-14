from fastapi.responses import HTMLResponse

DASHBOARD_HTML = r"""
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nicole Puzzle Coach</title>
<style>
:root{--bg:#f5f7fb;--card:#fff;--text:#1f2636;--muted:#70798b;--line:#e4e8ef;--accent:#ff6469;--shadow:0 8px 28px rgba(31,38,54,.07)}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--text)}
.wrap{max-width:1220px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:22px}
h1{margin:0;font-size:30px}.sub,.small{color:var(--muted)}.badge{padding:8px 12px;border-radius:999px;font-size:13px;font-weight:800;background:#eef3ff}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:var(--shadow)}
.kpi{grid-column:span 3}.third{grid-column:span 4}.half{grid-column:span 6}.full{grid-column:span 12}
.label{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}.value{font-size:30px;font-weight:900;margin-top:7px}
h2{font-size:19px;margin:0 0 14px}.list{display:grid;gap:9px}.item{padding:12px;border:1px solid var(--line);border-radius:12px;background:#fafafa}.item strong{display:block}
.pill{display:inline-block;margin:5px 5px 0 0;padding:4px 8px;border-radius:999px;background:#eef0f4;font-size:12px}
input,select,textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;color:var(--text)}
.formgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.wide{grid-column:1/-1}
button,.btn{border:0;border-radius:11px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block}.primary{background:var(--accent);color:#fff}.secondary{background:#eef0f4;color:var(--text)}
.hero{background:linear-gradient(135deg,#fff,#fff3f3)}.metricrow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.metric{background:#fafafa;border:1px solid var(--line);padding:12px;border-radius:12px}.metric b{font-size:20px}
@media(max-width:900px){.kpi,.third,.half{grid-column:span 12}.formgrid,.metricrow{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<header><div><h1>🧩 Nicole Puzzle Coach</h1><div class="sub">Speed-Puzzling Training & Turniervorbereitung</div></div><div id="systemBadge" class="badge">System wird geprüft…</div></header>

<div class="grid">
<section class="card kpi"><div class="label">System</div><div class="value" id="systemKpi">–</div><div class="small" id="systemText"></div></section>
<section class="card kpi"><div class="label">MySpeedPuzzling</div><div class="value" id="mspKpi">–</div><div class="small" id="mspText"></div></section>
<section class="card kpi"><div class="label">Form</div><div class="value" id="trendKpi">–</div><div class="small">letzte Solo-Ergebnisse</div></section>
<section class="card kpi"><div class="label">Konsistenz</div><div class="value" id="consistencyKpi">–</div><div class="small">0–100</div></section>

<section class="card half hero"><h2>🏆 Mein nächstes Turnier</h2><div id="nextMspCompetition" class="small">Prüfe bestätigte Anmeldung…</div></section>
<section class="card half hero"><h2>🎯 Coach-Empfehlung</h2><div id="coachRecommendation" class="small">Analysiere MySpeedPuzzling-Ergebnisse…</div></section>

<section class="card full"><h2>✅ Meine bestätigten Turniere</h2><div id="mspCompetitions" class="list"></div></section>

<section class="card full"><h2>📈 Automatische Trainingsanalyse</h2>
<div class="metricrow">
<div class="metric"><div class="label">Ergebnisse gesamt</div><b id="autoTotal">–</b><div class="small" id="autoModes"></div></div>
<div class="metric"><div class="label">Schnellste erfasste Zeit</div><b id="autoBest">–</b><div class="small" id="autoBestInfo"></div></div>
<div class="metric"><div class="label">Letztes Ergebnis</div><b id="autoLatest">–</b><div class="small">automatisch aus MySpeedPuzzling</div></div>
</div></section>

<section class="card half"><h2>🧩 Leistung nach Teilezahl</h2><div id="piecePerformance" class="list"><div class="small">Analyse wird geladen…</div></div></section>
<section class="card half"><h2>🏭 Leistung nach Hersteller</h2><div id="manufacturerPerformance" class="list"><div class="small">Analyse wird geladen…</div></div></section>

<section class="card half"><h2>⏱️ Letzte MySpeedPuzzling-Ergebnisse</h2><div id="autoTrainings" class="list"></div></section>
<section class="card half"><h2>✍️ Training zusätzlich manuell erfassen</h2><div class="formgrid">
<input id="sDate" type="date"><input id="sPuzzle" placeholder="Puzzlename"><input id="sManufacturer" placeholder="Hersteller"><input id="sPieces" type="number" placeholder="Teilezahl">
<select id="sMode"><option value="solo">Solo</option><option value="duo">Duo</option><option value="team">Team</option></select><input id="sDuration" placeholder="Zeit, z.B. 42:15">
<input id="sTarget" placeholder="Zielzeit, z.B. 40:00"><input id="sFocus" placeholder="Fokus, z.B. Sortieren"><textarea id="sNotes" class="wide" placeholder="Notizen"></textarea>
<button class="primary wide" onclick="addTraining()">Training speichern</button>
</div></section>

<section class="card full"><h2>📝 Zusätzliche manuelle Trainings</h2><div id="manualTrainings" class="list"></div></section>

<section class="card full"><h2>🧠 Tournament Intelligence</h2>
<div class="small">V5.4 kombiniert bestätigte Turnieranmeldungen mit den echten MySpeedPuzzling-Ergebnissen. Die Form wird aus den letzten Solo-Ergebnissen normalisiert auf Zeit pro 100 Teile berechnet, damit unterschiedliche Teilezahlen nicht direkt miteinander vermischt werden.</div>
<div style="margin-top:12px"><a class="btn secondary" href="/docs" target="_blank">API-Dokumentation</a> <a class="btn secondary" href="/msp/my-competitions?refresh=true" target="_blank">Anmeldungen neu prüfen</a> <a class="btn secondary" href="/sync" target="_blank">MySpeedPuzzling neu synchronisieren</a></div>
</section>
</div></div>

<script>
function timeToSeconds(v){if(!v)return null;let p=v.split(':').map(Number);if(p.some(Number.isNaN))return null;if(p.length===3)return p[0]*3600+p[1]*60+p[2];if(p.length===2)return p[0]*60+p[1];return Number(v)}
async function getj(u){let r=await fetch(u),d=await r.json();if(!r.ok)throw new Error(d.detail||'Fehler');return d}
function dateText(v){if(!v)return'–';try{return new Date(v).toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit',year:'numeric'})}catch(e){return v}}
function countdownText(v){if(!v)return'';let ms=new Date(v)-new Date();if(ms<=0)return'Heute / gestartet';let d=Math.floor(ms/86400000),h=Math.floor((ms%86400000)/3600000);return d>1?`Noch ${d} Tage`:d===1?`Noch 1 Tag ${h} Std.`:`Noch ${h} Stunden`}
function pct(v){if(v==null)return'–';return `${v>0?'+':''}${v}%`}
async function loadAll(){
 try{let st=await getj('/coach/status');systemKpi.textContent='OK';systemText.textContent=`Backend V${st.version} · Datenbank ok`;systemBadge.textContent='🟢 System bereit';mspKpi.textContent=st.has_myspeedpuzzling_data?'LIVE':(st.oauth_configured?'READY':'WAIT');mspText.textContent=st.has_myspeedpuzzling_data?'Daten synchronisiert':'Verbindung möglich'}catch(e){systemBadge.textContent='🔴 Fehler'}

 try{
   let a=await getj('/coach/msp-training-summary');
   trendKpi.textContent=pct(a.form_percent);consistencyKpi.textContent=a.consistency_score==null?'–':a.consistency_score;
   coachRecommendation.innerHTML=`<strong>${a.recommendation}</strong>`;
   autoTotal.textContent=a.total_results;autoModes.textContent=`Solo ${a.mode_counts.solo} · Duo ${a.mode_counts.duo} · Team ${a.mode_counts.team}`;
   if(a.best_overall){autoBest.textContent=a.best_overall.time;autoBestInfo.textContent=`${a.best_overall.puzzle_name} · ${a.best_overall.pieces||'?'} Teile · ${a.best_overall.mode}`;}
   autoLatest.textContent=a.latest_result_at?dateText(a.latest_result_at):'–';
   autoTrainings.innerHTML=a.latest_results.length?a.latest_results.map(r=>`<div class="item"><strong>${r.puzzle_name}</strong><div class="small">${dateText(r.finished_at)} · ${r.manufacturer} · ${r.pieces||'?'} Teile · ${r.mode.toUpperCase()} · ${r.time}</div>${r.first_attempt?'<span class="pill">1. Versuch</span>':''}</div>`).join(''):'<div class="small">Keine Ergebnisse.</div>';
   piecePerformance.innerHTML=a.piece_groups.length?a.piece_groups.slice(0,10).map(g=>`<div class="item"><strong>${g.pieces} Teile</strong><div class="small">${g.count} Solo-Ergebnisse · Ø ${g.average} · Best ${g.best}</div>${g.trend_percent!=null?`<span class="pill">Trend ${pct(g.trend_percent)}</span>`:''}</div>`).join(''):'<div class="small">Noch keine ausreichenden Daten.</div>';
   manufacturerPerformance.innerHTML=a.manufacturer_groups.length?a.manufacturer_groups.slice(0,10).map(g=>`<div class="item"><strong>${g.manufacturer}</strong><div class="small">${g.count} Solo-Ergebnisse · Ø ${g.avg_time_per_100} pro 100 Teile</div></div>`).join(''):'<div class="small">Noch keine ausreichenden Daten.</div>';
 }catch(e){coachRecommendation.textContent='Trainingsanalyse konnte nicht geladen werden.'}

 try{
   let data=await getj('/msp/my-competitions?limit=30');let rows=data.competitions||[];
   if(rows.length){let c=rows[0];nextMspCompetition.innerHTML=`<strong>${c.name}</strong><br>${dateText(c.date_from)}${c.location?' · '+c.location:''}${c.country_code?' · '+c.country_code.toUpperCase():''}<br><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>`;
   mspCompetitions.innerHTML=rows.map(c=>`<div class="item"><strong>${c.name}</strong><div class="small">${dateText(c.date_from)}${c.date_to?' – '+dateText(c.date_to):''}${c.location?' · '+c.location:''}</div><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>${c.link?`<br><a class="btn secondary" style="margin-top:8px" href="${c.link}" target="_blank">Turnier öffnen</a>`:''}</div>`).join('')}
   else{nextMspCompetition.textContent='Keine bestätigte zukünftige Anmeldung gefunden.';mspCompetitions.innerHTML='<div class="small">Keine bestätigten zukünftigen Turniere.</div>'}
 }catch(e){nextMspCompetition.textContent='Anmeldungen konnten nicht geprüft werden.'}

 try{let rows=await getj('/training-sessions');manualTrainings.innerHTML=rows.length?rows.slice(0,12).map(s=>`<div class="item"><strong>${s.puzzle_name}</strong><div class="small">${s.date} · ${s.mode}${s.duration_seconds?' · '+Math.floor(s.duration_seconds/60)+':'+String(s.duration_seconds%60).padStart(2,'0'):''}</div></div>`).join(''):'<div class="small">Keine zusätzlichen manuellen Trainings.</div>'}catch(e){}
}
async function addTraining(){let b={date:sDate.value,puzzle_name:sPuzzle.value.trim(),manufacturer:sManufacturer.value||null,piece_count:sPieces.value?Number(sPieces.value):null,mode:sMode.value,duration_seconds:timeToSeconds(sDuration.value),target_seconds:timeToSeconds(sTarget.value),focus:sFocus.value||null,notes:sNotes.value||null};if(!b.date||!b.puzzle_name){alert('Datum und Puzzlename fehlen.');return}let r=await fetch('/training-sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});if(!r.ok){alert('Speichern fehlgeschlagen');return}location.reload()}
sDate.valueAsDate=new Date();loadAll();
</script></body></html>
"""

def dashboard():
    return HTMLResponse(DASHBOARD_HTML)
