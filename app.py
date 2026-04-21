# app.py - NASA Grid Lap Times

# Streamlit web app: select track, class, and date range
# Deploy free at: https://streamlit.io/cloud

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone, date

st.set_page_config(
    page_title='NASA Grid Laps',
    page_icon=':checkered_flag:',
    layout='centered',
)

st.markdown("""
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
  div[data-testid="stDownloadButton"]
