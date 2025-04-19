"""
Script to install the Visio service as a Windows service.
"""
import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import subprocess

class VisioService(win32serviceutil.ServiceFramework):
    _svc_name_ = "VisioService"
    _svc_display_name_ = "Visio MPC Service"
    _svc_description_ = "Provides a service for MPC server to interact with Microsoft Visio"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = False
        self.process = None
        
        # Set up logging
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'visio_service.log')
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('VisioService')

    def SvcStop(self):
        self.logger.info('Stopping service')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
        # Kill the process
        if self.process:
            try:
                self.process.terminate()
                self.logger.info('Process terminated')
            except Exception as e:
                self.logger.error(f'Error terminating process: {e}')

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.logger.info('Starting service')
        self.is_running = True
        self.main()

    def main(self):
        # Path to the Visio service script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_visio_service.py')
        
        # Start the Visio service as a subprocess
        self.logger.info(f'Starting {script_path}')
        try:
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.logger.info(f'Started process with PID {self.process.pid}')
            
            # Wait for the stop event or process termination
            while self.is_running:
                # Check if the process is still running
                if self.process.poll() is not None:
                    self.logger.error(f'Process terminated unexpectedly with return code {self.process.returncode}')
                    stdout, stderr = self.process.communicate()
                    self.logger.error(f'stdout: {stdout.decode("utf-8", errors="ignore")}')
                    self.logger.error(f'stderr: {stderr.decode("utf-8", errors="ignore")}')
                    
                    # Restart the process
                    self.logger.info('Restarting process')
                    self.process = subprocess.Popen(
                        [sys.executable, script_path],
                        cwd=os.path.dirname(os.path.abspath(__file__)),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    self.logger.info(f'Restarted process with PID {self.process.pid}')
                
                # Wait for the stop event for 5 seconds
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop event received, exit the loop
                    break
                
            self.logger.info('Service stopped')
            
        except Exception as e:
            self.logger.error(f'Error running process: {e}')
            self.is_running = False

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VisioService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(VisioService) 