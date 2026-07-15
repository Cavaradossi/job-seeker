# Sync docs/skill/job-seeker/ -> .codex/skills/, .cursor/skills/, and .workbuddy/skills/
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Src  = Join-Path $Root 'docs\skill\job-seeker'
$Codex = Join-Path $Root '.codex\skills\job-seeker'
$Cur  = Join-Path $Root '.cursor\skills\job-seeker'
$Wb   = Join-Path $Root '.workbuddy\skills\job-seeker'
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false

if (-not (Test-Path (Join-Path $Src 'SKILL.md'))) {
  throw "Missing $Src\SKILL.md"
}

foreach ($dir in @($Codex, $Cur, $Wb)) {
  New-Item -ItemType Directory -Force -Path (Join-Path $dir 'references') | Out-Null
}
New-Item -ItemType Directory -Force -Path (Join-Path $Codex 'agents') | Out-Null

foreach ($f in @('SKILL.md', 'SKILL.zh-CN.md', 'checklist.md')) {
  $from = Join-Path $Src $f
  if (Test-Path $from) {
    Copy-Item $from (Join-Path $Codex $f) -Force
    Copy-Item $from (Join-Path $Cur $f) -Force
    Copy-Item $from (Join-Path $Wb $f) -Force
  }
}

$codexSkillPath = Join-Path $Codex 'SKILL.md'
$codexSkill = Get-Content $codexSkillPath -Raw -Encoding UTF8
$codexSkill = $codexSkill -replace '(?m)^(version|tags):.*\r?\n', ''
[System.IO.File]::WriteAllText($codexSkillPath, $codexSkill, $Utf8NoBom)

Copy-Item (Join-Path $Src 'references\*') (Join-Path $Codex 'references\') -Force
Copy-Item (Join-Path $Src 'references\*') (Join-Path $Cur 'references\') -Force
Copy-Item (Join-Path $Src 'references\*') (Join-Path $Wb 'references\') -Force
Copy-Item (Join-Path $Src 'agents\openai.yaml') (Join-Path $Codex 'agents\openai.yaml') -Force

$skillPath = Join-Path $Wb 'SKILL.md'
$lines = [System.Collections.Generic.List[string]](Get-Content $skillPath -Encoding UTF8)
if (-not ($lines -match '^agent_created:')) {
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -eq '---') {
      $lines.Insert($i, 'agent_created: true')
      break
    }
  }
  [System.IO.File]::WriteAllText($skillPath, ($lines -join "`r`n") + "`r`n", $Utf8NoBom)
}

Write-Host "Synced: $Src -> $Codex, $Cur, $Wb"
