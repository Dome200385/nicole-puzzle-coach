from fastapi.responses import HTMLResponse

DASHBOARD_HTML = r"""
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nicole Puzzle Coach</title>
<style>
:root{
  --bg:#f6f7fb; --card:#ffffff; --text:#202637; --muted:#6b7280;
  --line:#e5e7eb; --accent:#ff6469; --good:#18a66a; --warn:#d99018;
  --shadow:0 8px 30px rgba(28,35,55,.07);
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--text)}
.wrap{max-width:1200px;margin:auto;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:24px}
h1{margin:0;font-size:30px}.sub{color:var(--muted);margin-top:5px}
.badge{padding:8px 12px;border-radius:999px;font-size:13px;font-weight:700;background:#eef2ff}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:var(--shadow)}
.kpi{grid-column:span 3}.half{grid-column:span 6}.full{grid-column:span 12}
.label{font-size:13px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.value{font-size:28px;font-weight:800;margin-top:8px}.small{font-size:14px;color:var(--muted)}
h2{font-size:19px;margin:0 0 14px}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
button,.btn{border:0;border-radius:11px;padding:10px 14px;font-weight:750;cursor:pointer;text-decoration:none;display:inline-block}
.primary{background:var(--accent);color:#fff}.secondary{background:#eef0f4;color:var(--text)}
input,select,textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;color:var(--text)}
.formgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.formgrid .wide{grid-column:1/-1}
.list{display:grid;gap:9px}.item{padding:12px;border:1px solid var(--line);border-radius:12px;background:#fafafa}
.item strong{display:block}.pill{display:inline-block;margin:5px 5px 0 0;padding:4px 8px;border-radius:999px;background:#eee;font-size:12px}
.good{color:var(--good)}.warn{color:var(--warn)}.muted{color:var(--muted)}
.hero{background:linear-gradient(135deg,#fff,#fff1f2)}
.score{font-size:44px;font-weight:900}
@media(max-width:850px){.kpi,.half{grid-column:span 12}.formgrid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <h1>🧩 Nicole Puzzle Coach</h1>
    <div class="sub">Persönliches Speed-Puzzling Training & Turniervorbereitung</div>
  </div>
  <div id="systemBadge" class="badge">System wird geprüft…</div>
</header>

<div class="grid">
  <section class="card kpi"><div class="label">System</div><div class="value" id="systemKpi">–</div><div class="small" id="systemText">Lade…</div></section>
  <section class="card kpi"><div class="label">MySpeedPuzzling</div><div class="value" id="mspKpi">–</div><div class="small" id="mspText">Lade…</div></section>
  <section class="card kpi"><div class="label">Turniere</div><div class="value" id="tournamentCount">0</div><div class="small">geplant</div></section>
  <section class="card kpi"><div class="label">Trainings</div><div class="value" id="trainingCount">0</div><div class="small">erfasst</div></section>

  <section class="card half hero">
    <h2>🏆 Nächstes Turnier</h2>
    <div id="nextTournament" class="muted">Noch kein Turnier eingetragen.</div>
    <div id="readinessBox" style="margin-top:14px"></div>
  </section>

  <section class="card half hero">
    <h2>🎯 Nächstes Puzzle</h2>
    <div id="nextPuzzle" class="muted">Wird verfügbar, sobald MySpeedPuzzling-Daten synchronisiert sind.</div>
  </section>

  <section class="card half">
    <h2>Turnier eintragen</h2>
    <div class="formgrid">
      <input id="tName" placeholder="Turniername">
      <input id="tDate" type="date">
      <input id="tLocation" placeholder="Ort">
      <select id="tMode"><option value="solo">Solo</option><option value="duo">Duo</option><option value="team">Team</option></select>
      <input id="tManufacturer" placeholder="Hersteller, z.B. Ravensburger">
      <input id="tPieces" type="number" placeholder="Teilezahl, z.B. 500">
      <input id="tLimit" type="number" placeholder="Zeitlimit in Minuten">
      <select id="tPriority"><option value="normal">Normal</option><option value="high">Hohe Priorität</option><option value="main">Hauptziel</option></select>
      <textarea id="tNotes" class="wide" placeholder="Notizen / Regeln"></textarea>
      <button class="primary wide" onclick="addTournament()">Turnier speichern</button>
    </div>
  </section>

  <section class="card half">
    <h2>Training erfassen</h2>
    <div class="formgrid">
      <input id="sDate" type="date">
      <input id="sPuzzle" placeholder="Puzzlename">
      <input id="sManufacturer" placeholder="Hersteller">
      <input id="sPieces" type="number" placeholder="Teilezahl">
      <select id="sMode"><option value="solo">Solo</option><option value="duo">Duo</option><option value="team">Team</option></select>
      <input id="sDuration" type="text" placeholder="Zeit, z.B. 42:15">
      <input id="sTarget" type="text" placeholder="Zielzeit, z.B. 40:00">
      <input id="sFocus" placeholder="Fokus, z.B. Sortieren">
      <textarea id="sNotes" class="wide" placeholder="Notizen"></textarea>
      <button class="primary wide" onclick="addTraining()">Training speichern</button>
    </div>
  </section>

  <section class="card half"><h2>📅 Geplante Turniere</h2><div id="tournaments" class="list"></div></section>
  <section class="card half"><h2>⏱️ Letzte Trainings</h2><div id="trainings" class="list"></div></section>

  <section class="card full">
    <h2>🧠 Tournament Intelligence</h2>
    <div class="small">Diese Ebene wird nach dem MySpeedPuzzling-Sync und der Turnierdaten-Pipeline aktiviert: Ravensburger-Historie, Neuheiten, internationale Wettbewerbe und später Community-Signale mit Backtesting.</div>
    <div class="row" style="margin-top:12px">
      <a class="btn secondary" href="/docs" target="_blank">API-Dokumentation</a>
      <a id="oauthBtn" class="btn secondary" href="/auth/myspeedpuzzling/login">MySpeedPuzzling verbinden</a>
    </div>
  </section>
</div>
</div>

<script>
function timeToSeconds(v){
  if(!v) return null;
  let p=v.split(':').map(Number);
  if(p.some(Number.isNaN)) return null;
  if(p.length===3) return p[0]*3600+p[1]*60+p[2];
  if(p.length===2) return p[0]*60+p[1];
  return Number(v);
}
function fmtSeconds(s){
  if(s==null) return "–";
  const h=Math.floor(s/3600), m=Math.floor((s%3600)/60), sec=s%60;
  return h ? `${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}` : `${m}:${String(sec).padStart(2,'0')}`;
}
async function jget(url){
  const r=await fetch(url); const data=await r.json();
  if(!r.ok) throw new Error(data.detail||'Fehler');
  return data;
}
async function loadAll(){
  try{
    const st=await jget('/coach/status');
    document.getElementById('systemKpi').textContent=st.database==='ok'?'OK':'!';
    document.getElementById('systemText').textContent=`Backend V${st.version} · Datenbank ${st.database}`;
    document.getElementById('systemBadge').textContent=st.database==='ok'?'🟢 System bereit':'🟠 Prüfen';
    document.getElementById('mspKpi').textContent=st.has_myspeedpuzzling_data?'LIVE':(st.oauth_configured?'READY':'WAIT');
    document.getElementById('mspText').textContent=st.has_myspeedpuzzling_data?'Daten synchronisiert':(st.oauth_configured?'Verbindung möglich':'Freigabe ausstehend');
    if(!st.oauth_configured) document.getElementById('oauthBtn').style.opacity=.45;
  }catch(e){ document.getElementById('systemBadge').textContent='🔴 Fehler'; }

  let tournaments=[];
  try{ tournaments=await jget('/tournaments'); }catch(e){}
  document.getElementById('tournamentCount').textContent=tournaments.length;
  renderTournaments(tournaments);

  let trainings=[];
  try{ trainings=await jget('/training-sessions'); }catch(e){}
  document.getElementById('trainingCount').textContent=trainings.length;
  renderTrainings(trainings);

  const upcoming=tournaments.filter(t=>new Date(t.date)>=new Date(new Date().toDateString())).sort((a,b)=>new Date(a.date)-new Date(b.date));
  if(upcoming.length){
    const t=upcoming[0];
    document.getElementById('nextTournament').innerHTML=`<strong>${t.name}</strong><br>${t.date}${t.location?' · '+t.location:''}<br><span class="pill">${t.mode}</span>${t.manufacturer?`<span class="pill">${t.manufacturer}</span>`:''}${t.piece_count?`<span class="pill">${t.piece_count} Teile</span>`:''}`;
    try{
      const r=await jget('/coach/readiness/'+t.id);
      document.getElementById('readinessBox').innerHTML=`<div class="label">Readiness</div><div class="score">${r.readiness.score}</div><div>${r.readiness.label}</div>`;
    }catch(e){}
    try{
      const p=await jget('/coach/next-puzzle?tournament_id='+t.id);
      if(p.status==='ok'){
        document.getElementById('nextPuzzle').innerHTML=`<strong>${p.puzzle_name}</strong><br>${p.manufacturer||''} ${p.piece_count?`· ${p.piece_count} Teile`:''}<br><span class="pill">Trainingswert ${p.training_score}/100</span>${p.target_seconds?`<span class="pill">Ziel ${fmtSeconds(p.target_seconds)}</span>`:''}<p class="small">${p.reason}</p>`;
      }
    }catch(e){}
  }
}
function renderTournaments(rows){
  const el=document.getElementById('tournaments');
  if(!rows.length){el.innerHTML='<div class="muted">Noch keine Turniere.</div>';return;}
  el.innerHTML=rows.map(t=>`<div class="item"><strong>${t.name}</strong><div class="small">${t.date}${t.location?' · '+t.location:''}</div><span class="pill">${t.mode}</span>${t.manufacturer?`<span class="pill">${t.manufacturer}</span>`:''}${t.piece_count?`<span class="pill">${t.piece_count} Teile</span>`:''}</div>`).join('');
}
function renderTrainings(rows){
  const el=document.getElementById('trainings');
  if(!rows.length){el.innerHTML='<div class="muted">Noch keine Trainings erfasst.</div>';return;}
  el.innerHTML=rows.slice(0,8).map(s=>`<div class="item"><strong>${s.puzzle_name}</strong><div class="small">${s.date} · ${s.mode}${s.duration_seconds?' · '+fmtSeconds(s.duration_seconds):''}</div>${s.focus?`<span class="pill">${s.focus}</span>`:''}</div>`).join('');
}
async function addTournament(){
  const body={
    name:tName.value.trim(), date:tDate.value, location:tLocation.value||null, mode:tMode.value,
    manufacturer:tManufacturer.value||null, piece_count:tPieces.value?Number(tPieces.value):null,
    time_limit_minutes:tLimit.value?Number(tLimit.value):null, priority:tPriority.value,
    international:true, notes:tNotes.value||null
  };
  if(!body.name||!body.date){alert('Turniername und Datum fehlen.');return;}
  const r=await fetch('/tournaments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok){alert('Speichern fehlgeschlagen');return;} location.reload();
}
async function addTraining(){
  const body={
    date:sDate.value, puzzle_name:sPuzzle.value.trim(), manufacturer:sManufacturer.value||null,
    piece_count:sPieces.value?Number(sPieces.value):null, mode:sMode.value,
    duration_seconds:timeToSeconds(sDuration.value), target_seconds:timeToSeconds(sTarget.value),
    focus:sFocus.value||null, notes:sNotes.value||null
  };
  if(!body.date||!body.puzzle_name){alert('Datum und Puzzlename fehlen.');return;}
  const r=await fetch('/training-sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok){alert('Speichern fehlgeschlagen');return;} location.reload();
}
document.getElementById('tDate').valueAsDate=new Date();
document.getElementById('sDate').valueAsDate=new Date();
loadAll();
</script>
</body>
</html>
"""

def dashboard():
    return HTMLResponse(DASHBOARD_HTML)
