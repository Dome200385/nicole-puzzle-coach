from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean, pstdev


def _dt(value):
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return datetime.min


def _fmt(seconds):
    if seconds is None:
        return None
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def normalize_results(results_payload):
    """Normalize the real MySpeedPuzzling /me/results structure."""
    rows = []
    if not isinstance(results_payload, dict):
        return rows

    for mode in ("solo", "duo", "team"):
        block = results_payload.get(mode) or {}
        source = block.get("results", []) if isinstance(block, dict) else []
        for raw in source:
            if not isinstance(raw, dict):
                continue
            seconds = raw.get("time_seconds")
            pieces = raw.get("pieces_count")
            if not isinstance(seconds, (int, float)) or seconds <= 0:
                continue
            if not isinstance(pieces, (int, float)) or pieces <= 0:
                pieces = None

            pace100 = (seconds / pieces * 100.0) if pieces else None
            rows.append({
                "time_id": raw.get("time_id"),
                "puzzle_id": raw.get("puzzle_id"),
                "puzzle_name": raw.get("puzzle_name") or "Unbekanntes Puzzle",
                "manufacturer": raw.get("manufacturer_name") or "Unbekannt",
                "pieces": int(pieces) if pieces else None,
                "seconds": float(seconds),
                "time": _fmt(seconds),
                "finished_at": raw.get("finished_at"),
                "mode": mode,
                "first_attempt": raw.get("first_attempt"),
                "puzzle_image": raw.get("puzzle_image"),
                "pace_per_100": pace100,
            })

    rows.sort(key=lambda r: _dt(r.get("finished_at")), reverse=True)
    return rows


def _piece_groups(rows):
    groups = defaultdict(list)
    for r in rows:
        if r["pieces"]:
            groups[r["pieces"]].append(r)

    output = []
    for pieces, group in groups.items():
        if len(group) < 2:
            continue
        times = [r["seconds"] for r in group]
        recent = sorted(group, key=lambda r: _dt(r["finished_at"]), reverse=True)
        recent5 = recent[:5]
        previous5 = recent[5:10]
        trend = None
        if len(recent5) >= 3 and len(previous5) >= 3:
            old = mean(r["seconds"] for r in previous5)
            new = mean(r["seconds"] for r in recent5)
            if old:
                trend = round((old - new) / old * 100.0, 1)
        output.append({
            "pieces": pieces,
            "count": len(group),
            "best_seconds": min(times),
            "best": _fmt(min(times)),
            "average_seconds": round(mean(times)),
            "average": _fmt(mean(times)),
            "recent5_average": _fmt(mean(r["seconds"] for r in recent5)),
            "trend_percent": trend,
        })

    output.sort(key=lambda x: (-x["count"], x["pieces"]))
    return output


def _manufacturer_groups(rows):
    groups = defaultdict(list)
    for r in rows:
        if r["manufacturer"]:
            groups[r["manufacturer"]].append(r)

    output = []
    for manufacturer, group in groups.items():
        if len(group) < 3:
            continue
        paces = [r["pace_per_100"] for r in group if r["pace_per_100"]]
        output.append({
            "manufacturer": manufacturer,
            "count": len(group),
            "avg_seconds_per_100": round(mean(paces), 1) if paces else None,
            "avg_time_per_100": _fmt(mean(paces)) if paces else None,
        })

    output.sort(key=lambda x: (-x["count"], x["manufacturer"].lower()))
    return output[:12]


def _form_and_consistency(solo_rows):
    usable = [r for r in solo_rows if r["pace_per_100"]]
    if len(usable) < 6:
        return None, None, "Noch zu wenige vergleichbare Solo-Ergebnisse."

    recent = usable[:10]
    previous = usable[10:20]

    recent_paces = [r["pace_per_100"] for r in recent]
    form = None
    if len(previous) >= 5:
        old = mean(r["pace_per_100"] for r in previous)
        new = mean(recent_paces)
        if old:
            form = round((old - new) / old * 100.0, 1)

    avg = mean(recent_paces)
    cv = (pstdev(recent_paces) / avg) if avg else 1
    consistency = max(0, min(100, round(100 - cv * 100)))

    if form is None:
        recommendation = "Weitere aktuelle Solo-Ergebnisse sammeln, damit der Formtrend stabil berechnet werden kann."
    elif form >= 5:
        recommendation = "Aktuelle Form ist klar positiv. Tempo halten und gezielt unter Turnierbedingungen trainieren."
    elif form >= 0:
        recommendation = "Form ist stabil bis leicht positiv. Fokus auf konstante Abläufe und sauberes Sortieren."
    elif form > -5:
        recommendation = "Leichter Formrückgang. Eine kontrollierte Einheit mit Fokus auf Fehlervermeidung ist sinnvoll."
    else:
        recommendation = "Deutlicher Formrückgang in den letzten Ergebnissen. Belastung reduzieren und Technik/Konsistenz priorisieren."

    return form, consistency, recommendation


def build_training_summary(results_payload):
    rows = normalize_results(results_payload)
    solo = [r for r in rows if r["mode"] == "solo"]

    form, consistency, recommendation = _form_and_consistency(solo)

    best = min(rows, key=lambda r: r["seconds"], default=None)
    mode_counts = {
        mode: sum(1 for r in rows if r["mode"] == mode)
        for mode in ("solo", "duo", "team")
    }

    latest = rows[:12]
    return {
        "total_results": len(rows),
        "mode_counts": mode_counts,
        "best_overall": best,
        "form_percent": form,
        "consistency_score": consistency,
        "recommendation": recommendation,
        "latest_results": latest,
        "piece_groups": _piece_groups(solo),
        "manufacturer_groups": _manufacturer_groups(solo),
        "latest_result_at": latest[0]["finished_at"] if latest else None,
        "method": {
            "form": "Recent 10 vs previous 10 Solo results, normalized to seconds per 100 pieces.",
            "consistency": "Variation of recent 10 Solo results, normalized to seconds per 100 pieces.",
        },
    }
