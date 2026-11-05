#!/usr/bin/env bash
# Start the detector:  bash run_mac_linux.sh   then open http://127.0.0.1:8000
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "Installing packages (first run only takes a minute)..."
python -m pip install -q -r requirements.txt
if [ ! -f models/url.joblib ]; then
  echo "No trained models found - downloading data and training (about 3 minutes)..."
  bash scripts/get_data.sh
  (cd src && python -m phishdetect.train)
fi
echo
echo "Detector running at http://127.0.0.1:8000  (press Ctrl+C to stop)"
( sleep 2; (open http://127.0.0.1:8000 || xdg-open http://127.0.0.1:8000) >/dev/null 2>&1 ) &
python -m uvicorn phishdetect.api:app --app-dir src --port 8000
