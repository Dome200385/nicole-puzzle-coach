from statistics import mean,pstdev
def readiness_score(sessions,t):
    rel=[]
    for s in sessions:
        if t.get("manufacturer") and s.get("manufacturer") and t["manufacturer"].lower() not in s["manufacturer"].lower(): continue
        if t.get("piece_count") and s.get("piece_count") and t["piece_count"]!=s["piece_count"]: continue
        rel.append(s)
    if not rel: return {"score":25,"label":"Noch zu wenig turnierspezifisches Training","components":{"specific_training":0,"consistency":0,"target_achievement":0}}
    times=[s["duration_seconds"] for s in rel if s.get("duration_seconds")]
    targets=[(s["duration_seconds"],s["target_seconds"]) for s in rel if s.get("duration_seconds") and s.get("target_seconds")]
    specific=min(100,len(rel)*12); consistency=50
    if len(times)>=3 and mean(times)>0: consistency=max(0,min(100,100-(pstdev(times)/mean(times))*220))
    target=50 if not targets else 100*sum(a<=b for a,b in targets)/len(targets)
    score=round(specific*.4+consistency*.35+target*.25)
    label="Sehr gut vorbereitet" if score>=85 else "Gut auf Kurs" if score>=70 else "Aufbauphase" if score>=50 else "Mehr gezieltes Training nötig"
    return {"score":score,"label":label,"components":{"specific_training":round(specific),"consistency":round(consistency),"target_achievement":round(target),"relevant_sessions":len(rel)}}
