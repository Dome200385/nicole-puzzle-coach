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
.trainingPriorityGroup>.item:first-of-type+ .item{margin-top:0!important}
  .trainingPriorityGroup{display:flex;flex-direction:column;gap:10px}
  .trainingPriorityGroup>.item,.trainingAnalysisBottom .trainingDropdownBody>.item{margin:0!important}
  .trainingDropdownBody{display:flex;flex-direction:column;gap:10px}
  .trainingListIntro{margin-bottom:0}
  .loanActions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
  .restoreBtn{background:#eef0f4;color:var(--text);border:0;border-radius:9px;padding:7px 10px;font-weight:800;cursor:pointer}
}
@media(max-width:760px){
  #wmWeeklyPlan{display:flex;flex-direction:column;gap:7px}
  .weeklySession{padding:0!important;overflow:hidden;margin:0!important}
  .weeklySession summary{
    list-style:none;display:grid;grid-template-columns:30px 58px minmax(0,1fr) auto;
    gap:9px;align-items:center;padding:10px;cursor:pointer
  }
  .weeklySession summary::-webkit-details-marker{display:none}
  .weeklySession summary:after{content:"›";font-size:22px;color:#94a3b8;grid-column:4;grid-row:1;justify-self:end;transform:rotate(90deg)}
  .weeklySession[open] summary:after{transform:rotate(-90deg)}
  .weeklyIndex{
    width:28px;height:28px;border-radius:50%;background:#f1f5f9;
    display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px
  }
  .weeklyThumb{width:58px;height:58px;border-radius:9px;object-fit:cover;background:#f1f5f9}
  .weeklyThumbEmpty{display:flex;align-items:center;justify-content:center;font-size:22px}
  .weeklySummaryText{min-width:0;padding-right:3px}
  .weeklySessionTitle{display:flex;align-items:center;gap:6px;min-width:0}
  .weeklySessionTitle strong{font-size:14px;line-height:1.15}
  .weeklyPuzzleName{font-size:13px;font-weight:700;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.18}
  .weeklySummaryText .small{font-size:10px;line-height:1.2;margin-top:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .weeklyIntensity{font-size:8px;white-space:nowrap;flex:0 0 auto}
  .weeklyDetail{border-top:1px solid var(--border);padding:10px 12px 12px}
  .weeklyFacts{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:2px}
  .weeklyFact{background:#f8fafc;border:1px solid #eef2f7;border-radius:9px;padding:8px 9px;min-width:0}
  .weeklyFact span{display:block;font-size:9px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
  .weeklyFact strong{display:block;font-size:13px;line-height:1.2;margin-top:2px;overflow-wrap:anywhere}
  .weeklyCoachReason{font-size:10px;line-height:1.35;color:var(--muted);margin-top:8px}
  .weeklyPills{margin-top:7px}
}

.wmHeroGrid{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:10px;margin:4px 0 12px}.wmHeroReadiness,.wmHeroGoal{border:1px solid var(--line);border-radius:14px;background:#fafafa;padding:14px}.wmHeroReadiness strong{display:block;font-size:34px;margin-top:4px}.wmHeroGoal strong{display:block;font-size:24px;margin-top:4px}.wmMovedPanels{display:grid;gap:10px}.wmMovedPanels .readinessInfo,.wmMovedPanels #readinessTrendPanel{margin:0}
.wmDashboard .simHero{margin:10px 0 0}.wmProgressCompact{display:flex;gap:8px;flex-wrap:wrap}.wmProgressCompact span{background:#f8fafc;border:1px solid #eef2f7;border-radius:10px;padding:8px 10px;font-size:12px}.wmProgressCompact b{display:block;font-size:9px;text-transform:uppercase;color:var(--muted);letter-spacing:.04em}.wmMobileBars .pbarTime,.wmMobileBars .pbarDate{font-size:9px;white-space:nowrap}
@media(max-width:760px){.wmDashboard>h2{font-size:19px}.wmHeroGrid{grid-template-columns:1fr 1fr}.wmHeroReadiness{grid-column:1/-1}.wmHeroReadiness strong{font-size:40px}.wmHeroGoal strong{font-size:22px}.wmMovedPanels .readinessInfo{padding:10px}.wmMovedPanels .readinessFormula{grid-template-columns:1fr 1fr}.wmMovedPanels #readinessTrendBars{height:70px}.wmMobileBars{gap:7px}.wmMobileBars .pbarTime,.wmMobileBars .pbarDate{font-size:8px}.wmDashboard .simHero h2{font-size:18px}}

/* V6.10.4 hard mobile page isolation: prevents content leaking between tabs */
@media(max-width:760px){
  body[data-current-page="today"] section[data-app-page]:not([data-app-page="today"]),
  body[data-current-page="training"] section[data-app-page]:not([data-app-page="training"]),
  body[data-current-page="wm"] section[data-app-page]:not([data-app-page="wm"]),
  body[data-current-page="progress"] section[data-app-page]:not([data-app-page="progress"]),
  body[data-current-page="more"] section[data-app-page]:not([data-app-page="more"]){display:none!important}
  .todayGridSingle{grid-template-columns:1fr!important}
  .wmHeroGrid{grid-template-columns:1fr 1fr!important}
  .wmHeroReadiness{grid-column:1/-1!important}
}

@media(max-width:760px){
  .grid>section[data-app-page]{display:none!important}
  .grid>section[data-app-page].appPageActive:not([hidden]){display:block!important}
  .grid>section.card.kpi[data-app-page="today"].appPageActive:not([hidden]):nth-of-type(1),
  .grid>section.card.kpi[data-app-page="today"].appPageActive:not([hidden]):nth-of-type(3){grid-column:span 6!important}
  .grid>section.card.kpi[data-app-page="today"].appPageActive:not([hidden]):nth-of-type(2){grid-column:1/-1!important}
}
@media(min-width:761px){.grid>section[data-app-page][hidden]{display:block!important}}

@media(max-width:760px){
  body[data-app-current="today"] .trainingOnlyPuzzleLists,
  body[data-app-current="today"] #appTraining,
  body[data-app-current="today"] #appWM,
  body[data-app-current="today"] [data-app-page="progress"]{display:none!important}
}

@media(max-width:760px){
  .trainingWeeklyPlan{margin-top:10px!important}
  .trainingDropdown{padding:0!important;overflow:hidden;margin-top:8px!important}
  .trainingDropdown summary{
    list-style:none;cursor:pointer;padding:11px 12px;font-weight:800;
    display:flex;align-items:center;justify-content:space-between;gap:10px
  }
  .trainingDropdown summary::-webkit-details-marker{display:none}
  .trainingDropdown summary:after{
    content:"⌄";font-size:16px;color:#94a3b8;transition:transform .15s ease
  }
  .trainingDropdown[open] summary:after{transform:rotate(180deg)}
  .trainingDropdownBody{
    border-top:1px solid var(--border);
    padding:10px 12px 12px
  }
}

@media(max-width:760px){
 .puzzleChoiceDetail{border-top:1px solid #e5e7eb}
 .puzzleChoiceDetail:first-of-type{border-top:0}
 .puzzleChoiceDetail summary{list-style:none;display:grid;grid-template-columns:52px minmax(0,1fr) auto;gap:9px;align-items:center;padding:9px 0;cursor:pointer}
 .puzzleChoiceDetail summary::-webkit-details-marker{display:none}
 .puzzleChoiceDetail summary:after{content:"›";font-size:20px;color:#94a3b8;transform:rotate(90deg)}
 .puzzleChoiceDetail[open] summary:after{transform:rotate(-90deg)}
 .puzzleChoiceThumb{width:52px;height:52px;border-radius:8px;object-fit:cover;background:#f1f5f9}
 .puzzleChoiceDetail summary span{min-width:0}
 .puzzleChoiceDetail summary strong{display:block;font-size:13px;line-height:1.2}
 .puzzleChoiceDetail summary small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
 .puzzleChoiceBody{padding:0 0 10px 61px;font-size:11px;line-height:1.4;color:var(--muted)}
}

@media(max-width:760px){
 .puzzleChoiceDetail{border-top:1px solid #e5e7eb}
 .puzzleChoiceDetail:first-of-type{border-top:0}
 .puzzleChoiceDetail summary{list-style:none;display:grid;grid-template-columns:54px minmax(0,1fr) auto;gap:9px;align-items:center;padding:9px 0;cursor:pointer}
 .puzzleChoiceDetail summary::-webkit-details-marker{display:none}
 .puzzleChoiceDetail summary:after{content:"›";font-size:20px;color:#94a3b8;transform:rotate(90deg)}
 .puzzleChoiceDetail[open] summary:after{transform:rotate(-90deg)}
 .puzzleChoiceThumb{width:54px;height:54px;border-radius:8px;object-fit:cover;background:#f1f5f9}
 .puzzleChoiceDetail summary span{min-width:0}
 .puzzleChoiceDetail summary strong{display:block;font-size:13px;line-height:1.2}
 .puzzleChoiceDetail summary small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
 .puzzleChoiceBody{padding:0 0 10px 63px;font-size:11px;line-height:1.4;color:var(--muted)}
}

@media(max-width:760px){
  .trainingDropdownBody{padding:8px 9px 10px!important}
  .trainingListIntro{margin:2px 2px 8px!important}
  .trainingPuzzleSession{margin:0!important}
  .trainingPuzzleSession:first-of-type{margin-top:0!important}
  .trainingPuzzleSession + .trainingPuzzleSession{margin-top:10px!important}

  /* One visual system for every puzzle card in Training */
  .trainingPuzzleSession summary{
    grid-template-columns:32px 68px minmax(0,1fr) 18px!important;
    gap:10px!important;
    align-items:center!important;
    min-height:102px;
    padding:12px!important;
  }
  .trainingPuzzleSession .weeklyIndex{
    width:32px;height:32px;font-size:14px
  }
  .trainingPuzzleSession .weeklyThumb{
    width:68px;height:68px;border-radius:11px;object-fit:cover
  }
  .trainingPuzzleSession .weeklySummaryText{
    display:flex;flex-direction:column;justify-content:center;min-width:0;
    padding:0!important
  }
  .trainingPuzzleSession .weeklySessionTitle{
    display:flex;align-items:flex-start;justify-content:space-between;gap:6px
  }
  .trainingPuzzleSession .weeklySessionTitle strong{
    font-size:15px!important;line-height:1.18!important;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden
  }
  .trainingPuzzleSession .weeklyPuzzleName{
    font-size:12px!important;line-height:1.25!important;margin-top:3px!important;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis
  }
  .trainingPuzzleSession .weeklySummaryText .small{
    font-size:11px!important;line-height:1.28!important;margin-top:3px!important;
    display:block!important;white-space:normal!important
  }
  .trainingPuzzleSession .weeklyFacts{grid-template-columns:1fr 1fr}
  .trainingPuzzleSession summary:after{grid-column:4!important}

  .skipBtnCompact{
    margin:8px 0 0!important;padding:7px 10px!important;
    font-size:11px!important;line-height:1.1!important;
    width:max-content;max-width:100%;
    background:#fff!important;border:1px solid #e89191!important;
    color:#a63a3a!important;border-radius:9px!important
  }

  /* Today-training hero: explanation and action may never run into each other */
  .trainingQuick{padding:14px!important}
  .trainingQuickHero{grid-template-columns:92px minmax(0,1fr)!important;gap:14px!important}
  .trainingQuickImage{width:92px!important;height:92px!important;border-radius:13px!important}
  .trainingQuickMain strong{font-size:19px!important;line-height:1.15!important}
  .trainingQuickReason{margin-top:10px!important}
  .trainingQuickReasonText{
    display:block;font-size:11px;line-height:1.45;color:var(--muted);
    overflow-wrap:anywhere
  }
  .trainingQuickAction{display:block;margin-top:10px}
  .trainingQuickAction .skipBtn{
    margin:0!important;width:100%;padding:10px 12px!important;
    font-size:13px!important
  }

  /* Weekly plan uses the same spacing and dimensions */
  #wmWeeklyPlan{gap:10px!important}
  #wmWeeklyPlan .weeklySession{margin:0!important}
}

.diagPre{
 white-space:pre-wrap;word-break:break-word;
 font-size:10px;line-height:1.35;
 background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;
 padding:9px;margin-top:8px;max-height:300px;overflow:auto
}
.diagDetails summary{cursor:pointer}

/* === TRAINING FIXED GRID CARDS === */
@media(max-width:760px){
  .trainingPuzzleSession{margin:0!important;border-radius:14px!important;overflow:hidden}
  .trainingPuzzleSession + .trainingPuzzleSession{margin-top:10px!important}

  .trainingPuzzleSession > summary{
    display:grid!important;
    grid-template-columns:36px 74px minmax(0,1fr) 68px 18px!important;
    column-gap:10px!important;
    align-items:center!important;
    min-height:116px!important;
    padding:12px 10px!important;
    list-style:none!important
  }
  .trainingPuzzleSession > summary::-webkit-details-marker{display:none!important}

  .trainingPuzzleSession .weeklyIndex{
    grid-column:1!important;width:34px!important;height:34px!important;min-width:34px!important;
    display:flex!important;align-items:center!important;justify-content:center!important;
    margin:0!important;align-self:center!important;
    background:#f1f5f9!important;color:#475569!important;border:0!important;box-shadow:none!important
  }
  .trainingPuzzleSession .weeklyThumb{
    grid-column:2!important;width:74px!important;height:74px!important;
    max-width:74px!important;max-height:74px!important;object-fit:cover!important;
    border-radius:12px!important;margin:0!important;align-self:center!important
  }
  .trainingPuzzleSession .weeklySummaryText{
    grid-column:3!important;min-width:0!important;padding:0!important;margin:0!important;align-self:center!important
  }
  .trainingPuzzleSession .weeklySessionTitle{
    display:block!important;position:relative!important;min-width:0!important
  }
  .trainingPuzzleSession .weeklySessionTitle strong{
    display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;
    overflow:hidden!important;font-size:15px!important;line-height:1.18!important;margin:0!important;max-width:100%!important
  }
  .trainingPuzzleSession .weeklyPuzzleName{
    margin-top:3px!important;font-size:12px!important;line-height:1.22!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important
  }
  .trainingPuzzleSession .weeklySummaryText>.small{
    display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;
    overflow:hidden!important;margin-top:3px!important;font-size:11px!important;line-height:1.25!important;min-height:28px!important
  }
  .trainingPuzzleSession .weeklyIntensity{
    position:absolute!important;left:calc(100% + 10px)!important;top:0!important;
    width:68px!important;margin:0!important;text-align:center!important;white-space:nowrap!important;
    font-size:10px!important;padding:5px 4px!important
  }
  .trainingPuzzleSession > summary:after{
    grid-column:5!important;justify-self:center!important;align-self:center!important;margin:0!important
  }
  .trainingPuzzleSession .skipBtnCompact{
    display:block!important;margin:8px 0 0!important;width:100%!important;max-width:190px!important;
    min-height:34px!important;padding:7px 10px!important;font-size:11px!important;line-height:1.1!important;white-space:nowrap!important
  }
  .trainingPuzzleSession .weeklyDetail{
    margin:0 10px 10px 130px!important;padding-top:8px!important
  }

  #wmWeeklyPlan .trainingPuzzleSession > summary{
    grid-template-columns:36px 74px minmax(0,1fr) 68px 18px!important
  }

  .trainingQuick{padding:14px!important}
  .trainingQuickHero{
    display:grid!important;grid-template-columns:96px minmax(0,1fr)!important;
    gap:14px!important;align-items:center!important
  }
  .trainingQuickImage{width:96px!important;height:96px!important;border-radius:13px!important;margin:0!important}
  .trainingQuickMain{min-width:0!important}
  .trainingQuickMain strong{font-size:19px!important;line-height:1.15!important}
  .trainingQuickStats{grid-template-columns:1fr 1fr 1fr 1fr!important;gap:6px!important;margin-top:12px!important}
  .trainingQuickStats>div{padding:8px!important;min-height:62px!important}
  .trainingQuickStats span{font-size:9px!important}
  .trainingQuickStats strong{font-size:13px!important;line-height:1.2!important}
  .trainingQuickReason{margin-top:9px!important}
  .trainingQuickReasonText{font-size:10.5px!important;line-height:1.38!important}
  .trainingQuickAction{margin-top:9px!important}
  .trainingQuickAction .skipBtn{
    width:auto!important;min-width:190px!important;max-width:100%!important;padding:9px 12px!important
  }
}


/* === SKIP BUTTON PLACEMENT: MEDIAN / REPEAT / UNSOLVED ONLY === */
@media(max-width:760px){
  #medianGapFocus .trainingPuzzleSession > summary,
  #repeatPriority .trainingPuzzleSession > summary,
  #unsolvedLibrary .trainingPuzzleSession > summary{
    grid-template-columns:36px 74px minmax(0,1fr) 18px!important;
    grid-template-rows:auto auto!important;
    column-gap:10px!important;
    row-gap:8px!important;
    align-items:center!important;
    min-height:132px!important
  }

  #medianGapFocus .trainingPuzzleSession .weeklyIndex,
  #repeatPriority .trainingPuzzleSession .weeklyIndex,
  #unsolvedLibrary .trainingPuzzleSession .weeklyIndex{
    grid-column:1!important;
    grid-row:1 / 3!important;
    align-self:center!important
  }

  #medianGapFocus .trainingPuzzleSession .weeklyThumb,
  #repeatPriority .trainingPuzzleSession .weeklyThumb,
  #unsolvedLibrary .trainingPuzzleSession .weeklyThumb{
    grid-column:2!important;
    grid-row:1 / 3!important;
    align-self:center!important
  }

  #medianGapFocus .trainingPuzzleSession .weeklySummaryText,
  #repeatPriority .trainingPuzzleSession .weeklySummaryText,
  #unsolvedLibrary .trainingPuzzleSession .weeklySummaryText{
    grid-column:3!important;
    grid-row:1!important;
    align-self:end!important;
    min-width:0!important
  }

  /* Repeat-priority badge remains inside the text block, but no longer steals text width. */
  #repeatPriority .trainingPuzzleSession .weeklyIntensity{
    position:static!important;
    display:inline-block!important;
    width:auto!important;
    margin:5px 0 0!important;
    padding:4px 9px!important;
    text-align:center!important
  }

  #medianGapFocus .trainingPuzzleSession .skipBtnCompact,
  #repeatPriority .trainingPuzzleSession .skipBtnCompact,
  #unsolvedLibrary .trainingPuzzleSession .skipBtnCompact{
    grid-column:3!important;
    grid-row:2!important;
    justify-self:start!important;
    align-self:start!important;
    display:block!important;
    width:auto!important;
    min-width:156px!important;
    max-width:100%!important;
    min-height:36px!important;
    margin:0!important;
    padding:8px 12px!important;
    white-space:nowrap!important;
    font-size:11px!important;
    line-height:1.1!important
  }

  #medianGapFocus .trainingPuzzleSession > summary:after,
  #repeatPriority .trainingPuzzleSession > summary:after,
  #unsolvedLibrary .trainingPuzzleSession > summary:after{
    grid-column:4!important;
    grid-row:1 / 3!important;
    align-self:center!important
  }

  #medianGapFocus .trainingPuzzleSession .weeklyDetail,
  #repeatPriority .trainingPuzzleSession .weeklyDetail,
  #unsolvedLibrary .trainingPuzzleSession .weeklyDetail{
    margin-left:130px!important
  }
}


/* === SAFE TRAINING INFO ENRICHMENT === */
@media(max-width:760px){
  #medianGapFocus .weeklyDetail,
  #repeatPriority .weeklyDetail,
  #unsolvedLibrary .weeklyDetail{
    margin:0 12px 14px 130px!important;
    padding-top:10px!important
  }
  .trainingFacts4{
    display:grid!important;
    grid-template-columns:1fr 1fr!important;
    gap:8px!important
  }
  .trainingFacts4 .weeklyFact{
    min-width:0!important;
    min-height:70px!important;
    padding:10px!important;
    border:1px solid #e4e8ef!important;
    border-radius:11px!important;
    background:#fff!important
  }
  .trainingFacts4 .weeklyFact span{
    display:block!important;
    color:#7a8393!important;
    font-size:9px!important;
    line-height:1.15!important;
    text-transform:uppercase!important;
    letter-spacing:.035em!important
  }
  .trainingFacts4 .weeklyFact strong{
    display:block!important;
    margin-top:5px!important;
    color:#344054!important;
    font-size:14px!important;
    line-height:1.2!important;
    overflow-wrap:anywhere!important
  }
  .trainingCoachNote{
    width:100%!important;
    box-sizing:border-box!important;
    margin-top:10px!important;
    padding:11px 12px!important;
    border:1px solid #e4e8ef!important;
    border-radius:11px!important;
    background:#f6f8fb!important;
    color:#667085!important;
    font-size:11px!important;
    line-height:1.45!important
  }
  .trainingCoachNote strong{
    display:block!important;
    margin-bottom:4px!important;
    color:#344054!important;
    font-size:11px!important
  }
}


/* =========================================================
   TRAINING VISUAL UNIFICATION — CSS ONLY
   No logic / order / data / structure changes
   ========================================================= */
@media(max-width:760px){

  /* ---------- Shared card language ---------- */
  .trainingPuzzleSession,
  #wmWeeklyPlan .weeklySession{
    border:1px solid #e1e6ee!important;
    border-radius:16px!important;
    background:#fff!important;
    box-shadow:none!important;
    overflow:hidden!important;
  }

  .trainingPuzzleSession + .trainingPuzzleSession,
  #wmWeeklyPlan .weeklySession + .weeklySession{
    margin-top:12px!important;
  }

  /* ---------- Shared top row ---------- */
  .trainingPuzzleSession > summary,
  #wmWeeklyPlan .weeklySession > summary{
    padding:14px 12px!important;
  }

  .trainingPuzzleSession .weeklyThumb,
  #wmWeeklyPlan .weeklyThumb{
    width:82px!important;
    height:82px!important;
    max-width:82px!important;
    max-height:82px!important;
    border-radius:14px!important;
    object-fit:cover!important;
    background:#f4f6f9!important;
  }

  .trainingPuzzleSession .weeklyIndex,
  #wmWeeklyPlan .weeklyIndex{
    width:36px!important;
    height:36px!important;
    min-width:36px!important;
    border-radius:50%!important;
    background:#f5f7fa!important;
    color:#475467!important;
    font-size:15px!important;
    font-weight:700!important;
  }

  .trainingPuzzleSession .weeklySessionTitle strong,
  #wmWeeklyPlan .weeklySessionTitle strong{
    color:#202939!important;
    font-size:16px!important;
    line-height:1.22!important;
    font-weight:750!important;
  }

  .trainingPuzzleSession .weeklyPuzzleName,
  #wmWeeklyPlan .weeklyPuzzleName{
    color:#667085!important;
    font-size:12.5px!important;
    line-height:1.3!important;
    font-weight:600!important;
  }

  .trainingPuzzleSession .weeklySummaryText > .small,
  #wmWeeklyPlan .weeklySummaryText > .small{
    color:#667085!important;
    font-size:11.5px!important;
    line-height:1.35!important;
  }

  .weeklyIntensity{
    border:0!important;
    border-radius:999px!important;
    background:#f2f4f7!important;
    color:#475467!important;
    font-weight:600!important;
    box-shadow:none!important;
  }

  /* ---------- Skip button: identical everywhere ---------- */
  .trainingPuzzleSession .skipBtnCompact,
  #wmWeeklyPlan .skipBtnCompact,
  .trainingQuickAction .skipBtn{
    box-sizing:border-box!important;
    min-height:42px!important;
    border:1.5px solid #df8e8e!important;
    border-radius:12px!important;
    background:#fff!important;
    color:#a83f3f!important;
    font-size:12.5px!important;
    line-height:1.1!important;
    font-weight:750!important;
    box-shadow:none!important;
  }

  #medianGapFocus .trainingPuzzleSession .skipBtnCompact,
  #repeatPriority .trainingPuzzleSession .skipBtnCompact,
  #unsolvedLibrary .trainingPuzzleSession .skipBtnCompact{
    width:100%!important;
    max-width:none!important;
    min-width:0!important;
  }

  /* ---------- Expanded detail: use full usable card width ---------- */
  #medianGapFocus .weeklyDetail,
  #repeatPriority .weeklyDetail,
  #unsolvedLibrary .weeklyDetail,
  #wmWeeklyPlan .weeklyDetail{
    box-sizing:border-box!important;
    margin:0!important;
    padding:0 14px 14px 14px!important;
    width:100%!important;
  }

  /* Key change: metrics no longer look like a narrow right-side column */
  #medianGapFocus .trainingFacts4,
  #repeatPriority .trainingFacts4,
  #unsolvedLibrary .trainingFacts4,
  #wmWeeklyPlan .weeklyFacts{
    display:grid!important;
    grid-template-columns:1fr 1fr!important;
    gap:9px!important;
    width:100%!important;
    margin-top:8px!important;
  }

  #medianGapFocus .trainingFacts4 .weeklyFact,
  #repeatPriority .trainingFacts4 .weeklyFact,
  #unsolvedLibrary .trainingFacts4 .weeklyFact,
  #wmWeeklyPlan .weeklyFact{
    box-sizing:border-box!important;
    min-width:0!important;
    min-height:82px!important;
    padding:12px!important;
    border:1px solid #e2e7ee!important;
    border-radius:13px!important;
    background:#fbfcfd!important;
    box-shadow:none!important;
  }

  #medianGapFocus .weeklyFact span,
  #repeatPriority .weeklyFact span,
  #unsolvedLibrary .weeklyFact span,
  #wmWeeklyPlan .weeklyFact span{
    display:block!important;
    color:#7b8493!important;
    font-size:9.5px!important;
    line-height:1.15!important;
    font-weight:500!important;
    text-transform:uppercase!important;
    letter-spacing:.035em!important;
  }

  #medianGapFocus .weeklyFact strong,
  #repeatPriority .weeklyFact strong,
  #unsolvedLibrary .weeklyFact strong,
  #wmWeeklyPlan .weeklyFact strong{
    display:block!important;
    margin-top:7px!important;
    color:#273142!important;
    font-size:16px!important;
    line-height:1.18!important;
    font-weight:750!important;
    overflow-wrap:anywhere!important;
  }

  /* ---------- Coach card: same visual component everywhere ---------- */
  .trainingCoachNote,
  .weeklyCoachReason,
  #wmWeeklyPlan .weeklyCoachReason{
    box-sizing:border-box!important;
    width:100%!important;
    margin:10px 0 0!important;
    padding:12px 13px!important;
    border:1px solid #dbe6f4!important;
    border-radius:13px!important;
    background:#f7faff!important;
    color:#5f6b7c!important;
    font-size:11.5px!important;
    line-height:1.48!important;
    box-shadow:none!important;
  }

  .trainingCoachNote strong,
  .weeklyCoachReason strong,
  #wmWeeklyPlan .weeklyCoachReason strong{
    display:block!important;
    margin:0 0 5px!important;
    color:#344054!important;
    font-size:12px!important;
    font-weight:750!important;
  }

  /* ---------- More compact expanded cards ---------- */
  #medianGapFocus .trainingPuzzleSession[open],
  #repeatPriority .trainingPuzzleSession[open],
  #unsolvedLibrary .trainingPuzzleSession[open],
  #wmWeeklyPlan .weeklySession[open]{
    padding-bottom:0!important;
    background:#fff!important;
  }

  /* ---------- Adaptive Preparation / "Heute trainieren" ----------
     Same visual language, without touching its structure. */
  .trainingQuick{
    border:1px solid #e1e6ee!important;
    border-radius:16px!important;
    background:#fff!important;
    box-shadow:none!important;
    padding:16px!important;
  }

  .trainingQuickHero{
    gap:14px!important;
    align-items:center!important;
  }

  .trainingQuickImage{
    width:96px!important;
    height:96px!important;
    border-radius:14px!important;
    object-fit:cover!important;
    background:#f4f6f9!important;
  }

  .trainingQuickMain .eyebrow,
  .trainingQuickMain .small{
    color:#7b8493!important;
  }

  .trainingQuickMain strong{
    color:#202939!important;
    font-size:20px!important;
    line-height:1.15!important;
    font-weight:750!important;
  }

  .trainingQuickStats{
    display:grid!important;
    grid-template-columns:1fr 1fr!important;
    gap:9px!important;
    margin-top:13px!important;
  }

  .trainingQuickStats > div{
    box-sizing:border-box!important;
    min-height:82px!important;
    padding:12px!important;
    border:1px solid #e2e7ee!important;
    border-radius:13px!important;
    background:#fbfcfd!important;
  }

  .trainingQuickStats span{
    display:block!important;
    color:#7b8493!important;
    font-size:9.5px!important;
    line-height:1.15!important;
    text-transform:uppercase!important;
    letter-spacing:.035em!important;
  }

  .trainingQuickStats strong{
    display:block!important;
    margin-top:7px!important;
    color:#273142!important;
    font-size:16px!important;
    line-height:1.18!important;
    font-weight:750!important;
  }

  .trainingQuickReason{
    box-sizing:border-box!important;
    width:100%!important;
    margin-top:10px!important;
    padding:12px 13px!important;
    border:1px solid #dbe6f4!important;
    border-radius:13px!important;
    background:#f7faff!important;
  }

  .trainingQuickReasonText{
    color:#5f6b7c!important;
    font-size:11.5px!important;
    line-height:1.48!important;
  }

  /* ---------- Weekly-plan list ----------
     Same look, same existing layout/order/behavior. */
  #wmWeeklyPlan{
    gap:12px!important;
  }

  #wmWeeklyPlan .weeklySession{
    margin:0!important;
  }

  #wmWeeklyPlan .weeklyDetail{
    border-top:0!important;
  }

  #wmWeeklyPlan .weeklyPills{
    margin-top:10px!important;
    gap:6px!important;
  }

  #wmWeeklyPlan .pill{
    border:0!important;
    background:#f2f4f7!important;
    color:#475467!important;
    border-radius:999px!important;
    box-shadow:none!important;
  }

  /* ---------- Section containers ---------- */
  .trainingDropdownBody{
    padding:10px!important;
  }

  .trainingListIntro{
    margin:4px 4px 14px!important;
    color:#77808f!important;
    line-height:1.45!important;
  }
}

</style></head>
<body><div class="wrap">
<header><div><h1>🧩 Nicole Puzzle Coach</h1><div class="sub">Speed-Puzzling Training & Turniervorbereitung</div></div><div class="headerRight"><span class="techStatus"><strong id="systemKpi">–</strong> <span id="systemText">System</span> · <strong id="mspKpi">–</strong> <span id="mspText">MySpeedPuzzling</span></span><div id="systemBadge" class="badge">System wird geprüft…</div><button id="mspRefreshBtn" class="secondary compactRefresh" onclick="refreshFromMSP()">↻ MySpeedPuzzling aktualisieren</button><span id="syncStatusText" class="syncStatusText" aria-live="polite"></span></div></header>

<div class="grid"><div id="appPageHeading" class="appPageHeading">Heute</div>
<section class="card kpi third" data-app-page="today"><div class="label">Form · vs MSP-Median <button class="infoBtn" onclick="showInfo('form')">i</button></div><div class="value" id="trendKpi">–</div><div class="small">letzter Solo-Versuch je vergleichbarem 500er</div></section>
<section class="card kpi third" data-app-page="today"><div class="label">WM-Readiness <button class="infoBtn" onclick="showInfo('readiness')">i</button></div><div class="value" id="readinessTopKpi">–</div><div class="small">50 = MSP-Median-Niveau · 60+ = solide WM-Form</div></section>
<section class="card kpi third" data-app-page="today"><div class="label">Konsistenz <button class="infoBtn" onclick="showInfo('consistency')">i</button></div><div class="value" id="consistencyKpi">–</div><div class="small">median-relative Stabilität · 0–100</div></section>

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

</div>
</div>

<div id="unavailableBox" class="item loanBox" style="display:none;margin-top:10px"><strong>📦 Aktuell nicht verfügbare / ausgeliehene Puzzles</strong><div class="small">Diese Puzzles werden in allen Empfehlungen und im gesamten Wochenplan ausgeschlossen.</div><div id="unavailableList" style="margin-top:7px"></div><button class="secondary" style="margin-top:7px" onclick="restoreAllPuzzles()">Alle wieder verfügbar</button></div><div class="trainingAnalysisBottom trainingOnlyPuzzleLists" style="margin-top:16px">
<h2>🧠 Weitere Trainingsauswahl</h2>

<details class="item trainingDropdown">
<summary>🎯 Größte Abstände zum MSP-Median · Top 5</summary>
<div id="medianGapFocus" class="small trainingDropdownBody">Medianvergleich wird berechnet…</div>
</details>

<details class="item trainingDropdown">
<summary>🔁 Wo lohnt sich die nächste Wiederholung am meisten?</summary>
<div id="repeatPriority" class="small trainingDropdownBody">Wiederholungs-Priorität wird berechnet…</div>
</details>

<details class="item trainingDropdown">
<summary>🆕 Noch ungelöste Puzzle in meiner Library</summary>
<div id="unsolvedLibrary" class="small trainingDropdownBody">Library wird geprüft…</div>
</details>
</div>


</section>



<section class="card full appSection wmDashboard" id="appWM" data-app-page="wm"><h2>🏁 WM · Wettkampfvorbereitung</h2><div class="legacyDataSinks" aria-hidden="true" style="display:none"><span id="wmGoalFirstTry"></span><span id="wmGoalRepeat"></span><span id="wmStretch"></span><span id="wmZone"></span><span id="wmTarget"></span><span id="wmTrend"></span><span id="wmTrainingType"></span><span id="wmTrainingReason"></span><span id="wmRecommendation"></span><span id="wmLoad7"></span><span id="wmLoad7Info"></span><span id="wmLoad14"></span><span id="wmLoad14Info"></span><span id="wmPace100"></span><span id="wmWeakness"></span><span id="wmStats"></span></div><div class="legacyDataSinks" aria-hidden="true" style="display:none"><span id="wmReadiness"></span><span id="wmPhase"></span></div>
<div class="wmHeroGrid">
<div class="wmHeroReadiness"><div class="label">WM-Readiness</div><strong id="wmTabReadiness">–</strong><div class="small" id="wmTabReadinessCompact">Wettkampfform · vergleichbare 500er</div></div>
<div class="wmHeroGoal"><div class="label">First Try</div><strong id="wmTabFirstTry">–</strong></div>
<div class="wmHeroGoal"><div class="label">Bekannt / mehrfach</div><strong id="wmTabRepeat">–</strong></div>
</div>
<div class="item simHero" id="wmSimulationCard" style="margin-top:10px"><h2>🏁 WM-Simulation <span class="pill">V6.10.4</span></h2>
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

<div class="wmMovedPanels"><div id="readinessTrendPanel" class="item" style="margin-top:10px">
<strong>📈 WM-Readiness-Verlauf</strong>
<div class="small">Tägliche Entwicklung der Readiness bis zur WM. Pro Tag wird der aktuelle Wert gespeichert.</div>
<div id="readinessTrendSummary" style="margin-top:6px;font-weight:700">Erster Verlaufspunkt wird gespeichert…</div>
<div id="readinessTrendBars" style="display:flex;align-items:flex-end;gap:4px;height:82px;margin-top:8px"></div>
<div id="readinessTrendChanges" class="small" style="margin-top:7px"></div>
</div>
<h2 style="margin-top:16px">📈 Fortschritt bis zur WM</h2>
<div class="small">Letzte 10 vergleichbare 500er im Verhältnis zum WM-Ziel.
</div>
<div id="wmProgressSummary" class="item" style="margin-top:10px">Fortschritt wird berechnet…</div>
<div id="wmProgressChart" class="item" style="margin-top:8px"></div>
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
<div style="margin-top:9px"><strong>Kontrolle der letzten vergleichbaren 500er</strong><div id="readinessMedianAudit" class="small" style="margin-top:5px">–</div></div></details>
</div>
</section>

<section class="card full" data-app-page="progress"><h2>🇨🇭 Schweizer Motivationsranking</h2>
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
















</div></div>

<div id="infoModal" class="modal" onclick="if(event.target===this)closeInfo()"><div class="modalbox"><div id="infoContent"></div><button class="secondary" onclick="closeInfo()">Schliessen</button></div></div>
<script>
const NPC_FRONTEND_VERSION='6.13.1';
function showInfo(type){
 const form=`<h2>ℹ️ Was bedeutet Form?</h2><p><b>Form</b> zeigt, ob Nicole aktuell schneller oder langsamer puzzelt als in der vorherigen Vergleichsperiode. Dafür werden die letzten 10 Solo-Ergebnisse mit den vorherigen 10 verglichen und auf <b>Zeit pro 100 Teile</b> normalisiert.</p><div class="scale"><div><b>Positiver Wert:</b> aktuell schneller. Beispiel +11,7 % = die normalisierte Zeit ist rund 11,7 % besser als zuvor.</div><div><b>Um 0 %:</b> Leistung weitgehend stabil.</div><div><b>Negativer Wert:</b> aktuell langsamer als in der vorherigen Periode.</div></div><p class="small">Die Zahl ist ein Trendindikator, keine Gewinnwahrscheinlichkeit und keine Prognose einer einzelnen Puzzlezeit.</p>`;
 const con=`<h2>ℹ️ Was bedeutet Konsistenz?</h2><p><b>Konsistenz</b> misst, wie ähnlich die letzten 10 normalisierten Solo-Leistungen sind. Auch hier wird Zeit pro 100 Teile verwendet, damit verschiedene Teilezahlen besser vergleichbar sind.</p><div class="scale"><div><b>90–100:</b> sehr konstante Leistungen</div><div><b>80–89:</b> gute bis hohe Konstanz</div><div><b>70–79:</b> merkliche Schwankungen</div><div><b>unter 70:</b> starke Schwankungen; Ursachen genauer analysieren</div></div><p class="small">Ein hoher Wert bedeutet nicht automatisch schnell. Ideal ist eine hohe Konsistenz zusammen mit einer starken bzw. steigenden Form.</p>`;
 infoContent.innerHTML=type==='form'?form:con;infoModal.classList.add('open')
}
function closeInfo(){infoModal.classList.remove('open')}

function timeToSeconds(v){if(!v)return null;let p=v.split(':').map(Number);if(p.some(Number.isNaN))return null;if(p.length===3)return p[0]*3600+p[1]*60+p[2];if(p.length===2)return p[0]*60+p[1];return Number(v)}
function displayPuzzleTime(v){if(!v)return '–';let sec=timeToSeconds(String(v));if(sec==null||!Number.isFinite(sec))return v;let h=Math.floor(sec/3600),m=Math.floor((sec%3600)/60),ss=Math.floor(sec%60);return h>0?`${h}:${String(m).padStart(2,'0')}:${String(ss).padStart(2,'0')}`:`${m}:${String(ss).padStart(2,'0')}`}
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
  unavailableList.innerHTML=arr.map(p=>`<div class="item"><div class="puzzleRow">${p.image_url?`<img class="puzzleImg" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy">`:''}<div class="puzzleInfo"><strong>📦 ${readinessEsc(p.name||'Puzzle')}</strong><div class="small">Aktuell ausgeliehen / nicht verfügbar</div><div class="loanActions"><button class="restoreBtn" onclick='restorePuzzle(${JSON.stringify(p.id)})'>↩ Wieder verfügbar</button></div></div></div></div>`).join('');
}
function isPuzzleUnavailable(p){return !!(p&&p.id!=null&&unavailableIds().includes(String(p.id)))}
function skipButtonHtml(p,label='Skip – ausgeliehen'){
  if(!p||p.id==null)return '';
  return `<button class="skipBtn" style="margin-top:8px" onclick='skipPuzzle(${JSON.stringify(p)})'>${label}</button>`;
}
function summarySkipButtonHtml(p,label='Skip – ausgeliehen'){
  if(!p||p.id==null)return '';
  const payload=JSON.stringify(p);
  return `<button type="button" class="skipBtn skipBtnCompact" onclick='event.preventDefault();event.stopPropagation();skipPuzzle(${payload})'>${label}</button>`;
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
 const el=document.getElementById('medianGapFocus'); if(!el)return;
 el.textContent='Top-5-Medianvergleich wird berechnet…';
 try{
  const mg=await getj('/coach/median-gap-focus');
  if(!mg.available){el.textContent=mg.message||'Kein Median-Abstand verfügbar.';return}
  const items=((Array.isArray(mg.items)&&mg.items.length)?mg.items:[mg]).filter(p=>!isPuzzleUnavailable(p));
  el.innerHTML=`<div class="small trainingListIntro">${mg.message||''}</div>`+
   items.map((p,i)=>{
    let pct='–';
    try{
      const toSec=v=>{
        if(v==null)return null;
        const a=String(v).split(':').map(Number);
        if(a.some(x=>!Number.isFinite(x)))return null;
        return a.length===3?a[0]*3600+a[1]*60+a[2]:a.length===2?a[0]*60+a[1]:null;
      };
      const a=toSec(p.last_time),m=toSec(p.median);
      if(a!=null&&m>0){const x=((a-m)/m)*100;pct=`${x>0?'+':''}${x.toFixed(1)}%`;}
    }catch(_){}
    const coach=p.gap
      ? `Aktuell ${p.gap}${pct!=='–'?` (${pct})`:''} über dem MSP-Median. Fokus auf konstantes Sortieren, einen sauberen Start und kontrollierte Wiederholung statt reine Bestzeitjagd.`
      : 'Geeignet für gezielte Technikarbeit und eine kontrollierte Wiederholung gegen den MSP-Median.';
    return `<details class="item weeklySession trainingPuzzleSession"><summary>
    <div class="weeklyIndex">${i+1}</div>
    ${p.image_url?`<img class="weeklyThumb" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.style.display='none'">`:`<div class="weeklyThumb weeklyThumbEmpty">🧩</div>`}
    <div class="weeklySummaryText">
      <div class="weeklySessionTitle"><strong>${readinessEsc(p.name||'Puzzle')}</strong></div>
      <div class="weeklyPuzzleName">${p.manufacturer?readinessEsc(p.manufacturer):'Puzzle'}</div>
      <div class="small">Abstand zum MSP-Median ${p.gap||'–'}</div>
    </div>
    ${summarySkipButtonHtml(p)}
   </summary>
   <div class="weeklyDetail">
     <div class="weeklyFacts trainingFacts4">
       <div class="weeklyFact"><span>Letzte Zeit</span><strong>${p.last_time||'–'}</strong></div>
       <div class="weeklyFact"><span>MSP-Median</span><strong>${p.median||'–'}</strong></div>
       <div class="weeklyFact"><span>Abstand</span><strong>${p.gap||'–'}</strong></div>
       <div class="weeklyFact"><span>Abstand %</span><strong>${pct}</strong></div>
     </div>
     <div class="trainingCoachNote"><strong>Coach</strong>${readinessEsc(coach)}</div>
   </div></details>`;
   }).join('');
 }catch(e){el.textContent='Medianvergleich derzeit nicht verfügbar.'}
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
    // /sync itself succeeded. Secondary dashboard panels must never turn this
    // into the misleading message "Sync fehlgeschlagen".
    const reloadJobs=[loadAll()];
    if(trainingExtrasLoaded)reloadJobs.push(loadMedianGapFocus(),loadRepeatPriority(),loadUnsolvedLibrary());
    if(progressExtrasLoaded)reloadJobs.push(loadPuzzleProgress());
    const reloadResults=await Promise.allSettled(reloadJobs);
    const partialReload=reloadResults.some(x=>x.status==='rejected');
    if(btn)btn.textContent=n?`✓ ${n} neue Ergebnis${n===1?'':'se'}`:'✓ Aktuell';
    if(status)status.textContent=partialReload?'Synchronisiert · einzelne Ansicht wird nachgeladen':'Synchronisierung abgeschlossen';
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
 const el=document.getElementById('unsolvedLibrary'); if(!el)return;
 try{
  const d=await getj('/coach/unsolved-library');
  if(!d.available||!d.items?.length){el.textContent=d.message||'Keine ungelösten Library-Puzzle gefunden.';return}
  el.innerHTML=`<div class="small trainingListIntro"><strong>${d.count}</strong> Puzzle ohne Solo-Ergebnis.</div>`+
   d.items.filter(p=>!isPuzzleUnavailable(p)).map((p,i)=>{
     let diff='–';
     try{
       const dl=p.difficulty_label||p.msp_insights?.difficulty_label||p.puzzle?.msp_insights?.difficulty_label||'';
       const dpRaw=p.difficulty_percent??p.msp_insights?.difficulty_percent??p.puzzle?.msp_insights?.difficulty_percent;
       if(dl){
         diff=String(dl);
         const dp=Number(dpRaw);
         if(Number.isFinite(dp)) diff+=` · ${dp>0?'+':''}${dp.toFixed(1)}% ggü. Ø`;
       }
     }catch(_){}
     let pred='–';
     try{
       const pv=p.prediction||p.msp_prediction||p.puzzle?.msp_prediction||'';
       if(pv) pred=displayPuzzleTime(pv);
     }catch(_){}
     const coach=(diff!=='–'||pred!=='–')
       ? `Echter First Try${diff!=='–'?` · Difficulty ${diff}`:''}${pred!=='–'?` · MSP Prediction ${pred}`:''}. Gut geeignet für eine unverfälschte Standortbestimmung ohne Erinnerungseffekt.`
       : 'Noch ohne Solo-Ergebnis. Ideal für einen echten First Try; für dieses Puzzle liefert MSP aktuell keine Difficulty oder Prediction.';
     return `<details class="item weeklySession trainingPuzzleSession"><summary>
      <div class="weeklyIndex">${i+1}</div>
      ${p.image_url?`<img class="weeklyThumb" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.style.display='none'">`:`<div class="weeklyThumb weeklyThumbEmpty">🧩</div>`}
      <div class="weeklySummaryText">
        <div class="weeklySessionTitle"><strong>${readinessEsc(p.name||'Puzzle')}</strong></div>
        <div class="weeklyPuzzleName">${p.manufacturer?readinessEsc(p.manufacturer):'Puzzle'}</div>
        <div class="small">Noch kein Solo-Ergebnis</div>
      </div>
      ${summarySkipButtonHtml(p)}
     </summary>
     <div class="weeklyDetail">
       <div class="weeklyFacts trainingFacts4">
         <div class="weeklyFact"><span>Teile</span><strong>${p.pieces||'–'}</strong></div>
         <div class="weeklyFact"><span>Difficulty</span><strong>${readinessEsc(diff)}</strong></div>
         <div class="weeklyFact"><span>MSP Prediction</span><strong>${readinessEsc(pred)}</strong></div>
         <div class="weeklyFact"><span>Status</span><strong>First Try</strong></div>
       </div>
       <div class="trainingCoachNote"><strong>Coach</strong>${readinessEsc(coach)}</div>
     </div></details>`;
   }).join('');
 }catch(e){el.textContent='Ungelöste Library derzeit nicht verfügbar.'}
}
async function loadRepeatPriority(){
 const el=document.getElementById('repeatPriority'); if(!el)return;
 try{
  const d=await getj('/coach/repeat-priority?limit=5');
  if(!d.available||!d.items?.length){el.textContent=d.message||'Keine geeigneten Wiederholungs-Puzzle gefunden.';return}
  el.innerHTML=`<div class="small trainingListIntro">${d.message||''}</div>`+
   d.items.filter(p=>!isPuzzleUnavailable(p)).map((p,i)=>`<details class="item weeklySession trainingPuzzleSession"><summary>
    <div class="weeklyIndex">${i+1}</div>
    ${p.image_url?`<img class="weeklyThumb" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.style.display='none'">`:`<div class="weeklyThumb weeklyThumbEmpty">🧩</div>`}
    <div class="weeklySummaryText">
      <div class="weeklySessionTitle"><strong>${readinessEsc(p.name||'Puzzle')}</strong><span class="pill weeklyIntensity">${p.label||''}</span></div>
      <div class="weeklyPuzzleName">${p.manufacturer?readinessEsc(p.manufacturer):'Puzzle'}</div>
      <div class="small">Priorität ${p.score!=null?p.score+'/100':'–'}</div>
    </div>
    ${summarySkipButtonHtml(p)}
   </summary>
   <div class="weeklyDetail">
     <div class="weeklyFacts trainingFacts4">
       <div class="weeklyFact"><span>Letzte Zeit</span><strong>${p.latest||'–'}</strong></div>
       <div class="weeklyFact"><span>Best</span><strong>${p.best||'–'}</strong></div>
       <div class="weeklyFact"><span>MSP-Median</span><strong>${p.median||'–'}</strong></div>
       <div class="weeklyFact"><span>Zuletzt</span><strong>${p.days_since_last_solve!=null?'vor '+p.days_since_last_solve+' Tagen':'–'}</strong></div>
     </div>
     ${p.reasons?.length?`<div class="trainingCoachNote"><strong>Coach</strong>${readinessEsc(p.reasons.join(' · '))}</div>`:''}
   </div></details>`).join('');
 }catch(e){el.textContent='Wiederholungs-Priorität derzeit nicht verfügbar.'}
}

function showAppPage(page,scrollTop=true){
  document.body.dataset.appCurrent=page;
  document.body.dataset.currentPage=page;
  const mobile=window.matchMedia('(max-width:760px)').matches;
  const labels={today:'Heute',training:'Training',wm:'WM',progress:'Fortschritt',more:'Mehr'};
  const targetMap={today:'appToday',training:'appTraining',wm:'appWM',progress:'appProgress',more:'appMore'};
  const buttons=[...document.querySelectorAll('.appBottomNav button')];
  buttons.forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  if(!mobile){
    document.querySelectorAll('.grid>section[data-app-page]').forEach(el=>{el.style.display='';el.classList.remove('appPageActive')});
    document.getElementById(targetMap[page])?.scrollIntoView({behavior:'smooth',block:'start'});
    return;
  }
  document.querySelectorAll('.grid>section[data-app-page]').forEach(el=>{
    const active=el.dataset.appPage===page;
    el.classList.toggle('appPageActive',active);
    el.style.display=active?'block':'none';
  });
  const h=document.getElementById('appPageHeading'); if(h)h.textContent=labels[page]||'';
  if(scrollTop)window.scrollTo({top:0,behavior:'smooth'});
  if(page==='training')loadTrainingExtrasOnce();
  if(page==='progress')loadProgressExtrasOnce();
}
// npcTabResizeFix
window.addEventListener('resize',()=>{
  if(!window.matchMedia('(max-width:760px)').matches){
    document.querySelectorAll('.grid>section[data-app-page]').forEach(el=>{el.hidden=false;});
  }
});
function initAppNavigation(){
  const map={appToday:'today',appTraining:'training',appWM:'wm',appProgress:'progress',appMore:'more'};
  const buttons=[...document.querySelectorAll('.appBottomNav button')];
  buttons.forEach(btn=>{
    btn.dataset.page=map[btn.dataset.target]||'today';
    btn.addEventListener('click',()=>showAppPage(btn.dataset.page));
  });
  showAppPage('today',false);
}

function renderWeeklyPlanFallback(w){
  const el=document.getElementById('wmWeeklyPlan');
  if(!el)return;
  try{
    const rows=Array.isArray(w?.weekly_plan)?w.weekly_plan:[];
    if(!rows.length){
      el.innerHTML='<div class="small">Aktuell kein Wochenplan verfügbar. Bitte MySpeedPuzzling aktualisieren.</div>';
      return;
    }
    el.innerHTML=rows.map((s,i)=>{
      const p=s?.puzzle||{};
      const has=!!p.available;
      const image=has&&p.image_url?`<img class="weeklyThumb" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.style.display='none'">`:`<div class="weeklyThumb weeklyThumbEmpty">🧩</div>`;
      let details='';
      if(has){
        let delta='–';
        if(p.msp_last_time_seconds!=null&&p.msp_median_seconds!=null&&Number(p.msp_median_seconds)>0){
          const d=((Number(p.msp_last_time_seconds)/Number(p.msp_median_seconds))-1)*100;
          delta=`${d>0?'+':''}${d.toFixed(1)}% ${d<=0?'unter':'über'} Median`;
        }
        details=`<div class="weeklyDetail"><div class="weeklyFacts">
          <div class="weeklyFact"><span>MSP-Median</span><strong>${p.msp_median||'–'}</strong></div>
          <div class="weeklyFact"><span>Letzte Zeit</span><strong>${p.msp_last_time||'–'}</strong></div>
          <div class="weeklyFact"><span>vs. Median</span><strong>${delta}</strong></div>
          <div class="weeklyFact"><span>WM-Fit</span><strong>${p.wm_fit?.score!=null?p.wm_fit.score+'/100':'–'}</strong></div>
        </div><div class="weeklyCoachReason"><strong>Coach:</strong> ${p.reason||'Passend für diese Einheit.'}</div></div>`;
      }else{
        details=`<div class="weeklyDetail small">${p.reason||'Für diese Einheit ist kein vollständiges Puzzle nötig.'}</div>`;
      }
      return `<details class="item weeklySession"${i===0?' open':''}><summary>
        <div class="weeklyIndex">${i+1}</div>${image}
        <div class="weeklySummaryText"><div class="weeklySessionTitle"><strong>${s?.session||'Training'}</strong><span class="pill weeklyIntensity">${s?.intensity||''}</span></div>
        ${has?`<div class="weeklyPuzzleName">${p.name||'Puzzle'}</div>`:''}<div class="small">${s?.goal||''}</div>${has?summarySkipButtonHtml(p):''}</div>
      </summary>${details}</details>`;
    }).join('');
  }catch(e){
    el.innerHTML='<div class="small">Wochenplan konnte nicht dargestellt werden.</div>';
  }
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
 if(reason){
   const reasonText=readinessEsc(pick(p.reason,p.recommendation_reason,p.note,''));
   const action=!isPuzzleUnavailable(p)?`<span class="trainingQuickAction">${skipButtonHtml(p,'Skip – aktuell ausgeliehen')}</span>`:'';
   reason.innerHTML=`<span class="trainingQuickReasonText">${reasonText}</span>${action}`;
 }
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
  window.addEventListener('load',async()=>{
    try{
      const reg=await navigator.serviceWorker.register('/sw.js?v=6131');
      await reg.update();
      let reloading=false;
      navigator.serviceWorker.addEventListener('controllerchange',()=>{
        if(reloading)return;
        reloading=true;
        location.reload();
      });
    }catch(e){}
  });
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

async function runTournamentDiagnostics(){
 const status=document.getElementById('tournamentDiagStatus');
 const list=document.getElementById('tournamentDiagSteps');
 if(!status||!list)return;
 status.textContent='Diagnose läuft…';
 list.innerHTML='';
 try{
   const d=await Promise.race([
     (async()=>{
       const r=await fetch('/msp/tournament-diagnostics',{cache:'no-store'});
       const txt=await r.text();
       let obj;
       try{obj=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
       if(!r.ok)throw new Error(`HTTP ${r.status}: ${JSON.stringify(obj).slice(0,300)}`);
       return obj;
     })(),
     new Promise((_,reject)=>setTimeout(()=>reject(new Error('diagnostic_timeout')),30000))
   ]);
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · ${d.summary?.elapsed_ms??'–'} ms · confirmed <strong>${d.summary?.confirmed_count??'–'}</strong> · raw <strong>${d.summary?.raw_count??'–'}</strong>`;
   list.innerHTML=(d.steps||[]).map(s=>{
     let extra='';
     if(s.count!=null)extra+=` · Count ${s.count}`;
     if(s.names?.length)extra+=`<div class="small" style="margin-top:5px">${s.names.map(x=>readinessEsc(x)).join(' · ')}</div>`;
     if(s.error)extra+=`<div class="small" style="color:#b91c1c;margin-top:5px">${readinessEsc(s.error)}</div>`;
     if(s.top_level_keys?.length)extra+=`<div class="small">Keys: ${s.top_level_keys.map(readinessEsc).join(', ')}</div>`;
     if(s.rows?.length){
       extra+=s.rows.map(r=>{
         const title=readinessEsc(r.name||r.id||'Eintrag');
         let body='';
         if(r.participation)body+=`<div class="small"><strong>Participation:</strong> ${readinessEsc(JSON.stringify(r.participation))}</div>`;
         if(r.fields)body+=`<pre class="diagPre">${readinessEsc(JSON.stringify(r.fields,null,2))}</pre>`;
         return `<details class="item diagDetails"><summary><strong>${title}</strong></summary>${body}</details>`;
       }).join('');
     }
     return `<div class="item"><strong>${s.ok?'✅':'❌'} ${s.step}</strong>${extra}${s.elapsed_ms!=null?`<div class="small">${s.elapsed_ms} ms</div>`:''}</div>`;
   }).join('');
 }catch(e){
   status.textContent='Diagnose fehlgeschlagen oder Timeout.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}

async function runRegistrationDiagnostics(){
 const status=document.getElementById('registrationDiagStatus');
 const list=document.getElementById('registrationDiagList');
 if(!status||!list)return;
 status.textContent='Registration-Diagnose läuft…';
 list.innerHTML='';
 try{
   const d=await Promise.race([
     (async()=>{
       const r=await fetch('/msp/registration-diagnostics',{cache:'no-store'});
       const txt=await r.text();
       let obj;
       try{obj=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
       if(!r.ok)throw new Error(`HTTP ${r.status}: ${JSON.stringify(obj).slice(0,300)}`);
       return obj;
     })(),
     new Promise((_,reject)=>setTimeout(()=>reject(new Error('diagnostic_timeout')),45000))
   ]);
   const s=d.summary||{};
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · ${s.elapsed_ms??'–'} ms · erfolgreiche Endpunkte <strong>${s.successful_count??0}</strong> · Nicole-Matches <strong>${s.player_match_count??0}</strong>`;
   let targetHtml=(d.targets||[]).map(t=>`<div class="item"><strong>🎯 ${readinessEsc(t.name||'Turnier')}</strong><div class="small">${readinessEsc(t.id||'')} · ${readinessEsc(t.date_from||'')}</div></div>`).join('');
   let probeHtml=(d.probes||[]).map(p=>{
     const shape=p.shape?readinessEsc(JSON.stringify(p.shape)):'';
     return `<div class="item">
       <strong>${p.ok?'✅':'❌'} ${readinessEsc(p.label||p.path||'Probe')}</strong>
       <div class="small">${readinessEsc(p.path||'')}</div>
       ${p.ok?`<div class="small">Shape: ${shape}</div><div class="small">Nicole-ID gefunden: <strong>${p.authenticated_player_match?'JA':'nein'}</strong></div>`:`<div class="small" style="color:#b91c1c">${readinessEsc(p.error||'Fehler')}</div>`}
       ${p.elapsed_ms!=null?`<div class="small">${p.elapsed_ms} ms</div>`:''}
     </div>`;
   }).join('');
   list.innerHTML=targetHtml+probeHtml;
 }catch(e){
   status.textContent='Registration-Diagnose fehlgeschlagen oder Timeout.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}


async function runRouteDiagnostics(){
 const status=document.getElementById('routeDiagStatus');
 const list=document.getElementById('routeDiagList');
 if(!status||!list)return;
 status.textContent='MSP-Datenstrukturen werden geprüft…';
 list.innerHTML='';
 try{
   const r=await fetch('/msp/api-route-diagnostics',{cache:'no-store'});
   const txt=await r.text();
   let d; try{d=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
   if(!r.ok)throw new Error(`HTTP ${r.status}`);

   status.innerHTML=`Version <strong>${d.version}</strong> · nutzbare Schemas <strong>${d.summary?.usable_schema_count??0}</strong> · CrowdSec <strong>${d.summary?.crowdsec_count??0}</strong> · Relation-Hits <strong>${d.summary?.relation_hit_count??0}</strong>`;

   const schemas=(d.schema_checks||[]).map(s=>`<div class="item">
     <strong>${s.usable_schema?'✅':'⚠️'} ${readinessEsc(s.url||'Schema')}</strong>
     <div class="small">HTTP ${s.status??'–'} · ${readinessEsc(s.content_type||'')}</div>
     ${s.note?`<div class="small">${readinessEsc(s.note)}</div>`:''}
   </div>`).join('');

   const rels=(d.relation_checks||[]).map(x=>{
     const hits=x.relation_like_fields||[];
     return `<details class="item"><summary><strong>${x.error?'❌':'✅'} ${readinessEsc(x.label||'Quelle')}</strong></summary>
       ${x.error?`<div class="small" style="color:#b91c1c">${readinessEsc(x.error)}</div>`:''}
       ${x.type?`<div class="small">Typ: ${readinessEsc(x.type)}${x.count!=null?' · Count '+x.count:''}</div>`:''}
       ${x.keys?.length?`<div class="small">Keys: ${x.keys.map(readinessEsc).join(', ')}</div>`:''}
       ${hits.length?`<pre class="diagPre">${readinessEsc(JSON.stringify(hits,null,2))}</pre>`:'<div class="small">Keine turnierbezogenen Relationsfelder gefunden.</div>'}
     </details>`;
   }).join('');

   const summaryHits=d.summary?.relation_hits||[];
   const summary=summaryHits.length?`<div class="item"><strong>🎯 Gefundene Relationsfelder</strong><pre class="diagPre">${readinessEsc(JSON.stringify(summaryHits,null,2))}</pre></div>`:'<div class="item small">Keine offensichtlichen Registration-/Participation-Felder in den funktionierenden MSP-Antworten gefunden.</div>';

   list.innerHTML=summary+rels+schemas;
 }catch(e){
   status.textContent='Datenstruktur-Diagnose fehlgeschlagen.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}

async function runRegistrationFingerprint(){
 const status=document.getElementById('fingerprintStatus');
 const list=document.getElementById('fingerprintList');
 if(!status||!list)return;
 status.textContent='Fingerprint wird geprüft…';
 list.innerHTML='';
 try{
   const r=await fetch('/msp/registration-fingerprint',{cache:'no-store'});
   const txt=await r.text();
   let d; try{d=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
   if(!r.ok)throw new Error(`HTTP ${r.status}`);
   const s=d.summary||{};
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · Relations <strong>${s.relation_hit_count??0}</strong> · Nicole-ID-Matches <strong>${s.player_match_count??0}</strong> · ${s.elapsed_ms??'–'} ms`;

   const rows=(d.sources||[]).map(src=>{
     const rel=src.relation_hits||[];
     const matches=src.player_matches||[];
     return `<details class="item"><summary><strong>${src.error?'❌':'✅'} ${readinessEsc(src.label||'Quelle')}</strong></summary>
       ${src.error?`<div class="small" style="color:#b91c1c">${readinessEsc(src.error)}</div>`:''}
       ${src.relation_hit_count!=null?`<div class="small">Relations: ${src.relation_hit_count} · Nicole-ID-Matches: ${src.player_match_count||0}</div>`:''}
       ${matches.length?`<div class="small"><strong>🎯 Nicole-ID gefunden</strong></div><pre class="diagPre">${readinessEsc(JSON.stringify(matches,null,2))}</pre>`:''}
       ${rel.length?`<pre class="diagPre">${readinessEsc(JSON.stringify(rel,null,2))}</pre>`:'<div class="small">Keine relevanten Relationspfade.</div>'}
     </details>`;
   }).join('');

   const matchSources=s.player_match_sources||[];
   const summary=matchSources.length
      ? `<div class="item"><strong>🎯 Nicole-ID gefunden in:</strong><div class="small">${matchSources.map(readinessEsc).join(' · ')}</div></div>`
      : `<div class="item small"><strong>Kein persönlicher Player-ID-Fingerprint in den geprüften MSP-Antworten gefunden.</strong></div>`;

   list.innerHTML=summary+rows;
 }catch(e){
   status.textContent='Fingerprint-Diagnose fehlgeschlagen.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}


async function runNicoleCompetitionTrace(){
 const status=document.getElementById('traceStatus');
 const list=document.getElementById('traceList');
 if(!status||!list)return;
 status.textContent='Competition Trace läuft…';
 list.innerHTML='';
 try{
   const r=await fetch('/msp/nicole-competition-trace',{cache:'no-store'});
   const txt=await r.text();
   let d; try{d=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
   if(!r.ok)throw new Error(`HTTP ${r.status}`);
   const s=d.summary||{};
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · Matches <strong>${s.player_match_count??0}</strong> · Traces <strong>${s.trace_count??0}</strong> · Solo ${s.modes?.solo??0} · Duo ${s.modes?.duo??0} · Team ${s.modes?.team??0}`;

   const headline=(s.competition_names_found||[]).length
      ? `<div class="item"><strong>🏁 Gefundene Competition-Namen</strong><div class="small">${(s.competition_names_found||[]).map(readinessEsc).join(' · ')}</div></div>`
      : `<div class="item small"><strong>Keine eindeutigen Competition-Namen direkt neben Nicoles ID gefunden.</strong></div>`;

   const rows=(d.traces||[]).map((t,i)=>`<details class="item"><summary><strong>${i+1}. ${readinessEsc((t.mode||'unknown').toUpperCase())}${t.competition_name?' · '+readinessEsc(t.competition_name):''}</strong></summary>
      <div class="small">Pfad: ${readinessEsc(t.path||'')}</div>
      ${t.competition_id?`<div class="small">Competition-ID: ${readinessEsc(String(t.competition_id))}</div>`:''}
      ${t.date?`<div class="small">Datum: ${readinessEsc(String(t.date))}</div>`:''}
      ${t.status?`<div class="small">Status: ${readinessEsc(String(t.status))}</div>`:''}
      ${t.location?`<div class="small">Ort: ${readinessEsc(String(t.location))}</div>`:''}
      <pre class="diagPre">${readinessEsc(JSON.stringify(t.context,null,2))}</pre>
   </details>`).join('');

   list.innerHTML=headline+rows;
 }catch(e){
   status.textContent='Competition Trace fehlgeschlagen.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}


async function runCompetitionStructureMap(){
 const status=document.getElementById('structureMapStatus');
 const list=document.getElementById('structureMapList');
 if(!status||!list)return;
 status.textContent='Competition-Strukturen werden kartiert…';
 list.innerHTML='';
 try{
   const r=await fetch('/msp/competition-structure-map',{cache:'no-store'});
   const txt=await r.text();
   let d; try{d=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
   if(!r.ok)throw new Error(`HTTP ${r.status}`);
   const s=d.summary||{};
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · Competitions <strong>${s.competition_count??0}</strong> · Schemas <strong>${s.unique_schema_count??0}</strong> · relevante Felder <strong>${s.interesting_field_count??0}</strong>`;

   const targetHtml=(d.targets||[]).map(t=>`<details class="item"><summary><strong>🎯 ${readinessEsc(t.name||'Target')}</strong></summary><pre class="diagPre">${readinessEsc(JSON.stringify(t.fields,null,2))}</pre></details>`).join('');

   const diffHtml=(s.target_schema_differences||[]).map(x=>`<div class="item"><strong>🔬 ${readinessEsc(x.name||'Target')}</strong>
      <div class="small">Extra vs. common: ${readinessEsc((x.extra_vs_common||[]).join(', ')||'–')}</div>
      <div class="small">Fehlt vs. common: ${readinessEsc((x.missing_vs_common||[]).join(', ')||'–')}</div>
   </div>`).join('');

   const personal=(s.personal_like_samples||[]).length
      ? `<details class="item"><summary><strong>👤 Competitions mit personal-/registration-ähnlichen Feldern (${s.competitions_with_personal_like_fields||0})</strong></summary><pre class="diagPre">${readinessEsc(JSON.stringify(s.personal_like_samples,null,2))}</pre></details>`
      : `<div class="item small"><strong>Keine Competition enthält eindeutige persönliche Registration-/Participant-Felder.</strong></div>`;

   const fieldHtml=`<details class="item"><summary><strong>🧩 Relevante Felder</strong></summary><pre class="diagPre">${readinessEsc(JSON.stringify(d.fields||[],null,2))}</pre></details>`;
   const schemaHtml=`<details class="item"><summary><strong>🧱 Schema-Signaturen</strong></summary><pre class="diagPre">${readinessEsc(JSON.stringify(d.samples||[],null,2))}</pre></details>`;

   list.innerHTML=targetHtml+diffHtml+personal+fieldHtml+schemaHtml;
 }catch(e){
   status.textContent='Structure Mapper fehlgeschlagen.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}


async function runResultCompetitionReverseMap(){
 const status=document.getElementById('reverseMapStatus');
 const list=document.getElementById('reverseMapList');
 if(!status||!list)return;
 status.textContent='Reverse Mapping läuft…';
 list.innerHTML='';
 try{
   const r=await fetch('/msp/result-competition-reverse-map',{cache:'no-store'});
   const txt=await r.text();
   let d; try{d=JSON.parse(txt)}catch(_){throw new Error(`HTTP ${r.status}: ${txt.slice(0,300)}`)}
   if(!r.ok)throw new Error(`HTTP ${r.status}`);
   const s=d.summary||{};
   status.innerHTML=`Version <strong>${d.version||'–'}</strong> · Competitions <strong>${s.competition_count??0}</strong> · starke Matches <strong>${s.strong_match_count??0}</strong> · ${s.elapsed_ms??'–'} ms`;

   const strong=(s.strong_matches||[]).length
      ? `<div class="item"><strong>🎯 Starke Zuordnungen</strong><pre class="diagPre">${readinessEsc(JSON.stringify(s.strong_matches,null,2))}</pre></div>`
      : `<div class="item small"><strong>Keine starke direkte Result→Competition-Zuordnung gefunden.</strong></div>`;

   const modes=(d.modes||[]).map(m=>{
     const best=m.best_competition_matches||[];
     const locals=m.local_result_matches||[];
     return `<details class="item"><summary><strong>${readinessEsc((m.mode||'unknown').toUpperCase())} · ${m.result_count??0} Resultate</strong></summary>
       <div class="small">Player-ID-Match: ${m.player_id_match?'ja':'nein'}</div>
       ${best.length?`<div class="small"><strong>Beste globalen Competition-Matches</strong></div><pre class="diagPre">${readinessEsc(JSON.stringify(best,null,2))}</pre>`:'<div class="small">Keine globalen Matches.</div>'}
       ${locals.length?`<div class="small"><strong>Lokale Result-Matches</strong></div><pre class="diagPre">${readinessEsc(JSON.stringify(locals,null,2))}</pre>`:'<div class="small">Keine lokalen Result-Matches.</div>'}
       <details><summary class="small">Kontext anzeigen</summary><pre class="diagPre">${readinessEsc(JSON.stringify(m.context_rows||[],null,2))}</pre></details>
     </details>`;
   }).join('');

   list.innerHTML=strong+modes;
 }catch(e){
   status.textContent='Reverse Mapper fehlgeschlagen.';
   list.innerHTML=`<div class="item small">${readinessEsc(e.message||e)}</div>`;
 }
}





function renderConfirmedTournamentData(data){
  const rows=(data&&Array.isArray(data.competitions))?data.competitions:[];
  const nextEl=document.getElementById('nextMspCompetition');
  const listEl=document.getElementById('mspCompetitions');

  if(rows.length){
    const c=rows[0];
    if(nextEl){
      nextEl.innerHTML=`<strong>${readinessEsc(c.name||'Turnier')}</strong><br>${dateText(c.date_from)}${c.location?' · '+readinessEsc(c.location):''}${c.country_code?' · '+readinessEsc(String(c.country_code).toUpperCase()):''}<br><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>`;
    }
    if(listEl){
      listEl.innerHTML=rows.map(c=>`<div class="item"><strong>${readinessEsc(c.name||'Turnier')}</strong><div class="small">${dateText(c.date_from)}${c.date_to?' – '+dateText(c.date_to):''}${c.location?' · '+readinessEsc(c.location):''}${c.country_code?' · '+readinessEsc(String(c.country_code).toUpperCase()):''}</div><span class="pill">✅ Angemeldet</span><span class="pill">⏳ ${countdownText(c.date_from)}</span>${c.link?`<br><a class="btn secondary" style="margin-top:8px" href="${readinessEsc(c.link)}" target="_blank">Turnier öffnen</a>`:''}</div>`).join('');
    }
  }else{
    if(nextEl) nextEl.textContent='Keine bestätigte zukünftige Anmeldung gefunden.';
    if(listEl) listEl.innerHTML='<div class="small">Keine bestätigten zukünftigen Turniere.</div>';
  }
}

function renderTournamentLoadError(){
  const nextEl=document.getElementById('nextMspCompetition');
  const listEl=document.getElementById('mspCompetitions');
  if(nextEl) nextEl.textContent='Turnierdaten derzeit nicht verfügbar.';
  if(listEl) listEl.innerHTML='<div class="small">Bestätigte Turniere derzeit nicht abrufbar.</div>';
}

async function loadAll(){renderUnavailable();
 let coreHasMspData=false;
 let coreDataSource='none';
 // Performance V6.9.6: independent API calls start immediately in parallel.
 const exPrefetch=unavailableIds();
 const statusPromise=getj('/coach/status');
 const summaryPromise=getj('/coach/msp-training-summary');
 const wmPlanPromise=getj('/coach/wm-plan'+(exPrefetch.length?'?exclude_puzzle_ids='+encodeURIComponent(exPrefetch.join(',')):''));
 const swissPromise=Promise.race([
   getj('/coach/swiss-ranking'),
   new Promise((_,reject)=>setTimeout(()=>reject(new Error('swiss_timeout')),6000))
 ]);
 const competitionsPromise=Promise.race([
   getj('/msp/my-competitions?limit=30'),
   new Promise((_,reject)=>setTimeout(()=>reject(new Error('competition_timeout')),14000))
 ]);
 // Render tournament cards immediately when this request resolves.
 // Do not wait for the comparatively expensive WM-plan rendering below.
 competitionsPromise
   .then(data=>renderConfirmedTournamentData(data))
   .catch(()=>renderTournamentLoadError());


 try{let st=await statusPromise;
   if(st.version && st.version!==NPC_FRONTEND_VERSION){
     const key='npc_version_reload_'+st.version;
     if(!sessionStorage.getItem(key)){
       sessionStorage.setItem(key,'1');
       location.replace('/dashboard?v='+encodeURIComponent(st.version)+'&t='+Date.now());
       return;
     }
   }
   coreHasMspData=!!st.has_myspeedpuzzling_data;coreDataSource=st.data_source||'none';systemKpi.textContent='OK';systemText.textContent=`Backend V${st.version} · Frontend V${NPC_FRONTEND_VERSION} · Datenbank ok`;systemBadge.textContent='🟢 System bereit';mspKpi.textContent=st.has_myspeedpuzzling_data?'DATA':(st.pat_configured?'PAT':(st.oauth_configured?'READY':'WAIT'));mspText.textContent=st.data_source==='legacy'?'Historische DB-Daten aktiv':(st.has_myspeedpuzzling_data?`MSP-Daten synchronisiert · Snapshot #${st.latest_snapshot_id||'–'}`:(st.pat_configured?'PAT eingerichtet · noch kein Snapshot':'Verbindung möglich'))}catch(e){systemBadge.textContent='🔴 Fehler'}

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
   setTimeout(()=>renderWeeklyPlanFallback(w),0);
   const weeklyPlanEl=document.getElementById('wmWeeklyPlan');
   if(weeklyPlanEl){
   weeklyPlanEl.innerHTML=(w.weekly_plan||[]).map((s,i)=>{
       let p=s.puzzle||{};
       let compactImage=p.available&&p.image_url?`<img class="weeklyThumb" src="${p.image_url}" alt="${readinessEsc(p.name||'Puzzle')}" loading="lazy" onerror="this.style.display='none'">`:`<div class="weeklyThumb weeklyThumbEmpty">🧩</div>`;
       let compactName=p.available?(p.name||'Puzzle'):(p.not_required?'Technik / Recovery':'Kein Puzzle');
       let diff=p.msp_insights?.difficulty_label||'–';
       if(p.msp_insights?.difficulty_percent!=null){let dp=Number(p.msp_insights.difficulty_percent);diff=`${diff.charAt(0).toUpperCase()+diff.slice(1)} · ${dp>0?'+':''}${dp.toFixed(1)}% ggü. Ø`;}
       let medianDelta='–';
       if(p.msp_last_time_seconds!=null&&p.msp_median_seconds!=null&&p.msp_median_seconds>0){
         let d=((p.msp_last_time_seconds/p.msp_median_seconds)-1)*100;
         medianDelta=`${d>0?'+':''}${d.toFixed(1)}% ${d<=0?'unter':'über'} Median`;
       }else if(p.median_gap){medianDelta=p.median_gap+' über Median';}
       let detail=p.available
         ? `<div class="weeklyDetail"><div class="weeklyFacts"><div class="weeklyFact"><span>MSP-Median</span><strong>${p.msp_median||'–'}</strong></div><div class="weeklyFact"><span>Letzte Zeit</span><strong>${p.msp_last_time||'–'}</strong></div><div class="weeklyFact"><span>vs. Median</span><strong>${medianDelta}</strong></div><div class="weeklyFact"><span>MSP Prediction</span><strong>${displayPuzzleTime(p.msp_prediction)}</strong></div><div class="weeklyFact"><span>Difficulty</span><strong>${diff}</strong></div><div class="weeklyFact"><span>WM-Fit</span><strong>${p.wm_fit?.score!=null?p.wm_fit.score+'/100':'–'}</strong></div></div><div class="weeklyCoachReason"><strong>Coach:</strong> ${p.reason||p.wm_fit?.summary||'Passend für diese Trainingseinheit.'}</div><div class="weeklyPills"><span class="pill">${p.previous_solo_solves||0} Solo-Läufe</span>${p.days_since_last_solve!=null?`<span class="pill">zuletzt vor ${p.days_since_last_solve} Tagen</span>`:'<span class="pill">noch nie Solo gelöst</span>'}${p.wm_suitability?`<span class="pill ${p.wm_suitability.level==='hoch'||p.wm_suitability.level==='gut'?'wmGood':''}">${p.wm_suitability.label}</span>`:''}</div>${p.competition_risk?.score>=80?`<div class="small riskHigh" style="padding:7px;border-radius:8px;margin-top:7px">⚠️ ${p.competition_risk.reason}</div>`:''}</div>`
         : `<div class="weeklyDetail small">${p.reason||'Für diese Technik-/Recovery-Einheit ist kein vollständiges Puzzle nötig.'}</div>`;
       let displayName=p.available?compactName:'';
       return `<details class="item weeklySession trainingPuzzleSession"${i===0?' open':''}><summary><div class="weeklyIndex">${i+1}</div>${compactImage}<div class="weeklySummaryText"><div class="weeklySessionTitle"><strong>${s.session}</strong><span class="pill weeklyIntensity">${s.intensity}</span></div>${displayName?`<div class="weeklyPuzzleName">${displayName}</div>`:''}<div class="small">${s.goal}</div>${p.available?summarySkipButtonHtml(p):''}</div></summary>${detail}</details>`;
     }).join('')||'<div class="small">Kein Trainingsplan verfügbar.</div>';
   }
   // Competition cards are rendered only from /msp/my-competitions.
   // Resilient/fallback state remains internal and is intentionally not shown
   // as a user-facing banner.

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
   
   wmTabReadiness.textContent=(w.readiness_score!=null?w.readiness_score+'/100':(w.readiness!=null?w.readiness+'/100':'–'));wmTabFirstTry.textContent=w.wm_goal_first_try||w.wm_goal_realistic||'–';const wmTabRepeat=document.getElementById('wmTabRepeat');if(wmTabRepeat)wmTabRepeat.textContent=w.wm_goal_repeat||w.dynamic_target||'–';wmTabStretch.textContent=w.wm_goal_stretch||'–';
   let pr=w.progress_recent||[];
   if(pr.length){
     let vals=pr.map(x=>x.seconds), mn=Math.min(...vals,w.wm_goal_stretch_seconds||99999), mx=Math.max(...vals);
     let span=Math.max(1,mx-mn);
     wmProgressSummary.innerHTML=`<div class="wmProgressCompact"><span><b>Ø letzte 10</b> ${w.recent10||'–'}</span><span><b>Trainingsziel</b> ${w.dynamic_target||'–'}</span>${w.trend10_percent!=null?`<span><b>Trend</b> ${pct(w.trend10_percent)}</span>`:''}</div>`;
     wmProgressChart.innerHTML=`<div class="progressBars wmMobileBars">${pr.map((x,i)=>{let h=35+((mx-x.seconds)/span)*105;let d=x.finished_at?new Date(x.finished_at).toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit'}):'';let show=(i===0||i===pr.length-1||i%3===0);return `<div class="pbar" title="${x.puzzle_name||''} · ${x.time}"><div class="pbarFill" style="height:${Math.max(20,h)}px"></div><div class="pbarTime">${show?displayPuzzleTime(x.time):''}</div><div class="pbarDate">${show?d:''}</div></div>`}).join('')}</div><div class="progressLegend"><span class="pill">WM-Ziel: ${w.wm_goal_realistic}</span><span class="pill">Stretch: ${w.wm_goal_stretch}</span></div>`;
   }else{wmProgressSummary.textContent='Noch nicht genügend 500er-Daten.';wmProgressChart.innerHTML='';}

   // weekly plan is rendered immediately after wm-plan resolves (see above)

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
    return HTMLResponse(
        DASHBOARD_HTML,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-NPC-Version": "6.13.1",
        },
    )
