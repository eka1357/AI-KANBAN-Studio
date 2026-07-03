# Scripts

Start and stop scripts for all platforms. All scripts must be run from the project root directory.

## start.ps1 / start.sh

Runs `docker compose up --build -d` and prints the local URL.

## stop.ps1 / stop.sh

Runs `docker compose down`.

## Usage

Windows (PowerShell):
  .\scripts\start.ps1
  .\scripts\stop.ps1

Mac/Linux:
  chmod +x scripts/start.sh scripts/stop.sh
  ./scripts/start.sh
  ./scripts/stop.sh