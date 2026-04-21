# Deploying to Streamlit Community Cloud (Free)

Total time: ~10 minutes. No credit card. No server to manage.

-----

## What you need

- A free GitHub account → https://github.com
- A free Streamlit account → https://streamlit.io (sign in with GitHub)

-----

## Step 1 — Create a GitHub repository

1. Go to https://github.com/new
1. Name it something like `nasa-grid-laps`
1. Set it to **Public** (required for the free Streamlit tier)
1. Click **Create repository**

-----

## Step 2 — Upload the files

Upload these two files to your new repo (drag and drop on GitHub works):

```
app.py
requirements.txt
```

That’s it. No other files needed.

-----

## Step 3 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io
1. Click **New app**
1. Select your GitHub repo (`nasa-grid-laps`)
1. Set **Main file path** to `app.py`
1. Click **Deploy**

Streamlit will install your dependencies and spin up the app.
It takes about 2–3 minutes the first time.

-----

## Step 4 — Share the link

Once deployed, you get a permanent URL like:

```
https://your-username-nasa-grid-laps-app-xxxxxx.streamlit.app
```

Send that link to anyone. They open it in a browser — no install needed.

-----

## Updating the app later

Just edit `app.py` on GitHub (or push a new version).
Streamlit automatically redeploys within ~30 seconds.

-----

## Keeping it alive

Free Streamlit apps “sleep” after 7 days of no visits.
They wake back up the moment someone opens the link (takes ~30 seconds).
If you want it always-on, just visit it once a week, or upgrade to a paid plan.

-----

## Running locally (for testing)

```bash
pip install streamlit speedhive-tools pandas
streamlit run app.py
```

Opens at http://localhost:8501

-----

## Troubleshooting

**“Module not found: mylaps_client_wrapper”**
Make sure `speedhive-tools` is in `requirements.txt` (it is).
Redeploy if needed via the Streamlit Cloud dashboard.

**App loads but shows no tracks**
The Speedhive API may be slow on first load.
Results are cached for 1 hour after the first successful fetch.

**Track dropdown is empty**
Try switching to “Type manually” mode and entering a track fragment directly.
