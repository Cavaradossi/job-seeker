---
name: job-seeker
description: >-
  管理求职 LaTeX 简历变体：按 JD 定制 bullet、编译 PDF、Markdown/DOCX/PDF/LaTeX
  互转、推荐变体、浏览器辅助投递（默认 dry-run/rehearse，提交须人工确认）、
  更新投递 tracker、检查诚实边界。在用户提到申职器、job-seeker、简历、JD、
  编译、格式转换、投递时使用。
version: 0.2.0
tags: [resume, job-search, latex, career, convert, apply, 申职器]
language: zh-CN
---

# job-seeker — 申职器（中文 Skill）

多版本 LaTeX 简历 + 格式转换 + 浏览器辅助投递（人工确认）工作流。
强制诚实边界，避免夸大 scope、指标或职级。

英文版：同目录 `SKILL.md`。Cursor 规则：`.cursor/rules/resume-editing.mdc`。

## 编辑器路径

| 编辑器 | 路径 |
|--------|------|
| **Cursor** | `.cursor/skills/job-seeker/`（仓库已内置） |
| WorkBuddy | `.workbuddy/skills/job-seeker/`（frontmatter 加 `agent_created: true`） |
| 便携源（优先在此改） | `docs/skill/job-seeker/` |

Windows 说明：[`docs/BUILD_WINDOWS.md`](../../BUILD_WINDOWS.md)  
Cursor 说明：[`docs/skill/CURSOR.md`](../CURSOR.md)

## 何时使用

- 粘贴 JD，要定制简历或推荐变体
- 编译 / 重建 PDF（Windows：`.\build_resumes.ps1`；macOS/Linux：`./build_resumes.sh`）
- 格式转换（`python -m convert ...`）
- 投递 dry-run / 彩排（`python -m apply --dry-run ...`）
- 编辑 `docs/experience_bank.md` 或 `.tex` bullet
- 更新 tracker、检查 bullet 是否夸大
- 询问申职器项目本身

## 1. 仓库地图（相对路径）

```
./
├── resume_template/          # 公开样例 +  bundled 中文字体
├── LaTeX_Resume_CN/          # 你的中文简历（本地创建，gitignore）
├── LaTeX_Resume_EN/          # 你的英文简历（本地创建，gitignore）
├── convert/                  # python -m convert
├── apply/                    # python -m apply
├── docs/experience_bank.md   # 私有 bullet 库（从 .example 复制）
├── build_resumes.ps1         # Windows 编译
├── build_resumes.sh          # macOS/Linux 编译
└── scripts/sync_skills.ps1   # 改 Skill 后同步镜像
```

首次使用：复制 `resume_template/` 到 `LaTeX_Resume_*` 并填写个人信息，勿提交公开仓库。

## 2. 标准流程

### A. 新 JD → 定制简历

1. 读 JD（粘贴 / URL / `docs/jd_mapping/<公司>.md`）
2. **先读** `docs/experience_bank.md`，禁止编造
3. 推荐变体：`python -m apply --jd-file <文件> --dry-run`
4. **方案 A（默认）**：复制通用 `.tex`，只改 `\centerline` headline
   - **或用起草器自动化（Phase 4）**：`python -m job_seeker tailor --jd-file <文件>`
     按 JD 关键词给经历库 bullet 打分，并写入定制变体 `.tex`（替换基础模板里
     `% >>> TAILOR BLOCK <SCRIPT> START/END` 标记区——绝不编造）。搭配
     `python -m job_seeker cover-letter --jd-file <文件>` 生成脚本感知的求职信草稿。
5. 编译并核对页数（JD 版目标 **1 页**）
6. 更新 `outputs/job_application_tracker.csv`

### B. 改 bullet / 技能行

1. 若影响多份简历，先改 `docs/experience_bank.md`
2. 同步改各 `LaTeX_Resume_*/*.tex`
3. 重新编译，英文通用版保持 **1 页**

### C. 格式转换

```powershell
python -m convert --input resume.tex --output outputs/resume.pdf
python -m convert --list-routes
```

- 排版真相源：`.tex → .pdf`（xelatex）
- LaTeX ↔ DOCX **有损**，须提醒用户
- PDF → Markdown 仅提取文本，不支持扫描件 OCR

### D. 投递（彩排 / 预填）

```powershell
$env:JOB_SEEKER_NAME = "Your Name"
$env:JOB_SEEKER_EMAIL = "you@example.com"
python -m apply --jd-file apply\samples\sample_jd.html --dry-run
```

**铁律：** 禁止自动提交；Boss直聘/LinkedIn 仅打开页面展示数据；凭证只用环境变量。

### E. 投递后

- 写入 tracker（见 `docs/tracker_schema.md`）
- 可选：`history/apply_<date>.log`、cover note

## 3. 变体选用

| 变体 | 源 `.tex` | 场景 |
|------|-----------|------|
| 样例 | `resume_template/sample-resume-en_US-zh_CN.tex` | 首次编译 / CI |
| 中文通用 | `LaTeX_Resume_CN/resume-zh_job.tex` | 国内开发岗 |
| 中文运维 | `resume-zh_backend_ops.tex` | 后端 / 运维 |
| 中文 AI | `resume-zh_ai_eval.tex` | RAG / 大模型 |
| 英文通用 | `LaTeX_Resume_EN/resume_job_en.tex` | 英文岗（1 页） |

> **按文字系统打标签的变体。** `LaTeX_Resume_*` 目录是以**文字系统 / 脚本**为键，
> 而非「英文 vs 中文」。`CN`/`EN` 只是众多后缀里的两个——你可以自建
> （`LaTeX_Resume_AR/`、`LaTeX_Resume_RU/`、`LaTeX_Resume_JA/`……），
> `build_resumes.sh` 和变体解析器会自动识别。job-seeker 把**每种脚本都当一等公民**；
> 公开仓库只随附维护者所用的中文 / 英文样例模板。任意语种的设计见 §6。

详见 `references/variant_playbook.md`。

## 4. 诚实边界

### §4.1 内容真实

- 不编造指标；职级不夸大（Technical Lead ≠ Staff）
- 「维护/扩展现有平台」≠「从零开发」
- RAG 写真实参数（TopK、阈值、分块策略）
- Workflow POC ≠ 自主 Agent / 生产系统

### §4.2 技能行

- 只写：语言、开发工具链、AI 工具（Cursor/Codex/Trae）
- **不要**在 Skills 里堆 RAG/Kafka/Agent 栈 — 写在项目 bullet 里
- AI 助手不是编程语言

### §4.3 开源项目表述

- 按实际领域中性描述；GitHub 链接**单独一行**
- 不把研究工具包写成实盘交易 / 订单路由

### §4.4 篇幅

- JD 版 + 英文通用：**1 页**（`enumitem` 压缩）
- 中文完整版（含科研）可多页

### §4.5 起草-审稿双轮（模型无关）

为 JD 定制变体时，**写两轮，不是一轮**。这是纯提示工程，在任何编辑器
（Cursor / Codex / WorkBuddy）下都成立，不需要付费订阅或特定模型。

1. **起草者。** 依所选模板 + 经历库产出定制 `.tex` 变体，按 JD 裁剪/加权
   bullet。守住诚实（§4.1）。`python -m job_seeker tailor --jd-file <jd>` 命令
   （Phase 4）离线自动化这一轮：按 JD 关键词重叠给经历库 bullet 打分，并替换
   基础模板标记区的经历条目。
2. **审稿者（独立一轮 / 新上下文）。** 只重读 JD + 草稿，批判而非奉承：
   - 弱动词、套话、废话（"utilized""leveraged""various"）。
   - bullet 读起来比实际工作更强（§4.1 注水）。
   - JD 关键词只是挂名出现（堆词而无实质）。
   - 孤行、溢出、§4.4 要求 1 页却超页。
   - 有真实数字却未量化。
3. **修订。** 只采纳能让 bullet 更真实的批评；若某条批评会导致注水，拒绝
   并注明理由。

审稿轮是建议性的——绝不自动改稿。它执行与起草轮相同的诚实规则，职责是
抓住单轮容易漏掉的问题。

## 5. 编译

**Windows**

```powershell
.\build_resumes.ps1
```

**macOS / Linux**

```bash
./build_resumes.sh
```

样例仅编译：

```powershell
cd resume_template
xelatex -interaction=nonstopmode sample-resume-en_US-zh_CN.tex
```

## 6. i18n / 任意文字系统设计

job-seeker 是**脚本无关（script-agnostic）**的：每种文字系统都是一等公民——
汉字（CJK）、拉丁、西里尔、阿拉伯、希伯来、天城文（Devanagari）、希腊，乃至更多。
CJK 是**试验场**（内置 CJK 字体 + xelatex 是最难的部分）；一旦跑通，拉丁 / 西里尔 /
阿拉伯 / 希伯来只是字体 + bidi 的工作，而非重写。

- **文本路径与脚本无关。** `convert/` 流水线保留任意 Unicode 脚本；变体解析器与
  技能缺口（`--upskill`）分词器是**脚本感知**的（非 ASCII-only），非拉丁 JD 也能正确处理。
- **变体目录按脚本打标签。** `LaTeX_Resume_<SCRIPT>/`——可自建
  （`AR`/`RU`/`JA`/……）；`build_resumes.sh` 与解析器自动识别。
- **渲染（v0.4）：** `resume.cls` 自动加载 `fonts_any_script.sty`，它通过
  `ucharclasses` **按 Unicode 区块切换字体**——无需改动你的 `.tex`。`fonts/Noto/`
  内置 **Noto** 字体（由 `scripts/fetch_noto_fonts.sh` 拉取），为西里尔 / 希腊 /
  阿拉伯 / 希伯来 / 天城文提供**字形覆盖（无豆腐块）**，全部按 **LTR** 排布。
  已验证：*任意单一*文字系统的简历都能干净渲染；*双语*简历（拉丁 + 一种非拉丁脚本，
  如阿拉伯文 + 英文）在每段脚本之后都能正确恢复主字体。
  - **已知限制（v0.4）：** 同一文档**内联混排两种及以上非拉丁脚本**可能让字体卡在
    上一个脚本——这是 `ucharclasses` 在多个脚本类同时激活时的已知脆弱性。简历场景
    罕见；建议每份简历只用一种脚本（或拉丁 + 一种脚本）。
  - **RTL 排序**（阿拉伯 / 希伯来正确的从右到左流向）是已规划的 **v0.5** 实验项——
    `bidi`/`polyglossia` 与 `resume.cls` 的 `titlesec`/`hyperref`/`enumitem` 排版宏
    冲突，因此 v0.4 只交付 LTR 字形覆盖（文字可见，只是未重排）。
- **门户按语言感知。** `apply/portals.yaml` 条目可带 `languages:` / `scripts:`，
  使 `--recommend-platforms` 也能按语言匹配。
- **护城河审计（v0.5）。** `python -m job_seeker i18n-audit` 静态扫描工具链，查
  ASCII-only 分词器、硬编码 CN/EN 变体对、以及回潮的 CJK-only / 单脚本措辞——一个
  CI 可用的守卫，确保脚本无关的护城河不破（`--strict` 时遇到 ERROR 非零退出）。
  当前代码树报告 0 ERROR / 0 WARN。
- **语言标签变体清单（v0.5）。** 每个 `LaTeX_Resume_<SCRIPT>/` 可带 `variant.json`
  （`{name, script, language, base_template}`）。一条命令新增脚本变体——
  `python -m job_seeker init-variant --script RU` 从 `resume_template/` 脚手架出
  `LaTeX_Resume_RU/` 并写入清单；`python -m job_seeker list-variants` 列出已有变体。

这才是相对「英文优先」工具真正的护城河：我们假设*任意语言*，而不只是英文。

## 7. Agent 行为（Cursor）

1. 改 bullet 前读 `docs/experience_bank.md`
2. 不擅自重构 `convert/`、`apply/` 核心
3. 不 silent commit/push
4. 文档与命令兼顾 Windows（`.\build_resumes.ps1`、`\` 路径）与 Unix
5. 默认 `apply --dry-run`； live 提交须用户明确确认

## 8. 占位符

示例用 `YOUR_NAME`、`your-email@example.com`、`your-org/job-seeker`，勿写入真实 PII。

## 9. 不在范围内

- 未经确认自动提交投递
- 把 tracker、experience bank、私有 `.tex` 提交到公开仓库
- 扫描件 PDF 的 OCR
