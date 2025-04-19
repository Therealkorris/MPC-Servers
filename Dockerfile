# Use a Windows-based Python image
FROM mcr.microsoft.com/windows/servercore:ltsc2019
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Python
RUN Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe" -OutFile "python-3.12.1-amd64.exe" ; \
    Start-Process -FilePath "python-3.12.1-amd64.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait ; \
    Remove-Item -Path "python-3.12.1-amd64.exe"

# Copy application files
WORKDIR /app
COPY src /app/src
COPY examples /app/examples
COPY mpc-config.json /app/mpc-config.json
COPY run.py /app/run.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Note: The container won't have access to Visio unless the host system's Visio
# is explicitly shared with the container, which is complex in practice.
# This image is primarily for running the backend services that don't require
# direct Visio interaction.

# Set the entrypoint to run the MPC server
ENTRYPOINT ["python", "run.py"]
CMD ["--transport", "sse", "--host", "0.0.0.0", "--port", "8050"] 