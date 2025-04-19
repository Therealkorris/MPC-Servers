@echo off
echo Testing Docker Container Connections...
echo.

echo Testing MPC Server connectivity...
curl -v http://localhost:8050/health

echo.
echo Testing Visio Service connectivity...
curl -v http://localhost:8051/health

echo.
echo If both tests returned "healthy" status, the setup is working correctly.
echo If not, check Docker logs with: docker logs mpc-server
echo. 