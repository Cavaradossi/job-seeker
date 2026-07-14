# Experience Bank (Example)

> Template for your bullet material library. Copy this file to `doc/experience_bank.md` and replace all placeholders with your real experience. **Never commit the real `experience_bank.md` to a public repo** — it's gitignored.

---

## How to use this file

1. Before editing any resume `.tex`, read this file first
2. Pick bullets that match the target JD — **do not invent**
3. If you need a new bullet, add it here first (so it's reusable across variants)
4. Keep honesty boundaries (see Skill §6.1–§6.4): no inflated metrics, no exaggerated titles

---

## Role: ROLE_TITLE @ COMPANY_X (YYYY-MM — YYYY-MM)

### Context

- Team size: TEAM_SIZE
- Your role: YOUR_ACTUAL_ROLE (not aspirational)
- Tech stack: LANGUAGES, FRAMEWORKS, TOOLS

### Bullet material

#### Component: COMPONENT_A

- Designed and maintained COMPONENT_A, processing METRIC_N events/day
- Reduced METRIC_X by PERCENT_Y% through OPTIMIZATION_DESCRIPTION
- Led TEAM_SIZE engineers through LIFECYCLE_PHASE (design → deploy → operate)

#### Component: COMPONENT_B

- Built TOOL_B for PURPOSE, replacing manual PROCESS
- Implemented FEATURE_C with TECH_STACK, serving METRIC_N users
- Maintained EXISTING_PLATFORM (not greenfield — describe accurately)

### Honesty boundaries (per role)

- **Do not claim**: ASPIRATIONAL_CLAIM (e.g. "architected from scratch" if you maintained an existing system)
- **Correct framing**: ACTUAL_SCOPE (e.g. "developed and maintained PDI on existing platform")
- **POC vs production**: If it was a POC, say "POC" — don't imply production deployment

---

## Role: ROLE_TITLE_2 @ COMPANY_Y (YYYY-MM — YYYY-MM)

### Context

- Team size: TEAM_SIZE
- Your role: YOUR_ACTUAL_ROLE
- Tech stack: LANGUAGES, FRAMEWORKS, TOOLS

### Bullet material

#### Component: COMPONENT_D

- Shipped FEATURE_E using FRAMEWORK_F, achieving METRIC_G
- Collaborated with TEAM_H on CROSS_TEAM_INITIATIVE
- Wrote TOOL_I for AUTOMATION_PURPOSE, saving METRIC_J hours/week

### Honesty boundaries

- **Do not claim**: ASPIRATIONAL_CLAIM
- **Correct framing**: ACTUAL_SCOPE

---

## Personal open-source project: YOUR_OPEN_SOURCE_PROJECT

### Framing

- **EN title**: YOUR_OPEN_SOURCE_PROJECT — Open-Core Research Workflow Framework
- **CN title**: YOUR_OPEN_SOURCE_PROJECT — 开源研究工作流框架
- **GitHub**: https://github.com/your-org/YOUR_OPEN_SOURCE_PROJECT

### Bullets

- Internal workflow abstraction → recipe chain → staged artifacts + schema ID
- Extension-pack boundary for third-party plugins
- Artifact audit / golden test / parity checking
- Published to PyPI

### Honesty boundaries

- **Do not write**: live trading, order routing, market-specific, signals product
- **Do write**: reproducible research workflows, artifact-driven engineering
- GitHub URL on its own line (prevents PDF line-wrap issues)

---

## Skills section templates

### job / JD variant

```
Skills: Python, SQL, Bash, C++ | Git, SVN, Jira | Codex, Cursor, Trae
```

### ai_eval variant

```
Skills: Python, SQL, LaTeX | AI Tools: Cursor, Codex, Trae | Dev: Git, Linux, SVN, Jira
```

### backend_ops variant

```
Skills: Python, Bash, SQL | Oracle | Git, SVN, Jira | AI Tools: Cursor, Codex, Trae
```

### Rules

- Skills section lists **languages, AI tools, dev toolchain** only
- **No** RAG stack, Agent workflows, or framework buzzwords in Skills (those go in bullets)
- **No** writing Codex/Cursor/Trae as "programming languages"
