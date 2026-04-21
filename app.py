# app.py - NASA Grid Lap Times

# Streamlit web app: select track, class, and date range

# Deploy free at: https://streamlit.io/cloud

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone, date

st.set_page_config(
page_title=“NASA Grid Laps”,
page_icon=”:checkered_flag:”,
layout=“centered”,
)

st.markdown(”””

<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
  .stApp { background-color: #0f1117; color: #e8e8e8; }

  .page-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 3px solid #e94560;
    padding: 1.5rem 1.5rem 1.2rem;
    margin-bottom: 1.5rem;
    border-radius: 0 0 8px 8px;
  }
  .page-header h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem; font-weight: 700;
    letter-spacing: 0.05em; color: #ffffff; margin: 0 0 0.2rem;
  }
  .page-header p { color: #a0aec0; font-size: 0.9rem; margin: 0; }
  .accent { color: #e94560; }

  .section-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #e94560; margin-bottom: 0.3rem;
  }

  .pill {
    display: inline-block; padding: 0.2rem 0.7rem;
    border-radius: 20px; font-size: 0.78rem;
    font-weight: 600; letter-spacing: 0.05em;
  }
  .pill-success { background: #1c4532; color: #68d391; }
  .pill-warn    { background: #744210; color: #f6ad55; }
  .pill-info    { background: #1a365d; color: #63b3ed; }

  .grid-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.88rem; margin-top: 1rem;
  }
  .grid-table thead tr { background: #e94560; color: white; }
  .grid-table thead th {
    font-family: 'Barlow Condensed', sans-serif; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 0.6rem 0.75rem; text-align: left;
  }
  .grid-table tbody tr:nth-child(even) { background: #1a1f2e; }
  .grid-table tbody tr:nth-child(odd)  { background: #151929; }
  .grid-table tbody tr:hover           { background: #0f3460; }
  .grid-table td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid #2d3748; color: #e8e8e8;
  }
  .grid-table td.pos { color: #a0aec0; font-size: 0.82rem; width: 2rem; }
  .grid-table td.laptime {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem; color: #68d391; font-weight: 600;
  }
  .grid-table tbody tr:first-child td.laptime { color: #f6e05e; }
  .grid-table td.meta { color: #a0aec0; font-size: 0.8rem; }

  div[data-testid="stButton"] > button {
    background: #e94560 !important; color: white !important;
    border: none !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.1rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 0.7rem 2rem !important; border-radius: 4px !important;
    width: 100% !important; margin-top: 0.5rem !important;
  }
  div[data-testid="stDownloadButton"] > button {
    background: #2d3748 !important; color: #e8e8e8 !important;
    border: 1px solid #4a5568 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 600 !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    width: 100% !important;
  }
  div[data-testid="stSelectbox"] label,
  div[data-testid="stDateInput"] label,
  div[data-testid="stTextInput"] label,
  div[data-testid="stNumberInput"] label,
  div[data-testid="stRadio"] label {
    color: #a0aec0 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
  }
  div[data-testid="stExpander"] {
    background: #1a1f2e !important;
    border: 1px solid #2d3748 !important;
    border-radius: 6px !important;
  }
  footer { visibility: hidden; }
</style>

“””, unsafe_allow_html=True)

# ––––– header ———————————————————–

st.markdown(”””

<div class="page-header">
  <h1>NASA <span class="accent">Grid</span> Laps</h1>
  <p>Fastest lap per driver -- sorted for race day grid lineup</p>
</div>
""", unsafe_allow_html=True)

# ––––– helpers –––––––––––––––––––––––––––––

def lap_to_seconds(lap_time):
if not lap_time:
return None
try:
s = str(lap_time).strip()
if “:” in s:
m, sec = s.split(”:”, 1)
return int(m) * 60 + float(sec)
return float(s)
except (ValueError, AttributeError):
return None

def seconds_to_lap(secs):
m = int(secs // 60)
s = secs % 60
return “%d:%06.3f” % (m, s)

def parse_event_date(ev):
for key in (“date”, “startDate”, “start_date”, “eventDate”, “event_date”):
val = ev.get(key)
if val:
try:
dt = datetime.fromisoformat(str(val).replace(“Z”, “+00:00”))
return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
except ValueError:
continue
return None

def name_matches(name, query):
return query.strip().lower() in name.lower()

def get_field(d, *keys):
for k in keys:
v = d.get(k)
if v:
return v
return None

# ––––– cached API calls ———————————————––

@st.cache_resource(show_spinner=False)
def get_client():
from mylaps_client_wrapper import SpeedhiveClient
return SpeedhiveClient()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_events(org_id):
client = get_client()
return list(client.iter_events(org_id))

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_sessions(event_id):
client = get_client()
return client.get_sessions(event_id) or []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_results(session_id):
client = get_client()
return client.get_results(session_id) or []

# ––––– org config (collapsible, advanced) —————————––

with st.expander(“Advanced: Organisation Settings”, expanded=False):
org_id = st.number_input(
“Speedhive Org ID”,
min_value=1, value=41593, step=1,
help=“Find your org ID in the Speedhive URL: speedhive.mylaps.com/organizations/XXXXX”,
)
st.caption(“Default 41593 = NASA Mid-Atlantic”)

# ––––– main filters (always visible) ————————————

st.markdown(”#### Filters”)

col_a, col_b = st.columns(2)
with col_a:
date_from = st.date_input(“From”, value=date.today() - timedelta(days=365))
with col_b:
date_to = st.date_input(“To”, value=date.today())

track_input_mode = st.radio(
“Track selection”, [“Choose from list”, “Type manually”], horizontal=True
)

track_filter = “”
if track_input_mode == “Choose from list”:
with st.spinner(“Loading tracks…”):
try:
all_events_for_list = fetch_all_events(org_id)
cutoff_dt = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
track_names = set()
for ev in all_events_for_list:
ev_date = parse_event_date(ev)
if ev_date and ev_date < cutoff_dt:
continue
loc = ev.get(“location”) or ev.get(“venue”) or ev.get(“name”) or “”
if loc:
track_names.add(loc.strip())
track_list = sorted(track_names)
choice = st.selectbox(“Track”, [”(all tracks)”] + track_list)
track_filter = “” if choice == “(all tracks)” else choice
except Exception as e:
st.error(“Could not load tracks: %s” % e)
track_filter = st.text_input(“Track name fragment”)
else:
track_filter = st.text_input(
“Track name fragment”,
placeholder=“e.g. Carolina”,
)

class_filter = st.text_input(
“Class / session filter”,
value=“Spec E30”,
placeholder=“e.g. Spec E30, TTD, TTA”,
help=“Leave blank to show all classes”,
)

run_btn = st.button(“FETCH GRID”, use_container_width=True)

if not run_btn:
st.stop()

# ––––– run query ––––––––––––––––––––––––––––

from_dt = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
to_dt   = datetime.combine(date_to,   datetime.max.time()).replace(tzinfo=timezone.utc)

progress_bar = st.progress(0, text=“Loading events…”)
status_text  = st.empty()

try:
all_events = fetch_all_events(org_id)
except Exception as e:
st.error(“Could not connect to Speedhive API: %s” % e)
st.stop()

matching_events = []
for ev in all_events:
ev_name = ev.get(“name”, “”) or “”
ev_loc  = ev.get(“location”, “”) or ev.get(“venue”, “”) or “”
combined = ev_name + “ “ + ev_loc
if track_filter and not name_matches(combined, track_filter):
continue
ev_date = parse_event_date(ev)
if ev_date:
if ev_date < from_dt or ev_date > to_dt:
continue
matching_events.append(ev)

if not matching_events:
progress_bar.empty()
st.warning(
“No events found for ‘%s’ between %s and %s. “
“Try a shorter name fragment or switch to ‘Type manually’.”
% (track_filter or “all tracks”, date_from, date_to)
)
st.stop()

driver_best = {}
total = len(matching_events)

for i, ev in enumerate(matching_events):
ev_id    = ev.get(“id”)
ev_name  = ev.get(“name”, str(ev_id))
ev_date  = parse_event_date(ev)
date_str = ev_date.date().isoformat() if ev_date else “–”

```
pct = int((i / total) * 100)
progress_bar.progress(pct, text="Scanning: %s (%d/%d)" % (ev_name, i + 1, total))
status_text.caption("%s  |  %s" % (date_str, ev_name))

try:
    sessions = fetch_sessions(ev_id)
except Exception:
    continue

for sess in sessions:
    sess_id    = sess.get("id")
    sess_name  = sess.get("name", "") or ""
    sess_class = (
        sess.get("class") or sess.get("className") or
        sess.get("class_name") or sess.get("group") or ""
    )
    combined_sess = sess_name + " " + sess_class
    if class_filter and not name_matches(combined_sess, class_filter):
        continue

    try:
        results = fetch_results(sess_id)
    except Exception:
        continue

    for entry in results:
        driver   = get_field(entry, "driver", "driverName", "driver_name", "name") or "Unknown"
        best_raw = get_field(entry, "bestLap", "best_lap", "bestLapTime", "best_lap_time")
        best_sec = lap_to_seconds(best_raw)
        if best_sec is None:
            continue
        existing = driver_best.get(driver)
        if existing is None or best_sec < existing["_seconds"]:
            driver_best[driver] = {
                "Driver":   driver,
                "Best Lap": seconds_to_lap(best_sec),
                "_seconds": best_sec,
                "Event":    ev_name,
                "Session":  sess_name,
                "Date":     date_str,
            }
```

progress_bar.progress(100, text=“Done!”)
progress_bar.empty()
status_text.empty()

if not driver_best:
st.warning(
“Events were found but no lap data matched class ‘%s’. “
“Try a shorter fragment like ‘E30’, or leave blank for all classes.”
% class_filter
)
st.stop()

grid = sorted(driver_best.values(), key=lambda r: r[”_seconds”])

# summary pills

track_label = track_filter or “All Tracks”
class_label = class_filter or “All Classes”
date_label  = “%s to %s” % (date_from, date_to)

st.markdown(”””

<div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin:1rem 0;">
  <span class="pill pill-info">%s</span>
  <span class="pill pill-success">%s</span>
  <span class="pill pill-warn">%s</span>
  <span class="pill pill-info">%d drivers</span>
</div>
""" % (track_label, class_label, date_label, len(grid)), unsafe_allow_html=True)

# results table

rows_html = “”
for pos, row in enumerate(grid, 1):
rows_html += (
“<tr>”
“<td class='pos'>%d</td>”
“<td><strong>%s</strong></td>”
“<td class='laptime'>%s</td>”
“<td class='meta'>%s</td>”
“<td class='meta'>%s</td>”
“</tr>”
) % (pos, row[“Driver”], row[“Best Lap”], row[“Event”], row[“Date”])

st.markdown(”””

<table class="grid-table">
  <thead>
    <tr>
      <th>#</th><th>Driver</th><th>Best Lap</th>
      <th>Event</th><th>Date</th>
    </tr>
  </thead>
  <tbody>%s</tbody>
</table>
""" % rows_html, unsafe_allow_html=True)

st.markdown(”<br>”, unsafe_allow_html=True)

# CSV download

df = pd.DataFrame([
{
“Position”: pos,
“Driver”:   r[“Driver”],
“Best Lap”: r[“Best Lap”],
“Event”:    r[“Event”],
“Session”:  r[“Session”],
“Date”:     r[“Date”],
}
for pos, r in enumerate(grid, 1)
])

csv_bytes = df.to_csv(index=False).encode(“utf-8”)
fname = “grid_%s_%s.csv” % (
(track_filter or “all”).replace(” “, “*”),
(class_filter or “all”).replace(” “, “*”),
)

st.download_button(
label=“Download CSV (open in Excel)”,
data=csv_bytes,
file_name=fname,
mime=“text/csv”,
use_container_width=True,
)
st.caption(“You can also select all rows in the table and paste directly into Excel.”)