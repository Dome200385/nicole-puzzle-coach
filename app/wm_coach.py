from __future__ import annotations
from datetime import datetime, timezone
from statistics import mean, median, pstdev

def _dt(value):
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace("Z","+00:00"))
    except Exception: return None

def _fmt(seconds):
    if seconds is None: return None
    seconds=int(round(seconds)); h,rem=divmod(seconds,3600); m,s=divmod(rem,60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def _days_until(value):
    dt=_dt(value)
    if not dt: return None
    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
    return max(0,int((dt-datetime.now(timezone.utc)).total_seconds()//86400))

def _phase(days):
    if days is None: return {"name":"Planung","description":"Turnierdatum nicht verfügbar."}
    if days>28: return {"name":"Aufbauphase","description":"Tempo und stabile Abläufe entwickeln."}
    if days>14: return {"name":"Spezifische WM-Phase","description":"500er-Fokus und Turniersimulationen erhöhen."}
    if days>7: return {"name":"Schärfungsphase","description":"Qualität vor Umfang; gezielte Simulationen."}
    if days>2: return {"name":"Tapering","description":"Belastung reduzieren, Rhythmus und Sicherheit halten."}
    return {"name":"Turniermodus","description":"Keine harten Einheiten mehr; Fokus auf Frische und Routine."}

def build_wm_plan(all_results, my_competitions, target_pieces=500):
    comps=(my_competitions or {}).get("competitions",[])
    next_comp=comps[0] if comps else None
    days=_days_until(next_comp.get("date_from")) if next_comp else None
    phase=_phase(days)
    rows=[r for r in all_results if r.get("mode")=="solo" and r.get("pieces")==target_pieces and isinstance(r.get("seconds"),(int,float))]
    rows.sort(key=lambda r:_dt(r.get("finished_at")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    if not rows:
        return {"target_pieces":target_pieces,"next_competition":next_comp,"days_until":days,"phase":phase,"readiness_score":None,"recommendation":f"Noch keine Solo-Ergebnisse mit {target_pieces} Teilen vorhanden."}

    times=[r["seconds"] for r in rows]
    r5=rows[:5]; r10=rows[:10]; r20=rows[:20]; prev10=rows[10:20]
    avg5=mean(r["seconds"] for r in r5); avg10=mean(r["seconds"] for r in r10); avg20=mean(r["seconds"] for r in r20)
    trend=None
    if len(prev10)>=5:
        old=mean(r["seconds"] for r in prev10)
        trend=round((old-avg10)/old*100,1) if old else None

    # Current performance zone from recent 10: central range, less sensitive to one outlier.
    recent_times=sorted(r["seconds"] for r in r10)
    lo=recent_times[max(0,int(len(recent_times)*0.2)-1)]
    hi=recent_times[min(len(recent_times)-1,int(len(recent_times)*0.8))]
    # Dynamic target: challenging but grounded between current average and recent best.
    recent_best=min(recent_times)
    target=max(recent_best, avg10*0.92)

    cv=pstdev(recent_times)/avg10 if len(recent_times)>1 and avg10 else 1
    consistency=max(0,min(100,round(100-cv*100)))
    trend_score=50 if trend is None else max(0,min(100,50+trend*3))
    volume_score=min(100,len(rows)/50*100)
    recency_score=100
    if rows and _dt(rows[0].get("finished_at")):
        last=_dt(rows[0]["finished_at"])
        if last.tzinfo is None:last=last.replace(tzinfo=timezone.utc)
        age=max(0,(datetime.now(timezone.utc)-last).days)
        recency_score=max(0,100-age*5)
    readiness=round(.35*consistency+.30*trend_score+.20*volume_score+.15*recency_score)

    if days is not None and days<=7:
        recommendation=f"500er kontrolliert statt maximal: Zielkorridor {_fmt(target)}–{_fmt(target*1.06)}. Keine unnötige Ermüdung."
    elif trend is not None and trend>=5:
        recommendation=f"Nächste Einheit: 500 Teile als Turniersimulation. Zielkorridor {_fmt(target)}–{_fmt(target*1.05)}; gleiche Start- und Sortierroutine wie an der WM."
    elif consistency<80:
        recommendation=f"Nächste Einheit: 500 Teile kontrolliert. Ziel {_fmt(avg10)} oder schneller, aber Priorität auf gleichmässigem Ablauf und Fehlervermeidung."
    else:
        recommendation=f"Nächste Einheit: 500 Teile mit moderatem Zeitdruck. Zielkorridor {_fmt(target)}–{_fmt(target*1.06)}."

    return {
        "target_pieces":target_pieces,"next_competition":next_comp,"days_until":days,"phase":phase,
        "count":len(rows),"best":_fmt(min(times)),"median":_fmt(median(times)),"average_all":_fmt(mean(times)),
        "recent5":_fmt(avg5),"recent10":_fmt(avg10),"recent20":_fmt(avg20),
        "trend10_percent":trend,"current_zone":{"from":_fmt(lo),"to":_fmt(hi)},
        "dynamic_target":_fmt(target),"consistency_500":consistency,"readiness_score":readiness,
        "recommendation":recommendation,
        "readiness_explanation":"Kombiniert 500er-Konsistenz, aktuellen Trend, Datenmenge und Aktualität der Trainings.",
    }
