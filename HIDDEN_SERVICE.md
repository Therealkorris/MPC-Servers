# Running the Visio Service Without a Visible Window

There are two ways to run the Visio service so that it doesn't show a visible command window on your desktop:

## Option 1: Using pythonw.exe (Simple)

The updated `start-mpc-servers.bat` file now uses `pythonw.exe` instead of `python.exe` to run the Visio service. This runs the Python interpreter without a console window.

**To use this option:**
1. Simply run `start-mpc-servers.bat` as usual
2. No command window will appear for the Visio service
3. To stop everything, run `stop-mpc-servers.bat`

This is the simplest option and works well for most users.

## Option 2: Installing as a Windows Service (Advanced)

For a more permanent solution, you can install the Visio service as a Windows service that starts automatically when Windows boots.

**To install as a service:**
1. Run `install_service.bat` (requires administrator privileges)
2. The service will be installed but not started
3. To start the service: `python install_as_service.py start`
4. To stop the service: `python install_as_service.py stop`
5. To remove the service: `python install_as_service.py remove`

**Benefits of running as a service:**
- Starts automatically when Windows starts
- Runs in the background with no visible window
- Can be managed through Windows Services management console
- Automatically restarts if it crashes

**Note:** The Windows service option requires the `pywin32` package, which will be installed automatically by the install script if needed.

## Troubleshooting

If you encounter issues with either approach:

1. Check the log files:
   - For the pythonw approach: Look for `visio_service.log` in the project directory
   - For the Windows service: Look for entries in the Windows Event Log

2. If Visio operations aren't working:
   - Make sure Visio is installed and working on your system
   - Try running `python run_visio_service.py` directly to see any error messages

3. If port 8052 is already in use:
   - Edit `run_visio_service.py` to use a different port
   - Update `docker-compose.yml` to point to the new port 