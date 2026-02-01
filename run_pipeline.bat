@echo off
echo Running Enterprise Data Pipeline...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the pipeline
cd src
python pipeline.py
cd ..

echo.
echo Pipeline execution completed!
echo Check logs\ directory for detailed logs
echo.
pause