# job-seeker — 申职器

> **语言**：[English](README.md) · [简体中文](README.zh-CN.md)

开源简历管理工具集：LaTeX 模板 + 跨平台编译脚本 + 按 JD 定制简历的 Agent Skill。

> **状态**：v0.2 — 模板 + 编译脚本 + Skill 骨架 + **格式互转 pipeline（Phase 2）** + **浏览器辅助投递（Phase 3）**。

## 仓库内容

| 路径 | 说明 |
|------|------|
| `resume_template/` | 干净的 LaTeX 简历模板（上游：billryan/HouJP）。自带 bundled 字体，无需安装系统字体。 |
| `build_resumes.sh` | macOS/Linux 编译脚本（xelatex + 页数统计）。参考实现，按你的目录结构改写。 |
| `build_resumes.ps1` | Windows 编译脚本（PowerShell，行为等价）。 |
| `doc/BUILD_MAC.md` | macOS 安装 TeX Live 指南（MacTeX / BasicTeX / 免 sudo 用户级安装）。 |
| `doc/job_seeker_opensource_plan.md` | 完整开源计划：范围、隐私策略、三阶段路线图。 |
| `doc/experience_bank.example.md` | 经历素材库模板（仅占位符）。 |
| `doc/tracker_schema.md` | 投递 tracker CSV 列定义。 |
| `docs/skill/job-seeker/` | 可移植 Agent Skill（编辑器无关）。可导入 WorkBuddy、Cursor 或手动使用。 |
| `.workbuddy/skills/job-seeker/` | WorkBuddy 原生 Skill（在 WorkBuddy 中克隆本仓库时自动加载）。 |
| `.github/workflows/build-resumes.yml` | CI：push/PR 时自动编译模板样例。 |
| `convert/` | **Phase 2** — 格式互转 pipeline（MD ↔ DOCX ↔ PDF ↔ LaTeX），基于 pandoc + xelatex，adapter 模式。见 [`convert/README.md`](convert/README.md)。 |
| `apply/` | **Phase 3** — 浏览器辅助投递：读 JD → 推荐变体 → 预填表单 → 人工确认提交 → 记录 tracker。见 [`apply/README.md`](apply/README.md)。 |
| `requirements.txt` | `convert/` 与 `apply/` 的 Python 依赖（`pip install -r requirements.txt`）。 |

## 快速开始

### 1. 安装 TeX

完整说明见 [`doc/BUILD_MAC.md`](doc/BUILD_MAC.md)。简版（macOS + Homebrew）：

```bash
brew install --cask mactex
```

### 2. 编译样例

模板自带一个样例 `.tex`：

```bash
cd resume_template
xelatex -interaction=nonstopmode HouJP-en_US-zh_CN.tex
# → 生成 HouJP-en_US-zh_CN.pdf
```

### 3. 创建你自己的简历变体

1. 把 `resume_template/` 复制为 `LaTeX_Resume_CN/`（或 `LaTeX_Resume_EN/`）
2. 重命名并改写 `.tex`（替换 `YOUR_NAME`、`your-email@example.com`）
3. 基于[样例模板](doc/experience_bank.example.md)创建 `doc/experience_bank.md`
4. 按你的文件列表改写 `build_resumes.sh`（编辑 `CN_FILES`、`EN_FILES` 数组）
5. 运行 `./build_resumes.sh` 编译所有变体

### 4. 使用 Agent Skill

Skill 教会 AI agent 简历编辑工作流：读经历素材库 → 编辑 `.tex` → 编译 → 检查页数 → 更新 tracker。

- **WorkBuddy**：`.workbuddy/skills/job-seeker/` 自动加载，直接对话即可。
- **Cursor**：把 `docs/skill/job-seeker/` 复制到 `.cursor/skills/job-seeker/`。
- **其他编辑器**：见 [`docs/skill/job-seeker/README.md`](docs/skill/job-seeker/README.md)。

## 诚实边界

Skill 强制诚实规则，防止简历注水：

- **§6.1 内容真实性**：不编造指标，不夸大头衔
- **§6.2 技能行纪律**：Skills 区只作简短关键词索引，不写项目专属技术栈或框架术语
- **§6.3 来源诚实**：实事求是描述项目，不锚定在单一项目上
- **§6.4 篇幅**：JD 定制版目标 1 页；完整版可多页

完整规则见 [`docs/skill/job-seeker/SKILL.md`](docs/skill/job-seeker/SKILL.md) §4。

## 路线图

| 阶段 | 状态 | 范围 |
|------|------|------|
| **Phase 1** | ✅ v0.1 | 跨平台编译 + Skill 骨架 + 开源计划 |
| **Phase 2** | ✅ v0.2 | 格式互转：Markdown ↔ DOCX ↔ PDF ↔ LaTeX（pandoc + xelatex，adapter 模式，BFS pipeline） |
| **Phase 3** | ✅ v0.2 | 浏览器辅助投递：读 JD → 预填表单 → 人工确认提交（站点 adapter、确认门、审计）。实时预填需 Playwright；dry-run 与确认门现已可用。 |

### Phase 2 快速开始

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -m convert --input resume_template/HouJP-en_US-zh_CN.tex --output outputs/sample.pdf
python -m convert --input resume_template/HouJP-en_US-zh_CN.tex --output outputs/sample.docx
python -m convert --list-routes
```

### Phase 3 快速开始

```bash
source .venv/bin/activate
python -m apply --jd-file apply/samples/sample_jd.html --dry-run          # JD + 变体 + PDF
python -m apply --jd-file apply/samples/sample_jd.html --rehearse         # 确认门暂停演示
python -m apply --url https://example.com/jobs/123 --dry-run              # 实时 HTTP 抓取 JD
```

完整计划：[`doc/job_seeker_opensource_plan.md`](doc/job_seeker_opensource_plan.md)。

## 许可证

MIT — 见 [`LICENSE`](LICENSE)。

`resume_template/` 目录源自 [billryan/RUC-Thesis](https://github.com/billryan/resume) 模板（同为 MIT）。所有 bundled 字体保留其原始许可证。

## 贡献

本项目处于早期阶段。仓库公开后欢迎提 Issue 与 PR。当前方向见[开源计划](doc/job_seeker_opensource_plan.md)。
