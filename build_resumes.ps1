# Build all resume PDFs and copy to outputs/ (Windows)
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $root 'outputs'
$cn = Join-Path $root 'LaTeX_Resume_CN'
$en = Join-Path $root 'LaTeX_Resume_EN'

$cnFiles = @(
  'resume-zh_CN', 'resume-zh_job', 'resume-zh_backend_ops', 'resume-zh_ai_eval',
  'resume-zh_jd_annichiman', 'resume-zh_jd_bilaiwu', 'resume-zh_jd_miaoda', 'resume-zh_jd_bytedance'
)
$enFiles = @('resume_job_en', 'resume_backend_ops', 'resume_ai_eval', 'resume_web3')

$cnMap = @{
  'resume-zh_CN.pdf' = 'resume-zh_CN.pdf'
  'resume-zh_job.pdf' = 'resume_job_cn.pdf'
  'resume-zh_backend_ops.pdf' = 'resume_backend_ops_cn.pdf'
  'resume-zh_ai_eval.pdf' = 'resume_ai_eval_cn.pdf'
  'resume-zh_jd_annichiman.pdf' = 'resume_jd_annichiman_cn.pdf'
  'resume-zh_jd_bilaiwu.pdf' = 'resume_jd_bilaiwu_cn.pdf'
  'resume-zh_jd_miaoda.pdf' = 'resume_jd_miaoda_cn.pdf'
  'resume-zh_jd_bytedance.pdf' = 'resume_jd_bytedance_cn.pdf'
}
$enMap = @{
  'resume_job_en.pdf' = 'resume_job_en.pdf'
  'resume_backend_ops.pdf' = 'resume_backend_ops.pdf'
  'resume_ai_eval.pdf' = 'resume_ai_eval.pdf'
  'resume_web3.pdf' = 'resume_web3.pdf'
}

$pageReport = @()
$xelatex = $null

function Find-Executable {
  param([string]$Name)

  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  $candidates = @()
  foreach ($base in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
    if ($base) {
      $candidates += Get-ChildItem -Path (Join-Path $base 'MiKTeX\miktex\bin') -Recurse -Filter "$Name.exe" -File -ErrorAction SilentlyContinue
    }
  }
  $candidates += Get-ChildItem -Path (Join-Path $HOME 'texlive') -Recurse -Filter "$Name.exe" -File -ErrorAction SilentlyContinue
  $candidates += Get-ChildItem -Path 'C:\texlive' -Recurse -Filter "$Name.exe" -File -ErrorAction SilentlyContinue

  $hit = $candidates | Sort-Object FullName -Descending | Select-Object -First 1
  if ($hit) { return $hit.FullName }
  return $null
}

function Test-Xelatex {
  $script:xelatex = Find-Executable 'xelatex'
  if (-not $script:xelatex) {
    Write-Error @"
xelatex not found on PATH or common MiKTeX/TeX Live locations.

Install MiKTeX: https://miktex.org/download
Then open a new PowerShell window and retry.

See docs/BUILD_WINDOWS.md
"@
  }

  $texBin = Split-Path -Parent $script:xelatex
  if (($env:PATH -split ';') -notcontains $texBin) {
    $env:PATH = "$texBin;$env:PATH"
  }
}

function Get-PageCountFromLog {
  param([string]$LogPath)
  if (-not (Test-Path $LogPath)) { return '?' }
  $line = Select-String -Path $LogPath -Pattern 'Output written on .+ \((\d+) pages?\)' | Select-Object -First 1
  if ($line -and $line.Matches.Groups.Count -ge 2) {
    return $line.Matches.Groups[1].Value
  }
  return '?'
}

function Build-TexDir {
  param([string]$Dir, [string[]]$Files)
  if (-not (Test-Path $Dir)) {
    throw "Directory not found: $Dir`nCopy resume_template/ to LaTeX_Resume_CN/ or LaTeX_Resume_EN/ first. See docs/BUILD_WINDOWS.md"
  }
  Push-Location $Dir
  try {
    foreach ($f in $Files) {
      Write-Host "xelatex $f.tex"
      & $script:xelatex -interaction=nonstopmode "$f.tex" | Out-Null
      if ($LASTEXITCODE -ne 0) { throw "xelatex failed: $f (see $Dir\$f.log)" }
      $pages = Get-PageCountFromLog (Join-Path $Dir "$f.log")
      $script:pageReport += "$f`: $pages page(s)"
    }
  } finally {
    Pop-Location
  }
}

Test-Xelatex
New-Item -ItemType Directory -Force -Path $out | Out-Null

Write-Host '=== Building Chinese resumes ==='
Build-TexDir $cn $cnFiles
Write-Host '=== Copying CN PDFs to outputs/ ==='
foreach ($pair in $cnMap.GetEnumerator()) {
  Copy-Item (Join-Path $cn $pair.Key) (Join-Path $out $pair.Value) -Force
  Write-Host "      -> outputs/$($pair.Value)"
}

Write-Host '=== Building English resumes ==='
Build-TexDir $en $enFiles
Write-Host '=== Copying EN PDFs to outputs/ ==='
foreach ($pair in $enMap.GetEnumerator()) {
  Copy-Item (Join-Path $en $pair.Key) (Join-Path $out $pair.Value) -Force
  Write-Host "      -> outputs/$($pair.Value)"
}

Write-Host '=== Cleaning up build artifacts ==='
foreach ($d in @($cn, $en)) {
  if (Test-Path $d) {
    foreach ($ext in @('aux', 'log', 'out', 'pdf')) {
      Get-ChildItem $d -Filter "*.$ext" -File -ErrorAction SilentlyContinue | Remove-Item -Force
    }
  }
}

Write-Host ''
Write-Host 'Done. PDFs in outputs/'
Write-Host ''
Write-Host 'Page counts:'
foreach ($line in $pageReport) {
  Write-Host "  - $line"
}
