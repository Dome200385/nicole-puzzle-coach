from fastapi.responses import HTMLResponse

DASHBOARD_HTML = r"""
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f5f7fb">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Puzzle Coach">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="/pwa/icon-192.png">
<link rel="apple-touch-icon" href="/pwa/icon-192.png">
<title>Nicole Puzzle Coach</title>
<style>
:root{--bg:#f5f7fb;--card:#fff;--text:#1f2636;--muted:#70798b;--line:#e4e8ef;--accent:#ff6469;--shadow:0 8px 28px rgba(31,38,54,.07)}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--text)}
.wrap{max-width:1220px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:22px}
h1{margin:0;font-size:30px}.sub,.small{color:var(--muted)}.badge{padding:8px 12px;border-radius:999px;font-size:13px;font-weight:800;background:#eef3ff}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:var(--shadow)}
.kpi{grid-column:span 3}.third{grid-column:span 4}.half{grid-column:span 6}.full{grid-column:span 12}
.label{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}.value{font-size:30px;font-weight:900;margin-top:7px}
h2{font-size:19px;margin:0 0 14px}.list{display:grid;gap:9px}.item{padding:12px;border:1px solid var(--line);border-radius:12px;background:#fafafa}.item strong{display:block}.puzzleRow{display:flex;gap:14px;align-items:flex-start}.puzzleImg{width:115px;height:90px;object-fit:contain;background:#fff;border:1px solid var(--line);border-radius:10px;flex:0 0 auto}.puzzleInfo{min-width:0;flex:1}.riskHigh{background:#fff0f0}.wmGood{background:#eef9f1}.activeTraining{border:2px solid #7a89ff}.wmFit{font-weight:800;background:#eef3ff}.fitReason{margin-top:5px;font-size:12px;color:var(--muted)}.skipBtn{background:#fff;border:1px solid #ff8d8d;color:#b52f36;padding:7px 10px;border-radius:9px;font-weight:700}.loanBox{background:#fff7e8}.rankMe{border:2px solid #66c98d}.rankRow{display:grid;grid-template-columns:48px 1fr auto;gap:10px;align-items:center}.rankNum{font-size:18px;font-weight:900}.rankTime{text-align:right;font-weight:800}.progressBars{display:flex;align-items:flex-end;gap:7px;height:170px;padding:14px 8px 4px;border-bottom:1px solid var(--line)}.pbar{flex:1;min-width:18px;text-align:center}.pbarFill{background:#cfd8f7;border-radius:7px 7px 2px 2px;min-height:8px}.pbarTime{font-size:10px;font-weight:800;margin-top:5px}.pbarDate{font-size:9px;color:var(--muted)}.progressLegend{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.simHero{background:linear-gradient(135deg,#f8fbff,#fff6f5)}.simGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.simMetric{padding:12px;border:1px solid var(--line);border-radius:12px;background:#fff}.historyRow{display:grid;grid-template-columns:70px 1fr auto auto;gap:10px;align-items:center}.scoreGood{background:#edf9f1}.scoreMid{background:#fff7e5}.scoreBad{background:#fff0f0}.progressTargets{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px}.targetCard{padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff}.targetCard b{font-size:18px}
.pill{display:inline-block;margin:5px 5px 0 0;padding:4px 8px;border-radius:999px;background:#eef0f4;font-size:12px}
input,select,textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;color:var(--text)}
.formgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.wide{grid-column:1/-1}
button,.btn{border:0;border-radius:11px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block}.primary{background:var(--accent);color:#fff}.secondary{background:#eef0f4;color:var(--text)}
.hero{background:linear-gradient(135deg,#fff,#fff3f3)}.metricrow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.metric{background:#fafafa;border:1px solid var(--line);padding:12px;border-radius:12px}.metric b{font-size:20px}
.infoBtn{border:1px solid var(--line);background:#eef3ff;color:var(--text);width:20px;height:20px;padding:0;border-radius:50%;font-size:12px;line-height:18px;margin-left:4px}
.modal{display:none;position:fixed;inset:0;background:rgba(20,25,35,.45);z-index:99;align-items:center;justify-content:center;padding:20px}.modal.open{display:flex}.modalbox{max-width:620px;width:100%;background:#fff;border-radius:18px;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.2)}.modalbox h2{margin-bottom:10px}.modalbox p{line-height:1.5}.scale{display:grid;gap:7px;margin:14px 0}.scale div{padding:9px;border-radius:9px;background:#f5f7fb}
@media(max-width:900px){.kpi,.third,.half{grid-column:span 12}.formgrid,.metricrow,.simGrid,.progressTargets{grid-template-columns:1fr}.historyRow{grid-template-columns:50px 1fr auto}}
.goalSplit{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:4px 0}.goalSplit b{font-size:18px}
.headerRight{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}.techStatus{font-size:10px;color:#788295;background:#eef2f7;border-radius:999px;padding:5px 8px}.techStatus strong{font-size:10px;color:#344054}.compactRefresh{font-size:10px!important;padding:5px 8px!important}.grid>.kpi.third{grid-column:span 4}.readinessInfo{background:#f8fafc;border:1px solid #dbe4ef;border-radius:12px;padding:11px;margin:10px 0}.readinessInfo summary{cursor:pointer;font-weight:800}.readinessFormula{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}.readinessFormula .part{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:7px}@media(max-width:900px){.readinessFormula{grid-template-columns:1fr}.headerRight{justify-content:flex-start}.techStatus{white-space:normal}}

@keyframes npcSpin{to{transform:rotate(360deg)}}
#mspRefreshBtn.syncing::before{content:"";display:inline-block;width:11px;height:11px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;margin-right:6px;vertical-align:-2px;animation:npcSpin .75s linear infinite}
#mspRefreshBtn.syncing{cursor:wait;opacity:.85}
.syncStatusText{font-size:10px;color:var(--muted);min-width:110px}
@media(prefers-reduced-motion:reduce){#mspRefreshBtn.syncing::before{animation:none;border-right-color:currentColor}}

.mobileOnly{display:none}
.appBottomNav{display:none}
@media(max-width:760px){
  body{padding-bottom:84px}
  .wrap{padding:10px 10px 20px}
  header{align-items:flex-start;gap:8px}
  header h1{font-size:22px}
  header .sub{font-size:11px}
  .headerRight{gap:4px}
  .techStatus{display:none}
  #systemBadge{font-size:9px;padding:4px 7px}
  #mspRefreshBtn{font-size:9px!important;padding:5px 7px!important}
  .syncStatusText{display:none}
  .grid{gap:9px}
  .grid>.kpi.third{grid-column:span 4}
  .kpi{min-height:88px;padding:12px}
  .kpi .value{font-size:25px}
  .kpi .small{font-size:10px}
  .card{padding:12px;border-radius:14px}
  .card h2{font-size:15px}
  .mobileOnly{display:block}
  .todayCard{background:#fff}
  .todayGrid{display:grid;grid-template-columns:1fr;gap:8px}
  .todayGrid>div{border:1px solid var(--border);border-radius:10px;padding:9px}
  .todayGrid strong{font-size:14px}
  .appBottomNav{
    display:grid;grid-template-columns:repeat(5,1fr);
    position:fixed;left:0;right:0;bottom:0;z-index:50;
    background:rgba(255,255,255,.96);backdrop-filter:blur(12px);
    border-top:1px solid #dfe4ec;
    padding:6px max(6px,env(safe-area-inset-right)) calc(6px + env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left));
  }
  .appBottomNav button{
    border:0;background:transparent;color:#475569;
    min-height:48px;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:1px;border-radius:10px;font-size:17px
  }
  .appBottomNav button small{font-size:9px}
  .appBottomNav button.active{background:#eef2f7;color:#0f172a;font-weight:800;box-shadow:inset 0 0 0 1px #d9e0e8}
  .metricrow{grid-template-columns:1fr}
  .metric{min-width:0}
  .puzzleRow{align-items:flex-start}
  .puzzleImg{width:72px;height:72px}
}
@media(display-mode:standalone){
  header{padding-top:max(4px,env(safe-area-inset-top))}
}

@media(max-width:760px){
  header{
    display:grid;
    grid-template-columns:1fr auto;
    align-items:start;
    column-gap:8px;
    row-gap:3px;
    padding-bottom:2px;
  }
  header>div:first-child{min-width:0}
  header h1{font-size:20px;line-height:1.05;margin-bottom:2px}
  header .sub{font-size:10px;line-height:1.2;max-width:220px}
  .headerRight{align-items:flex-end;justify-content:flex-start;flex-direction:column;gap:4px}
  #systemBadge{font-size:8px;padding:3px 6px;white-space:nowrap}
  #mspRefreshBtn{font-size:8px!important;padding:4px 6px!important;white-space:nowrap}
  .grid>.kpi.third{grid-column:span 6}
  .grid>.kpi.third:nth-of-type(2){
    grid-column:1/-1;
    order:-1;
  }
  .grid>.kpi.third:nth-of-type(2) .value{font-size:34px}
  .grid>.kpi.third:nth-of-type(2){min-height:100px}
  .grid>.kpi.third:nth-of-type(1),
  .grid>.kpi.third:nth-of-type(3){min-height:92px}
  .kpi .label{font-size:11px;line-height:1.1}
  .kpi .value{font-size:28px}
  .kpi .small{font-size:9px;line-height:1.25}
  .todayHero{display:grid;grid-template-columns:74px 1fr;gap:10px;align-items:center;margin-top:6px}
  .todayPuzzleImage{width:74px;height:74px;border-radius:10px;background:#f1f5f9;overflow:hidden;display:flex;align-items:center;justify-content:center}
  .todayPuzzleImage img{width:100%;height:100%;object-fit:cover}
  .todayHeroText{min-width:0}
  .todayHeroText strong{display:block;font-size:17px;line-height:1.15}
  .todayGrid{grid-template-columns:1fr 1fr!important;margin-top:10px}
  .todayAction{width:100%;margin-top:10px;min-height:44px}
}

@media(max-width:760px){
  .grid>section[data-app-page]{display:none}
  .grid>section[data-app-page].appPageActive{display:block}
  .grid>section.card[data-app-page].appPageActive{grid-column:1/-1}
  .grid>section.card.kpi[data-app-page="today"].appPageActive:nth-of-type(1),
  .grid>section.card.kpi[data-app-page="today"].appPageActive:nth-of-type(3){grid-column:span 6}
  .grid>section.card.kpi[data-app-page="today"].appPageActive:nth-of-type(2){grid-column:1/-1}
  .appPageHeading{display:block;grid-column:1/-1;margin:3px 2px 0;font-size:11px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:.08em}
}
@media(min-width:761px){.appPageHeading{display:none}}
@media(max-width:760px){
#appTraining{padding:12px}#appTraining>h2{font-size:18px;margin-bottom:8px}
.trainingQuick{display:block;background:#fff;border:1px solid var(--border);border-radius:14px;padding:12px;margin:8px 0 10px}
.trainingQuickHero{display:grid;grid-template-columns:76px 1fr;gap:11px;align-items:center}
.trainingQuickImage{width:76px;height:76px;border-radius:11px;overflow:hidden;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-size:28px}
.trainingQuickImage img{width:100%;height:100%;object-fit:cover}.trainingQuickMain{min-width:0}.trainingQuickMain strong{display:block;font-size:18px;line-height:1.15}
.trainingQuickStats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.trainingQuickStats>div{border:1px solid var(--border);border-radius:10px;padding:9px}
.trainingQuickStats span{display:block}.trainingQuickStats strong{display:block;font-size:16px;margin-top:2px}.trainingPriorityGroup>.item{margin-top:9px!important}
#appTraining>.metricrow{grid-template-columns:1fr 1fr;gap:8px}#appTraining>.metricrow .metric{padding:10px}#appTraining>.metricrow .metric .label{font-size:10px}
#appTraining>.metricrow .metric b{font-size:18px}#appTraining>.metricrow .metric .small{font-size:9px;line-height:1.25}#appTraining>.metricrow .metric:nth-child(3){grid-column:1/-1}
#readinessInfoBox{margin-top:10px}#readinessInfoBox summary{font-size:12px}#wmSimulationCard h2{font-size:15px}}
@media(max-width:760px){
.trainingDuplicatePuzzle{display:none!important}
.trainingQuickFacts{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:8px}
.trainingQuickFacts>div{background:#f8fafc;border-radius:9px;padding:8px 9px}
.trainingQuickFacts span{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
.trainingQuickFacts strong{display:block;font-size:15px;margin-top:2px}
.trainingQuickReason{font-size:11px;line-height:1.35;color:var(--muted);margin-top:8px}
.trainingPriorityGroup>.item:first-of-type+ .item{margin-top:8px!important}
}</style></head>
<body><div class="wrap">
<header><div><h1>🧩 Nicole Puzzle Coach</h1><div class="sub">Speed-Puzzling Training & Turniervorbereitung</div></div><div class="headerRight"><span class="techStatus"><strong id="systemKpi">–</strong> <span id="systemText">System</span> · <strong id="mspKpi">–</strong> <span id="mspText">MySpeedPuzzling</span></span><div id="systemBadge" class="badge">System wird geprüft…</div><button id="mspRefreshBtn" class="secondary compactRefresh" onclick="refreshFromMSP()">↻ MySpeedPuzzling aktualisieren</button><span id="syncStatusText" class="syncStatusText" aria-live="polite"></span></div></header>

<div class="grid"><div id="appPageHeading" class="appPageHeading">Heute</div>
<section class="card kpi third" data-app-page="today"><div class="label">Form · vs MSP-Median <button class="infoBtn" onclick="showInfo('form')">i</button></div><div class="value" id="trendKpi">–</div><div class="small">letzter Solo-Versuch je vergleichbarem 500er</div></section>
<section class="card kpi third" data-app-page="today"><div class="label">WM-Readiness <button class="infoBtn" onclick="document.getElementById('readinessInfoBox').open=true;document.getElementById('readinessInfoBox').scrollIntoView({behavior:'smooth',block:'center'})">i</button></div><div class="value" id="readinessTopKpi">–</div><div class="small">50 = MSP-Median-Niveau · 60+ = solide WM-Form</div></section>
<section class="card kpi third" data-app-page="today"><div class="label">Konsistenz <button class="infoBtn" onclick="showInfo('consistency')">i</button></div><div class="value" id="consistencyKpi">–</div><div class="small">median-relative Stabilität · 0–100</div></section>

<section id="resilientBanner" class="card full" data-app-page="today" style="display:none;background:#fff8e6;border-color:#f0d99b">
  <strong>🛡️ Resilient Mode</strong>
  <div id="resilientText" class="small" style="margin-top:4px"></div>
</section>

<section id="mobileTodayCard" class="card full mobileOnly todayCard" data-app-page="today">
<h2>✨ Heute</h2>
<div class="todayHero">
<div id="todayPuzzleImage" class="todayPuzzleImage"></div>
<div class="todayHeroText">
<div class="label">Nächstes Puzzle</div>
<strong id="todayPuzzle">Wird geladen…</strong>
<div class="small" id="todayPuzzleMeta"></div>
</div>
</div>
<div class="todayGrid">
<div><div class="label">Training</div><strong id="todayTraining">Wird geladen…</strong></div>
<div><div class="label">Readiness</div><strong id="todayReadiness">–</strong></div>
</div>
<button type="button" class="primary todayAction" id="todayTrainingBtn">Training ansehen</button>
</section>
<section class="card half hero appSection" id="appToday" data-app-page="today"><h2>🏆 Mein nächstes Turnier</h2><div id="nextMspCompetition" class="small">Prüfe bestätigte Anmeldung…</div></section>
<section class="card half hero" data-app-page="today"><h2>🎯 Coach-Empfehlung</h2><div id="coachRecommendation" class="small">Analysiere MySpeedPuzzling-Ergebnisse…</div></section>

<section class="card full" data-app-page="today"><h2>✅ Meine bestätigten Turniere</h2><div id="mspCompetitions" class="list"></div></section>

<section class="card full hero appSection" id="appTraining" data-app-page="training"><h2>🏁 WM Coach · Adaptive Preparation</h2><div class="mobileOnly trainingQuick">
<div class="trainingQuickHero"><div id="trainingQuickImage" class="trainingQuickImage">🧩</div><div class="trainingQuickMain"><div class="label">Heute trainieren</div><strong id="trainingQuickPuzzle">Wird geladen…</strong><div id="trainingQuickMeta" class="small"></div></div></div>
<div class="trainingQuickStats"><div><span class="label">Training</span><strong id="trainingQuickType">–</strong></div><div><span class="label">Ziel</span><strong id="trainingQuickTarget">–</strong></div></div>
<div class="trainingQuickFacts">
  <div><span>MSP-Median</span><strong id="trainingQuickMedian">–</strong></div>
  <div><span>Letzte Zeit</span><strong id="trainingQuickLast">–</strong></div>
  <div><span>vs. Median</span><strong id="trainingQuickDelta">–</strong></div>
  <div><span>WM-Fit</span><strong id="trainingQuickFit">–</strong></div>
</div>
<div id="trainingQuickReason" class="trainingQuickReason"></div>
</div><div class="trainingPriorityGroup"><div class="item trainingDuplicatePuzzle" style="margin-top:12px"><strong>🧩 Nächstes empfohlenes Puzzle</strong><div id="wmNextPuzzle" class="small">Bibliothek wird ausgewertet…</div></div>
<div class="item" style="margin-top:10px"><strong>📅 Plan für die aktuelle Trainingswoche</strong><div id="wmWeeklyPlan" class="list" style="margin-top:8px"></div></div>
<div class="item simHero" id="wmSimulationCard" style="margin-top:10px"><h2>🏁 WM-Simulation <span class="pill">V6.9.6</span></h2>
<div class="small">Eigenständige WM-Simulation mit einem <strong>anderen Puzzle als im normalen Wochenplan</strong>. Ausgeliehene Puzzles bleiben ausgeschlossen.</div>
<div id="wmSimSuggestion" class="item" style="margin-top:10px">Simulations-Puzzle wird gewählt…</div>
<div id="wmSimActive" class="item activeTraining" style="display:none;margin-top:10px">
  <strong>▶️ Laufende WM-Simulation</strong>
  <div class="puzzleRow" style="margin-top:8px">
    <div id="wmSimImage"></div>
    <div class="puzzleInfo">
      <strong id="wmSimName"></strong>
      <div id="wmSimGoals" class="small"></div>
      <div id="wmSimResult" class="small" style="margin-top:6px"></div>
      <button class="primary" style="margin-top:8px" onclick="checkWMSimulation()">Ergebnis synchronisieren & auswerten</button>
      <button class="secondary" style="margin-top:8px" onclick="cancelWMSimulation()">Abbrechen</button>
    </div>
  </div>
</div>
<div class="item" style="margin-top:10px">
  <strong>📚 Simulationshistorie</strong>
  <div id="wmSimSummary" class="small" style="margin-top:5px"></div>
  <div id="wmSimHistory" class="list" style="margin-top:8px"></div>
</div>
</div>
</div>

<div class="metricrow">
<div class="metric"><div class="label">WM-Readiness · Detail</div><b id="wmReadiness">–</b><div class="small" id="wmPhase">–</div></div>
<div class="metric"><div class="label">Realistisches Puzzle-Ziel</div>
<div class="goalSplit"><span class="small">First Try</span><b id="wmGoalFirstTry">–</b></div>
<div class="goalSplit"><span class="small">bekannt / mehrfach gemacht</span><b id="wmGoalRepeat">–</b></div>
<div class="small">First Try wird bewusst langsamer bewertet, da Bild, Sortierung und Suchmuster noch unbekannt sind.</div></div>
<div class="metric"><div class="label">Stretch Goal</div><b id="wmStretch">–</b><div class="small">ambitionierter Best-Case-Tag</div></div>
</div>
<div class="metricrow" style="margin-top:10px">
<div class="metric"><div class="label">Aktuelle 500er-Zone</div><b id="wmZone">–</b><div class="small">zentrale Zone der letzten 10</div></div>
<div class="metric"><div class="label">Trainings-Zielzeit</div><b id="wmTarget">–</b><div class="small" id="wmTrend">–</div></div>
<div class="metric"><div class="label">Nächster Trainingstyp</div><b id="wmTrainingType">–</b><div class="small" id="wmTrainingReason">–</div></div>
</div>
<details class="readinessInfo" id="readinessInfoBox"><summary>ℹ️ WM-Readiness: Definition & Berechnungsnachweis</summary>
<div class="small" style="margin-top:7px"><strong>Skala:</strong> 50/100 = ungefähr MSP-Median-Niveau. 100/100 = außergewöhnlich starke, stabile und aktuelle WM-Form über mehrere unterschiedliche 500er. Schwierige Puzzle werden fair bewertet, weil nicht die Rohzeit zählt, sondern Nicoles letzter Versuch relativ zum MSP-Median genau dieses Puzzles. Trainingsbelastung hat keinen Einfluss auf diesen Wert.</div>
<div class="readinessFormula">
<div class="part"><strong>Basis</strong><div id="readinessBaseInfo" class="small">–</div></div>
<div class="part"><strong>Konsistenz</strong><div id="readinessConsistencyInfo" class="small">–</div></div>
<div class="part"><strong>Median-Treffer</strong><div id="readinessHitInfo" class="small">–</div></div>
<div class="part"><strong>Aktualität</strong><div id="readinessRecencyInfo" class="small">–</div></div>
<div class="part"><strong>Verbesserung</strong><div id="readinessImprovementInfo" class="small">–</div></div>
<div class="part"><strong>Datenbasis</strong><div id="readinessSampleInfo" class="small">–</div></div>
</div><div id="readinessMethodText" class="small" style="margin-top:8px">–</div>
<div id="readinessZoneBox" class="item" style="margin-top:8px;background:#f8fafc">
<strong id="readinessZoneTitle">Readiness-Zone</strong>
<div id="readinessZoneText" class="small" style="margin-top:3px">–</div>
<div class="small" style="margin-top:5px">Orientierung: 50 = MSP-Median-Niveau · 60 = solide WM-Form · 70 = starke WM-Form · 80 = sehr starke WM-Form · 90+ = außergewöhnliche WM-Form.</div>
</div>
<div class="parts" style="margin-top:8px">
<div class="part"><strong>Ø letzte 10 vs. Median</strong><div id="readinessRawFormInfo" class="small">–</div></div>
<div class="part"><strong>Aktualitätsgewichteter Ø</strong><div id="readinessWeightedFormInfo" class="small">–</div></div>
<div class="part"><strong>Readiness-Formsignal</strong><div id="readinessBlendedFormInfo" class="small">–</div></div>
</div>
<div style="margin-top:9px"><strong>Kontrolle der letzten vergleichbaren 500er</strong><div id="readinessMedianAudit" class="small" style="margin-top:5px">–</div></div></details><div id="readinessTrendPanel" class="item" style="margin-top:10px">
<strong>📈 WM-Readiness-Verlauf</strong>
<div class="small">Tägliche Entwicklung der Readiness bis zur WM. Pro Tag wird der aktuelle Wert gespeichert.</div>
<div id="readinessTrendSummary" style="margin-top:6px;font-weight:700">Erster Verlaufspunkt wird gespeichert…</div>
<div id="readinessTrendBars" style="display:flex;align-items:flex-end;gap:4px;height:82px;margin-top:8px"></div>
<div id="readinessTrendChanges" class="small" style="margin-top:7px"></div>
</div>
<div class="item" style="margin-top:10px"><strong>Nächste empfohlene Einheit</strong><div id="wmRecommendation" class="small">WM-Plan wird berechnet…</div></div>
<div class="item" style="margin-top:10px"><strong>🎯 Größte Abstände zum MSP-Median · Top 5</strong><div id="medianGapFocus" class="small">Medianvergleich wird berechnet…</div></div><div class="item" style="margin-top:10px"><strong>🎯 Wo lohnt sich die nächste Wiederholung am meisten?</strong><div id="repeatPriority" class="small">Wiederholungs-Priorität wird berechnet…</div></div><div class="item" style="margin-top:10px"><strong>🆕 Noch ungelöste Puzzle in meiner Library</strong><div id="unsolvedLibrary" class="small">Library wird geprüft…</div></div>
<div class="metricrow" style="margin-top:10px"><div class="metric"><div class="label">Training Load · 7 Tage</div><b id="wmLoad7">–</b><div class="small" id="wmLoad7Info">–</div></div><div class="metric"><div class="label">Training Load · 14 Tage</div><b id="wmLoad14">–</b><div class="small" id="wmLoad14Info">–</div></div><div class="metric"><div class="label">WM-Pace / 100 Teile</div><b id="wmPace100">–</b><div class="small" id="wmWeakness">–</div></div></div>
<div class="item" style="margin-top:10px"><strong>500er-Leistungsbild</strong><div id="wmStats" class="small">–</div></div>
<div id="unavailableBox" class="item loanBox" style="display:none;margin-top:10px"><strong>📦 Aktuell nicht verfügbare / ausgeliehene Puzzles</strong><div class="small">Diese Puzzles werden in allen Empfehlungen und im gesamten Wochenplan ausgeschlossen.</div><div id="unavailableList" style="margin-top:7px"></div><button class="secondary" style="margin-top:7px" onclick="restoreAllPuzzles()">Alle wieder verfügbar</button></div>

</section>



<section class="card full appSection" id="appWM" data-app-page="wm"><h2>📈 Fortschritt bis zur WM</h2>
<div class="small">Die letzten 10 500er-Solozeiten im Vergleich zu aktuellem Niveau und WM-Zielen. Entscheidend ist das wiederholbare Leistungsniveau, nicht eine einzelne Bestzeit.
<div class="progressTargets">
<div class="targetCard"><div class="label">Aktuelles Niveau</div><b id="progressCurrent">–</b><div class="small">Ø letzte 10</div></div>
<div class="targetCard"><div class="label">Trainingsziel</div><b id="progressTraining">–</b></div>
<div class="targetCard"><div class="label">First-Try-Ziel</div><b id="progressGoal">–</b></div>
<div class="targetCard"><div class="label">Stretch Goal</div><b id="progressStretch">–</b></div>
</div></div>
<div id="wmProgressSummary" class="item" style="margin-top:10px">Fortschritt wird berechnet…</div>
<div id="wmProgressChart" class="item" style="margin-top:8px"></div>
</section>

<section class="card full" data-app-page="wm"><h2>🇨🇭 Schweizer Motivationsranking</h2>
<div class="small">Vergleich mit öffentlich verbundenen Schweizer Teilnehmern der Swiss Puzzle Championship. <strong>Kein offizielles Schweizer Ranking.</strong> Das Ranking dient nur als Motivation und beeinflusst den Trainingsplan nicht.</div>
<div id="swissRankSummary" class="item" style="margin-top:10px">Ranking wird geladen…</div>
<div id="swissRankList" class="list" style="margin-top:8px"></div>
</section>

<section class="card full" data-app-page="progress"><h2>📈 Automatische Trainingsanalyse</h2>
<div class="metricrow">
<div class="metric"><div class="label">Ergebnisse gesamt</div><b id="autoTotal">–</b><div class="small" id="autoModes"></div></div>
<div class="metric"><div class="label">Schnellste erfasste Zeit</div><b id="autoBest">–</b><div class="small" id="autoBestInfo"></div></div>
<div class="metric"><div class="label">Letztes Ergebnis</div><b id="autoLatest">–</b><div class="small">automatisch aus MySpeedPuzzling</div></div>
</div></section>

<section class="card half" data-app-page="progress"><h2>🧩 Leistung nach Teilezahl</h2><div id="piecePerformance" class="list"><div class="small">Analyse wird geladen…</div></div></section>
<section class="card half" data-app-page="progress"><h2>🏭 Leistung nach Hersteller</h2><div id="manufacturerPerformance" class="list"><div class="small">Analyse wird geladen…</div></div></section>

<section class="card half" data-app-page="progress"><h2>⏱️ Letzte MySpeedPuzzling-Ergebnisse</h2><div id="autoTrainings" class="list"></div></section>




<section class="card full appSection" id="appProgress" data-app-page="progress"><h2>📈 Fortschritt pro Puzzle</h2>
<div class="small">Verlauf der wiederholt gelösten Puzzle im Vergleich zu vorheriger Zeit, Bestzeit und MSP-Median.</div>
<div id="puzzleProgress" class="list" style="margin-top:8px">Fortschritt wird geladen…</div>
</section>

<section class="card full appSection" id="appMore" data-app-page="more"><h2>🧠 Tournament Intelligence</h2>
<div class="small">V6.9.6 MSP-only Puzzle Predictions + Frontend Snapshot Recovery: konkrete Puzzle-Prognosen stammen ausschliesslich aus MySpeedPuzzling; WM-Ziele und Coach-Logik bleiben unverändert. Lokale Turnier-Fallbacks: bei einem MySpeedPuzzling-Ausfall bleibt der letzte erfolgreiche Datenstand aktiv. WM-Fortschritt und transparentes Schweizer Benchmarking. Der Skip bleibt global: ausgeliehene Puzzles werden aus Hauptempfehlung und Wochenplan gleichzeitig entfernt. Das Schweizer Motivationsranking zeigt zusätzlich Abstand zu Platz 1, Abstand zum nächsten Platz und ein konkretes Ø-Ziel. Ausgeliehene Puzzles werden lokal übersprungen und können jederzeit wieder freigegeben werden: bekannte frühere Meisterschaftspuzzles werden für WM-Simulationen stark abgewertet. Puzzle-Fotos helfen beim Finden. Trainings können direkt gestartet und anschliessend mit dem neuen MySpeedPuzzling-Ergebnis automatisch gegen die Zielzeit bewertet werden.</div>
<div style="margin-top:12px"><a class="btn secondary" href="/docs" target="_blank">API-Dokumentation</a> <a class="btn secondary" href="/msp/my-competitions?refresh=true" target="_blank">Anmeldungen neu prüfen</a> <a class="btn secondary" href="/sync" target="_blank">MySpeedPuzzling neu synchronisieren</a> <a class="btn secondary" href="/msp/library" target="_blank">Puzzle-Bibliothek prüfen</a></div>
</section>
</div></div>

<div id="infoModal" class="modal" onclick="if(event.target===this)closeInfo()"><div class="modalbox"><div id="infoContent"></div><button class="secondary" onclick="closeInfo()">Schliessen</button></div></div>
<script>
function showInfo(type){
 const form=`<h2>ℹ️ Was bedeutet Form?</h2><p><b>Form</b> zeigt, ob Nicole aktuell schneller oder langsamer puzzelt als in der vorherigen Vergleichsperiode. Dafür werden die letzten 10 Solo-Ergebnisse mit den vorherigen 10 verglichen und auf <b>Zeit pro 100 Teile</b> normalisiert.</p><div class="scale"><div><b>Positiver Wert:</b> aktuell schneller. Beispiel +11,7 % = die normalisierte Zeit ist rund 11,7 % besser als zuvor.</div><div><b>Um 0 %:</b> Leistung weitgehend stabil.</div><div><b>Negativer Wert:</b> aktuell langsamer als in der vorherigen Periode.</div></div><p class="small">Die Zahl ist ein Trendindikator, keine Gewinnwahrscheinlichkeit und keine Prognose einer einzelnen Puzzlezeit.</p>`;
 const con=`<h2>ℹ️ Was bedeutet Konsistenz?</h2><p><b>Konsistenz</b> misst, wie ähnlich die letzten 10 normalisierten Solo-Leistungen sind. Auch hier wird Zeit pro 100 Teile verwendet, damit verschiedene Teilezahlen besser vergleichbar sind.</p><div class="scale"><div><b>90–100:</b> sehr konstante Leistungen</div><div><b>80–89:</b> gute bis hohe Konstanz</div><div><b>70–79:</b> merkliche Schwankungen</div><div><b>unter 70:</b> starke Schwankungen; Ursachen genauer analysieren</div></div><p class="small">Ein hoher Wert bedeutet nicht automatisch schnell. Ideal ist eine hohe Konsistenz zusammen mit einer starken bzw. steigenden Form.</p>`;
 infoContent.innerHTML=type==='form'?form:con;infoModal.classList.add('open')
}
function closeInfo(){infoModal.classList.remove('open')}

function timeToSeconds(v){if(!v)return null;let p=v.split(':').map(Number);if(p.some(Number.isNaN))return null;if(p.length===3)return p[0]*3600+p[1]*60+p[2];if(p.length===2)return p[0]*60+p[1];return Number(v)}
async function getj(u){let r=await fetch(u),d=await r.json();if(!r.ok)throw new Error(d.detail||'Fehler');return d}
function dateText(v){if(!v)return'–';try{return new Date(v).toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit',year:'numeric'})}catch(e){return v}}
function countdownText(v){if(!v)return'';let ms=new Date(v)-new Date();if(ms<=0)return'Heute / gestartet';let d=Math.floor(ms/86400000),h=Math.floor((ms%86400000)/3600000);return d>1?`Noch ${d} Tage`:d===1?`Noch 1 Tag ${h} Std.`:`Noch ${h} Stunden`}
function pct(v){if(v==null)return'–';return `${v>0?'+':''}${v}%`}
function puzzleImg(p){
  if(!p||!p.image_url)return '';
  return `<img class="puzzleImg" src="${p.image_url}" alt="${p.name||'Puzzle'}" loading="lazy" onerror="this.style.display='none'">`;
}

function puzzleInsightHtml(p){
  let i=p?.msp_insights||{},bits=[];
  if(i.difficulty_label){let pct=i.difficulty_percent!=null?` (${i.difficulty_percent>0?'+':''}${i.difficulty_percent}% ggü. Ø)`:'';
    bits.push(`Difficulty: ${i.difficulty_label}${pct}`);}
  let details=bits.length?`<div class="small" style="margin-top:5px"><strong>MSP:</strong> ${bits.join(' · ')}</div>`:'';
  let prediction='';
  if(p?.msp_prediction){let corridor=(p.msp_prediction_range_from&&p.msp_prediction_range_to)?` · Bereich ${p.msp_prediction_range_from}–${p.msp_prediction_range_to}`:'';
    prediction=`<div class="small" style="margin-top:4px"><strong>MSP Prediction:</strong> ${p.msp_prediction}${corridor}</div>`;
  } else {
    prediction=`<div class="small" style="margin-top:4px"><strong>MSP Prediction:</strong> derzeit nicht verfügbar</div>`;
  }
  let median='';
  if(p?.msp_median){
    if(p.median_training_required){
      median=`<div class="small medianTarget" style="margin-top:4px"><strong>🎯 MSP Median-Ziel:</strong> ${p.msp_median} · letzte Zeit ${p.msp_last_time||'–'} · <strong>weiter trainieren</strong>${p.median_gap?` (${p.median_gap} über Median)`:''}</div>`;
    }else{
      median=`<div class="small" style="margin-top:4px"><strong>MSP Median:</strong> ${p.msp_median}${p.msp_last_time?` · letzte Zeit ${p.msp_last_time}`:''}${p.msp_last_time_seconds!=null&&p.msp_median_seconds!=null&&p.msp_last_time_seconds<=p.msp_median_seconds?' · ✅ Median erreicht':''}</div>`;
    }
  }
  return details+prediction+median;
}
function goalTargetSeconds(text){
  if(!text)return null;
  let m=text.match(/(\d{1,2}):(\d{2})(?::(\d{2}))?/);
  if(!m)return null;
  if(m[3])return Number(m[1])*3600+Number(m[2])*60+Number(m[3]);
  return Number(m[1])*60+Number(m[2]);
}
function fmtSeconds(v){
  if(v==null)return '–';
  v=Math.round(v);let h=Math.floor(v/3600),m=Math.floor((v%3600)/60),sec=v%60;
  return h?`${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`:`${m}:${String(sec).padStart(2,'0')}`;
}

function fmtGap(v){
  if(v==null)return '–';
  v=Math.round(v);let m=Math.floor(v/60),s=v%60;
  return `${m}:${String(s).padStart(2,'0')}`;
}
function getActiveTraining(){try{return JSON.parse(localStorage.getItem('npc_active_training')||'null')}catch(e){return null}}
function getWMSimHistory(){try{return JSON.parse(localStorage.getItem('npc_wm_sim_history')||'[]')}catch(e){return []}}
function saveWMSimHistory(v){localStorage.setItem('npc_wm_sim_history',JSON.stringify(v))}
function getActiveWMSim(){try{return JSON.parse(localStorage.getItem('npc_active_wm_sim')||'null')}catch(e){return null}}
function startWMSimulation(puzzle,goalSeconds,realisticSeconds,stretchSeconds){
  if(!puzzle||!puzzle.available){alert('Kein geeignetes Puzzle verfügbar.');return}
  localStorage.setItem('npc_active_wm_sim',JSON.stringify({puzzle_id:puzzle.id||null,puzzle_name:puzzle.name,manufacturer:puzzle.manufacturer||null,image_url:puzzle.image_url||null,started_at:new Date().toISOString(),target_seconds:goalSeconds||realisticSeconds||null,realistic_goal_seconds:realisticSeconds||null,stretch_goal_seconds:stretchSeconds||null}));
  renderActiveWMSim();
}
function cancelWMSimulation(){localStorage.removeItem('npc_active_wm_sim');renderActiveWMSim()}
async function checkWMSimulation(){
  let s=getActiveWMSim(); if(!s)return;
  wmSimResult.textContent='MySpeedPuzzling wird synchronisiert…';
  try{await fetch('/sync')}catch(e){}
  let q=new URLSearchParams(); if(s.puzzle_id)q.set('puzzle_id',s.puzzle_id); q.set('puzzle_name',s.puzzle_name);q.set('started_at',s.started_at);
  if(s.target_seconds)q.set('target_seconds',s.target_seconds);if(s.realistic_goal_seconds)q.set('realistic_goal_seconds',s.realistic_goal_seconds);if(s.stretch_goal_seconds)q.set('stretch_goal_seconds',s.stretch_goal_seconds);
  try{
    let r=await getj('/coach/wm-simulation-feedback?'+q.toString());
    if(!r.found){wmSimResult.textContent=r.message||'Noch kein Ergebnis gefunden.';return}
    let hist=getWMSimHistory();hist.unshift({completed_at:new Date().toISOString(),puzzle_name:s.puzzle_name,manufacturer:s.manufacturer,image_url:s.image_url,actual_seconds:r.actual_seconds,target_seconds:r.target_seconds,realistic_goal_seconds:r.realistic_goal_seconds,stretch_goal_seconds:r.stretch_goal_seconds,simulation_score:r.simulation_score,status:r.status,label:r.label});saveWMSimHistory(hist.slice(0,30));
    localStorage.removeItem('npc_active_wm_sim');wmSimResult.innerHTML=`<strong>${r.label}</strong> · ${fmtSeconds(r.actual_seconds)} · Score ${r.simulation_score}/100`;renderWMSimHistory();setTimeout(()=>location.reload(),1200);
  }catch(e){wmSimResult.textContent='Simulationsauswertung fehlgeschlagen.'}
}
function renderActiveWMSim(){
  if(!document.getElementById('wmSimActive'))return;
  let s=getActiveWMSim();if(!s){wmSimActive.style.display='none';return}
  wmSimActive.style.display='block';wmSimName.textContent=s.puzzle_name;wmSimImage.innerHTML=s.image_url?`<img class="puzzleImg" src="${s.image_url}" alt="${s.puzzle_name}" onerror="this.style.display='none'">`:'';
  wmSimGoals.textContent=`Ziel ${fmtSeconds(s.target_seconds)} · WM-Ziel ${fmtSeconds(s.realistic_goal_seconds)} · Stretch ${fmtSeconds(s.stretch_goal_seconds)}`;wmSimResult.textContent='Simulation läuft / Ergebnis noch nicht geprüft.';
}
function renderWMSimHistory(){
  if(!document.getElementById('wmSimHistory'))return;
  let hist=getWMSimHistory();if(!hist.length){wmSimHistory.innerHTML='<div class="small">Noch keine WM-Simulation abgeschlossen.</div>';wmSimSummary.innerHTML='<strong>Noch keine Simulationsdaten</strong>';return}
  let last5=hist.slice(0,5),avg=Math.round(last5.reduce((a,x)=>a+x.actual_seconds,0)/last5.length),hit=last5.filter(x=>x.status==='ziel_erreicht').length,avgScore=Math.round(last5.reduce((a,x)=>a+(x.simulation_score||0),0)/last5.length),trend=null;
  if(hist.length>=4){let recent=hist.slice(0,2).reduce((a,x)=>a+x.actual_seconds,0)/2,older=hist.slice(2,4).reduce((a,x)=>a+x.actual_seconds,0)/2;trend=older?((older-recent)/older*100):null}
  wmSimSummary.innerHTML=`<strong>Letzte ${last5.length}: Ø ${fmtSeconds(avg)}</strong> · ${hit}/${last5.length} im Ziel · Ø Score ${avgScore}/100${trend!=null?` · Trend ${trend>0?'+':''}${trend.toFixed(1)}%`:''}`;
  wmSimHistory.innerHTML=hist.slice(0,8).map((x,i)=>`<div class="item ${x.simulation_score>=85?'scoreGood':x.simulation_score>=70?'scoreMid':'scoreBad'}"><div class="historyRow"><div>#${hist.length-i}</div><div><strong>${x.puzzle_name}</strong><div class="small">${new Date(x.completed_at).toLocaleDateString('de-CH')} · ${x.label}</div></div><div><strong>${fmtSeconds(x.actual_seconds)}</strong></div><div><strong>${x.simulation_score}/100</strong></div></div></div>`).join('');
}

function getUnavailablePuzzles(){try{return JSON.parse(localStorage.getItem('npc_unavailable_puzzles')||'[]')}catch(e){return []}}
function saveUnavailablePuzzles(v){localStorage.setItem('npc_unavailable_puzzles',JSON.stringify(v))}
function unavailableIds(){return getUnavailablePuzzles().map(x=>String(x.id||'')).filter(Boolean)}
function skipPuzzle(p){
  if(!p||!p.id)return;
  let arr=getUnavailablePuzzles();
  if(!arr.some(x=>String(x.id)===String(p.id))){
    arr.push({id:p.id,name:p.name,image_url:p.image_url||null,skipped_at:new Date().toISOString()});
    saveUnavailablePuzzles(arr);
  }
  wmNextPuzzle.innerHTML='<span class="small">Puzzle wird übersprungen – neue Empfehlung wird berechnet…</span>';
  wmWeeklyPlan.innerHTML='<div class="small">Wochenplan wird mit verfügbaren Puzzles neu berechnet…</div>';
  renderUnavailable();
  loadAll();
}
function restorePuzzle(id){
  saveUnavailablePuzzles(getUnavailablePuzzles().filter(x=>String(x.id)!==String(id)));
  loadAll();
}
function restoreAllPuzzles(){saveUnavailablePuzzles([]);loadAll()}
function renderUnavailable(){
  let arr=getUnavailablePuzzles();
  if(!arr.length){unavailableBox.style.display='none';return}
  unavailableBox.style.display='block';
  unavailableList.innerHTML=arr.map(p=>`<span class="pill">📦 ${p.name} <button onclick='restorePuzzle(${JSON.stringify(p.id)})' style="border:0;background:none;cursor:pointer">↩</button></span>`).join('');
}

function startTraining(session,puzzle,goal){
  if(!puzzle||!puzzle.available){alert('Für diese Einheit ist kein vollständiges Puzzle vorgesehen.');return}
  let active={
    session:session,
    puzzle_id:puzzle.id||null,
    puzzle_name:puzzle.name,
    image_url:puzzle.image_url||null,
    target_seconds:goalTargetSeconds(goal),
    goal:goal,
    started_at:new Date().toISOString()
  };
  localStorage.setItem('npc_active_training',JSON.stringify(active));
  renderActiveTraining();
}
async function checkTrainingResult(){
  let a=getActiveTraining();
  if(!a){alert('Kein aktives Training.');return}
  activeTrainingResult.textContent='Synchronisiere MySpeedPuzzling…';
  try{await fetch('/sync')}catch(e){}
  let q=new URLSearchParams();
  if(a.puzzle_id)q.set('puzzle_id',a.puzzle_id);
  q.set('puzzle_name',a.puzzle_name);
  q.set('started_at',a.started_at);
  if(a.target_seconds)q.set('target_seconds',a.target_seconds);
  try{
    let r=await getj('/coach/training-feedback?'+q.toString());
    if(!r.found){activeTrainingResult.textContent='Noch kein passendes neues Ergebnis gefunden.';return}
    let delta=r.delta_seconds;
    activeTrainingResult.innerHTML=`<strong>${r.label}</strong> · Zeit ${fmtSeconds(r.actual_seconds)}${r.target_seconds?` · Ziel ${fmtSeconds(r.target_seconds)}`:''}${delta!=null?` · Differenz ${delta>0?'+':''}${delta}s`:''}`;
    localStorage.setItem('npc_last_training_feedback',JSON.stringify(r));
    localStorage.removeItem('npc_active_training');
    setTimeout(()=>location.reload(),1400);
  }catch(e){activeTrainingResult.textContent='Ergebnisprüfung fehlgeschlagen.'}
}
function cancelTraining(){localStorage.removeItem('npc_active_training');renderActiveTraining()}
function renderActiveTraining(){
  // Manual "Training starten" UI was intentionally removed in V6.8.7.
  // Keep this function as a safe no-op for stale browser localStorage / old calls.
  const box=document.getElementById('activeTrainingBox');
  if(!box)return;
  const active=getActiveTraining();
  if(!active){box.style.display='none';return}
  box.style.display='block';
}


async function loadMedianGapFocus(){
  const el=document.getElementById('medianGapFocus');
  if(!el)return;
  el.textContent='Top-5-Medianvergleich wird berechnet…';
  try{
    const mg=await getj('/coach/median-gap-focus');
    if(mg.available){
      const items=(Array.isArray(mg.items)&&mg.items.length)?mg.items:[mg];
      el.innerHTML=`<div class="small" style="margin:5px 0 8px">${mg.message||''}</div>`+
        items.map((p,idx)=>`<div class="puzzleRow" style="margin-top:${idx?8:4}px;padding-top:${idx?8:0}px;${idx?'border-top:1px solid #e5e7eb;':''}">
          ${p.image_url?`<img class="puzzleImg" src="${p.image_url}" alt="${p.name||'Puzzle'}" loading="lazy" onerror="this.style.display='none'">`:''}
          <div class="puzzleInfo">
            <strong>${idx+1}. ${p.name||'Puzzle'}</strong>${p.manufacturer?' · '+p.manufacturer:''}
            <div class="small">Letzte Zeit <strong>${p.last_time||'–'}</strong> · MSP-Median <strong>${p.median||'–'}</strong> · Abstand <strong>${p.gap||'–'}</strong></div>
          </div>
        </div>`).join('');
    }else{
      el.textContent=mg.message||'Kein Median-Abstand verfügbar.';
    }
  }catch(e){
    el.textContent='Medianvergleich derzeit nicht verfügbar.';
  }
}


async function refreshFromMSP(){
  const btn=document.getElementById('mspRefreshBtn');
  const status=document.getElementById('syncStatusText');
  if(btn){
    btn.disabled=true;
    btn.classList.add('syncing');
    btn.textContent='Synchronisiere…';
  }
  if(status)status.textContent='MySpeedPuzzling wird geladen…';
  try{
    const r=await getj('/sync');
    const n=r.new_results_count||0;
    if(status)status.textContent='Daten geladen · Dashboard wird neu berechnet…';
    // Refresh core first; heavy detail areas only if the user has opened them.
    await loadAll();
    const extraJobs=[];
    if(trainingExtrasLoaded)extraJobs.push(loadMedianGapFocus(),loadRepeatPriority(),loadUnsolvedLibrary());
    if(progressExtrasLoaded)extraJobs.push(loadPuzzleProgress());
    if(extraJobs.length)await Promise.allSettled(extraJobs);
    if(btn)btn.textContent=n?`✓ ${n} neue Ergebnis${n===1?'':'se'}`:'✓ Aktuell';
    if(status)status.textContent='Synchronisierung abgeschlossen';
  }catch(e){
    if(btn)btn.textContent='⚠ Sync fehlgeschlagen';
    if(status)status.textContent='Bitte erneut versuchen';
  }finally{
    if(btn)btn.classList.remove('syncing');
    if(btn)setTimeout(()=>{
      btn.disabled=false;
      btn.textContent='↻ MySpeedPuzzling aktualisieren';
      if(status)status.textContent='';
    },2500);
  }
}

async function loadPuzzleProgress(){
  const el=document.getElementById('puzzleProgress');
  if(!el)return;
  try{
    const d=await getj('/coach/puzzle-progress?limit=8');
    if(!d.available||!d.items?.length){
      el.textContent=d.message||'Noch keine wiederholt gelösten Puzzle für einen Verlauf.';
      return;
    }
    el.innerHTML=d.items.map(p=>{
      let trend=p.delta_seconds<0?`✅ ${p.delta} schneller`:p.delta_seconds>0?`↗ ${p.delta} langsamer`:'gleich schnell';
      let med='';
      if(p.median_seconds!=null){
        const diff=p.vs_median_seconds;
        med=diff>0?` · Median ${p.median} · ${fmtSeconds(diff)} darüber`:` · Median ${p.median} · ✅ erreicht`;
      }
      return `<div class="puzzleRow" style="margin-top:8px;padding-top:8px;border-top:1px solid #e5e7eb">${p.image_url?`<img class="puzzleImg" src="${p.image_url}" alt="${p.name||'Puzzle'}" loading="lazy" onerror="this.style.display='none'">`:''}<div class="puzzleInfo"><strong>${p.name}</strong>${p.manufacturer?' · '+p.manufacturer:''}<div class="small">Letzte ${p.latest} · vorher ${p.previous} · Best ${p.best} · ${trend}${med}</div><span class="pill">${p.attempts} Solo-Läufe</span></div></div>`;
    }).join('');
  }catch(e){
    el.textContent='Puzzle-Fortschritt derzeit nicht verfügbar.';
  }
}

async function loadUnsolvedLibrary(){
 const el=document.getElementById('unsolvedLibrary');if(!el)return;
 try{const d=await getj('/coach/unsolved-library');
 if(!d.available||!d.items?.length){el.textContent=d.message||'Keine ungelösten Library-Puzzle gefunden.';return}
 el.innerHTML=`<div class="small" style="margin:5px 0 8px"><strong>${d.count}</strong> Puzzle ohne Solo-Ergebnis · ideal für First-Try-Training.</div>`+
 d.items.map((p,i)=>{const diff=p.difficulty_label?` · Difficulty <strong>${p.difficulty_label}</strong>${p.difficulty_percent!=null?' ('+Number(p.difficulty_percent).toFixed(2)+'%)':''}`:'';
 const pred=p.prediction?` · MSP Prediction <strong>${p.prediction}</strong>${p.prediction_low&&p.prediction_high?' ('+p.prediction_low+'–'+p.prediction_high+')':''}`:'';
 return `<div class="puzzleRow" style="margin-top:${i?8:4}px;padding-top:${i?8:0}px;${i?'border-top:1px solid #e5e7eb;':''}">${p.image_url?`<img class="puzzleImg" src="${p.image_url}" alt="${p.name||'Puzzle'}" loading="lazy" onerror="this.style.display='none'">`:''}<div class="puzzleInfo"><strong>${p.name||'Puzzle'}</strong>${p.manufacturer?' · '+p.manufacturer:''}<div class="small">${p.pieces?p.pieces+' Teile':'Teilezahl unbekannt'}${diff}${pred}</div><span class="pill">noch kein Solo-Ergebnis</span></div></div>`}).join('');
 }catch(e){el.textContent='Ungelöste Library derzeit nicht verfügbar.'}}
async function loadRepeatPriority(){
 const el=document.getElementById('repeatPriority');if(!el)return;
 try{const d=await getj('/coach/repeat-priority?limit=5');
 if(!d.available||!d.items?.length){el.textContent=d.message||'Keine geeigneten Wiederholungs-Puzzle gefunden.';return}
 el.innerHTML=`<div class="small" style="margin:5px 0 8px">${d.message||''}</div>`+d.items.map((p,i)=>{
 const med=p.median?` · MSP-Median <strong>${p.median}</strong>${p.median_gap?' · '+p.median_gap+' darüber':''}`:'';
 const prev=p.previous?` · vorher ${p.previous}`:'';
 const days=p.days_since_last_solve!=null?` · zuletzt vor ${p.days_since_last_solve} Tagen`:'';
 return `<div class="puzzleRow" style="margin-top:${i?8:4}px;padding-top:${i?8:0}px;${i?'border-top:1px solid #e5e7eb;':''}">${p.image_url?`<img class="puzzleImg" src="${p.image_url}" alt="${p.name||'Puzzle'}" loading="lazy" onerror="this.style.display='none'">`:''}<div class="puzzleInfo"><strong>${i+1}. ${p.name||'Puzzle'}</strong>${p.manufacturer?' · '+p.manufacturer:''}<div class="small">Priorität <strong>${p.score}/100</strong> · ${p.label}</div><div class="small">Letzte ${p.latest}${prev} · Best ${p.best}${med}${days}</div><div class="small">${(p.reasons||[]).join(' · ')}</div></div></div>`}).join('');
 }catch(e){el.textContent='Wiederholungs-Priorität derzeit nicht verfügbar.'}}


function showAppPage(page,scrollTop=true){
  const mobile=window.matchMedia('(max-width:760px)').matches;
  const labels={today:'Heute',training:'Training',wm:'WM',progress:'Fortschritt',more:'Mehr'};
  const targetMap={today:'appToday',training:'appTraining',wm:'appWM',progress:'appProgress',more:'appMore'};
  const buttons=[...document.querySelectorAll('.appBottomNav button')];
  buttons.forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  if(!mobile){
    document.getElementById(targetMap[page])?.scrollIntoView({behavior:'smooth',block:'start'});
    return;
  }
  document.querySelectorAll('.grid>section[data-app-page]').forEach(el=>{
    el.classList.toggle('appPageActive',el.dataset.appPage===page);
  });
  const h=document.getElementById('appPageHeading'); if(h)h.textContent=labels[page]||'';
  if(scrollTop)window.scrollTo({top:0,behavior:'smooth'});
  if(page==='training')loadTrainingExtrasOnce();
  if(page==='progress')loadProgressExtrasOnce();
}
function initAppNavigation(){
  const map={appToday:'today',appTraining:'training',appWM:'wm',appProgress:'progress',appMore:'more'};
  const buttons=[...document.querySelectorAll('.appBottomNav button')];
  buttons.forEach(btn=>{
    btn.dataset.page=map[btn.dataset.target]||'today';
    btn.addEventListener('click',()=>showAppPage(btn.dataset.page));
  });
  showAppPage('today',false);
}
function updateTrainingQuick(w){
 const p=w?.next_puzzle||{};
 const img=document.getElementById('trainingQuickImage'),name=document.getElementById('trainingQuickPuzzle'),meta=document.getElementById('trainingQuickMeta');
 const type=document.getElementById('trainingQuickType'),target=document.getElementById('trainingQuickTarget');
 const median=document.getElementById('trainingQuickMedian'),last=document.getElementById('trainingQuickLast'),delta=document.getElementById('trainingQuickDelta'),fit=document.getElementById('trainingQuickFit'),reason=document.getElementById('trainingQuickReason');
 const pick=(...v)=>v.find(x=>x!==undefined&&x!==null&&x!=='');
 if(name)name.textContent=p.name||'Noch keine Empfehlung';
 if(meta)meta.textContent=[p.manufacturer,p.pieces?`${p.pieces} Teile`:null].filter(Boolean).join(' · ');
 if(type)type.textContent=pick(w?.next_training?.type,w?.next_training_type,'–');
 if(target)target.textContent=pick(w?.dynamic_target,w?.wm_goal_first_try,p?.target_time,'–');
 const mt=(p.median_target&&typeof p.median_target==='object')?p.median_target:{};
 const med=pick(mt.median,p.msp_median,p.median_time,p.median,p.target_median);
 const lst=pick(mt.last,p.last_time,p.latest_time,p.last_result);
 let dlt=pick(p.delta_vs_median,p.median_delta,p.vs_median);
 if((dlt===undefined||dlt===null||dlt==='')&&mt.last_seconds!=null&&mt.median_seconds!=null&&Number(mt.median_seconds)>0){
   dlt=((Number(mt.last_seconds)-Number(mt.median_seconds))/Number(mt.median_seconds))*100;
 }
 const wfRaw=pick(p.wm_fit,p.wm_fit_score,p.fit_score);
 const wf=(wfRaw&&typeof wfRaw==='object')?pick(wfRaw.score,wfRaw.value,wfRaw.fit_score):wfRaw;
 if(median)median.textContent=med||'–';
 if(last)last.textContent=lst||'–';
 if(delta){
   if(typeof dlt==='number'&&Number.isFinite(dlt)) delta.textContent=`${dlt>0?'+':''}${dlt.toFixed(1)}% ${dlt>0?'über Median':dlt<0?'unter Median':'vs. Median'}`;
   else delta.textContent=dlt||'–';
 }
 if(fit)fit.textContent=(wf!==undefined&&wf!==null&&wf!=='')?(String(wf).includes('/100')?wf:`${wf}/100`):'–';
 if(reason)reason.textContent=pick(p.reason,p.recommendation_reason,p.note,'');
 if(img)img.innerHTML=p.image_url?`<img src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.parentElement.textContent='🧩'">`:'🧩';
}

function updateTodaySummary(w){
  const rp=document.getElementById('todayPuzzle');
  const rt=document.getElementById('todayTraining');
  const rr=document.getElementById('todayReadiness');
  const ri=document.getElementById('todayPuzzleImage');
  const rm=document.getElementById('todayPuzzleMeta');
  const btn=document.getElementById('todayTrainingBtn');
  const p=w?.next_puzzle||{};
  if(rp)rp.textContent=p.name||'Noch keine Empfehlung';
  if(rt)rt.textContent=w?.next_training?.type||'Noch kein Training';
  if(rr)rr.textContent=w?.readiness_score==null?'–':w.readiness_score+'/100';
  if(rm)rm.textContent=[p.manufacturer,p.pieces?`${p.pieces} Teile`:null].filter(Boolean).join(' · ');
  if(ri){
    ri.innerHTML=p.image_url?`<img src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.parentElement.textContent='🧩'">`:'🧩';
  }
  if(btn){
    btn.onclick=()=>showAppPage('training');
  }
}
if('serviceWorker' in navigator){
  window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}));
}
let trainingExtrasLoaded=false,progressExtrasLoaded=false;
function loadTrainingExtrasOnce(){
  if(trainingExtrasLoaded)return;
  trainingExtrasLoaded=true;
  Promise.allSettled([loadMedianGapFocus(),loadRepeatPriority(),loadUnsolvedLibrary()]);
}
function loadProgressExtrasOnce(){
  if(progressExtrasLoaded)return;
  progressExtrasLoaded=true;
  Promise.allSettled([loadPuzzleProgress()]);
}
function readinessEsc(value){
  return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function readinessTime(seconds){
  const n=Number(seconds);
  if(!Number.isFinite(n)||n<0)return '–';
  const s=Math.round(n);
  const h=Math.floor(s/3600);
  const m=Math.floor((s%3600)/60);
  const sec=s%60;
  return h>0?`${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`:`${m}:${String(sec).padStart(2,'0')}`;
}
async function loadAll(){renderUnavailable();
 // Performance V6.9.6: independent API calls start immediately in parallel.
 const exPrefetch=unavailableIds();
 const statusPromise=getj('/coach/status');
 const summaryPromise=getj('/coach/msp-training-summary');
 const wmPlanPromise=getj('/coach/wm-plan'+(exPrefetch.length?'?exclude_puzzle_ids='+encodeURIComponent(exPrefetch.join(',')):''));
 const swissPromise=getj('/coach/swiss-ranking');
 const competitionsPromise=getj('/msp/my-competitions?limit=30');

 try{let st=await statusPromise;systemKpi.textContent='OK';systemText.textContent=`Backend V${st.version} · Datenbank ok`;systemBadge.textContent='🟢 System bereit';mspKpi.textContent=st.data_source==='legacy'?'LEGACY':(st.has_myspeedpuzzling_data?'DATA':(st.pat_configured?'PAT':(st.oauth_configured?'READY':'WAIT')));mspText.textContent=st.data_source==='legacy'?'Historische DB-Daten aktiv':(st.has_myspeedpuzzling_data?`Letzter Datenstand verfügbar · Snapshot #${st.latest_snapshot_id||'–'}`:(st.pat_configured?'PAT eingerichtet · noch kein Snapshot':'Verbindung möglich'))}catch(e){systemBadge.textContent='🔴 Fehler'}

 try{
   let a=await summaryPromise;
   trendKpi.textContent=pct(a.form_percent);consistencyKpi.textContent=a.consistency_score==null?'–':a.consistency_score;
   coachRecommendation.innerHTML=`<strong>${a.recommendation}</strong>`;
   autoTotal.textContent=a.total_results;autoModes.textContent=`Solo ${a.mode_counts.solo} · Duo ${a.mode_counts.duo} · Team ${a.mode_counts.team}`;
   if(a.best_overall){autoBest.textContent=a.best_overall.time;autoBestInfo.textContent=`${a.best_overall.puzzle_name} · ${a.best_overall.pieces||'?'} Teile · ${a.best_overall.mode}`;}
   autoLatest.textContent=a.latest_result_at?dateText(a.latest_result_at):'–';
   autoTrainings.innerHTML=a.latest_results.length?a.latest_results.map(r=>`<div class="item"><strong>${r.puzzle_name}</strong><div class="small">${dateText(r.finished_at)} · ${r.manufacturer} · ${r.pieces||'?'} Teile · ${r.mode.toUpperCase()} · ${r.time}</div>${r.first_attempt?'<span class="pill">1. Versuch</span>':''}</div>`).join(''):'<div class="small">Keine Ergebnisse.</div>';
   piecePerformance.innerHTML=a.piece_groups.length?a.piece_groups.slice(0,10).map(g=>`<div class="item"><strong>${g.pieces} Teile</strong><div class="small">${g.count} Solo-Ergebnisse · Ø ${g.average} · Best ${g.best}</div>${g.trend_percent!=null?`<span class="pill">Trend ${pct(g.trend_percent)}</span>`:''}</div>`).join(''):'<div class="small">Noch keine ausreichenden Daten.</div>';
   manufacturerPerformance.innerHTML=a.manufacturer_groups.length?a.manufacturer_groups.slice(0,10).map(g=>`<div class="item"><strong>${g.manufacturer}</strong><div class="small">${g.count} Solo-Ergebnisse · Ø ${g.avg_time_per_100} pro 100 Teile</div></div>`).join(''):'<div class="small">Noch keine ausreichenden Daten.</div>';
 }catch(e){coachRecommendation.textContent='Trainingsanalyse konnte nicht geladen werden.'}



 async function captureAndRenderReadinessTrend(w){
   try{
     const payload={
       readiness:w.readiness_score,
       form_signal:w.readiness_form_percent??null,
       consistency:w.consistency_500??null,
       median_hits:w.median_hit_count??null,
       comparable_count:w.median_normalized_sample_count??null
     };
     const r=await fetch('/coach/readiness-history/capture',{
       method:'POST',
       headers:{'Content-Type':'application/json'},
       body:JSON.stringify(payload)
     });
     if(!r.ok)return;
     const d=await r.json();
     renderReadinessTrend(d.items||[]);
   }catch(e){}
 }
 function renderReadinessTrend(items){
   const box=document.getElementById('readinessTrendBars');
   const summary=document.getElementById('readinessTrendSummary');
   const changes=document.getElementById('readinessTrendChanges');
   if(!box||!summary||!changes)return;
   box.innerHTML='';
   if(!items.length){
     summary.textContent='Noch keine Verlaufspunkte gespeichert.';
     changes.textContent='';
     return;
   }
   const recent=items.slice(-30);
   const last=recent[recent.length-1];
   summary.textContent=`Aktuell ${Math.round(Number(last.readiness))}/100 · ${items.length} gespeicherte Tageswerte`;
   recent.forEach(x=>{
     const bar=document.createElement('div');
     bar.title=`${x.day} · ${Math.round(Number(x.readiness))}/100`;
     bar.style.flex='1';
     bar.style.minWidth='4px';
     bar.style.maxWidth='18px';
     bar.style.height=Math.max(4,Math.min(100,Number(x.readiness)))+'%';
     bar.style.background='currentColor';
     bar.style.opacity='.35';
     bar.style.borderRadius='3px 3px 0 0';
     box.appendChild(bar);
   });
   function delta(days){
     const target=new Date();
     target.setDate(target.getDate()-days);
     const targetDay=target.toISOString().slice(0,10);
     const previous=[...items].reverse().find(x=>x.day<=targetDay);
     if(!previous)return null;
     return Number(last.readiness)-Number(previous.readiness);
   }
   changes.textContent=[[7,delta(7)],[14,delta(14)],[30,delta(30)]]
     .map(([d,v])=>v==null?`${d} Tage: noch keine Daten`:`${d} Tage: ${v>=0?'+':''}${v.toFixed(0)} Punkte`)
     .join(' · ');
 }
 function readinessZone(score){
   const s=Number(score);
   if(!Number.isFinite(s)) return {title:'Readiness-Zone',text:'Noch keine belastbare Einstufung.'};
   if(s>=90) return {title:'90+ · Außergewöhnliche WM-Form',text:'Über mehrere unterschiedliche 500er deutlich und stabil über MSP-Median-Niveau.'};
   if(s>=80) return {title:'80–89 · Sehr starke WM-Form',text:'Klar überdurchschnittliches, stabiles Leistungsniveau mit sehr guter WM-Nähe.'};
   if(s>=70) return {title:'70–79 · Starke WM-Form',text:'Deutlich über MSP-Median-Niveau und bereits wettkampfnah.'};
   if(s>=60) return {title:'60–69 · Solide WM-Form',text:'Über MSP-Median-Niveau; gute Basis, aber noch Potenzial bei Stärke oder Stabilität.'};
   if(s>=50) return {title:'50–59 · MSP-Niveau / Aufbauzone',text:'Ungefähr MSP-Median-Niveau. Gute Basis, für starke WM-Form braucht es noch mehr wiederholbare Resultate über Median.'};
   return {title:'Unter 50 · Aufbauphase',text:'Aktuell unter dem angestrebten MSP-Median-Niveau; Fokus auf stabile, saubere 500er statt auf einzelne Bestzeiten.'};
 }

 try{
   let w=await wmPlanPromise;
   const resilientBannerEl=document.getElementById('resilientBanner');
   const resilientTextEl=document.getElementById('resilientText');
   if(w.data_mode==='snapshot'){
     if(resilientBannerEl) resilientBannerEl.style.display='block';
     if(resilientTextEl) resilientTextEl.innerHTML=`MySpeedPuzzling ist von Render aktuell nicht live erreichbar. Der Coach verwendet Snapshot <strong>#${w.snapshot_id||'–'}</strong>. Trainingsdaten, WM-Ziele und Wochenplan bleiben nutzbar. Bekannte Turnierdaten werden lokal ergänzt.${w.live_warning?`<br>${w.live_warning}`:''}`;
     mspKpi.textContent='CACHE';
     mspText.textContent=`Letzter erfolgreicher Datenstand · Snapshot #${w.snapshot_id||'–'}`;
   }else if(w.data_mode==='legacy'){
     if(resilientBannerEl) resilientBannerEl.style.display='block';
     if(resilientTextEl) resilientTextEl.innerHTML=`MySpeedPuzzling ist aktuell nicht live erreichbar und es existiert kein verwertbarer Snapshot. Der Coach rekonstruiert die Vorbereitung aus <strong>${w.legacy_result_count||0} historischen Trainingsdatensätzen</strong>. Puzzle-Bibliothek und Live-Turniere können dabei eingeschränkt sein.${w.live_warning?`<br>${w.live_warning}`:''}`;
     mspKpi.textContent='LEGACY';
     mspText.textContent='Historische DB-Daten aktiv';
   }else{
     if(resilientBannerEl) resilientBannerEl.style.display='none';
     mspKpi.textContent='LIVE';
     mspText.textContent='MySpeedPuzzling live verbunden · MSP Live-Sync aktiv';
   }
   let fallbackCompetition=w.next_competition||null;
   if(fallbackCompetition){
     nextMspCompetition.innerHTML=`<strong>${fallbackCompetition.name}</strong><br>${dateText(fallbackCompetition.date_from)}${fallbackCompetition.location?' · '+fallbackCompetition.location:''}${fallbackCompetition.country_code?' · '+fallbackCompetition.country_code.toUpperCase():''}<br><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(fallbackCompetition.date_from)}</span>${fallbackCompetition.registration_source==='local_fallback'?'<span class="pill">lokaler Fallback</span>':''}`;
     mspCompetitions.innerHTML=`<div class="item"><strong>${fallbackCompetition.name}</strong><div class="small">${dateText(fallbackCompetition.date_from)}${fallbackCompetition.date_to?' – '+dateText(fallbackCompetition.date_to):''}${fallbackCompetition.location?' · '+fallbackCompetition.location:''}</div><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(fallbackCompetition.date_from)}</span>${fallbackCompetition.registration_source==='local_fallback'?'<span class="pill">lokaler Fallback</span>':''}</div>`;
   }
   wmReadiness.textContent=w.readiness_score==null?'–':w.readiness_score+'/100';
   updateTodaySummary(w);
   updateTrainingQuick(w);
    if(document.getElementById('readinessTopKpi')) readinessTopKpi.textContent=w.readiness_score==null?'–':w.readiness_score+'/100';
    captureAndRenderReadinessTrend(w);
    if(document.getElementById('readinessZoneTitle') && document.getElementById('readinessZoneText')){
      const rz=readinessZone(w.readiness_score);
      let deltaText='';
      try{
        const prevRaw=localStorage.getItem('npc_readiness_previous');
        const prev=prevRaw==null?null:Number(prevRaw);
        const cur=Number(w.readiness_score);
        if(Number.isFinite(prev)&&Number.isFinite(cur)&&prev!==cur){
          const d=cur-prev; deltaText=` Seit der letzten geladenen Bewertung: ${d>0?'+':''}${d} Punkte.`;
        }
        if(Number.isFinite(cur)) localStorage.setItem('npc_readiness_previous',String(cur));
      }catch(e){}
      readinessZoneTitle.textContent=rz.title;
      readinessZoneText.textContent=rz.text+deltaText;
    }
    if(document.getElementById('readinessBaseInfo')) readinessBaseInfo.textContent=`${w.readiness_base??'–'} Punkte · 50 + 2 Punkte je Prozentpunkt unter/über MSP-Median`;
    if(document.getElementById('readinessConsistencyInfo')) readinessConsistencyInfo.textContent=`${w.readiness_consistency_modifier>=0?'+':''}${w.readiness_consistency_modifier??'–'} Punkte`;
    if(document.getElementById('readinessHitInfo')) readinessHitInfo.textContent=`${w.readiness_hit_modifier>=0?'+':''}${w.readiness_hit_modifier??'–'} Punkte · ${w.median_hit_count??0} von ${w.median_normalized_sample_count??0} unter/auf Median (${w.median_hit_rate??'–'}%)`;
    if(document.getElementById('readinessRecencyInfo')) readinessRecencyInfo.textContent=`${w.readiness_recency_modifier>=0?'+':''}${w.readiness_recency_modifier??'–'} Punkte`;
    if(document.getElementById('readinessImprovementInfo')) readinessImprovementInfo.textContent=`${w.readiness_improvement_modifier>=0?'+':''}${w.readiness_improvement_modifier??'–'} Punkte`;
    if(document.getElementById('readinessSampleInfo')) readinessSampleInfo.textContent=`${w.median_normalized_sample_count??0} vergleichbare 500er · Trainingsbelastung: kein Einfluss`;
    if(document.getElementById('readinessMethodText')) readinessMethodText.textContent=w.readiness_explanation||w.readiness_definition||'';
    if(document.getElementById('readinessRawFormInfo')) readinessRawFormInfo.textContent=(w.median_normalized_form_percent==null?'–':`${w.median_normalized_form_percent>=0?'+':''}${w.median_normalized_form_percent}%`);
    if(document.getElementById('readinessWeightedFormInfo')) readinessWeightedFormInfo.textContent=(w.weighted_form_percent==null?'–':`${w.weighted_form_percent>=0?'+':''}${w.weighted_form_percent}%`);
    if(document.getElementById('readinessBlendedFormInfo')) readinessBlendedFormInfo.textContent=(w.readiness_form_percent==null?'–':`${w.readiness_form_percent>=0?'+':''}${w.readiness_form_percent}% · 70% Gesamtform / 30% Aktualität`);
    if(document.getElementById('readinessMedianAudit')){
      try{
        const a=Array.isArray(w.median_samples)?w.median_samples:[];
        readinessMedianAudit.innerHTML=a.length?a.map((s,i)=>{
          const ok=s.median_reached===true;
          const pct=Number(s.performance_percent);
          const pctText=Number.isFinite(pct)?`${pct>=0?'+':''}${pct.toFixed(1)}%`:'–';
          return `<div style="padding:5px 0;border-top:${i?'1px solid #edf0f4':'0'}"><strong>${i+1}. ${readinessEsc(s.puzzle_name||'Puzzle')}</strong> · letzte Zeit ${readinessTime(s.seconds)} · MSP-Median ${readinessTime(s.median_seconds)} · <strong>${ok?'✓ Median erreicht':'✗ über Median'}</strong> · ${pctText}</div>`;
        }).join(''):'Keine vergleichbaren Median-Daten vorhanden.';
      }catch(auditError){
        readinessMedianAudit.textContent='Median-Nachweis konnte nicht dargestellt werden: '+(auditError?.message||'unbekannter Darstellungsfehler');
      }
    }
   wmPhase.textContent=(w.days_until!=null?`Noch ${w.days_until} Tage · `:'')+(w.phase?.name||'Planung')+' · '+(w.phase?.description||'')+(w.median_hit_rate!=null?` · ${w.median_hit_rate}% Median erreicht (${w.median_normalized_sample_count||0} Puzzle)`:``);
   if(document.getElementById('wmGoalFirstTry')) wmGoalFirstTry.textContent=w.wm_goal_first_try||w.wm_goal_realistic||'–';
   if(document.getElementById('wmGoalRepeat')) wmGoalRepeat.textContent=w.wm_goal_repeat||w.wm_goal_realistic||'–';
   wmStretch.textContent=w.wm_goal_stretch||'–';
   wmZone.textContent=w.current_zone?`${w.current_zone.from}–${w.current_zone.to}`:'–';
   wmTarget.textContent=w.dynamic_target||'–';
   wmTrend.textContent=w.trend10_percent==null?'Noch kein stabiler 500er-Trend':`500er-Trend ${pct(w.trend10_percent)}`;
   wmTrainingType.textContent=w.next_training?.type||'–';
   wmTrainingReason.textContent=w.next_training?`${w.next_training.intensity} · ${w.next_training.reason}`:'–';
   wmRecommendation.textContent=w.recommendation||'Trainingsplan aus vorhandenem Datenstand berechnet.';
   let np=w.next_puzzle||{};
   wmNextPuzzle.innerHTML=np.available
     ? `<div class="puzzleRow">${puzzleImg(np)}<div class="puzzleInfo"><strong>${np.name}</strong>${np.manufacturer?' · '+np.manufacturer:''}${np.pieces?' · '+np.pieces+' Teile':''}<br><span class="small">${np.reason}</span><br><span class="pill">Bibliothek: ${np.library_candidates} passende 500er</span><span class="pill">${np.previous_solo_solves||0} bisherige Solo-Läufe</span>${np.days_since_last_solve!=null?`<span class="pill">zuletzt vor ${np.days_since_last_solve} Tagen</span>`:'<span class="pill">noch nie Solo gelöst</span>'}${np.wm_fit?`<span class="pill wmFit">WM-Fit ${np.wm_fit.score}/100</span><div class="fitReason">${np.wm_fit.summary||''}</div>`:''}${puzzleInsightHtml(np)}${np.wm_suitability?`<span class="pill ${np.wm_suitability.level==='hoch'||np.wm_suitability.level==='gut'?'wmGood':''}">${np.wm_suitability.label}</span>`:''}${np.competition_risk?.score>=80?`<div class="small riskHigh" style="padding:7px;border-radius:8px;margin-top:7px">⚠️ ${np.competition_risk.reason}</div>`:''}<br><button class="skipBtn" onclick='skipPuzzle(${JSON.stringify(np)})'>Skip – aktuell ausgeliehen</button></div></div>`
     : `<span class="small">${np.reason||'Keine eindeutige Bibliotheks-Empfehlung verfügbar.'}</span><br><span class="pill">Bibliotheks-Puzzles erkannt: ${np.library_total||0}</span>`;
   wmLoad7.textContent=w.training_load_7?w.training_load_7.units.toFixed(1):'–'; wmLoad7Info.textContent=w.training_load_7?`${w.training_load_7.sessions} Einheiten · 500er-Äquivalente`:'–';
   wmLoad14.textContent=w.training_load_14?w.training_load_14.units.toFixed(1):'–'; wmLoad14Info.textContent=w.training_load_14?`${w.training_load_14.sessions} Einheiten · 500er-Äquivalente`:'–';
   wmPace100.textContent=w.wm_pace_per_100||'–'; wmWeakness.textContent=w.weakness_focus?`Aktueller Fokus: ${w.weakness_focus}`:'–';
   wmStats.textContent=w.count?`${w.count} × 500er Solo · Best ${w.best} · Median ${w.median} · Ø letzte 5 ${w.recent5} · Ø letzte 10 ${w.recent10} · Ø letzte 20 ${w.recent20}`:'Noch keine 500er-Daten.';
   progressCurrent.textContent=w.recent10||'–';progressTraining.textContent=w.dynamic_target||'–';progressGoal.textContent=w.wm_goal_first_try||w.wm_goal_realistic||'–';progressStretch.textContent=w.wm_goal_stretch||'–';
   let pr=w.progress_recent||[];
   if(pr.length){
     let vals=pr.map(x=>x.seconds), mn=Math.min(...vals,w.wm_goal_stretch_seconds||99999), mx=Math.max(...vals);
     let span=Math.max(1,mx-mn);
     wmProgressSummary.innerHTML=`<strong>Aktuelles Niveau: Ø ${w.recent10}</strong> · realistisches WM-Ziel <strong>${w.wm_goal_realistic}</strong> · Trainingsziel <strong>${w.dynamic_target}</strong>${w.trend10_percent!=null?`<div class="small">Trend gegenüber dem vorherigen Vergleichsfenster: <strong>${pct(w.trend10_percent)}</strong>. Ziele werden nach jeder Synchronisation neu berechnet.</div>`:''}`;
     wmProgressChart.innerHTML=`<div class="progressBars">${pr.map(x=>{let h=35+((mx-x.seconds)/span)*105;let d=x.finished_at?new Date(x.finished_at).toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit'}):'';return `<div class="pbar" title="${x.puzzle_name||''}"><div class="pbarFill" style="height:${Math.max(20,h)}px"></div><div class="pbarTime">${x.time}</div><div class="pbarDate">${d}</div></div>`}).join('')}</div><div class="progressLegend"><span class="pill">Ø letzte 10: ${w.recent10}</span><span class="pill">WM-Ziel: ${w.wm_goal_realistic}</span><span class="pill">Stretch: ${w.wm_goal_stretch}</span></div>`;
   }else{wmProgressSummary.textContent='Noch nicht genügend 500er-Daten.';wmProgressChart.innerHTML='';}

   wmWeeklyPlan.innerHTML=(w.weekly_plan||[]).map((s,i)=>{
     let p=s.puzzle||{};
     let puzzleLine=p.available
       ? `<div class="puzzleRow" style="margin-top:9px">${puzzleImg(p)}<div class="puzzleInfo"><strong>🧩 ${p.name}</strong>${p.manufacturer?' · '+p.manufacturer:''}${p.pieces?' · '+p.pieces+' Teile':''}<div class="small">${p.reason||''}</div><span class="pill">${p.previous_solo_solves||0} bisherige Solo-Läufe</span>${p.days_since_last_solve!=null?`<span class="pill">zuletzt vor ${p.days_since_last_solve} Tagen</span>`:'<span class="pill">noch nie Solo gelöst</span>'}${p.wm_fit?`<span class="pill wmFit">WM-Fit ${p.wm_fit.score}/100</span><div class="fitReason">${p.wm_fit.summary||''}</div>`:''}${puzzleInsightHtml(p)}${p.wm_suitability?`<span class="pill ${p.wm_suitability.level==='hoch'||p.wm_suitability.level==='gut'?'wmGood':''}">${p.wm_suitability.label}</span>`:''}${p.competition_risk?.score>=80?`<div class="small riskHigh" style="padding:7px;border-radius:8px;margin-top:7px">⚠️ ${p.competition_risk.reason}</div>`:''}<br><button class="skipBtn" style="margin-top:8px" onclick='skipPuzzle(${JSON.stringify(p)})'>Skip – ausgeliehen</button></div></div>`
       : (p.not_required?`<div class="small" style="margin-top:7px">🧩 ${p.reason}</div>`:`<div class="small" style="margin-top:7px">🧩 ${p.reason||'Kein Bibliotheks-Puzzle verfügbar.'}</div>`);
     return `<div class="item"><strong>${i+1}. ${s.session}</strong><div class="small">${s.goal}</div><span class="pill">${s.intensity}</span>${puzzleLine}</div>`;
   }).join('')||'<div class="small">Kein Trainingsplan verfügbar.</div>';
   let simCandidate=w.simulation_puzzle?.available?w.simulation_puzzle:null;
   let firstTrySec=w.wm_goal_first_try_seconds||w.wm_goal_realistic_seconds||goalTargetSeconds(w.wm_goal_realistic||'');
   let repeatSec=w.wm_goal_repeat_seconds||w.wm_goal_realistic_seconds||goalTargetSeconds(w.wm_goal_realistic||'');
   let realSec=(simCandidate && Number(simCandidate.previous_solo_solves||0)>0)?repeatSec:firstTrySec;
   let stretchSec=w.wm_goal_stretch_seconds||goalTargetSeconds(w.wm_goal_stretch||'');
   if(simCandidate){
     wmSimSuggestion.innerHTML=`<div class="puzzleRow">${puzzleImg(simCandidate)}<div class="puzzleInfo"><strong>🧩 ${simCandidate.name}</strong>${simCandidate.manufacturer?' · '+simCandidate.manufacturer:''}${simCandidate.pieces?' · '+simCandidate.pieces+' Teile':''}<div class="small">WM-Fit ${simCandidate.wm_fit?.score||'–'}/100 · Basis First Try ${w.wm_goal_first_try||w.wm_goal_realistic||'–'} · bekannt ${w.wm_goal_repeat||w.wm_goal_realistic||'–'} · MSP Prediction ${simCandidate.msp_prediction||'derzeit nicht verfügbar'}${simCandidate.msp_prediction_range_from&&simCandidate.msp_prediction_range_to?` · Bereich ${simCandidate.msp_prediction_range_from}–${simCandidate.msp_prediction_range_to}`:''} · Stretch ${w.wm_goal_stretch||'–'}</div><div class="small">Dieses Puzzle ist bewusst nicht im normalen Wochenplan enthalten und nicht als ausgeliehen markiert.</div><button class="primary" style="margin-top:8px" onclick='startWMSimulation(${JSON.stringify(simCandidate)},${realSec||'null'},${realSec||'null'},${stretchSec||'null'})'>WM-Simulation starten</button></div></div>`;
   }else{
     wmSimSuggestion.innerHTML='<div class="small">Aktuell kein zusätzliches verfügbares 500er-Puzzle für eine separate WM-Simulation gefunden.</div>';
   }


 }catch(e){
   wmRecommendation.textContent='WM-Coach konnte nicht live aktualisiert werden. Der letzte Server-Snapshot bleibt erhalten.';
   if(resilientBannerEl) resilientBannerEl.style.display='block';
   resilientText.textContent='Live-Aktualisierung fehlgeschlagen. Vorhandene Trainingsanalyse bleibt verfügbar.';
 }


 try{
   let r=await swissPromise;
   if(!r.players||!r.players.length){
     swissRankSummary.textContent=r.subtitle||'Vergleichsgruppe derzeit nicht verfügbar.';
     swissRankList.innerHTML='';
   }else{
     let me=r.nicole;
     swissRankSummary.innerHTML=me
       ? `<strong>Nicole: Platz ${me.rank} von ${r.count}</strong> · Ø ${me.average}${me.top?' · Best '+me.top:''}
          <div class="small" style="margin-top:5px">${me.rank>1?`🥇 Abstand zu Platz 1: <strong>${fmtGap(r.gap_to_first_seconds)}</strong> · 🎯 bis zum nächsten Platz: <strong>${fmtGap(r.gap_to_next_seconds)}</strong>`:'🥇 Aktuell Platz 1 in dieser Vergleichsgruppe.'}</div>
          ${r.target_average_seconds?`<div class="small">Motivationsziel: Ø <strong>${fmtSeconds(r.target_average_seconds)}</strong>${r.motivation?' · '+r.motivation:''}</div>`:''}
          <div class="small">${r.subtitle}</div><div class="small" style="margin-top:5px"><strong>Datenbasis:</strong> öffentlich angezeigte Profil-Durchschnittszeit${me.puzzles_solved!=null?' · '+me.puzzles_solved+' gelöste Puzzles bei Nicole':''}. Diese Kennzahl ist nicht auf identische 500er-Puzzles oder denselben Zeitraum normiert und wird deshalb bewusst nicht für den Trainingsplan verwendet.</div>`
       : `<strong>${r.count} Schweizer Vergleichsprofile gefunden</strong><div class="small">Nicole konnte in dieser Vergleichsgruppe aktuell nicht eindeutig zugeordnet werden. ${r.subtitle}</div>`;
     let show=[...r.players.slice(0,8)];
     if(me && !show.some(x=>x.player_id===me.player_id))show.push(me);
     swissRankList.innerHTML=show.map(x=>`<div class="item ${x.is_nicole?'rankMe':''}"><div class="rankRow"><div class="rankNum">#${x.rank}</div><div><strong>${x.is_nicole?'⭐ ':''}${x.name}</strong><div class="small">${x.puzzles_solved!=null?x.puzzles_solved+' Puzzles · ':''}${x.top?'Best '+x.top:''}</div></div><div class="rankTime">Ø ${x.average}</div></div></div>`).join('');
   }
 }catch(e){
   swissRankSummary.textContent='Schweizer Vergleich derzeit nicht verfügbar.';
   swissRankList.innerHTML='';
 }

 try{
   let data=await competitionsPromise;let rows=data.competitions||[];
   if(rows.length){let c=rows[0];nextMspCompetition.innerHTML=`<strong>${c.name}</strong><br>${dateText(c.date_from)}${c.location?' · '+c.location:''}${c.country_code?' · '+c.country_code.toUpperCase():''}<br><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>`;
   mspCompetitions.innerHTML=rows.map(c=>`<div class="item"><strong>${c.name}</strong><div class="small">${dateText(c.date_from)}${c.date_to?' – '+dateText(c.date_to):''}${c.location?' · '+c.location:''}</div><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>${c.link?`<br><a class="btn secondary" style="margin-top:8px" href="${c.link}" target="_blank">Turnier öffnen</a>`:''}</div>`).join('')}
   else{nextMspCompetition.textContent='Keine bestätigte zukünftige Anmeldung gefunden.';mspCompetitions.innerHTML='<div class="small">Keine bestätigten zukünftigen Turniere.</div>'}
 }catch(e){
   if(!nextMspCompetition.innerHTML || nextMspCompetition.textContent.includes('Prüfe bestätigte Anmeldung')){
     nextMspCompetition.textContent='Live-Anmeldung derzeit nicht erreichbar.';
   }
 }

}
document.addEventListener('DOMContentLoaded',()=>{
  initAppNavigation();
  renderActiveWMSim();
  renderWMSimHistory();
  loadAll();
});
</script><nav class="appBottomNav" aria-label="App Navigation">
<button type="button" data-target="appToday"><span>🏠</span><small>Heute</small></button>
<button type="button" data-target="appTraining"><span>🧩</span><small>Training</small></button>
<button type="button" data-target="appWM"><span>🏁</span><small>WM</small></button>
<button type="button" data-target="appProgress"><span>📈</span><small>Fortschritt</small></button>
<button type="button" data-target="appMore"><span>⋯</span><small>Mehr</small></button>
</nav>
</body></html>
"""

def dashboard():
    return HTMLResponse(DASHBOARD_HTML)
