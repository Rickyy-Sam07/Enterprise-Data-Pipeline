@echo off
echo Starting Sales Analytics Dashboard...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Streamlit dashboard
cd dashboard
streamlit run app.py
cd ..

pause