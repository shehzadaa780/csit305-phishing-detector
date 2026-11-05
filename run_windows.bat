@echo off
REM Double-click this file to start the detector, then open http://127.0.0.1:8000
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
if not exist .venv (
  echo Creating virtual environment...
  %PY% -m venv .venv || (echo Python 3.10+ is needed: install it from python.org and tick "Add to PATH". & pause & exit /b 1)
)
call .venv\Scripts\activate.bat
echo Installing packages (first run only takes a minute)...
python -m pip install -q -r requirements.txt || (echo Package install failed - check your internet connection. & pause & exit /b 1)
if not exist models\url.joblib (
  echo No trained models found - downloading data and training, about 3 minutes...
  bash scripts\get_data.sh || (echo Could not download data: install Git for Windows from git-scm.com. & pause & exit /b 1)
  pushd src & python -m phishdetect.train & popd
)
echo.
echo Detector running at http://127.0.0.1:8000  (close this window to stop it)
start "" http://127.0.0.1:8000
python -m uvicorn phishdetect.api:app --app-dir src --port 8000
pause
