# job-seeker — 申职器

> **语言**：[English](README.md) · [简体中文](README.zh-CN.md)

**几分钟内把一份干净的 LaTeX 简历按职位描述（JD）定制好** —— 还能在 Markdown / DOCX / PDF / LaTeX 之间互转，并可选地在浏览器里预填投递表单（带一道硬性的人工确认闸门，绝不自动提交）。自带 bundled CJK 字体，开箱即用；另附 Agent Skill，教会你的 AI 编辑器整套工作流。

`MIT` · 跨平台（macOS · Linux · Windows）· LaTeX + pandoc + Playwright

---

## ✨ 为什么用申职器？

一份简历投所有岗位会被筛掉；逐岗手改太慢；`.tex` / DOCX / Markdown 之间来回同步更痛苦；投递时还容易出错。申职器把这些串成一条顺滑的流水线：

- **任意格式进，任意格式出。** 从 `.tex`、`.md`、`.docx` 或 `.pdf` 起步都行——四种格式之间自由互转，无需手动同步。
- **按 JD 选变体。** 贴一段 JD，自动推荐合适的简历变体。
- **投递不失控。** 浏览器助手帮你预填表单，但**绝不自动提交**——每次提交都等你亲手按 `y`。
- **天生诚实。** 内置 Skill 强制反注水规则（不编造指标、不夸大头衔）。

## 🚀 功能特性

- **干净的 LaTeX 模板**，**自带 Adobe CJK 字体**——无需安装系统字体。
- **跨平台编译脚本**（`build_resumes.sh` / `.ps1`），带页数统计。
- **任意格式互转**（`convert/`）：LaTeX ↔ Markdown ↔ DOCX ↔ PDF——上传任一格式的简历，转成任意其他格式，adapter 模式 + BFS 自动路由（PDF 文本用 PyMuPDF 提取）。
- **JD → 变体推荐器**（`apply/`）：基于关键词规则，挑出最匹配的简历。
- **浏览器辅助投递**，含站点 adapter（Boss直聘 / LinkedIn / 通用 ATS）与**人工确认闸门**。
- **投递 tracker**（CSV）+ 历史审计日志，每次操作都留痕。
- **Agent Skill**（WorkBuddy / Cursor / 通用编辑器），固化工作流与诚实边界。
- **CI** 在每次 push/PR 时编译样例简历。

## 📦 安装

**前置依赖**

| 工具 | 用于 | 说明 |
|------|------|------|
| TeX Live（`xelatex`） | 编译 PDF | macOS：`brew install --cask mactex`——完整指南见 [`docs/BUILD_MAC.md`](docs/BUILD_MAC.md) |
| Python 3.10+ | `convert/` 与 `apply/` | |
| pandoc | DOCX / Markdown 转换 | 只编 PDF 的话仅需 `xelatex`；`brew install pandoc` |
| Playwright*（可选）* | `apply/` 实时浏览器预填 | `pip install playwright && playwright install chromium` |

**安装步骤**

```bash
git clone https://github.com/Cavaradossi/job-seeker.git
cd job-seeker
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## ⚡ 快速上手

### 1. 编译样例简历

```bash
cd resume_template
xelatex -interaction=nonstopmode sample-resume-en_US-zh_CN.tex
# → sample-resume-en_US-zh_CN.pdf（含 CJK 字体，无需额外配置）
```

### 2. 格式互转

```bash
# 输入格式由扩展名自动识别——.tex / .md / .docx / .pdf 任一格式都能作为起点
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.pdf
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.docx
python -m convert --input my_resume.pdf   --output outputs/my_resume.md    # PDF → Markdown（用 PyMuPDF 提取文本）
python -m convert --input my_resume.docx  --output outputs/my_resume.tex   # DOCX → LaTeX
python -m convert --list-routes           # 查看所有支持的转换
```

### 3. 按 JD 定制 & 演练投递流程

```bash
python -m apply --jd-file apply/samples/sample_jd.html --dry-run    # 读 JD → 推荐变体 → 出 PDF
python -m apply --url https://example.com/jobs/123 --dry-run        # 从网页实时抓取 JD
python -m apply --jd-file apply/samples/sample_jd.html --rehearse   # 体验确认闸门的暂停
```

## 💡 使用示例

**做一个 JD 专属变体。** 复制通用模板，只改 headline，编译：

```bash
cp resume_template/sample-resume-en_US-zh_CN.tex LaTeX_Resume_CN/resume-zh_jd_acme.tex
# 把 \centerline{...} 的 headline 改成贴合 JD 的表述，然后：
./build_resumes.sh
```

**把 Markdown 草稿转成 PDF**（用 pandoc 默认模板，不是简历排版，适合做草稿）：

```bash
python -m convert --input notes.md --output notes.pdf
```

**投递一个公开 ATS 岗位**（通用 adapter；实时预填需 Playwright）：

```bash
export JOB_SEEKER_NAME="你的名字"
export JOB_SEEKER_EMAIL="you@example.com"
python -m apply --url https://boards.greenhouse.io/acme/jobs/123 --variant resume_job_en
# → 打开浏览器、预填字段，然后在提交前【暂停】等你的 [y/N]
```

## ⚙️ 配置说明

- **投递档案**——通过环境变量设置（绝不写入仓库）：
  - `JOB_SEEKER_NAME`、`JOB_SEEKER_EMAIL`、`JOB_SEEKER_PHONE`
  - `JOB_SEEKER_CONFIRM=yes|no`——自动应答确认闸门（仅用于脚本/测试）
- **简历变体**——把你的 `.tex` 放进 `LaTeX_Resume_CN/` 或 `LaTeX_Resume_EN/`；渲染器会在这两个目录加 `resume_template/` 里查找。
- **工具发现**——`convert/tools.py` 先在 `PATH` 找 `pandoc` / `xelatex` / `latexmk`，找不到再回退到常见安装位置（MacTeX、`~/texlive/*/bin/*`、Homebrew、`~/.local/bin`），所以非交互式 shell 里也能用。
- **ToS 感知 adapter**——Boss直聘 与 LinkedIn 设了 `tos_blocks_automation = True`，`apply` 会降级为「打开页面 + 展示预填数据」，而不是去自动化它们。

## 📁 项目结构

```
job-seeker/
├── resume_template/        干净的 LaTeX 模板 + bundled CJK 字体 + fontawesome
├── convert/                Phase 2：格式互转 pipeline（MD/DOCX/PDF/LaTeX）
│   ├── adapters/           每种转换一个 adapter（pandoc / xelatex）
│   ├── pipeline.py         BFS 路由 + adapter 链式调用
│   └── cli.py              python -m convert ...
├── apply/                  Phase 3：浏览器辅助投递
│   ├── adapters/           站点 adapter（generic / boss_zhipin / linkedin）
│   ├── mapping/            JD→变体推荐 + 变体渲染
│   ├── confirm.py          人工确认闸门（submit() 永远阻塞在这里）
│   ├── audit.py            tracker CSV + 历史日志
│   └── cli.py              python -m apply ...
├── docs/                    编译指南、开源计划、tracker schema、经历库样例
├── docs/skill/job-seeker/  可移植 Agent Skill（WorkBuddy / Cursor / 通用）
├── build_resumes.sh/.ps1   跨平台编译脚本
└── requirements.txt        convert/ + apply/ 的 Python 依赖
```

## ❓ 常见问题（FAQ）

**需要安装系统字体吗？**
不需要。模板在 `resume_template/fonts/` 里自带 Adobe CJK 字体，任何机器上编译效果一致。

**必须装 pandoc 吗？**
只有要转 DOCX / Markdown 时才需要。`tex → pdf` 仅需 `xelatex`。

**它会自动提交我的投递吗？**
**绝不会。** `submit()` 一定会调用 `confirm()` 并阻塞，没有你的 `y` 什么都不会提交。对 Boss直聘 / LinkedIn（其 ToS 禁止自动化），它干脆不动手——打开页面、把数据展示给你手动粘贴。

**我的个人数据放在公开仓库里安全吗？**
设计上安全。`outputs/`（编译产物 + tracker CSV）、`history/`、`docs/experience_bank.md`、以及你真实的 `.tex` 变体都被 gitignore。公开仓库只有干净模板 + 代码，示例内容一律用 `YOUR_NAME` / `your-email@example.com` 占位符。

**Skill 支持哪些编辑器？**
WorkBuddy（从 `.workbuddy/skills/` 自动加载）、Cursor（把 `docs/skill/job-seeker/` 复制到 `.cursor/skills/`）、或任意编辑器——直接打开 `docs/skill/job-seeker/SKILL.md` 按流程走即可。

**能不能从 PDF 或 Word 文档起步，而不是 LaTeX？**
可以。上传 `.tex` / `.md` / `.docx` / `.pdf` 任一格式，转成任意其他格式，pipeline 会自动路由。PDF 在**入口只提取文本**（用 PyMuPDF）：扫描件/图片型 PDF 没有文本层，会被拒绝，排版与样式也无法还原。请把「PDF 进」理解为「先把内容抢救出来，再用 LaTeX 模板重新排版」。

**转出来的 DOCX 看起来有损——为什么？**
LaTeX ↔ DOCX 本质上有损：简历专属宏（`\name`、`\centerline`、`\datedsubsection`、图标等）无法保留。DOCX 只作可编辑的文本镜像，绝非排版精确的渲染。`.tex → .pdf` 才是真相之源。（CLI 会在每个有损步骤打印 `WARNING`。）

## 🤝 参与贡献

欢迎贡献——能做的事很多！几个适合上手的方向：

- **新站点 adapter**——为你常用的 ATS 写一个（Workday / Greenhouse / Lever 变体都欢迎），以 `apply/adapters/workday_generic.py` 为模板。
- **新转换 adapter**（如 HTML → PDF、或给扫描件 PDF 做 OCR）——实现 `convert/adapters/` 里的 `Adapter` ABC。
- **更多 JD → 变体规则**——见 `apply/mapping/jd_to_variant.py`。
- **更强的预填字段识别**启发式规则。

提 PR 前：

1. 读一遍[开源计划](docs/job_seeker_opensource_plan.md)，了解方向与隐私策略。
2. 遵守 [`docs/skill/job-seeker/SKILL.md`](docs/skill/job-seeker/SKILL.md) §6 的**诚实边界**——不注水、不编造指标。
3. 在 `convert/tests/` 或 `apply/tests/` 下加测试，跑 `pytest`（现有 33 个测试须保持全绿）。
4. 示例内容用占位符（`YOUR_NAME`、`your-email@example.com`）——绝不放真实个人信息。

## 📄 许可证

MIT——见 [`LICENSE`](LICENSE)。

`resume_template/` 目录源自 [billryan/resume](https://github.com/billryan/resume)（同为 MIT）。所有 bundled 字体保留其原始许可证。
