# 🌕 Astron1221 Moon Phase Calendar

A Python astronomy project that generates a **complete lunar calendar** with illumination, phase, and event correlations — then visualizes it in both **Jupyter Notebook** and an interactive **Streamlit web app**.  

---

## 🧠 Overview

The Moon Phase Calendar calculates the **phase, illumination fraction, Earth–Moon distance**, and **dark-sky observing windows** for the year 2025.  
It merges these data with a user-provided `events.csv` file to explore how moonlight conditions relate to personal or astronomical events.  
The accompanying **Streamlit app** lets users look up lunar data for any date interactively.

---

## ✨ Features

### Core (Python + Jupyter)
- 🧮 Generates daily lunar data between two given dates.
- 🌙 Computes **Moon phase angle**, **illumination fraction**, and **phase name**.
- 📏 Calculates **Earth–Moon distance** in kilometers.
- 🌑 Flags **dark-sky nights** (<20% illumination) for observing opportunities.
- 🌕 Detects **supermoons** (closest full moons to Earth).
- 🔵 Detects **blue moons** (two full moons in one month).
- 🌘 Finds **lunar eclipses** in a given year using `eclipselib`.
- 📅 Merges results with `events.csv` (user events like observations, birthdays, etc.).
- 📈 Plots illumination over time with shaded dark-sky windows and event markers.

### Interactive (Streamlit App)
- 🗓️ **Date lookup**: select any date and see moon phase + illumination instantly.
- 📍 **Optional location input** (latitude/longitude) to compute rise/set times.
- 📅 **Event correlation**: shows personal events for selected dates.
- 🔭 **Nearby date table**: ±3 days around selected date for context.
- 🌕 **Dynamic metrics**: phase, illumination %, distance, dark-sky flag.

---

## 📂 Project Structure
Astron1221-Moon-Phase-Calendar/
│
├── Project2_Trusko_Cheng.ipynb # Main notebook: lunar data, plotting, detection
├── app.py # Streamlit app: interactive moon phase viewer
├── events.csv # User events (date, title, category, notes)
│
├── data/ # Auto-created by Skyfield
├── de440s.bsp # stores DE440 ephemeris
├── requirements.txt # Dependencies list
├── .gitignore # Ignore /data, /venv, .ipynb_checkpoints
└── README.md # This file

---

## How to Use the Streamlit App
1. Install web dependencies
- In your terminal, type: pip install streamlit pandas numpy skyfield matplotlib astropy

2. Run the Streamlit App
- In your terminal, type: streamlit run app.py

3. Open the provided URL (usually http://localhost:8501) to:
- Pick a date
- See moon phase, illumination, and dark-sky info
- View related events and nearby dates