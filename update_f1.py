"""data/f1 에 아직 없는 2026 라운드를 Jolpica API에서 받아 이어 붙인다.

python3 update_f1.py --check   # 이미 있는 15라운드를 API로 다시 만들어 기존 행과 비교만 한다 (파일 안 바뀜)
python3 update_f1.py           # 빠진 라운드를 추가한다 (바꾸는 표는 data/f1_backup/ 에 먼저 복사)

갱신 대상: races, results, qualifying, sprint_results, driver_standings, constructor_standings
(+ 새 드라이버/팀/서킷/상태가 있으면 drivers, constructors, circuits, status)
갱신 안 함: lap_times, pit_stops, constructor_results, tire_stints, weather, practice_results
"""
import csv
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request

DIR = "data/f1"
BACKUP = "data/f1_backup"
YEAR = 2026
API = f"https://api.jolpi.ca/ergast/f1/{YEAR}"
NULL = "\\N"
TABLES = ["races", "results", "qualifying", "sprint_results", "driver_standings",
          "constructor_standings", "drivers", "constructors", "circuits", "status"]


def get(path):
    url = f"{API}{path}" + ("&" if "?" in path else "?") + "limit=100"
    req = urllib.request.Request(url, headers={"User-Agent": "f1-dataset-updater"})
    for i in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.7)  # 요청 제한을 지키려고 천천히
                return json.load(r)["MRData"]
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 5:
                raise
            time.sleep(2 ** (i + 1))


def n(v):
    return NULL if v in (None, "") else str(v)


class Data:
    def __init__(self):
        self.rows = {}
        self.cols = {}
        for t in TABLES:
            with open(f"{DIR}/{t}.csv", newline="") as f:
                rd = csv.DictReader(f)
                self.cols[t] = rd.fieldnames
                self.rows[t] = list(rd)
        self.new = {t: [] for t in TABLES}
        self.next = {t: max(int(r[self.cols[t][0]]) for r in self.rows[t]) + 1 for t in TABLES}

    def add(self, table, row):
        row = {c: row.get(c, NULL) for c in self.cols[table]}
        row[self.cols[table][0]] = str(self.next[table])
        self.next[table] += 1
        self.new[table].append(row)
        self.rows[table].append(row)  # 같은 실행 안에서 다시 찾을 수 있게
        return row

    def find(self, table, col, value):
        for r in self.rows[table]:
            if r[col] == value:
                return r[self.cols[table][0]]
        return None


def driver_id(D, d):
    return D.find("drivers", "driverRef", d["driverId"]) or D.add("drivers", {
        "driverRef": d["driverId"], "number": n(d.get("permanentNumber")), "code": n(d.get("code")),
        "forename": d["givenName"], "surname": d["familyName"], "dob": n(d.get("dateOfBirth")),
        "nationality": n(d.get("nationality")), "url": n(d.get("url"))})["driverId"]


def constructor_id(D, c):
    return D.find("constructors", "constructorRef", c["constructorId"]) or D.add("constructors", {
        "constructorRef": c["constructorId"], "name": c["name"],
        "nationality": n(c.get("nationality")), "url": n(c.get("url"))})["constructorId"]


def circuit_id(D, c):
    loc = c["Location"]
    return D.find("circuits", "circuitRef", c["circuitId"]) or D.add("circuits", {
        "circuitRef": c["circuitId"], "name": c["circuitName"], "location": loc["locality"],
        "country": loc["country"], "lat": loc["lat"], "lng": loc["long"], "alt": "0",  # 고도는 API에 없음
        "url": n(c.get("url"))})["circuitId"]


def status_id(D, text):
    return D.find("status", "status", text) or D.add("status", {"status": text})["statusId"]


def result_row(D, race_id, r, sprint=False):
    fl = r.get("FastestLap") or {}
    pos_text = r["positionText"]
    row = {
        "raceId": str(race_id), "driverId": driver_id(D, r["Driver"]),
        "constructorId": constructor_id(D, r["Constructor"]), "number": n(r.get("number")),
        "grid": r["grid"], "position": r["position"] if pos_text.isdigit() else NULL,
        "positionText": pos_text, "positionOrder": r["position"],
        "points": r["points"] if sprint else str(float(r["points"])), "laps": r["laps"],
        "time": n((r.get("Time") or {}).get("time")), "milliseconds": n((r.get("Time") or {}).get("millis")),
        "fastestLap": n(fl.get("lap")), "fastestLapTime": n((fl.get("Time") or {}).get("time")),
        "statusId": status_id(D, r["status"]),
    }
    if not sprint:
        row["rank"] = n(fl.get("rank"))
        row["fastestLapSpeed"] = NULL  # README: 2025/2026 은 속도 값이 없음
    return row


def build_round(D, sched, race_id):
    """한 라운드의 모든 행을 만든다. 결과가 아직 없으면 None."""
    rnd = sched["round"]
    res = get(f"/{rnd}/results.json")["RaceTable"]["Races"]
    if not res:
        return None
    out = {t: [] for t in ["races", "results", "qualifying", "sprint_results",
                           "driver_standings", "constructor_standings"]}
    sess = lambda k, f: n((sched.get(k) or {}).get(f))
    out["races"].append({
        "raceId": str(race_id), "year": str(YEAR), "round": rnd,
        "circuitId": circuit_id(D, sched["Circuit"]), "name": sched["raceName"],
        "date": sched["date"], "time": n(sched.get("time")), "url": n(sched.get("url")),
        "fp1_date": sess("FirstPractice", "date"), "fp1_time": sess("FirstPractice", "time"),
        "fp2_date": sess("SecondPractice", "date"), "fp2_time": sess("SecondPractice", "time"),
        "fp3_date": sess("ThirdPractice", "date"), "fp3_time": sess("ThirdPractice", "time"),
        "quali_date": sess("Qualifying", "date"), "quali_time": sess("Qualifying", "time"),
        "sprint_date": sess("Sprint", "date"), "sprint_time": sess("Sprint", "time")})
    for r in res[0]["Results"]:
        out["results"].append(result_row(D, race_id, r))
    q = get(f"/{rnd}/qualifying.json")["RaceTable"]["Races"]
    for r in (q[0]["QualifyingResults"] if q else []):
        out["qualifying"].append({
            "raceId": str(race_id), "driverId": driver_id(D, r["Driver"]),
            "constructorId": constructor_id(D, r["Constructor"]), "number": n(r.get("number")),
            "position": r["position"], "q1": n(r.get("Q1")), "q2": n(r.get("Q2")), "q3": n(r.get("Q3"))})
    sp = get(f"/{rnd}/sprint.json")["RaceTable"]["Races"]
    for r in (sp[0]["SprintResults"] if sp else []):
        out["sprint_results"].append(result_row(D, race_id, r, sprint=True))
    ds = get(f"/{rnd}/driverStandings.json")["StandingsTable"]["StandingsLists"]
    for r in (ds[0]["DriverStandings"] if ds else []):
        out["driver_standings"].append({
            "raceId": str(race_id), "driverId": driver_id(D, r["Driver"]), "points": str(float(r["points"])),
            "position": n(r.get("position")), "positionText": r["positionText"], "wins": r["wins"]})
    cs = get(f"/{rnd}/constructorStandings.json")["StandingsTable"]["StandingsLists"]
    for r in (cs[0]["ConstructorStandings"] if cs else []):
        out["constructor_standings"].append({
            "raceId": str(race_id), "constructorId": constructor_id(D, r["Constructor"]),
            "points": str(float(r["points"])), "position": n(r.get("position")),
            "positionText": r["positionText"], "wins": r["wins"]})
    return out


def check(D, sched_by_round):
    """이미 있는 마지막 라운드를 API로 다시 만들어 기존 행과 같은지 비교한다."""
    last = max(int(r["round"]) for r in D.rows["races"] if r["year"] == str(YEAR))
    race = next(r for r in D.rows["races"] if r["year"] == str(YEAR) and int(r["round"]) == last)
    rid = race["raceId"]
    out = build_round(D, sched_by_round[str(last)], rid)
    keys = {"races": None, "results": ["driverId"], "qualifying": ["driverId"],
            "driver_standings": ["driverId"], "constructor_standings": ["constructorId"]}
    ok = True
    for t, k in keys.items():
        old = [r for r in D.rows[t] if r["raceId"] == rid and r not in D.new[t]]
        new = out[t]
        idcol = D.cols[t][0]
        cols = [c for c in D.cols[t] if c != idcol]
        o = sorted(tuple(r[c] for c in cols) for r in old)
        w = sorted(tuple(r[c] for c in cols) for r in new)
        diff = [c for c in cols if sorted(r[c] for r in old) != sorted(r[c] for r in new)]
        print(f"{t:22s} 기존 {len(old):3d}행 / API {len(new):3d}행 -> {'동일' if o == w else '다름: ' + str(diff)}")
        ok &= o == w
    print("새로 만들어진 드라이버/팀/서킷/상태:", {t: len(D.new[t]) for t in ["drivers", "constructors", "circuits", "status"]})
    return ok


def main():
    D = Data()
    sched = {r["round"]: r for r in get(".json")["RaceTable"]["Races"]}
    if "--check" in sys.argv:
        check(D, sched)
        return
    have = {r["round"] for r in D.rows["races"] if r["year"] == str(YEAR)}
    added = []
    for rnd in sorted(sched, key=int):
        if rnd in have:
            continue
        out = build_round(D, sched[rnd], D.next["races"])
        if out is None:
            continue  # 아직 안 열린 라운드
        for t, rows in out.items():
            for row in rows:
                D.add(t, row)
        added.append(rnd)
    if not added:
        print("추가할 라운드가 없습니다.")
        return
    os.makedirs(BACKUP, exist_ok=True)
    for t in TABLES:
        if D.new[t]:
            if not os.path.exists(f"{BACKUP}/{t}.csv"):  # 처음 백업만 남김
                shutil.copy(f"{DIR}/{t}.csv", f"{BACKUP}/{t}.csv")
            with open(f"{DIR}/{t}.csv", "rb+") as f:
                f.seek(-1, 2)
                if f.read(1) != b"\n":
                    f.write(b"\n")
            with open(f"{DIR}/{t}.csv", "a", newline="") as f:
                csv.DictWriter(f, D.cols[t], lineterminator="\n").writerows(D.new[t])
    print("추가한 라운드:", added)
    print("표별 추가 행:", {t: len(v) for t, v in D.new.items() if v})


if __name__ == "__main__":
    main()
