@echo off
echo MPC Docker Quick Cleanup

echo Stopping and removing mpc-server container...
docker stop mpc-server 2>nul
docker rm -f mpc-server 2>nul

echo Stopping and removing visio-service container...
docker stop visio-service 2>nul
docker rm -f visio-service 2>nul

echo Cleanup complete.
echo You can now run start-mpc-servers.bat
echo. 