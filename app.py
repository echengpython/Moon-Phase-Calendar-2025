import os
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
import streamlit as st

from skyfield.api import load, Topos
from skyfield import almanac

# ------------------------------------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Moon Phase Lookup",
    page_icon="🌙",
    layout="centered",
)

st.title("🌙 Moon Phase Lookup")
st.write("Pick a date and (optionally) a location to see the Moon phase, illumination, and dark-sky info.")


# ------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ILLUM_THRESHOLD = 0.20  # same as your notebook


# ------------------------------------------------------------
# CACHED EPHEMERIS LOADING
# (so Streamlit doesn’t download on every rerun)
# ------------------------------------------------------------
@st.cache_resource(show_spinner=True)
def load_ephemeris():
    ts = load.timescale()
    # this will download to ./data if not present
    eph = load("de440s.bsp")
    earth = eph["earth"]
    moon = eph["moon"]
    sun = eph["sun"]
    return ts, eph, earth, moon, sun


ts, eph, earth, moon, sun = load_ephemeris()


def generate_lunar_dataframe(start_date, end_date, observer_lat=None, observer_lon=None):
    """
    Generate a pandas DataFrame with lunar information for each day from start_date to end_date inclusive.
    Same logic as your notebook version.
    """
    start = pd.to_datetime(start_date).normalize()
    end = pd.to_datetime(end_date).normalize()
    days = pd.date_range(start, end, freq="D")

    # Skyfield times (00:00 UTC)
    t = ts.utc(days.year.values, days.month.values, days.day.values, 0, 0, 0)

    # phase angle + illum frac
    phase_angles = almanac.moon_phase(eph, t)
    illum_frac = (1 - np.cos(phase_angles.radians)) / 2.0

    # distance Earth→Moon (geocentric)
    moon_pos = earth.at(t).observe(moon)
    distances_au = moon_pos.distance().au
    AU_TO_KM = 149597870.7
    distances_km = distances_au * AU_TO_KM

    # phase name buckets
    phase_deg = phase_angles.degrees

    def phase_label(deg):
        deg = deg % 360
        if deg < 45 or deg >= 315:
            return "New"
        elif 45 <= deg < 135:
            return "First Quarter"
        elif 135 <= deg < 225:
            return "Full"
        elif 225 <= deg < 315:
            return "Last Quarter"
        else:
            return "Unknown"

    phase_names = [phase_label(d) for d in phase_deg]

    df = pd.DataFrame(
        {
            "date": days.date,
            "ts": t.utc_iso(),
            "phase_deg": phase_deg,
            "illum_frac": illum_frac,
            "distance_km": distances_km,
            "phase_name": phase_names,
        }
    ).set_index("date")

    df["dark_sky"] = df["illum_frac"] < ILLUM_THRESHOLD

    # optional rise/set
    if observer_lat is not None and observer_lon is not None:
        obs = Topos(latitude_degrees=observer_lat, longitude_degrees=observer_lon)
        f = almanac.risings_and_settings(eph, moon, obs)

        rises = []
        sets = []
        for day in days:
            t0 = ts.utc(day.year, day.month, day.day, 0, 0, 0)
            next_day = day + timedelta(days=1)
            t1 = ts.utc(next_day.year, next_day.month, next_day.day, 0, 0, 0)
            times, events = almanac.find_discrete(t0, t1, f)

            rise_time = None
            set_time = None
            for ti, ev in zip(times, events):
                if ev == 1 and rise_time is None:
                    rise_time = ti.utc_datetime()
                if ev == 0 and set_time is None:
                    set_time = ti.utc_datetime()
            rises.append(rise_time)
            sets.append(set_time)
        df["moon_rise_utc"] = rises
        df["moon_set_utc"] = sets

    return df


# ------------------------------------------------------------
# SIDEBAR: USER INPUTS
# ------------------------------------------------------------
st.sidebar.header("🔎 Lookup options")

# date picker
selected_date = st.sidebar.date_input(
    "Date to look up",
    value=date.today(),
    min_value=date(1900, 1, 1),
    max_value=date(2100, 12, 31),
)

# toggle location
use_location = st.sidebar.checkbox("Use observer location (for rise/set)?", value=False)

observer_lat = None
observer_lon = None
if use_location:
    observer_lat = st.sidebar.number_input("Latitude (deg)", value=39.9625, format="%.4f")
    observer_lon = st.sidebar.number_input("Longitude (deg)", value=-83.0032, format="%.4f")

# optional: show surrounding week
show_week = st.sidebar.checkbox("Show ±3 days around date", value=True)

# try to load events.csv like your notebook
events_df = None
events_path = "events.csv"
if os.path.exists(events_path):
    try:
        events_df = pd.read_csv(events_path, parse_dates=["date"])
        events_df["date"] = events_df["date"].dt.date
    except Exception as e:
        st.sidebar.warning(f"Could not read events.csv: {e}")


# ------------------------------------------------------------
# MAIN LOGIC: GET THAT DAY'S MOON INFO
# ------------------------------------------------------------
# just generate a 1-day dataframe
lunar_df = generate_lunar_dataframe(
    start_date=selected_date,
    end_date=selected_date,
    observer_lat=observer_lat,
    observer_lon=observer_lon,
)

row = lunar_df.iloc[0]

st.subheader(f"Results for {selected_date.isoformat()}")

col1, col2, col3 = st.columns(3)
col1.metric("Phase", row["phase_name"])
col2.metric("Illumination", f"{row['illum_frac']*100:.1f}%")
col3.metric("Distance", f"{row['distance_km']:,.0f} km")

st.write(
    f"**Dark-sky day (<{ILLUM_THRESHOLD*100:.0f}% illumination)?** "
    + ("✅ Yes" if row["dark_sky"] else "❌ No")
)

if use_location:
    st.markdown("**Rise / Set (UTC):**")
    st.write(f"- Moonrise: {row['moon_rise_utc'] if pd.notnull(row.get('moon_rise_utc')) else '—'}")
    st.write(f"- Moonset: {row['moon_set_utc'] if pd.notnull(row.get('moon_set_utc')) else '—'}")

# show event for that date if present
if events_df is not None:
    todays_events = events_df[events_df["date"] == selected_date]
    if not todays_events.empty:
        st.markdown("### 📅 Events on this date (from `events.csv`)")
        st.dataframe(todays_events)
    else:
        st.markdown("📅 No events in `events.csv` for this date.")
else:
    st.markdown("*(No `events.csv` found — skipping events.)*")


# ------------------------------------------------------------
# OPTIONAL: SHOW NEARBY DATES
# ------------------------------------------------------------
if show_week:
    start_week = selected_date - timedelta(days=3)
    end_week = selected_date + timedelta(days=3)
    week_df = generate_lunar_dataframe(
        start_week,
        end_week,
        observer_lat=observer_lat if use_location else None,
        observer_lon=observer_lon if use_location else None,
    ).reset_index()

    week_df["illum_%"] = (week_df["illum_frac"] * 100).map(lambda x: f"{x:.1f}%")
    week_df["date"] = pd.to_datetime(week_df["date"]).dt.date
    st.markdown("### Nearby dates")
    st.dataframe(
        week_df[["date", "phase_name", "illum_%", "dark_sky", "distance_km"]].rename(
            columns={
                "date": "Date",
                "phase_name": "Phase",
                "illum_%": "Illumination",
                "dark_sky": "Dark sky?",
                "distance_km": "Distance (km)",
            }
        ),
        hide_index=True,
    )


