@echo off
cd /d "%~dp0"
echo Starting Email Tracker...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
) else (
    call venv\Scripts\activate
)
pip install -r requirements.txt
start http://localhost:5000
python app.py
pause
