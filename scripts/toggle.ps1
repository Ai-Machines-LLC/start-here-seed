# toggle.ps1 (v0.4.0 draft) - turns a leader or a recurring cycle ON/OFF, or checks it (H30, L-17, L-18).
# Why: a pause must be a file anyone can read, never a deleted scheduled job. A missing entry counts as ON.
# Usage: toggle.ps1 -Kind Leader|Cycle -Name "<leader or group/cycle>" [-Set ON|OFF] [-Check]
#        -RolesFolder defaults to $env:SEED_ROLES_FOLDER (set by MANIFEST step 5), the folder holding LEADER_STATUS.txt / CYCLE_STATUS.txt.
# Why exit 0 when unknown: H30 calls -Check with no folder; an unknown folder must never block work, same as a missing file.
param([Parameter(Mandatory)][ValidateSet("Leader","Cycle")][string]$Kind, [Parameter(Mandatory)][string]$Name,
      [ValidateSet("ON","OFF")][string]$Set, [switch]$Check, [string]$RolesFolder = $env:SEED_ROLES_FOLDER)
if (-not $RolesFolder) { "RolesFolder unknown; treating $Name as ON"; exit 0 }
$file = Join-Path $RolesFolder ($(if ($Kind -eq "Leader") { "LEADER_STATUS.txt" } else { "CYCLE_STATUS.txt" }))
if (-not (Test-Path $file)) { "$file missing (H24: not recreated); treating $Name as ON"; exit 0 }
$lines = @(Get-Content $file | Where-Object { $_ -ne "" })
$hit = $lines | Where-Object { ($_ -split '\|')[0].Trim() -eq $Name } | Select-Object -Last 1
$state = if ($hit) { ($hit -split '\|')[1].Trim() } else { "ON" }
if ($Set) {
  $kept = @($lines | Where-Object { ($_ -split '\|')[0].Trim() -ne $Name }) + ("{0} | {1} | {2}" -f $Name, $Set, (Get-Date -Format "yyyy-MM-dd HH:mm"))
  Set-Content -Path $file -Value $kept; "$Kind $Name set $Set (was $state)"; exit 0 }
"$Kind $Name is $state"; if ($Check -and $state -eq "OFF") { exit 3 }
