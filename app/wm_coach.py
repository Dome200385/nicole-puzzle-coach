from __future__ import annotations
from datetime import datetime, timezone, timedelta
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
    if days is None:
        return {"key":"planning","name":"Planung","description":"Turnierdatum nicht verfügbar.","weekly_sessions":3}
    if days>28:
        return {"key":"build","name":"Aufbauphase","description":"Tempo und stabile Abläufe entwickeln.","weekly_sessions":4}
    if days>14:
        return {"key":"specific","name":"Spezifische WM-Phase","description":"500er-Fokus und echte Turniersimulationen erhöhen.","weekly_sessions":4}
    if days>7:
        return {"key":"sharpen","name":"Schärfungsphase","description":"Qualität vor Umfang; weniger, aber präzisere Einheiten.","weekly_sessions":3}
    if days>2:
        return {"key":"taper","name":"Tapering","description":"Belastung deutlich reduzieren; Rhythmus und Sicherheit halten.","weekly_sessions":2}
    return {"key":"race","name":"Turniermodus","description":"Keine harte Einheit mehr; Frische, Schlaf und Routine priorisieren.","weekly_sessions":0}

def _recent_training_days(rows, lookback=7):
    now=datetime.now(timezone.utc)
    dates=set()
    for r in rows:
        dt=_dt(r.get("finished_at"))
        if not dt: continue
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        if (now-dt).days <= lookback:
            dates.add(dt.date())
    return len(dates)

def _training_type(phase, trend, consistency, recent5, recent10, recent_days):
    key=phase["key"]
    if key=="race":
        return {"type":"Regeneration","intensity":"Sehr leicht","reason":"Turnier steht unmittelbar bevor."}
    if key=="taper":
        return {"type":"Kontrollierter 500er","intensity":"Leicht","reason":"Form erhalten ohne zusätzliche Ermüdung."}
    if recent_days>=5:
        return {"type":"Recovery / Technik","intensity":"Leicht","reason":"Viele Trainingstage in den letzten 7 Tagen."}
    if consistency < 80:
        return {"type":"Konstanztraining","intensity":"Moderat","reason":"Schwankungen reduzieren und Ablauf stabilisieren."}
    if trend is not None and trend >= 8:
        return {"type":"Turniersimulation","intensity":"Hoch","reason":"Starker positiver Trend erlaubt eine gezielte Belastung."}
    if recent5 < recent10 * .96:
        return {"type":"Speed-Run","intensity":"Hoch","reason":"Aktuelle Form ist schneller als der 10er-Schnitt."}
    if key in ("specific","sharpen"):
        return {"type":"Turniersimulation","intensity":"Hoch","reason":"WM-spezifische Phase."}
    return {"type":"Kontrollierter 500er","intensity":"Moderat","reason":"Tempo und Konstanz gemeinsam entwickeln."}

def _weekly_plan(phase, target, realistic_goal, stretch_goal, consistency, trend):
    key=phase["key"]
    if key=="race":
        return [
            {"session":"Ruhetag / Aktivierung","goal":"10–15 Min. leichte Sortier-/Start-Routine, kein vollständiges Puzzle.","intensity":"Sehr leicht"}
        ]
    if key=="taper":
        return [
            {"session":"Kontrollierter 500er","goal":f"Sauberer Lauf ohne Maximaldruck, ca. {_fmt(target*1.04)}–{_fmt(target*1.10)}.","intensity":"Leicht"},
            {"session":"Start-/Sortierroutine","goal":"20–30 Min. Startphase, Box öffnen, Rand/Sortierung reproduzierbar üben.","intensity":"Leicht"},
        ]
    if key=="sharpen":
        return [
            {"session":"Turniersimulation","goal":f"500 Teile, Ziel {realistic_goal} oder schneller; komplette WM-Routine.","intensity":"Hoch"},
            {"session":"Technik / Sortieren","goal":"Kurze Einheit mit Fokus auf Start, Farbfelder und Wechselkosten.","intensity":"Leicht"},
            {"session":"Kontrollierter 500er","goal":f"Konstant im Bereich {_fmt(target)}–{_fmt(target*1.06)} bleiben.","intensity":"Moderat"},
        ]
    if key=="specific":
        return [
            {"session":"Turniersimulation","goal":f"500 Teile, realistisches WM-Ziel {realistic_goal}.","intensity":"Hoch"},
            {"session":"Speed-Run","goal":f"500 Teile, aggressiver Start; Stretch Goal {stretch_goal} nur bei gutem Flow.","intensity":"Hoch"},
            {"session":"Konstanztraining","goal":f"500 Teile ohne Einbruch; Zielkorridor {_fmt(target)}–{_fmt(target*1.06)}.","intensity":"Moderat"},
            {"session":"Technik / Recovery","goal":"Sortieren, Starttechnik oder sehr lockere Einheit.","intensity":"Leicht"},
        ]
    return [
        {"session":"Kontrollierter 500er","goal":f"Stabiler Lauf im Zielkorridor {_fmt(target)}–{_fmt(target*1.08)}.","intensity":"Moderat"},
        {"session":"Speed-Run","goal":f"Tempo testen; realistisches Ziel {realistic_goal}.","intensity":"Hoch"},
        {"session":"Konstanztraining","goal":"Gleichmässige Zwischenphasen, wenig Such-/Wechselzeiten.","intensity":"Moderat"},
        {"session":"Technik / Recovery","goal":"Start, Sortieren, Randstrategie oder lockere Einheit.","intensity":"Leicht"},
    ]

def build_wm_plan(all_results, my_competitions, target_pieces=500):
    comps=(my_competitions or {}).get("competitions",[])
    next_comp=comps[0] if comps else None
    days=_days_until(next_comp.get("date_from")) if next_comp else None
    phase=_phase(days)

    rows=[r for r in all_results if r.get("mode")=="solo" and r.get("pieces")==target_pieces and isinstance(r.get("seconds"),(int,float))]
    rows.sort(key=lambda r:_dt(r.get("finished_at")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    if not rows:
        return {
            "target_pieces":target_pieces,"next_competition":next_comp,"days_until":days,"phase":phase,
            "readiness_score":None,"recommendation":f"Noch keine Solo-Ergebnisse mit {target_pieces} Teilen vorhanden.",
            "weekly_plan":[]
        }

    times=[r["seconds"] for r in rows]
    r5=rows[:5]; r10=rows[:10]; r20=rows[:20]; prev10=rows[10:20]
    avg5=mean(r["seconds"] for r in r5); avg10=mean(r["seconds"] for r in r10); avg20=mean(r["seconds"] for r in r20)

    trend=None
    if len(prev10)>=5:
        old=mean(r["seconds"] for r in prev10)
        trend=round((old-avg10)/old*100,1) if old else None

    recent_times=sorted(r["seconds"] for r in r10)
    lo=recent_times[max(0,int(len(recent_times)*0.2)-1)]
    hi=recent_times[min(len(recent_times)-1,int(len(recent_times)*0.8))]
    recent_best=min(recent_times)

    # Training target = demanding but repeatable, not simply the historical best.
    target=max(recent_best, avg10*0.92)

    # WM targets:
    # realistic = weighted blend of current 5/10 performance with modest improvement;
    # stretch = reachable high-performance day, but never faster than historical best.
    realistic=max(min(times), (avg5*.55 + avg10*.45)*.94)
    stretch=max(min(times), realistic*.94)

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

    recent_days=_recent_training_days(rows,7)
    training=_training_type(phase,trend,consistency,avg5,avg10,recent_days)
    weekly=_weekly_plan(phase,target,_fmt(realistic),_fmt(stretch),consistency,trend)

    if training["type"]=="Turniersimulation":
        recommendation=f"Nächste Einheit: 500er Turniersimulation. Ziel { _fmt(realistic) } oder schneller; Stretch { _fmt(stretch) } nur bei sauberem Flow. Gleiche Start- und Sortierroutine wie an der WM."
    elif training["type"]=="Speed-Run":
        recommendation=f"Nächste Einheit: 500er Speed-Run. Zielbereich {_fmt(target)}–{_fmt(realistic)}. Tempo testen, aber nicht auf Kosten einer chaotischen Startphase."
    elif training["type"]=="Konstanztraining":
        recommendation=f"Nächste Einheit: kontrollierter 500er. Ziel {_fmt(avg10)} oder schneller. Hauptziel: geringe Schwankungen und keine lange schwache Zwischenphase."
    elif training["type"]=="Recovery / Technik":
        recommendation="Nächste Einheit leicht halten: Start-/Sortierroutine oder lockeres Puzzle. Keine zusätzliche harte 500er-Belastung."
    elif training["type"]=="Regeneration":
        recommendation="Kein vollständiger Speed-Run mehr. Schlaf, Frische, Material und Start-Routine priorisieren."
    else:
        recommendation=f"Nächste Einheit: kontrollierter 500er im Bereich {_fmt(target)}–{_fmt(target*1.06)}. Fokus auf reproduzierbaren Ablauf."

    return {
        "target_pieces":target_pieces,"next_competition":next_comp,"days_until":days,"phase":phase,
        "count":len(rows),"best":_fmt(min(times)),"median":_fmt(median(times)),"average_all":_fmt(mean(times)),
        "recent5":_fmt(avg5),"recent10":_fmt(avg10),"recent20":_fmt(avg20),
        "trend10_percent":trend,"current_zone":{"from":_fmt(lo),"to":_fmt(hi)},
        "dynamic_target":_fmt(target),
        "wm_goal_realistic":_fmt(realistic),
        "wm_goal_stretch":_fmt(stretch),
        "consistency_500":consistency,"readiness_score":readiness,
        "next_training":training,
        "recent_training_days_7":recent_days,
        "weekly_plan":weekly,
        "recommendation":recommendation,
        "readiness_explanation":"Kombiniert 500er-Konsistenz, aktuellen Trend, Datenmenge und Aktualität der Trainings.",
        "goal_explanation":"Realistisches WM-Ziel basiert auf den letzten 5/10 500er-Solozeiten mit moderater Fortschrittsannahme. Stretch Goal ist bewusst ambitionierter, bleibt aber durch die historische Bestzeit begrenzt."
    }
