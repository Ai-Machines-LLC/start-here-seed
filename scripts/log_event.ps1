# log_event.ps1 (v0.3.0 draft) - appends one work event to Bots\05 Logs\EVENTS.csv (H30).
# Why: metrics come from a log, never from a bot's memory. Events: task_start, task_done, handoff_sent,
# handoff_received, report, waiting. Usage: log_event.ps1 -Bot "<name>" -Event task_done -Detail "<path rev>"
param([Parameter(Mandatory)][string]$Bot,
      [Parameter(Mandatory)][ValidateSet("task_start","task_done","handoff_sent","handoff_received","report","waiting")][string]$Event,
      [string]$Detail = "")
$log = Join-Path $PSScriptRoot "..\05 Logs\EVENTS.csv"
if (-not (Test-Path $log)) { "EVENTS.csv missing at $log (H24: not recreated; run bootstrap.ps1)"; exit 1 }
$q = { param($v) '"' + ($v -replace '"','""') + '"' }
Add-Content -Path $log -Value ("{0},{1},{2},{3}" -f (Get-Date -Format "yyyy-MM-dd HH:mm"), (& $q $Bot), $Event, (& $q $Detail))
"logged $Event for $Bot"
