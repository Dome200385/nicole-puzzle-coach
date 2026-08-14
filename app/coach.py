from datetime import datetime, date
from statistics import mean, median, pstdev
from collections import defaultdict

def _list_from_payload(payload, keys=("results", "items", "data", "collections", "puzzles")):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []

def _first(d, keys, default=None):
    if not isinstance(d, dict):
        return default
    for key in keys:
        if key in d and d[key] not in (None, ""):
            return d[key]
    return default

def _seconds(row):
    value = _first(row, ("duration_seconds", "time_seconds", "seconds", "solving_time_seconds", "time"))
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        parts = value.split(":")
        try:
            parts = [int(x) for x in parts]
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            if len(parts) == 2:
                return parts[0] * 60 + parts[1]
        except Exception:
            return None
    return None

def _pieces(row):
    value = _first(row, ("piece_count", "pieces", "number_of_pieces", "numberOfPieces"))
    try:
        return int(value) if value is not None else None
    except Exception:
        return None

def _puzzle_id(row):
    value = _first(row, ("puzzle_id", "puzzleId", "id"))
    return str(value) if value is not None else None

def _name(row):
    return str(_first(row, ("puzzle_name", "name", "title"), "Unbekanntes Puzzle"))

def _manufacturer(row):
    value = _first(row, ("manufacturer", "brand", "producer"))
    if isinstance(value, dict):
        return str(_first(value, ("name", "title"), ""))
    return str(value or "")

def _date_value(row):
    raw = _first(row, ("date", "solved_at", "created_at", "createdAt"))
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(str(raw), "%Y-%m-%d")
        except Exception:
            return None

def normalize_results(results_payload):
    rows = []
    if isinstance(results_payload, dict):
        for mode, payload in results_payload.items():
            if mode == "error":
                continue
            source = _list_from_payload(payload)
            for row in source:
                if isinstance(row, dict):
                    rows.append({
                        "mode": mode,
                        "puzzle_id": _puzzle_id(row),
                        "name": _name(row),
                        "manufacturer": _manufacturer(row),
                        "pieces": _pieces(row),
                        "seconds": _seconds(row),
                        "date": _date_value(row),
                        "raw": row,
                    })
    else:
        for row in _list_from_payload(results_payload):
            if isinstance(row, dict):
                rows.append({
                    "mode": str(_first(row, ("mode", "type"), "solo")),
                    "puzzle_id": _puzzle_id(row),
                    "name": _name(row),
                    "manufacturer": _manufacturer(row),
                    "pieces": _pieces(row),
                    "seconds": _seconds(row),
                    "date": _date_value(row),
                    "raw": row,
                })
    return rows

def normalize_owned(collections_payload):
    collections = _list_from_payload(collections_payload, ("collections", "items", "data"))
    items = []
    seen = set()

    def add_item(row, collection_name=None):
        if not isinstance(row, dict):
            return
        pid = _puzzle_id(row)
        key = pid or (_name(row), _manufacturer(row), _pieces(row))
        if key in seen:
            return
        seen.add(key)
        items.append({
            "puzzle_id": pid,
            "name": _name(row),
            "manufacturer": _manufacturer(row),
            "pieces": _pieces(row),
            "collection": collection_name,
            "raw": row,
        })

    for collection in collections:
        if not isinstance(collection, dict):
            continue
        nested = _list_from_payload(collection, ("items", "puzzles", "data"))
        if nested:
            cname = str(_first(collection, ("name", "title"), ""))
            for row in nested:
                add_item(row, cname)
        else:
            add_item(collection, None)
    return items

def performance_summary(results_payload, mode="solo", pieces=None):
    rows = [
        r for r in normalize_results(results_payload)
        if r["mode"] == mode and r["seconds"] and (pieces is None or r["pieces"] == pieces)
    ]
    if not rows:
        return {"count": 0, "message": "Noch keine passenden Resultate vorhanden."}

    rows.sort(key=lambda r: r["date"] or datetime.min)
    times = [r["seconds"] for r in rows]
    recent = times[-10:]
    previous = times[-20:-10] if len(times) >= 11 else times[:-len(recent)]

    baseline = median(times)
    recent_avg = mean(recent)
    previous_avg = mean(previous) if previous else baseline
    trend_pct = round((previous_avg - recent_avg) / previous_avg * 100, 1) if previous_avg else 0

    consistency = 100.0
    if len(recent) >= 3 and mean(recent) > 0:
        cv = pstdev(recent) / mean(recent)
        consistency = max(0, min(100, 100 - cv * 250))

    best = min(rows, key=lambda r: r["seconds"])
    worst = max(rows, key=lambda r: r["seconds"])

    return {
        "count": len(rows),
        "baseline_seconds": round(baseline),
        "recent_average_seconds": round(recent_avg),
        "trend_percent": trend_pct,
        "consistency_score": round(consistency),
        "best": {"name": best["name"], "seconds": best["seconds"], "pieces": best["pieces"]},
        "worst": {"name": worst["name"], "seconds": worst["seconds"], "pieces": worst["pieces"]},
    }

def owned_vs_history(results_payload, collections_payload):
    results = normalize_results(results_payload)
    owned = normalize_owned(collections_payload)
    owned_ids = {x["puzzle_id"] for x in owned if x["puzzle_id"]}
    solved_ids = {x["puzzle_id"] for x in results if x["puzzle_id"]}

    historical_not_owned = [r for r in results if r["puzzle_id"] and r["puzzle_id"] not in owned_ids]
    owned_unsolved = [p for p in owned if p["puzzle_id"] and p["puzzle_id"] not in solved_ids]

    return {
        "owned_count": len(owned),
        "solved_result_count": len(results),
        "historical_solved_not_owned_count": len(historical_not_owned),
        "owned_unsolved_count": len(owned_unsolved),
        "historical_solved_not_owned": historical_not_owned[:100],
        "owned_unsolved": owned_unsolved[:100],
    }

def tournament_readiness(training_sessions, tournament):
    relevant = []
    for s in training_sessions:
        if tournament.get("mode") and s.get("mode") and tournament["mode"] != s["mode"]:
            continue
        if tournament.get("manufacturer") and s.get("manufacturer"):
            if tournament["manufacturer"].lower() not in s["manufacturer"].lower():
                continue
        if tournament.get("piece_count") and s.get("piece_count"):
            if tournament["piece_count"] != s["piece_count"]:
                continue
        relevant.append(s)

    if not relevant:
        return {
            "score": 20,
            "label": "Noch zu wenig turnierspezifisches Training",
            "components": {"specific_training": 0, "consistency": 0, "target_achievement": 0}
        }

    times = [s["duration_seconds"] for s in relevant if s.get("duration_seconds")]
    target_pairs = [
        (s["duration_seconds"], s["target_seconds"])
        for s in relevant
        if s.get("duration_seconds") and s.get("target_seconds")
    ]

    specific = min(100, len(relevant) * 12)
    consistency = 50
    if len(times) >= 3 and mean(times) > 0:
        consistency = max(0, min(100, 100 - (pstdev(times) / mean(times)) * 240))

    target_achievement = 50
    if target_pairs:
        hits = sum(actual <= target for actual, target in target_pairs)
        target_achievement = 100 * hits / len(target_pairs)

    score = round(specific * 0.40 + consistency * 0.35 + target_achievement * 0.25)
    label = (
        "Sehr gut vorbereitet" if score >= 85 else
        "Gut auf Kurs" if score >= 70 else
        "Aufbauphase" if score >= 50 else
        "Mehr gezieltes Training nötig"
    )
    return {
        "score": score,
        "label": label,
        "components": {
            "specific_training": round(specific),
            "consistency": round(consistency),
            "target_achievement": round(target_achievement),
            "relevant_sessions": len(relevant),
        }
    }

def next_puzzle_recommendation(results_payload, collections_payload, tournament=None):
    results = normalize_results(results_payload)
    owned = normalize_owned(collections_payload)

    solved_ids = {r["puzzle_id"] for r in results if r["puzzle_id"]}
    solo_by_pieces = {}
    for r in results:
        if r["mode"] == "solo" and r["seconds"] and r["pieces"]:
            solo_by_pieces.setdefault(r["pieces"], []).append(r["seconds"])

    candidates = []
    for p in owned:
        if p["puzzle_id"] and p["puzzle_id"] in solved_ids:
            continue
        score = 40.0
        reasons = []
        if tournament:
            target_mfr = (tournament.get("manufacturer") or "").lower()
            if target_mfr and target_mfr in p["manufacturer"].lower():
                score += 25
                reasons.append("passt zum Hersteller des geplanten Turniers")
            target_pieces = tournament.get("piece_count")
            if target_pieces and p["pieces"] == target_pieces:
                score += 25
                reasons.append("passt exakt zur Turnier-Teilezahl")
        if "ravensburger" in p["manufacturer"].lower():
            score += 5
            reasons.append("Ravensburger-Training")
        if p["pieces"] in solo_by_pieces and len(solo_by_pieces[p["pieces"]]) >= 3:
            score += 5
            reasons.append("genügend persönliche Vergleichsdaten für eine Zielzeit")
        candidates.append((score, p, reasons))

    if not candidates:
        return {"status": "no_candidate", "message": "Noch kein ungelöstes Puzzle aus der aktuellen Bibliothek erkannt."}

    candidates.sort(key=lambda x: x[0], reverse=True)
    score, puzzle, reasons = candidates[0]
    target_seconds = None
    history = solo_by_pieces.get(puzzle["pieces"], [])
    if history:
        target_seconds = round(median(history) * 0.97)

    return {
        "status": "ok",
        "puzzle_id": puzzle["puzzle_id"],
        "puzzle_name": puzzle["name"],
        "manufacturer": puzzle["manufacturer"],
        "piece_count": puzzle["pieces"],
        "training_score": round(min(score, 100), 1),
        "target_seconds": target_seconds,
        "reason": ", ".join(reasons) if reasons else "ungelöstes Puzzle aus der aktuellen Bibliothek",
    }

def manual_training_overview(sessions):
    valid = [s for s in sessions if s.get("duration_seconds")]
    if not valid:
        return {
            "count": len(sessions),
            "timed_count": 0,
            "best_seconds": None,
            "average_seconds": None,
            "recent_average_seconds": None,
            "trend_percent": None,
            "consistency_score": None,
            "by_pieces": [],
            "by_manufacturer": [],
            "recommendation": "Erfasse einige Trainingszeiten, damit der Coach Muster erkennen kann."
        }

    valid = sorted(valid, key=lambda x: x.get("date") or "")
    times = [s["duration_seconds"] for s in valid]
    recent = times[-5:]
    previous = times[-10:-5] if len(times) >= 6 else times[:-len(recent)]

    avg = mean(times)
    recent_avg = mean(recent)
    previous_avg = mean(previous) if previous else avg
    trend = round((previous_avg - recent_avg) / previous_avg * 100, 1) if previous_avg else 0

    consistency = 100
    if len(recent) >= 3 and mean(recent) > 0:
        consistency = max(0, min(100, 100 - (pstdev(recent) / mean(recent)) * 250))

    by_pieces = []
    groups = defaultdict(list)
    for s in valid:
        if s.get("piece_count"):
            groups[s["piece_count"]].append(s["duration_seconds"])
    for pieces, vals in sorted(groups.items()):
        by_pieces.append({
            "piece_count": pieces,
            "count": len(vals),
            "average_seconds": round(mean(vals)),
            "best_seconds": min(vals),
        })

    by_manufacturer = []
    mgroups = defaultdict(list)
    for s in valid:
        m = (s.get("manufacturer") or "").strip()
        if m:
            mgroups[m].append(s["duration_seconds"])
    for m, vals in sorted(mgroups.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))[:8]:
        by_manufacturer.append({
            "manufacturer": m,
            "count": len(vals),
            "average_seconds": round(mean(vals)),
            "best_seconds": min(vals),
        })

    recommendation = "Weiter konstant trainieren."
    if len(valid) < 4:
        recommendation = "Noch 2–3 Trainings mit Zeit erfassen, damit Form und Konsistenz belastbarer werden."
    elif consistency < 65:
        recommendation = "Fokus auf Konstanz: gleiche Teilezahl mehrfach trainieren und Zielzeit nur leicht verschärfen."
    elif trend < -3:
        recommendation = "Leistung zuletzt schwächer: heute ein vertrautes Puzzleformat mit sauberer Technik statt Maximaltempo."
    elif trend > 3 and consistency >= 75:
        recommendation = "Form ist gut: nächste Session als Turniersimulation mit realem Zeitlimit durchführen."

    return {
        "count": len(sessions),
        "timed_count": len(valid),
        "best_seconds": min(times),
        "average_seconds": round(avg),
        "recent_average_seconds": round(recent_avg),
        "trend_percent": trend,
        "consistency_score": round(consistency),
        "by_pieces": by_pieces,
        "by_manufacturer": by_manufacturer,
        "recommendation": recommendation,
    }

def tournament_countdown(tournaments):
    today = date.today()
    upcoming = []
    for t in tournaments:
        try:
            d = datetime.strptime(t["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        if d >= today:
            upcoming.append((d, t))
    if not upcoming:
        return None
    upcoming.sort(key=lambda x: x[0])
    d, t = upcoming[0]
    return {
        "id": t["id"],
        "name": t["name"],
        "date": t["date"],
        "days_left": (d - today).days,
        "location": t.get("location"),
        "mode": t.get("mode"),
        "manufacturer": t.get("manufacturer"),
        "piece_count": t.get("piece_count"),
    }
