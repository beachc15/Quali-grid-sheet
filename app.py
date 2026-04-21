# app.py - NASA Grid Lap Times
# Streamlit web app using MyLaps Event Results API directly.
# Deploy free at: https://streamlit.io/cloud

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone, date

st.set_page_config(
    page_title='NASA Grid Laps',
    page_icon=':checkered_flag:',
    layout='centered',
)

st.markdown('''
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
  .pill {
    display: inline-block; padding: 0.2rem 0.7rem;
    border-radius: 20px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em;
  }
  .pill-success { background: #1c4532; color: #68d391; }
  .pill-warn    { background: #744210; color: #f6ad55; }
  .pill-info    { background: #1a365d; color: #63b3ed; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-top: 1rem; }
  .grid-table thead tr { background: #e94560; color: white; }
  .grid-table thead th {
    font-family: 'Barlow Condensed', sans-serif; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 0.6rem 0.75rem; text-align: left;
  }
  .grid-table tbody tr:nth-child(even) { background: #1a1f2e; }
  .grid-table tbody tr:nth-child(odd)  { background: #151929; }
  .grid-table tbody tr:hover           { background: #0f3460; }
  .grid-table td { padding: 0.55rem 0.75rem; border-bottom: 1px solid #2d3748; color: #e8e8e8; }
  .grid-table td.pos { color: #a0aec0; font-size: 0.82rem; width: 2rem; }
  .grid-table td.laptime { font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; color: #68d391; font-weight: 600; }
  .grid-table tbody tr:first-child td.laptime { color: #f6e05e; }
  .grid-table td.meta { color: #a0aec0; font-size: 0.8rem; }
  div[data-testid="stButton"] > button {
    background: #e94560 !important; color: white !important; border: none !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.1rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 0.7rem 2rem !important; border-radius: 4px !important; width: 100% !important;
  }
  div[data-testid="stDownloadButton"] > button {
    background: #2d3748 !important; color: #e8e8e8 !important;
    border: 1px solid #4a5568 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 600 !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important; width: 100% !important;
  }
  div[data-testid="stSelectbox"] label,
  div[data-testid="stDateInput"] label,
  div[data-testid="stTextInput"] label,
  div[data-testid="stNumberInput"] label,
  div[data-testid="stRadio"] label,
  div[data-testid="stCheckbox"] label {
    color: #a0aec0 !important; font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
  }
  div[data-testid="stExpander"] { background: #1a1f2e !important; border: 1px solid #2d3748 !important; border-radius: 6px !important; }
  footer { visibility: hidden; }
</style>
''', unsafe_allow_html=True)

st.markdown('''
<div class="page-header">
  <h1>NASA <span class="accent">Grid</span> Laps</h1>
  <p>Fastest lap per driver -- sorted for race day grid lineup</p>
</div>
''', unsafe_allow_html=True)


# ---------- API ---------------------------------------------------------------

BASE = 'https://eventresults-api.speedhive.com'
HEADERS = {'Origin': 'https://sporthive.com', 'Accept': 'application/json'}


def api_get(path, params=None):
    r = requests.get(BASE + path, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_events(org_id):
    events = []
    offset = 0
    page_size = 100
    while True:
        batch = api_get(
            '/organizations/%d/events' % org_id,
            params={'count': page_size, 'offset': offset}
        )
        if not isinstance(batch, list):
            batch = batch.get('events') or batch.get('content') or batch.get('data') or []
        if not batch:
            break
        events.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return events


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_sessions(event_id):
    try:
        data = api_get('/events/%d/sessions' % event_id)
        if isinstance(data, list):
            return data
        sessions = list(data.get('sessions') or [])
        def flatten(groups):
            for g in (groups or []):
                sessions.extend(g.get('sessions') or [])
                flatten(g.get('subGroups') or [])
        flatten(data.get('groups') or [])
        return sessions
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_classification(session_id):
    try:
        data = api_get('/sessions/%d/classification' % session_id)
        if isinstance(data, list):
            return data
        return data.get('rows') or []
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_lapdata(session_id):
    # Paginate through all participants; each page = one participant.
    # Returns list of (driver_name, class_name, best_lap_seconds).
    results = []
    offset = 0
    page_size = 500
    seen = set()
    while True:
        try:
            data = api_get(
                '/sessions/%d/lapdata' % session_id,
                params={'count': page_size, 'offset': offset}
            )
        except Exception:
            break
        if not data:
            break
        info    = data.get('lapDataInfo') or {}
        p_info  = info.get('participantInfo') or {}
        driver  = (p_info.get('name') or '').strip() or 'Unknown'
        p_class = (p_info.get('class') or '').strip()
        laps    = data.get('laps') or []
        if driver in seen:
            break
        if driver != 'Unknown':
            seen.add(driver)
        best = None
        for lap in laps:
            lt = lap.get('lapTime')
            if lt is None:
                continue
            if isinstance(lt, str):
                t = parse_time_str(lt)
            else:
                raw = float(lt)
                t = raw / 1000.0 if raw > 10000 else raw
            if t and 30.0 <= t <= 900.0:
                if best is None or t < best:
                    best = t
        if driver != 'Unknown' and best is not None:
            results.append((driver, p_class, best))
        if not laps:
            break
        offset += page_size
        if offset > 300 * page_size:
            break
    return results



# ---------- helpers -----------------------------------------------------------

# Best lap for a car race at a road course is typically between 45s and 9min.
LAP_MIN_SECONDS = 45.0
LAP_MAX_SECONDS = 540.0  # 9 minutes


def parse_time_str(value):
    '''Parse a time string like M:SS.mmm or H:MM:SS.mmm to seconds. Returns None on failure.'''
    if value is None:
        return None
    s = str(value).strip()
    if not s or s in ('-', 'DNS', 'DNF', 'DQ', 'N/A', ''):
        return None
    try:
        if ':' in s:
            parts = s.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        v = float(s)
        # Raw milliseconds
        if v > 600000:
            return v / 1000.0
        if v > 10000:
            return v / 1000.0
        return v
    except (ValueError, IndexError):
        return None


def best_lap_from_fields(fields, min_sec=30.0, max_sec=900.0):
    '''
    From additionalFields[], find the value that looks most like a single lap time.
    Strategy: pick the SMALLEST time that falls within the plausible lap time range.
    This ignores total race time (too large) and gap/diff values (too small).
    '''
    best = None
    for f in (fields or []):
        t = parse_time_str(f)
        if t is None:
            continue
        if t < min_sec or t > max_sec:
            continue
        if best is None or t < best:
            best = t
    return best


def seconds_to_lap(secs):
    m = int(secs // 60)
    s = secs % 60
    return '%d:%06.3f' % (m, s)


def event_track_name(ev):
    loc = ev.get('location')
    if isinstance(loc, dict):
        return loc.get('name') or ''
    return str(loc) if loc else ''


def event_datetime(ev):
    for key in ('startDate', 'start_date', 'date', 'eventDate'):
        val = ev.get(key)
        if val:
            try:
                dt = datetime.fromisoformat(str(val).replace('Z', '+00:00'))
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def name_matches(text, query):
    return query.strip().lower() in (text or '').lower()


# ---------- advanced settings -------------------------------------------------

with st.expander('Advanced: Organisation Settings', expanded=False):
    org_id = st.number_input(
        'Speedhive Org ID', min_value=1, value=41593, step=1,
        help='Find your org ID in the Speedhive URL: speedhive.mylaps.com/organizations/XXXXX',
    )
    st.caption('Default 41593 = NASA Mid-Atlantic')
    debug_mode = st.checkbox('Debug mode (show raw API data for first matching session)')

# ---------- filters -----------------------------------------------------------

st.markdown('#### Filters')

col_a, col_b = st.columns(2)
with col_a:
    date_from = st.date_input('From', value=date.today() - timedelta(days=365))
with col_b:
    date_to = st.date_input('To', value=date.today())

track_input_mode = st.radio('Track selection', ['Choose from list', 'Type manually'], horizontal=True)

track_filter = ''
if track_input_mode == 'Choose from list':
    with st.spinner('Loading tracks...'):
        try:
            all_ev = fetch_all_events(org_id)
            from_dt_list = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
            track_names = set()
            for ev in all_ev:
                ev_dt = event_datetime(ev)
                if ev_dt and ev_dt < from_dt_list:
                    continue
                t = event_track_name(ev)
                if t:
                    track_names.add(t)
            track_list = sorted(track_names)
            if track_list:
                choice = st.selectbox('Track', ['(all tracks)'] + track_list)
                track_filter = '' if choice == '(all tracks)' else choice
            else:
                st.warning('No tracks found -- try "Type manually" or check the Org ID.')
                track_filter = st.text_input('Track name fragment', placeholder='e.g. Carolina')
        except Exception as e:
            st.error('Could not load tracks: %s' % e)
            track_filter = st.text_input('Track name fragment', placeholder='e.g. Carolina')
else:
    track_filter = st.text_input('Track name fragment', placeholder='e.g. Carolina')

class_filter = st.text_input(
    'Class / session filter', value='Spec E30',
    placeholder='e.g. Spec E30, TTD, TTA',
    help='Leave blank to show all classes.',
)

run_btn = st.button('FETCH GRID', use_container_width=True)
if not run_btn:
    st.stop()

# ---------- fetch + filter events --------------------------------------------

from_dt = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
to_dt   = datetime.combine(date_to,   datetime.max.time()).replace(tzinfo=timezone.utc)

prog   = st.progress(0, text='Loading events...')
status = st.empty()

try:
    all_events = fetch_all_events(org_id)
except Exception as e:
    prog.empty()
    st.error('Could not connect to Speedhive API: %s' % e)
    st.stop()

matching = []
for ev in all_events:
    track   = event_track_name(ev)
    ev_name = ev.get('name', '') or ''
    if track_filter and not name_matches(track, track_filter) and not name_matches(ev_name, track_filter):
        continue
    ev_dt = event_datetime(ev)
    if ev_dt and (ev_dt < from_dt or ev_dt > to_dt):
        continue
    matching.append(ev)

if not matching:
    prog.empty()
    st.warning('No events found for "%s" in the selected date range.' % (track_filter or 'all tracks'))
    st.stop()

# ---------- scan sessions + classification ------------------------------------

driver_best  = {}
debug_shown  = False
total        = len(matching)

for i, ev in enumerate(matching):
    ev_id    = ev.get('id')
    ev_name  = ev.get('name', str(ev_id)) or str(ev_id)
    ev_dt    = event_datetime(ev)
    date_str = ev_dt.date().isoformat() if ev_dt else '--'
    track    = event_track_name(ev) or ev_name

    prog.progress(int(i / total * 100), text='Scanning %d/%d: %s' % (i + 1, total, ev_name))
    status.caption('%s  |  %s' % (date_str, ev_name))

    for sess in fetch_sessions(ev_id):
        sess_id    = sess.get('id') or sess.get('sessionId')
        sess_name  = sess.get('name', '') or ''
        sess_group = sess.get('groupName', '') or ''

        # Only process sessions where the session name OR group name starts with 'lightning race'
        # Group name holds 'Lightning Race 1 $$$'; session name may hold the class e.g. 'Spec E30'
        sess_n = sess_name.strip().lower()
        sess_g = sess_group.strip().lower()
        is_lightning_race = sess_n.startswith('lightning race') or sess_g.startswith('lightning race')
        if not debug_mode and not is_lightning_race:
            continue

        # ---- debug: show raw API response for first session ---------------
        if debug_mode and not debug_shown:
            debug_shown = True
            prog.empty()
            status.empty()
            st.warning('DEBUG MODE -- Session: **%s** | Group: **%s**' % (sess_name, sess_group))
            st.markdown('**sess_name repr:** `%s`' % repr(sess_name))
            st.markdown('**sess_group repr:** `%s`' % repr(sess_group))
            st.markdown('**is_lightning_race:** `%s`' % is_lightning_race)
            # Show raw lapdata API response
            try:
                raw = api_get('/sessions/%d/lapdata' % sess_id, params={'count': 10, 'offset': 0})
                st.markdown('**Raw /lapdata response type:** `%s`' % type(raw).__name__)
                if isinstance(raw, dict):
                    st.markdown('**Top-level keys:** `%s`' % list(raw.keys()))
                    lap_data_info = raw.get('lapDataInfo') or {}
                    st.markdown('**lapDataInfo:** `%s`' % lap_data_info)
                    laps = raw.get('laps') or []
                    st.markdown('**laps count:** `%d`' % len(laps))
                    if laps:
                        st.markdown('**First lap keys:** `%s`' % list(laps[0].keys()))
                        st.markdown('**First lap:** `%s`' % laps[0])
                elif isinstance(raw, list):
                    st.markdown('**List length:** `%d`' % len(raw))
                    if raw:
                        st.markdown('**First item keys:** `%s`' % list(raw[0].keys()) if isinstance(raw[0], dict) else str(raw[0]))
                else:
                    st.markdown('**Raw value:** `%s`' % str(raw))
            except Exception as ex:
                st.error('lapdata API call failed: %s' % ex)
            st.info('Turn off Debug mode once you understand the structure.')
            st.stop()
        # ------------------------------------------------------------------

        # Use lapdata endpoint -- additionalFields has car metadata, not lap times
        for (driver, lap_class, best_sec) in fetch_lapdata(sess_id):
            if class_filter:
                if not name_matches(lap_class, class_filter) and \
                   not name_matches(sess_name + ' ' + sess_group, class_filter):
                    continue
            existing = driver_best.get(driver)
            if existing is None or best_sec < existing['_sec']:
                driver_best[driver] = {
                    'Driver':   driver,
                    'Class':    lap_class,
                    'Best Lap': seconds_to_lap(best_sec),
                    '_sec':     best_sec,
                    'Event':    ev_name,
                    'Track':    track,
                    'Session':  sess_name,
                    'Date':     date_str,
                }

prog.progress(100, text='Done!')
prog.empty()
status.empty()

if not driver_best:
    st.warning(
        'No lap data found matching your filters.\n\n'
        'Tips:\n'
        '- Enable Debug mode in Advanced Settings to see what class names and fields the API actually returns.\n'
        '- Try leaving the class filter blank to see ALL results first.'
    )
    st.stop()

# ---------- render results ----------------------------------------------------

grid = sorted(driver_best.values(), key=lambda r: r['_sec'])

track_label = track_filter or 'All Tracks'
class_label = class_filter or 'All Classes'
date_label  = '%s to %s' % (date_from, date_to)

st.markdown('''
<div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin:1rem 0;">
  <span class="pill pill-info">%s</span>
  <span class="pill pill-success">%s</span>
  <span class="pill pill-warn">%s</span>
  <span class="pill pill-info">%d drivers</span>
</div>
''' % (track_label, class_label, date_label, len(grid)), unsafe_allow_html=True)

rows_html = ''
for pos, row in enumerate(grid, 1):
    rows_html += (
        '<tr>'
        '<td class="pos">%d</td>'
        '<td><strong>%s</strong></td>'
        '<td class="laptime">%s</td>'
        '<td class="meta">%s</td>'
        '<td class="meta">%s</td>'
        '</tr>'
    ) % (pos, row['Driver'], row['Best Lap'], row['Event'], row['Date'])

st.markdown('''
<table class="grid-table">
  <thead><tr><th>#</th><th>Driver</th><th>Best Lap</th><th>Event</th><th>Date</th></tr></thead>
  <tbody>%s</tbody>
</table>
''' % rows_html, unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

df = pd.DataFrame([
    {'Position': pos, 'Driver': r['Driver'], 'Class': r['Class'],
     'Best Lap': r['Best Lap'], 'Event': r['Event'], 'Track': r['Track'],
     'Session': r['Session'], 'Date': r['Date']}
    for pos, r in enumerate(grid, 1)
])

fname = 'grid_%s_%s.csv' % (
    (track_filter or 'all').replace(' ', '_'),
    (class_filter or 'all').replace(' ', '_'),
)
st.download_button(
    label='Download CSV (open in Excel)',
    data=df.to_csv(index=False).encode('utf-8'),
    file_name=fname,
    mime='text/csv',
    use_container_width=True,
)
st.caption('You can also select all rows in the table and paste directly into Excel.')