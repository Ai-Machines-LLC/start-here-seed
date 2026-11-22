# bootstrap.ps1 (v0.3.0 draft) - creates the generic bot-system folder tree and empty control files.
# Why: one script makes the layout identical on every new system and never overwrites existing work.
# -Encoding: answer to FIRST_BOT_QUESTIONS Q6 ("UTF8" or "1252"); control files are written in it (H27).
param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$Companies,
      [string]$TimeZone = "UTC", [ValidateSet("UTF8","1252")][string]$Encoding = "UTF8")
$ErrorActionPreference = "Stop"
if (-not (Test-Path $Root)) { throw "Root '$Root' does not exist. Create it yourself, then rerun (H24: never recreate a missing target)." }
$enc = if ($Encoding -eq "1252") { [System.Text.Encoding]::GetEncoding(1252) } else { New-Object System.Text.UTF8Encoding($false) }
function New-Dir($p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null; "created  $p" } else { "exists   $p" } }
function New-File($p, $body) { if (-not (Test-Path $p)) { [System.IO.File]::WriteAllText($p, $body + "`r`n", $enc); "created  $p" } else { "exists   $p (left as is)" } }
$bots = Join-Path $Root "Bots"
New-Dir $bots
"00 archive","01 How-Tos","02 Libraries","03 tools","04 Scripts","05 Logs","06 Lessons" | ForEach-Object { New-Dir (Join-Path $bots $_) }
New-File (Join-Path $bots "01 How-Tos\INDEX.txt") "HOW-TOS INDEX (one line per how-to: file | what it covers | owner)"
New-File (Join-Path $bots "DECISIONS.txt") "DECISIONS (newest first). date time $TimeZone | Designer's exact words | what it decides"
New-File (Join-Path $bots "OWNERS.txt") "OWNERS. route | owner bot | reviewer bot | leader"
New-File (Join-Path $bots "_BOT_IDS.txt") "_BOT_IDS. bot name (<CODE>-<Project>-<Role>, bootstrap/NAMING.txt) | bot id | counter name | company"
New-File (Join-Path $bots "MOVE_LOCK.txt") "MOVE_LOCK. date time | bot | HELD or RELEASED | path | reason"
New-File (Join-Path $bots "CORRECTIONS_LOG.csv") "date,bot,mistake,cause,fix,check_added"
New-File (Join-Path $bots "CHANGE_LOG.csv") "date,bot,path,revision,sha256,what,reviewer"
New-File (Join-Path $bots "05 Logs\EVENTS.csv") "time,bot,event,detail"
New-File (Join-Path $bots "05 Logs\METRICS.txt") "METRICS (one line per bot, written by bot_metrics; empty until it exists)"
foreach ($s in "log_event.ps1","toggle.ps1") {
  $src = Join-Path $PSScriptRoot $s; $dst = Join-Path $bots "04 Scripts\$s"
  if (-not (Test-Path $dst)) { Copy-Item $src $dst; "created  $dst" } else { "exists   $dst (left as is)" } }
if ((Get-Command git -ErrorAction SilentlyContinue) -and -not (Test-Path (Join-Path $bots "03 tools\.git"))) { git -C (Join-Path $bots "03 tools") init | Out-Null; "git init 03 tools" }
$i = 10
foreach ($c in ($Companies -split ",")) {
  $name = $c.Trim(); if (-not $name) { continue }
  $cdir = Join-Path $Root ("{0:D2} {1}" -f $i, $name); $i += 10
  New-Dir $cdir; New-Dir (Join-Path $cdir "00 archive"); New-Dir (Join-Path $cdir "01 Projects")
}
