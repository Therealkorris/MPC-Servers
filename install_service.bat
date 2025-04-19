@echo off
echo Installing Visio MPC Service...

REM Check if pywin32 is installed
pip show pywin32 > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing pywin32...
    pip install pywin32
)

REM Install the service
python install_as_service.py install

echo.
echo Service installed. You can now:
echo - Start the service: python install_as_service.py start
echo - Stop the service: python install_as_service.py stop
echo - Remove the service: python install_as_service.py remove
echo.
echo Note: The service will start automatically when Windows starts.
echo To use the service now, run: python install_as_service.py start
echo. 