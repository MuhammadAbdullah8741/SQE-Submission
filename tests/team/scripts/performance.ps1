$ErrorActionPreference='Stop'
Set-Location (Resolve-Path "$PSScriptRoot/../../..")
$root=(Get-Location).Path
$results=@()
foreach($users in @(1,5)) {
 foreach($repeat in @(1,2)) {
  node tests/team/scripts/seed.cjs
  if($LASTEXITCODE -ne 0){throw 'Seed failed'}
  docker run --rm -e "VUS=$users" -v "${root}:/work" grafana/k6:latest run --summary-export "/work/tests/team/evidence/k6-$users-$repeat.json" /work/tests/team/performance/workload.js *> "tests/team/evidence/k6-$users-$repeat.log"
  $results += @{vus=$users;run=$repeat;exitCode=$LASTEXITCODE}
 }
}
$results | ConvertTo-Json | Set-Content tests/team/evidence/k6-run-status.json
