from __future__ import annotations
from datetime import datetime, timezone
from statistics import mean, median, pstdev


def _dt(value):
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace('Z','+00:00'))
    except Exception: return None

def _fmt(seconds):
    if seconds is None: return None
    seconds=int(round(seconds)); h,rem=divmod(seconds,3600); m,s=divmod(rem,60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'

def _days_until(value):
    dt=_dt(value)
    if not dt: return None
    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
    return max(0,int((dt-datetime.now(timezone.utc)).total_seconds()//86400))

def _phase(days):
    if days is None: return {'key':'planning','name':'Planung','description':'Turnierdatum nicht verfügbar.','weekly_sessions':3}
    if days>28: return {'key':'build','name':'Aufbauphase','description':'Tempo und stabile Abläufe entwickeln.','weekly_sessions':4}
    if days>14: return {'key':'specific','name':'Spezifische WM-Phase','description':'500er-Fokus und echte Turniersimulationen erhöhen.','weekly_sessions':4}
    if days>7: return {'key':'sharpen','name':'Schärfungsphase','description':'Qualität vor Umfang; weniger, aber präzisere Einheiten.','weekly_sessions':3}
    if days>2: return {'key':'taper','name':'Tapering','description':'Belastung deutlich reduzieren; Rhythmus und Sicherheit halten.','weekly_sessions':2}
    return {'key':'race','name':'Turniermodus','description':'Keine harte Einheit mehr; Frische, Schlaf und Routine priorisieren.','weekly_sessions':0}

def _recent_training_days(rows, lookback=7):
    now=datetime.now(timezone.utc); dates=set()
    for r in rows:
        dt=_dt(r.get('finished_at'))
        if not dt: continue
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        if 0 <= (now-dt).days <= lookback: dates.add(dt.date())
    return len(dates)

def _training_load(rows, days):
    now=datetime.now(timezone.utc); selected=[]
    for r in rows:
        dt=_dt(r.get('finished_at'))
        if not dt: continue
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        age=(now-dt).total_seconds()/86400
        if 0 <= age <= days: selected.append(r)
    # Piece-weighted load: a 500er = 1.0 unit. Keeps mixed piece counts comparable.
    units=sum(max(0,float(r.get('pieces') or 0))/500 for r in selected)
    return {'days':days,'sessions':len(selected),'units':round(units,1)}

def _training_type(phase, trend, consistency, recent5, recent10, recent_days):
    key=phase['key']
    if key=='race': return {'type':'Regeneration','intensity':'Sehr leicht','reason':'Turnier steht unmittelbar bevor.'}
    if key=='taper': return {'type':'Kontrollierter 500er','intensity':'Leicht','reason':'Form erhalten ohne zusätzliche Ermüdung.'}
    if recent_days>=5: return {'type':'Recovery / Technik','intensity':'Leicht','reason':'Viele Trainingstage in den letzten 7 Tagen.'}
    if consistency < 80: return {'type':'Konstanztraining','intensity':'Moderat','reason':'Schwankungen reduzieren und Ablauf stabilisieren.'}
    if trend is not None and trend >= 8: return {'type':'Turniersimulation','intensity':'Hoch','reason':'Starker positiver Trend erlaubt eine gezielte Belastung.'}
    if recent5 < recent10 * .96: return {'type':'Speed-Run','intensity':'Hoch','reason':'Aktuelle Form ist schneller als der 10er-Schnitt.'}
    if key in ('specific','sharpen'): return {'type':'Turniersimulation','intensity':'Hoch','reason':'WM-spezifische Phase.'}
    return {'type':'Kontrollierter 500er','intensity':'Moderat','reason':'Tempo und Konstanz gemeinsam entwickeln.'}

def _weekly_plan(phase, target, realistic_goal, stretch_goal):
    key=phase['key']
    if key=='race': return [{'session':'Ruhetag / Aktivierung','goal':'10–15 Min. leichte Sortier-/Start-Routine, kein vollständiges Puzzle.','intensity':'Sehr leicht'}]
    if key=='taper': return [
        {'session':'Kontrollierter 500er','goal':f'Sauberer Lauf ohne Maximaldruck, ca. {_fmt(target*1.04)}–{_fmt(target*1.10)}.','intensity':'Leicht'},
        {'session':'Start-/Sortierroutine','goal':'20–30 Min. Startphase, Box öffnen, Rand/Sortierung reproduzierbar üben.','intensity':'Leicht'}]
    if key=='sharpen': return [
        {'session':'Turniersimulation','goal':f'500 Teile, Ziel {realistic_goal} oder schneller; komplette WM-Routine.','intensity':'Hoch'},
        {'session':'Technik / Sortieren','goal':'Kurze Einheit mit Fokus auf Start, Farbfelder und Wechselkosten.','intensity':'Leicht'},
        {'session':'Kontrollierter 500er','goal':f'Konstant im Bereich {_fmt(target)}–{_fmt(target*1.06)} bleiben.','intensity':'Moderat'}]
    if key=='specific': return [
        {'session':'Turniersimulation','goal':f'500 Teile, realistisches WM-Ziel {realistic_goal}.','intensity':'Hoch'},
        {'session':'Speed-Run','goal':f'500 Teile, aggressiver Start; Stretch Goal {stretch_goal} nur bei gutem Flow.','intensity':'Hoch'},
        {'session':'Konstanztraining','goal':f'500 Teile ohne Einbruch; Zielkorridor {_fmt(target)}–{_fmt(target*1.06)}.','intensity':'Moderat'},
        {'session':'Technik / Recovery','goal':'Sortieren, Starttechnik oder sehr lockere Einheit.','intensity':'Leicht'}]
    return [
        {'session':'Kontrollierter 500er','goal':f'Stabiler Lauf im Zielkorridor {_fmt(target)}–{_fmt(target*1.08)}.','intensity':'Moderat'},
        {'session':'Speed-Run','goal':f'Tempo testen; realistisches Ziel {realistic_goal}.','intensity':'Hoch'},
        {'session':'Konstanztraining','goal':'Gleichmässige Zwischenphasen, wenig Such-/Wechselzeiten.','intensity':'Moderat'},
        {'session':'Technik / Recovery','goal':'Start, Sortieren, Randstrategie oder lockere Einheit.','intensity':'Leicht'}]

def _extract_library_puzzles(payload):
    """Best-effort extraction from /me/collections without inventing puzzle names."""
    found={}
    def walk(obj, inherited_owned=False):
        if isinstance(obj, dict):
            owned=inherited_owned or bool(obj.get('owned') or obj.get('is_owned') or obj.get('in_library'))
            candidate=obj.get('puzzle') if isinstance(obj.get('puzzle'),dict) else obj
            name=candidate.get('puzzle_name') or candidate.get('name') or candidate.get('title')
            pid=candidate.get('puzzle_id') or candidate.get('id')
            pieces=candidate.get('pieces_count') or candidate.get('piece_count') or candidate.get('pieces')
            manufacturer=candidate.get('manufacturer_name') or candidate.get('manufacturer') or candidate.get('brand')
            # Require puzzle-like evidence; generic collection names must not become recommendations.
            puzzle_like=bool(candidate.get('puzzle_id') or candidate.get('pieces_count') or candidate.get('piece_count') or candidate.get('puzzle_name') or isinstance(obj.get('puzzle'),dict))
            if name and puzzle_like:
                key=str(pid or (str(name).lower(), str(manufacturer).lower(), pieces))
                found[key]={'id':pid,'name':str(name),'manufacturer':manufacturer,'pieces':pieces,'owned':owned}
            for v in obj.values(): walk(v,owned)
        elif isinstance(obj,list):
            for v in obj: walk(v,inherited_owned)
    walk(payload)
    return list(found.values())

def _next_puzzle(library_payload, all_results, target_pieces, training_type):
    library=_extract_library_puzzles(library_payload)
    candidates=[]
    for p in library:
        try: pieces=int(p.get('pieces')) if p.get('pieces') is not None else None
        except Exception: pieces=None
        if pieces != target_pieces: continue
        candidates.append(p)
    if not candidates:
        return {'available':False,'name':None,'reason':f'Kein eindeutig identifizierbares {target_pieces}-Teile-Puzzle in der synchronisierten MySpeedPuzzling-Bibliothek gefunden. Es wird kein Name erfunden.','library_candidates':0}

    history={}
    for r in all_results:
        if r.get('mode')!='solo': continue
        pid=r.get('puzzle_id'); name=(r.get('puzzle_name') or '').strip().lower()
        key=str(pid) if pid else name
        if not key: continue
        history.setdefault(key,[]).append(r)

    scored=[]
    for p in candidates:
        key=str(p.get('id')) if p.get('id') else p['name'].strip().lower()
        solves=history.get(key,[])
        count=len(solves)
        # Simulations benefit from unseen/less-rehearsed puzzles; technique/recovery can reuse known material.
        if training_type in ('Turniersimulation','Speed-Run','Kontrollierter 500er'):
            score=100-count*18
            rationale='wenig bzw. noch nicht als Solo-Training gelöst – dadurch näher an einer echten Turniersituation' if count<=1 else 'passt zur 500er-Einheit und wurde bisher nicht übermässig oft trainiert'
        else:
            score=70+min(count,4)*5
            rationale='bekanntes 500er-Puzzle eignet sich für Technik, Routine und kontrolliertes Tempo'
        scored.append((score,p,count,rationale))
    scored.sort(key=lambda x:(-x[0],x[2],x[1]['name'].lower()))
    _,p,count,rationale=scored[0]
    return {'available':True,'id':p.get('id'),'name':p['name'],'manufacturer':p.get('manufacturer'),'pieces':target_pieces,'previous_solo_solves':count,'reason':rationale,'library_candidates':len(candidates)}

def build_wm_plan(all_results, my_competitions, library_payload=None, target_pieces=500):
    comps=(my_competitions or {}).get('competitions',[]); next_comp=comps[0] if comps else None
    days=_days_until(next_comp.get('date_from')) if next_comp else None; phase=_phase(days)
    rows=[r for r in all_results if r.get('mode')=='solo' and r.get('pieces')==target_pieces and isinstance(r.get('seconds'),(int,float))]
    rows.sort(key=lambda r:_dt(r.get('finished_at')) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    load7=_training_load(all_results,7); load14=_training_load(all_results,14)
    if not rows:
        return {'target_pieces':target_pieces,'next_competition':next_comp,'days_until':days,'phase':phase,'readiness_score':None,'recommendation':f'Noch keine Solo-Ergebnisse mit {target_pieces} Teilen vorhanden.','weekly_plan':[],'training_load_7':load7,'training_load_14':load14,'next_puzzle':_next_puzzle(library_payload or {},all_results,target_pieces,'Kontrollierter 500er')}

    times=[r['seconds'] for r in rows]; r5=rows[:5]; r10=rows[:10]; r20=rows[:20]; prev10=rows[10:20]
    avg5=mean(r['seconds'] for r in r5); avg10=mean(r['seconds'] for r in r10); avg20=mean(r['seconds'] for r in r20)
    trend=None
    if len(prev10)>=5:
        old=mean(r['seconds'] for r in prev10); trend=round((old-avg10)/old*100,1) if old else None
    recent_times=sorted(r['seconds'] for r in r10); lo=recent_times[max(0,int(len(recent_times)*.2)-1)]; hi=recent_times[min(len(recent_times)-1,int(len(recent_times)*.8))]; recent_best=min(recent_times)
    target=max(recent_best,avg10*.92); realistic=max(min(times),(avg5*.55+avg10*.45)*.94); stretch=max(min(times),realistic*.94)
    cv=pstdev(recent_times)/avg10 if len(recent_times)>1 and avg10 else 1; consistency=max(0,min(100,round(100-cv*100)))
    trend_score=50 if trend is None else max(0,min(100,50+trend*3)); volume_score=min(100,len(rows)/50*100)
    last=_dt(rows[0].get('finished_at')); age=max(0,(datetime.now(timezone.utc)-(last if last.tzinfo else last.replace(tzinfo=timezone.utc))).days) if last else 30; recency_score=max(0,100-age*5)
    # Load penalty prevents high solve volume from inflating readiness.
    load_penalty=max(0,(load7['units']-5)*3)
    readiness=max(0,min(100,round(.35*consistency+.30*trend_score+.20*volume_score+.15*recency_score-load_penalty)))
    recent_days=_recent_training_days(rows,7); training=_training_type(phase,trend,consistency,avg5,avg10,recent_days); weekly=_weekly_plan(phase,target,_fmt(realistic),_fmt(stretch))
    next_puzzle=_next_puzzle(library_payload or {},all_results,target_pieces,training['type'])
    if training['type']=='Turniersimulation': base=f'500er Turniersimulation. Ziel {_fmt(realistic)} oder schneller; Stretch {_fmt(stretch)} nur bei sauberem Flow.'
    elif training['type']=='Speed-Run': base=f'500er Speed-Run. Zielbereich {_fmt(target)}–{_fmt(realistic)}.'
    elif training['type']=='Konstanztraining': base=f'Kontrollierter 500er. Ziel {_fmt(avg10)} oder schneller; Schwankungen reduzieren.'
    elif training['type']=='Recovery / Technik': base='Einheit leicht halten: Start-/Sortierroutine oder lockeres Puzzle.'
    elif training['type']=='Regeneration': base='Kein vollständiger Speed-Run mehr. Frische und Start-Routine priorisieren.'
    else: base=f'Kontrollierter 500er im Bereich {_fmt(target)}–{_fmt(target*1.06)}.'
    recommendation=('Nächstes Puzzle: '+next_puzzle['name']+'. '+base) if next_puzzle.get('available') else base+' '+next_puzzle['reason']
    pace100=avg10/5
    weakness='Konstanz' if consistency<80 else ('Tempo' if trend is not None and trend<0 else ('Belastungssteuerung' if load7['units']>5 else 'Turnierroutine'))
    return {'target_pieces':target_pieces,'next_competition':next_comp,'days_until':days,'phase':phase,'count':len(rows),'best':_fmt(min(times)),'median':_fmt(median(times)),'average_all':_fmt(mean(times)),'recent5':_fmt(avg5),'recent10':_fmt(avg10),'recent20':_fmt(avg20),'trend10_percent':trend,'current_zone':{'from':_fmt(lo),'to':_fmt(hi)},'dynamic_target':_fmt(target),'wm_goal_realistic':_fmt(realistic),'wm_goal_stretch':_fmt(stretch),'consistency_500':consistency,'readiness_score':readiness,'next_training':training,'recent_training_days_7':recent_days,'weekly_plan':weekly,'recommendation':recommendation,'training_load_7':load7,'training_load_14':load14,'wm_pace_per_100':_fmt(pace100),'weakness_focus':weakness,'next_puzzle':next_puzzle,'readiness_explanation':'Kombiniert 500er-Konsistenz, Trend, Datenmenge, Aktualität und aktuelle Trainingsbelastung.','goal_explanation':'Realistisches WM-Ziel basiert auf den letzten 5/10 500er-Solozeiten; Stretch Goal bleibt durch die historische Bestzeit begrenzt.'}
