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

def _as_int(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None


# Puzzles confirmed by user feedback as originating from a prior championship.
# These are not deleted from the library; they are strongly de-prioritized for
# WM simulation because the preliminary round is expected to be closer to
# ordinary published retail puzzles not previously revealed at championships.
KNOWN_CHAMPIONSHIP_PUZZLES = {
    "art studio": {
        "source": "US-Meisterschaft",
        "confidence": "confirmed_by_user",
    },
}

_COMPETITION_WORDS = (
    "championship", "championships", "competition", "contest", "tournament",
    "meisterschaft", "national championship", "nationals", "speed puzzling event",
)

def _image_url(image):
    if not image:
        return None
    image = str(image).strip()
    if image.startswith("http://") or image.startswith("https://"):
        return image
    image = image.lstrip("/")
    return f"https://img.myspeedpuzzling.com/preset:puzzle_small/plain/{image}"

def _provenance_text(candidate):
    """
    Collect only provenance-like metadata. We deliberately do not classify
    championship origin solely from the puzzle title.
    """
    bits = []
    interesting = (
        "competition", "championship", "event", "contest", "tournament",
        "source", "origin", "edition", "category", "tag", "series",
    )

    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                low = str(key).lower()
                path = f"{prefix}.{low}" if prefix else low
                if any(k in low for k in interesting):
                    if isinstance(value, (str, int, float, bool)):
                        bits.append(f"{path}:{value}")
                    elif isinstance(value, dict):
                        for k2, v2 in value.items():
                            if isinstance(v2, (str, int, float, bool)):
                                bits.append(f"{path}.{k2}:{v2}")
                if isinstance(value, (dict, list)):
                    walk(value, path)
        elif isinstance(obj, list):
            for value in obj[:50]:
                walk(value, prefix)
    walk(candidate)
    return " | ".join(bits)

def _competition_risk(name, provenance):
    normalized = (name or "").strip().lower()
    if normalized in KNOWN_CHAMPIONSHIP_PUZZLES:
        info = KNOWN_CHAMPIONSHIP_PUZZLES[normalized]
        return {
            "score": 100,
            "level": "hoch",
            "reason": f"bereits als Meisterschaftspuzzle bekannt ({info['source']})",
            "source": info["source"],
        }

    text = (provenance or "").lower()
    if any(word in text for word in _COMPETITION_WORDS):
        return {
            "score": 90,
            "level": "hoch",
            "reason": "Bibliotheks-Metadaten weisen auf einen früheren Wettbewerb hin",
            "source": provenance,
        }

    return {
        "score": 0,
        "level": "niedrig",
        "reason": "kein Hinweis auf frühere Meisterschaftsnutzung gefunden",
        "source": None,
    }


def _wm_fit_score(puzzle, history, training_type):
    """
    Transparent WM-Fit score 0-100.
    This helper only ranks puzzle candidates. It does NOT alter readiness,
    goals, training load, pace or the weekly training logic.
    """
    history = history or []
    solves = len(history)
    pieces = int(puzzle.get("pieces") or 0)
    manufacturer = str(puzzle.get("manufacturer") or "").strip().lower()
    risk = puzzle.get("competition_risk") or {"score": 0}

    score = 50
    reasons = []

    if pieces == 500:
        score += 15
        reasons.append("500 Teile")
    else:
        score -= 20

    if manufacturer == "ravensburger":
        score += 8
        reasons.append("Ravensburger")

    if risk.get("score", 0) >= 80:
        score -= 45
        reasons.append("früherer Meisterschaftseinsatz")
    else:
        score += 12
        reasons.append("kein Meisterschaftshinweis")

    if solves == 0:
        score += 15
        reasons.append("noch nie Solo gelöst")
    elif solves == 1:
        score += 7
        reasons.append("1 Solo-Lauf")
    elif solves <= 3:
        score += 2
        reasons.append(f"{solves} Solo-Läufe")
    else:
        score -= min(12, (solves - 3) * 2)
        reasons.append(f"{solves} Solo-Läufe")

    days = _days_since_last_solve(history)
    if days is None:
        score += 5
        reasons.append("kein Erinnerungsvorteil")
    elif days >= 180:
        score += 5
        reasons.append("lange nicht gelöst")
    elif days >= 90:
        score += 2
    elif days <= 30:
        score -= 8
        reasons.append("kürzlich gelöst")

    # Role-specific, limited bonuses only.
    if training_type in ("Turniersimulation", "Speed-Run"):
        if solves == 0:
            score += 8
            reasons.append("hoher Neuheitseffekt")
        if risk.get("score", 0) >= 80:
            score -= 15
    elif training_type == "Kontrollierter 500er":
        if 1 <= solves <= 3:
            score += 8
            reasons.append("guter Vergleichswert")
    elif training_type == "Konstanztraining":
        if 1 <= solves <= 4:
            score += 10
            reasons.append("guter Konstanzvergleich")
        elif solves == 0:
            score -= 5

    score = max(0, min(100, int(round(score))))
    label = "sehr hoch" if score >= 85 else "hoch" if score >= 70 else "mittel" if score >= 55 else "niedrig"

    unique = []
    for r in reasons:
        if r not in unique:
            unique.append(r)

    return {
        "score": score,
        "label": label,
        "summary": " · ".join(unique[:4]),
        "reasons": unique[:6],
    }

def _wm_suitability(puzzle, solve_count=0):
    risk = puzzle.get("competition_risk") or {"score": 0}
    if risk.get("score", 0) >= 80:
        return {
            "level": "niedrig",
            "label": "WM-Ähnlichkeit niedrig",
            "reason": "früheres Meisterschaftspuzzle – für eine realistische WM-Vorrunden-Simulation weniger geeignet",
        }
    if solve_count == 0:
        return {
            "level": "hoch",
            "label": "WM-Ähnlichkeit hoch",
            "reason": "veröffentlichtes Bibliotheks-Puzzle ohne bekannten Meisterschaftshinweis und ohne Erinnerungsvorteil",
        }
    if solve_count <= 2:
        return {
            "level": "gut",
            "label": "WM-Ähnlichkeit gut",
            "reason": "kein Meisterschaftshinweis und nur geringer Wiederholungsvorteil",
        }
    return {
        "level": "mittel",
        "label": "WM-Ähnlichkeit mittel",
        "reason": "kein Meisterschaftshinweis, aber durch Wiederholungen weniger wettkampfnah",
    }

def _extract_library_puzzles(payload):
    """
    Extract actual puzzle entries from the expanded MySpeedPuzzling library.

    V5.8 expects get_library() output, where every collection contains an
    items_payload fetched from /me/collections/{collectionId}/items.
    Parsing remains deliberately defensive because API field names can evolve.
    A recommendation is only returned when a real puzzle name is present.
    """
    found = {}

    def add_candidate(candidate, collection_name=None):
        if not isinstance(candidate, dict):
            return

        nested = candidate.get("puzzle")
        if isinstance(nested, dict):
            merged = dict(candidate)
            merged.update(nested)
            candidate = merged

        pid = (
            candidate.get("puzzle_id")
            or candidate.get("puzzleId")
            or candidate.get("id")
        )
        name = (
            candidate.get("puzzle_name")
            or candidate.get("puzzleName")
            or candidate.get("name")
            or candidate.get("title")
        )
        manufacturer = (
            candidate.get("manufacturer_name")
            or candidate.get("manufacturerName")
            or candidate.get("manufacturer")
            or candidate.get("brand")
        )
        if isinstance(manufacturer, dict):
            manufacturer = (
                manufacturer.get("name")
                or manufacturer.get("title")
                or manufacturer.get("manufacturer_name")
            )

        pieces = _as_int(
            candidate.get("pieces_count")
            or candidate.get("piecesCount")
            or candidate.get("piece_count")
            or candidate.get("pieces")
        )
        image = (
            candidate.get("puzzle_image")
            or candidate.get("image")
            or candidate.get("image_url")
            or candidate.get("thumbnail")
        )
        provenance = _provenance_text(candidate)
        competition_risk = _competition_risk(str(name or ""), provenance)

        # We never manufacture a name. Require a real name and at least one
        # piece of puzzle-specific evidence.
        puzzle_evidence = bool(pid or pieces or candidate.get("puzzle_id") or isinstance(nested, dict))
        if not name or not puzzle_evidence:
            return

        key = str(pid or (str(name).strip().lower(), str(manufacturer or "").strip().lower(), pieces))
        found[key] = {
            "id": pid,
            "name": str(name).strip(),
            "manufacturer": manufacturer,
            "pieces": pieces,
            "image": image,
            "image_url": _image_url(image),
            "collection": collection_name,
            "in_library": True,
            "provenance": provenance,
            "competition_risk": competition_risk,
        }

    def walk(obj, collection_name=None):
        if isinstance(obj, dict):
            # Avoid turning collection metadata itself into a puzzle.
            collection_keys = {"collection_id", "visibility", "description", "items_payload"}
            looks_like_collection = "collection_id" in obj and "items_payload" in obj
            if not looks_like_collection:
                add_candidate(obj, collection_name)

            next_collection = collection_name
            if looks_like_collection:
                next_collection = obj.get("name") or collection_name

            for key, value in obj.items():
                if key in ("description", "visibility"):
                    continue
                walk(value, next_collection)
        elif isinstance(obj, list):
            for value in obj:
                walk(value, collection_name)

    walk(payload)
    return list(found.values())

def _history_for_puzzle(all_results, puzzle):
    pid = puzzle.get("id")
    pname = (puzzle.get("name") or "").strip().lower()
    rows = []
    for r in all_results:
        if r.get("mode") != "solo":
            continue
        rid = r.get("puzzle_id")
        rname = (r.get("puzzle_name") or "").strip().lower()
        if (pid and rid and str(pid) == str(rid)) or (pname and rname == pname):
            rows.append(r)
    rows.sort(
        key=lambda r: _dt(r.get("finished_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return rows

def _days_since_last_solve(rows):
    if not rows:
        return None
    dt = _dt(rows[0].get("finished_at"))
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - dt).days)

def _next_puzzle(library_payload, all_results, target_pieces, training_type, excluded_ids=None):
    excluded_ids={str(x) for x in (excluded_ids or []) if x}
    library = _extract_library_puzzles(library_payload)
    candidates = [p for p in library if _as_int(p.get("pieces")) == target_pieces and str(p.get("id")) not in excluded_ids]

    if not candidates:
        return {
            "available": False,
            "name": None,
            "reason": (
                f"Kein konkret benanntes {target_pieces}-Teile-Puzzle wurde in den "
                "geladenen MySpeedPuzzling-Bibliotheks-Einträgen gefunden. "
                "Es wird kein Puzzle-Name erfunden."
            ),
            "library_total": len(library),
            "library_candidates": 0,
        }

    scored = []
    for puzzle in candidates:
        history = _history_for_puzzle(all_results, puzzle)
        solve_count = len(history)
        days_since = _days_since_last_solve(history)

        # Base score rewards a long gap since the last solve.
        score = 50.0
        if days_since is None:
            score += 35
        else:
            score += min(days_since, 120) / 4

        if training_type in ("Turniersimulation", "Speed-Run"):
            # Novelty is valuable: less memory advantage, closer to competition.
            score += max(0, 35 - solve_count * 10)
            if solve_count == 0:
                rationale = (
                    "noch nie als Solo-Ergebnis erfasst – dadurch besonders gut "
                    "für eine realistische Turniersimulation ohne Erinnerungsvorteil"
                )
            elif solve_count == 1:
                rationale = (
                    "erst einmal als Solo-Ergebnis erfasst – wenig Wiederholungsvorteil "
                    "und deshalb gut für wettkampfnahes Tempo"
                )
            else:
                rationale = (
                    "passt zur 500er-Einheit; die Auswahl bevorzugt innerhalb der "
                    "Bibliothek möglichst wenig wiederholte Puzzles"
                )

        elif training_type in ("Recovery / Technik", "Regeneration"):
            # Known puzzles are useful for technique because puzzle difficulty
            # is less likely to dominate the session.
            score += min(solve_count, 4) * 8
            if days_since is not None:
                score += min(days_since, 60) / 6
            rationale = (
                "bereits bekanntes Bibliotheks-Puzzle – dadurch geeignet für "
                "Start-, Sortier- und Technikarbeit ohne reine Bestzeitjagd"
            )

        elif training_type == "Konstanztraining":
            # Prefer one with at least one benchmark but avoid heavy repetition.
            score += 22 if 1 <= solve_count <= 3 else 0
            score -= max(0, solve_count - 3) * 6
            rationale = (
                "liefert einen brauchbaren Vergleichswert, ohne zu stark durch "
                "häufige Wiederholung verfälscht zu sein"
            )

        else:  # Controlled 500
            score += 18 if solve_count <= 2 else 0
            rationale = (
                "passt zur kontrollierten 500er-Einheit und bietet einen guten "
                "Kompromiss aus Vergleichbarkeit und geringem Wiederholungseffekt"
            )

        # WM relevance: championship-used puzzles are technically valid
        # training puzzles, but are poor proxies for a WM preliminary round
        # dominated by already-published retail puzzles that have not already
        # appeared at a championship.
        risk = puzzle.get("competition_risk") or {"score": 0}
        if training_type in ("Turniersimulation", "Speed-Run", "Kontrollierter 500er"):
            score -= risk.get("score", 0) * 8
        else:
            score -= risk.get("score", 0) * 1.5

        # Slight preference for Ravensburger because current 500er benchmark
        # data is dominated by Ravensburger, but never at the cost of inventing.
        manufacturer = str(puzzle.get("manufacturer") or "")
        if manufacturer.lower() == "ravensburger":
            score += 4

        scored.append((score, puzzle, history, rationale))

    scored.sort(
        key=lambda item: (
            -item[0],
            len(item[2]),
            item[1]["name"].lower(),
        )
    )
    score, puzzle, history, rationale = scored[0]
    days_since = _days_since_last_solve(history)

    return {
        "available": True,
        "id": puzzle.get("id"),
        "name": puzzle["name"],
        "manufacturer": puzzle.get("manufacturer"),
        "pieces": target_pieces,
        "image": puzzle.get("image"),
        "image_url": puzzle.get("image_url"),
        "collection": puzzle.get("collection"),
        "competition_risk": puzzle.get("competition_risk"),
        "wm_suitability": _wm_suitability(puzzle, len(history)),
        "wm_fit": _wm_fit_score(puzzle, history, training_type),
        "previous_solo_solves": len(history),
        "days_since_last_solve": days_since,
        "reason": rationale,
        "library_total": len(library),
        "library_candidates": len(candidates),
        "excluded_count": len({str(x) for x in (excluded_ids or []) if x}),
        "selection_score": round(score, 1),
    }



def _is_excluded_puzzle(puzzle, excluded_ids=None):
    excluded={str(x) for x in (excluded_ids or []) if x}
    pid=puzzle.get("id") if isinstance(puzzle,dict) else None
    return bool(pid and str(pid) in excluded)

def _weekly_plan_with_puzzles(weekly_plan, library_payload, all_results, target_pieces=500, excluded_ids=None):
    """
    Attach a concrete real MySpeedPuzzling library puzzle to each weekly
    full-puzzle session. Avoid duplicate puzzle assignments inside the same week.
    Technique-only sessions may intentionally have no full puzzle.
    """
    excluded_ids={str(x) for x in (excluded_ids or []) if x}
    library = _extract_library_puzzles(library_payload or {})
    candidates = [p for p in library if _as_int(p.get("pieces")) == target_pieces and str(p.get("id")) not in excluded_ids]
    used = set()
    enriched = []

    def training_type_for_session(name):
        n = (name or "").lower()
        if "turnier" in n:
            return "Turniersimulation"
        if "speed" in n:
            return "Speed-Run"
        if "konstanz" in n:
            return "Konstanztraining"
        if "technik" in n or "recovery" in n or "sortier" in n or "routine" in n:
            return "Recovery / Technik"
        return "Kontrollierter 500er"

    for session in weekly_plan or []:
        row = dict(session)
        session_name = row.get("session", "")
        ttype = training_type_for_session(session_name)

        # Pure technique/routine sessions do not need a complete puzzle.
        lower = session_name.lower()
        full_puzzle = not (
            ("technik" in lower or "routine" in lower or "aktivierung" in lower)
            and "500" not in lower
            and "turnier" not in lower
            and "speed" not in lower
            and "konstanz" not in lower
        )

        if not full_puzzle:
            row["puzzle"] = {
                "available": False,
                "not_required": True,
                "name": None,
                "reason": "Für diese Technik-/Routineeinheit ist kein vollständiges Puzzle nötig."
            }
            enriched.append(row)
            continue

        # Score each real candidate with the same principles as _next_puzzle,
        # while excluding puzzles already assigned elsewhere this week.
        ranked = []
        for puzzle in candidates:
            if _is_excluded_puzzle(puzzle, excluded_ids):
                continue
            key = str(puzzle.get("id") or puzzle.get("name"))
            if key in used:
                continue
            history = _history_for_puzzle(all_results, puzzle)
            solve_count = len(history)
            days_since = _days_since_last_solve(history)
            score = 50.0 + (35 if days_since is None else min(days_since, 120) / 4)

            if ttype in ("Turniersimulation", "Speed-Run"):
                score += max(0, 35 - solve_count * 10)
                reason = (
                    "für wettkampfnahes Tempo gewählt; wenig Wiederholung wird bevorzugt"
                    if solve_count else
                    "noch nie als Solo-Ergebnis erfasst – ideal für einen Lauf ohne Erinnerungsvorteil"
                )
            elif ttype == "Konstanztraining":
                score += 22 if 1 <= solve_count <= 3 else 0
                score -= max(0, solve_count - 3) * 6
                reason = "für Konstanztraining gewählt: vorhandener Vergleichswert bei begrenzter Wiederholung"
            elif ttype == "Recovery / Technik":
                score += min(solve_count, 4) * 8
                reason = "bekanntes Puzzle wird für Technikarbeit und einen kontrollierten Ablauf bevorzugt"
            else:
                score += 18 if solve_count <= 2 else 0
                reason = "für einen kontrollierten 500er als Balance aus Vergleichbarkeit und Neuheit gewählt"

            risk = puzzle.get("competition_risk") or {"score": 0}
            if ttype in ("Turniersimulation", "Speed-Run", "Kontrollierter 500er"):
                score -= risk.get("score", 0) * 8
            else:
                score -= risk.get("score", 0) * 1.5

            if str(puzzle.get("manufacturer") or "").lower() == "ravensburger":
                score += 4
            ranked.append((score, puzzle, history, reason))

        ranked.sort(key=lambda x: (-x[0], len(x[2]), x[1]["name"].lower()))
        if ranked:
            score, puzzle, history, reason = ranked[0]
            key = str(puzzle.get("id") or puzzle.get("name"))
            used.add(key)
            row["puzzle"] = {
                "available": True,
                "id": puzzle.get("id"),
                "name": puzzle.get("name"),
                "manufacturer": puzzle.get("manufacturer"),
                "pieces": puzzle.get("pieces"),
                "image": puzzle.get("image"),
                "image_url": puzzle.get("image_url"),
                "collection": puzzle.get("collection"),
                "competition_risk": puzzle.get("competition_risk"),
                "wm_suitability": _wm_suitability(puzzle, len(history)),
                "wm_fit": _wm_fit_score(puzzle, history, ttype),
                "previous_solo_solves": len(history),
                "days_since_last_solve": _days_since_last_solve(history),
                "reason": reason,
                "selection_score": round(score, 1),
            }
        else:
            row["puzzle"] = {
                "available": False,
                "not_required": False,
                "name": None,
                "reason": f"Kein weiteres eindeutig benanntes {target_pieces}-Teile-Puzzle aus der Bibliothek verfügbar."
            }
        enriched.append(row)
    return enriched

def build_wm_plan(all_results, my_competitions, library_payload=None, target_pieces=500, excluded_puzzle_ids=None):
    comps=(my_competitions or {}).get('competitions',[]); next_comp=comps[0] if comps else None
    days=_days_until(next_comp.get('date_from')) if next_comp else None; phase=_phase(days)
    rows=[r for r in all_results if r.get('mode')=='solo' and r.get('pieces')==target_pieces and isinstance(r.get('seconds'),(int,float))]
    rows.sort(key=lambda r:_dt(r.get('finished_at')) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    load7=_training_load(all_results,7); load14=_training_load(all_results,14)
    if not rows:
        return {'target_pieces':target_pieces,'next_competition':next_comp,'days_until':days,'phase':phase,'readiness_score':None,'recommendation':f'Noch keine Solo-Ergebnisse mit {target_pieces} Teilen vorhanden.','weekly_plan':[],'training_load_7':load7,'training_load_14':load14,'next_puzzle':_next_puzzle(library_payload or {},all_results,target_pieces,'Kontrollierter 500er',excluded_puzzle_ids)}

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
    recent_days=_recent_training_days(rows,7); training=_training_type(phase,trend,consistency,avg5,avg10,recent_days); weekly=_weekly_plan(phase,target,_fmt(realistic),_fmt(stretch)); weekly=_weekly_plan_with_puzzles(weekly,library_payload or {},all_results,target_pieces,excluded_puzzle_ids)
    next_puzzle=_next_puzzle(library_payload or {},all_results,target_pieces,training['type'],excluded_puzzle_ids)
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
