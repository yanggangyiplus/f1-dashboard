from pathlib import Path

import pandas as pd
import streamlit as st

DIR = Path(__file__).parent / "data" / "f1"
NOT_STARTED = ["Did not qualify", "Did not prequalify", "Did not start", "Withdrew"]


def rd(name):
    return pd.read_csv(DIR / f"{name}.csv", na_values=["\\N"])


@st.cache_data(show_spinner="데이터 불러오는 중…")
def load():
    races, circuits, drivers = rd("races"), rd("circuits"), rd("drivers")
    cons, status, res = rd("constructors"), rd("status"), rd("results")
    races["date"] = pd.to_datetime(races["date"])
    drivers["driver"] = drivers["forename"] + " " + drivers["surname"]
    drivers["dob"] = pd.to_datetime(drivers["dob"])
    cons = cons.rename(columns={"name": "team"})

    R = (res.merge(races[["raceId", "year", "round", "name", "date", "circuitId"]].rename(columns={"name": "race"}), on="raceId")
         .merge(drivers[["driverId", "driver", "nationality", "dob"]], on="driverId")
         .merge(cons[["constructorId", "team"]], on="constructorId")
         .merge(status, on="statusId"))
    R["positionText"] = R["positionText"].astype(str)
    R["started"] = ~R["status"].isin(NOT_STARTED) & ~R["positionText"].isin(["F", "W"])
    R["classified"] = R["positionText"].str.isdigit()
    R["dnf"] = R["started"] & (R["positionText"] == "R")
    R["decade"] = (R["year"] // 10 * 10).astype(str) + "s"

    fin = races.sort_values("round").groupby("year").tail(1)[["raceId", "year"]]  # 시즌 마지막 라운드
    ds = rd("driver_standings").merge(drivers[["driverId", "driver"]], on="driverId")
    cs = rd("constructor_standings").merge(cons[["constructorId", "team"]], on="constructorId")
    return dict(R=R, races=races, circuits=circuits, drivers=drivers, cons=cons, ds=ds, cs=cs,
                fin=fin, weather=rd("weather"), tyre=rd("tire_stints"), ymax=int(R["year"].max()))
