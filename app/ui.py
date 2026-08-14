from fastapi.responses import HTMLResponse

DASHBOARD_HTML = r"""
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nicole Puzzle Coach</title>
<style>
:root{--bg:#f5f7fb;--card:#fff;--text:#1f2636;--muted:#70798b;--line:#e4e8ef;--accent:#ff6469;--good:#18a66a;--shadow:0 8px 28px rgba(31,38,54,.07)}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--text)}
.wrap{max-width:1220px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:22px}
h1{margin:0;font-size:30px}.sub{color:var(--muted);margin-top:5px}.badge{padding:8px 12px;border-radius:999px;font-size:13px;font-weight:800;background:#eef3ff}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:var(--shadow)}
.kpi{grid-column:span 3}.third{grid-column:span 4}.half{grid-column:span 6}.full{grid-column:span 12}
.label{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}.value{font-size:30px;font-weight:900;margin-top:7px}.small{font-size:14px;color:var(--muted)}
h2{font-size:19px;margin:0 0 14px}.list{display:grid;gap:9px}.item{padding:12px;border:1px solid var(--line);border-radius:12px;background:#fafafa}.item strong{display:block}
.pill{display:inline-block;margin:5px 5px 0 0;padding:4px 8px;border-radius:999px;background:#eef0f4;font-size:12px}
input,select,textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;color:var(--text)}
.formgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.wide{grid-column:1/-1}
button,.btn{border:0;border-radius:11px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block}.primary{background:var(--accent);color:#fff}.secondary{background:#eef0f4;color:var(--text)}
a{color:inherit}.hero{background:linear-gradient(135deg,#fff,#fff3f3)}
@media(max-width:900px){.kpi,.third,.half{grid-column:span 12}.formgrid{grid-template-columns:1fr}}
</style>
</head>
<body><div class="wrap">
<header><div><h1>🧩 Nicole Puzzle Coach</h1><div class="sub">Speed-Puzzling Training & Turniervorbereitung</div></div><div id="systemBadge" class="badge">System wird geprüft…</div></header>

<div class="grid">
<section class="card kpi"><div class="label">System</div><div class="value" id="systemKpi">–</div><div class="small" id="systemText"></div></section>
<section class="card kpi"><div class="label">MySpeedPuzzling</div><div class="value" id="mspKpi">–</div><div class="small" id="mspText"></div></section>
<section class="card kpi"><div class="label">Form</div><div class="value" id="trendKpi">–</div><div class="small">manuelle Trainings</div></section>
<section class="card kpi"><div class="label">Konsistenz</div><div class="value" id="consistencyKpi">–</div><div class="small">0–100</div></section>

<section class="card half hero"><h2>🏆 Nächstes MySpeedPuzzling-Turnier</h2><div id="nextMspCompetition" class="small">Lade Turniere…</div></section>
<section class="card half hero"><h2>🎯 Coach-Empfehlung</h2><div id="coachRecommendation" class="small">Lade Trainingsdaten…</div></section>

<section class="card full"><h2>🌍 Kommende Wettbewerbe</h2><div id="mspCompetitions" class="list"><div class="small">Lade Turniere…</div></div></section>

<section class="card half"><h2>Turnier manuell eintragen</h2><div class="formgrid">
<input id="tName" placeholder="Turniername"><input id="tDate" type="date"><input id="tLocation" placeholder="Ort">
<select id="tMode"><option value="solo">Solo</option><option value="duo">Duo</option><option value="team">Team</option></select>
<input id="tManufacturer" placeholder="Hersteller, z.B. Ravensburger"><input id="tPieces" type="number" placeholder="Teilezahl, z.B. 500">
<input id="tLimit" type="number" placeholder="Zeitlimit in Minuten"><select id="tPriority"><option value="normal">Normal</option><option value="high">Hohe Priorität</option><option value="main">Hauptziel</option></select>
<textarea id="tNotes" class="wide" placeholder="Notizen / Regeln"></textarea><button class="primary wide" onclick="addTournament()">Turnier speichern</button>
</div></section>

<section class="card half"><h2>Training erfassen</h2><div class="formgrid">
<input id="sDate" type="date"><input id="sPuzzle" placeholder="Puzzlename"><input id="sManufacturer" placeholder="Hersteller"><input id="sPieces" type="number" placeholder="Teilezahl">
<select id="sMode"><option value="solo">Solo</option><option value="duo">Duo</option><option value="team">Team</option></select><input id="sDuration" placeholder="Zeit, z.B. 42:15">
<input id="sTarget" placeholder="Zielzeit, z.B. 40:00"><input id="sFocus" placeholder="Fokus, z.B. Sortieren"><textarea id="sNotes" class="wide" placeholder="Notizen"></textarea>
<button class="primary wide" onclick="addTraining()">Training speichern</button>
</div></section>

<section class="card half"><h2>📅 Manuelle Turniere</h2><div id="tournaments" class="list"></div></section>
<section class="card half"><h2>⏱️ Letzte Trainings</h2><div id="trainings" class="list"></div></section>

<section class="card full"><h2>🧠 Tournament Intelligence</h2>
<div class="small">V5.2 lädt kommende Wettbewerbe direkt von MySpeedPuzzling. Zusätzlich gibt es einen technischen Teilnahme-Check, der prüft, ob Competition-Details Nicoles Registrierungsstatus enthalten.</div>
<div style="margin-top:12px">
<a class="btn secondary" href="/docs" target="_blank">API-Dokumentation</a>
<a class="btn secondary" href="/msp/participation-check" target="_blank">Teilnahme-Check</a>
</div></section>
</div></div>

<script>
function timeToSeconds(v){if(!v)return null;let p=v.split(':').map(Number);if(p.some(Number.isNaN))return null;if(p.length===3)return p[0]*3600+p[1]*60+p[2];if(p.length===2)return p[0]*60+p[1];return Number(v)}
async function getj(u){let r=await fetch(u),d=await r.json();if(!r.ok)throw new Error(d.detail||'Fehler');return d}
function dateText(v){if(!v)return'–';try{return new Date(v).toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit',year:'numeric'})}catch(e){return v}}
async function loadAll(){
 try{
   let st=await getj('/coach/status');
   systemKpi.textContent='OK';systemText.textContent=`Backend V${st.version} · Datenbank ok`;systemBadge.textContent='🟢 System bereit';
   mspKpi.textContent=st.has_myspeedpuzzling_data?'LIVE':(st.oauth_configured?'READY':'WAIT');
   mspText.textContent=st.has_myspeedpuzzling_data?'Daten synchronisiert':(st.oauth_configured?'Verbindung möglich':'Freigabe ausstehend');
 }catch(e){systemBadge.textContent='🔴 Fehler'}

 try{
   let summary=await getj('/coach/manual-summary');
   trendKpi.textContent=summary.trend_percent==null?'–':`${summary.trend_percent>0?'+':''}${summary.trend_percent}%`;
   consistencyKpi.textContent=summary.consistency_score==null?'–':summary.consistency_score;
   coachRecommendation.innerHTML=`<strong>${summary.recommendation}</strong>`;
 }catch(e){}

 try{
   let data=await getj('/msp/competitions/upcoming?limit=12');
   let rows=data.competitions||[];
   if(rows.length){
      let c=rows[0];
      nextMspCompetition.innerHTML=`<strong>${c.name||'Turnier'}</strong><br>${dateText(c.date_from)}${c.location?' · '+c.location:''}${c.country_code?' · '+String(c.country_code).toUpperCase():''}<br>${c.registration_link?`<a class="btn secondary" style="margin-top:10px" href="${c.registration_link}" target="_blank">Anmeldung</a>`:''}`;
      mspCompetitions.innerHTML=rows.map(c=>`<div class="item"><strong>${c.name||'Turnier'}</strong><div class="small">${dateText(c.date_from)}${c.location?' · '+c.location:''}${c.country_code?' · '+String(c.country_code).toUpperCase():''}</div>${c.is_online?'<span class="pill">Online</span>':'<span class="pill">Vor Ort</span>'}${c.status?`<span class="pill">${c.status}</span>`:''}${c.registration_link?`<br><a class="btn secondary" style="margin-top:8px" href="${c.registration_link}" target="_blank">Anmeldung</a>`:''}${c.results_link?` <a class="btn secondary" style="margin-top:8px" href="${c.results_link}" target="_blank">Resultate</a>`:''}</div>`).join('');
   } else {
      nextMspCompetition.textContent='Keine kommenden Wettbewerbe gefunden.';
      mspCompetitions.innerHTML='<div class="small">Keine kommenden Wettbewerbe gefunden.</div>';
   }
 }catch(e){
   nextMspCompetition.textContent='Turniere konnten nicht geladen werden.';
   mspCompetitions.innerHTML='<div class="small">Turniere konnten nicht geladen werden.</div>';
 }

 try{renderTournaments(await getj('/tournaments'))}catch(e){}
 try{renderTrainings(await getj('/training-sessions'))}catch(e){}
}
function renderTournaments(rows){tournaments.innerHTML=rows.length?rows.map(t=>`<div class="item"><strong>${t.name}</strong><div class="small">${t.date}${t.location?' · '+t.location:''}</div></div>`).join(''):'<div class="small">Noch keine manuellen Turniere.</div>'}
function renderTrainings(rows){trainings.innerHTML=rows.length?rows.slice(0,8).map(s=>`<div class="item"><strong>${s.puzzle_name}</strong><div class="small">${s.date} · ${s.mode}</div></div>`).join(''):'<div class="small">Noch keine Trainings.</div>'}
async function addTournament(){let b={name:tName.value.trim(),date:tDate.value,location:tLocation.value||null,mode:tMode.value,manufacturer:tManufacturer.value||null,piece_count:tPieces.value?Number(tPieces.value):null,time_limit_minutes:tLimit.value?Number(tLimit.value):null,priority:tPriority.value,international:true,notes:tNotes.value||null};if(!b.name||!b.date){alert('Turniername und Datum fehlen.');return}let r=await fetch('/tournaments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});if(!r.ok){alert('Speichern fehlgeschlagen');return}location.reload()}
async function addTraining(){let b={date:sDate.value,puzzle_name:sPuzzle.value.trim(),manufacturer:sManufacturer.value||null,piece_count:sPieces.value?Number(sPieces.value):null,mode:sMode.value,duration_seconds:timeToSeconds(sDuration.value),target_seconds:timeToSeconds(sTarget.value),focus:sFocus.value||null,notes:sNotes.value||null};if(!b.date||!b.puzzle_name){alert('Datum und Puzzlename fehlen.');return}let r=await fetch('/training-sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});if(!r.ok){alert('Speichern fehlgeschlagen');return}location.reload()}
tDate.valueAsDate=new Date();sDate.valueAsDate=new Date();loadAll();
</script></body></html>
"""

def dashboard():
    return HTMLResponse(DASHBOARD_HTML)
