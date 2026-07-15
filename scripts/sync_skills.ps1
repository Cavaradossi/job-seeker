# Sync docs/skill/job-seeker/ -> .cursor/skills/ and .workbuddy/skills/
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Src  = Join-Path $Root 'docs\skill\job-seeker'
$Cur  = Join-Path $Root '.cursor\skills\job-seeker'
$Wb   = Join-Path $Root '.workbuddy\skills\job-seeker'

if (-not (Test-Path (Join-Path $Src 'SKILL.md'))) {
  throw "Missing $Src\SKILL.md"
}

New-Item -ItemType Directory -Force -Path (Join-Path $Cur 'references') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Wb 'references') | Out-Null

foreach ($f in @('SKILL.md', 'SKILL.zh-CN.md', 'checklist.md')) {
  $from = Join-Path $Src $f
  if (Test-Path $from) {
    Copy-Item $from (Join-Path $Cur $f) -Force
    Copy-Item $from (Join-Path $Wb $f) -Force
  }
}

Copy-Item (Join-Path $Src 'references\*') (Join-Path $Cur 'references\') -Force
Copy-Item (Join-Path $Src 'references\*') (Join-Path $Wb 'references\') -Force

$skillPath = Join-Path $Wb 'SKILL.md'
$content = Get-Content $skillPath -Raw -Encoding UTF8
if ($content -notmatch 'agent_created:') {
  $content = $content -replace '(---\r?\n(?:.*?\r?\n)*?)(---\r?\n)', "`$1agent_created: true`r`n`$2"
  Set-Content -Path $skillPath -Value $content -Encoding UTF8 -NoNewline
}

Write-Host "Synced: $Src -> $Cur, $Wb"
