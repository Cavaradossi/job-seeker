# Build all resume PDFs and copy to outputs/
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $root 'outputs'
$cn = Join-Path $root 'LaTeX_Resume_CN'
$en = Join-Path $root 'LaTeX_Resume_EN'

function Build-TexDir {
    param([string]$Dir, [string[]]$Files)
    Push-Location $Dir
    try {
        foreach ($f in $Files) {
            Write-Host "xelatex $f.tex"
            xelatex -interaction=nonstopmode "$f.tex" | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "xelatex failed: $f" }
        }
    } finally {
        Pop-Location
    }
}

Build-TexDir $cn @('resume-zh_CN', 'resume-zh_job', 'resume-zh_backend_ops', 'resume-zh_ai_eval', 'resume-zh_jd_annichiman', 'resume-zh_jd_bilaiwu', 'resume-zh_jd_miaoda', 'resume-zh_jd_bytedance')
Copy-Item (Join-Path $cn 'resume-zh_CN.pdf') (Join-Path $out 'resume-zh_CN.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_job.pdf') (Join-Path $out 'resume_job_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_backend_ops.pdf') (Join-Path $out 'resume_backend_ops_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_ai_eval.pdf') (Join-Path $out 'resume_ai_eval_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_jd_annichiman.pdf') (Join-Path $out 'resume_jd_annichiman_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_jd_bilaiwu.pdf') (Join-Path $out 'resume_jd_bilaiwu_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_jd_miaoda.pdf') (Join-Path $out 'resume_jd_miaoda_cn.pdf') -Force
Copy-Item (Join-Path $cn 'resume-zh_jd_bytedance.pdf') (Join-Path $out 'resume_jd_bytedance_cn.pdf') -Force

Build-TexDir $en @('resume_job_en', 'resume_backend_ops', 'resume_ai_eval', 'resume_web3')
Copy-Item (Join-Path $en 'resume_job_en.pdf') (Join-Path $out 'resume_job_en.pdf') -Force
Copy-Item (Join-Path $en 'resume_backend_ops.pdf') (Join-Path $out 'resume_backend_ops.pdf') -Force
Copy-Item (Join-Path $en 'resume_ai_eval.pdf') (Join-Path $out 'resume_ai_eval.pdf') -Force
Copy-Item (Join-Path $en 'resume_web3.pdf') (Join-Path $out 'resume_web3.pdf') -Force

# Remove build artifacts from template dirs (PDFs already copied to outputs/)
foreach ($d in @($cn, $en)) {
    foreach ($ext in @('aux','log','out','pdf')) {
        Get-ChildItem $d -Filter "*.$ext" -File -ErrorAction SilentlyContinue | Remove-Item -Force
    }
}

Write-Host 'Done. PDFs in outputs/'
