# Variant Playbook — 申职器 Reference

> Sanitized copy of `outputs/resume_variant_playbook.md`. Personal identifiers replaced with placeholders. For the full version with real openers, see the original.

---

## Source file locations

| Use | Source `.tex` | Compile dir | Output PDF |
|-----|---------------|-------------|------------|
| CN full | `LaTeX_Resume_CN/resume-zh_CN.tex` | `LaTeX_Resume_CN/` | `resume-zh_CN.pdf` |
| CN general (1 page) | `LaTeX_Resume_CN/resume-zh_job.tex` | same | `resume_job_cn.pdf` |
| CN backend/ops | `LaTeX_Resume_CN/resume-zh_backend_ops.tex` | same | `resume_backend_ops_cn.pdf` |
| CN AI/RAG | `LaTeX_Resume_CN/resume-zh_ai_eval.tex` | same | `resume_ai_eval_cn.pdf` |
| EN general | `LaTeX_Resume_EN/resume_job_en.tex` | `LaTeX_Resume_EN/` | `resume_job_en.pdf` |
| EN backend/ops | `LaTeX_Resume_EN/resume_backend_ops.tex` | same | `resume_backend_ops.pdf` |
| EN AI/RAG | `LaTeX_Resume_EN/resume_ai_eval.tex` | same | `resume_ai_eval.pdf` |
| Web3 anonymous | `LaTeX_Resume_EN/resume_web3.tex` | same | `resume_web3.pdf` |

## Compile

```bash
./build_resumes.sh        # macOS / Linux
# .\build_resumes.ps1     # Windows
```

**Do not** place `.tex`, `resume.cls`, or fontawesome copies in `outputs/`.

## Document governance

| Directory | Use |
|-----------|-----|
| `docs/` | Technical docs (experience facts, system descriptions — reference before writing resumes) |
| `outputs/` | Deliverables: PDFs, job batches, tracker, this playbook |
| `history/` | Submitted-company and interview debriefs |
| `LaTeX_Resume_*` | Resume LaTeX sources and templates |

Flow: **check `docs/` → edit `LaTeX_*` → `./build_resumes.sh` → use `outputs/*.pdf` to apply.**

## Variant guidance

### 1. Web3 anonymous

- **Name**: `YOUR_PSEUDONYM` (use a consistent pseudonym for crypto/Web3 contexts)
- **Use for**: crypto, Web3, open-core, TG-intro roles
- **Main angle**: open-source research-workflow tooling, adapter-minded design, remote collaboration
- **Do not overstate**: deep Solidity, Rust, or chain-native engineering unless actually present

#### Opener (template)

> I build reproducible research workflow tooling and AI/data systems, and I recently open-sourced `YOUR_OPEN_SOURCE_PROJECT`, an open-core framework for reproducible research workflows.

#### DM template

> Hi, I am `YOUR_PSEUDONYM`. I have N years of production systems experience and recently open-sourced `YOUR_OPEN_SOURCE_PROJECT`. I am interested in your remote role and can work on backend, ops, workflow tooling, and AI/data tasks. Resume and GitHub attached.

### 2. Backend / ops

- **Name**: `YOUR_NAME` (real name for non-anonymous roles)
- **Use for**: backend, platform, SRE, ops, production support
- **Main angle**: production systems, RAG, ETL, stability, debugging

#### Opener (template)

> I am a backend and ops engineer with N years of production systems experience, plus RAG, API platform, and ETL work.

#### DM template

> Hi, I am `YOUR_NAME`. My background is in production systems, backend support, and workflow tooling. I have built RAG systems, secure APIs, and data pipelines, and I am interested in your remote backend/ops role. Resume and GitHub attached.

### 3. AI eval / benchmark

- **Name**: `YOUR_NAME`
- **Use for**: AI eval, benchmark, research tooling, applied LLM infra
- **Main angle**: measurable workflows, artifact-driven engineering, reproducibility

#### Opener (template)

> I build measurement-friendly workflow systems for data-heavy and AI-adjacent problems, with a focus on reproducibility and clear artifacts.

#### DM template

> Hi, I am `YOUR_NAME`. I work on reproducible workflow tooling, RAG systems, and data pipelines, and I am especially interested in AI evaluation and benchmark-oriented roles. Resume and GitHub attached.

---

## CN-specific guidance (for domestic applications)

- **Name**: `YOUR_NAME` (use the same real name consistently for domestic applications)
- **Do not**: use pseudonyms for domestic roles, claim market-specific features for your open-source project, treat small adapter projects as main projects
- **Do mention**: open-source research-workflow framework, AI-assisted dev workflow (Codex/Cursor/Trae)

### CN opener template

> 您好，我是 `YOUR_NAME`，`YOUR_INSTITUTION` 硕士，N 年金融生产系统经验（API、ETL、RAG 部署与运维）。维护开源研究工作流框架 `YOUR_OPEN_SOURCE_PROJECT`，日常用 Codex/Cursor/Trae 做重构、测试与 Code Review。附件为中文简历，GitHub：`YOUR_GITHUB_URL`

> Replace all placeholders with actual values when generating a real opener. Never write the maintainer's real identifiers into example/skill content.
