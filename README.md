# Resumaker

> 一个智能的 HTML 简历生成框架，配合 Agent Skills 实现场景化简历制作
> An intelligent HTML resume generator framework with Agent Skills integration for scenario-based resume creation

[English](#english) | [中文](#中文)

---

## 中文

### 特性

- **智能简历生成** - 根据目标职位、行业、风格偏好动态生成，无固定模板限制
- **高质量 PDF 输出** - 矢量 PDF，文字可选中，适合打印和在线投递
- **Agent Skills** - 内置设计指南，通过对话式交互完成简历制作
- **多种风格支持** - 极简、现代、传统、创意等多种设计风格
- **完全可定制** - 基于 Tailwind CSS，易于修改和扩展

### 快速开始

#### 环境要求

- Node.js 18+
- pnpm (推荐) 或 npm
- Google Chrome (用于 PDF 生成)
- [Claude Code](https://claude.ai/claude-code)

#### 安装

```bash
git clone https://github.com/your-username/resumaker.git
cd resumaker
pnpm install
```

#### 使用 Claude Code

在项目目录下启动 Claude Code，然后使用以下 skills：

```
/resume-new     # 智能生成新简历（会询问场景和偏好）
/resume-edit    # 编辑现有简历
/resume-pdf     # 生成 PDF
/resume-preview # 浏览器预览
```

#### 手动使用

```bash
# 生成 PDF（A4 缩放）
pnpm pdf

# 生成 PDF（保持原始尺寸）
pnpm pdf:natural

# 指定输入输出文件
node scripts/generate-resume-pdf.js --input html/resume.html --output pdf/resume.pdf
```

### 工作原理

Resumaker 不提供固定模板，而是通过 Agent Skills 中的**设计指南**，根据你的具体场景（目标职位、行业、风格偏好）动态生成最合适的简历。

#### 工作流程

1. **收集信息** - Claude 询问你的目标职位、行业、风格偏好
2. **整理资料** - 你提供个人信息、工作经历、项目经历等
3. **生成简历** - Claude 根据设计指南生成专业的 HTML 简历
4. **预览调整** - 在浏览器中预览，使用 `/resume-edit` 调整内容
5. **导出 PDF** - 使用 `/resume-pdf` 生成高质量 PDF

### 项目结构

```
resumaker/
├── assets/              # 图片素材（头像、项目截图等）
├── html/                # 生成的 HTML 简历
├── pdf/                 # 生成的 PDF
├── reference/           # 参考资料
├── scripts/
│   └── generate-resume-pdf.js  # PDF 生成脚本
├── .claude/
│   └── skills/          # Claude Code Agent Skills
│       ├── resume-new/      # 智能生成（含设计指南）
│       ├── resume-edit/     # 智能编辑
│       ├── resume-pdf/      # PDF 生成
│       └── resume-preview/  # 预览
├── package.json
└── README.md
```

### Skills 参考

| Skill | 描述 |
|-------|------|
| `/resume-new` | 智能生成简历，根据场景动态生成 HTML |
| `/resume-edit` | 编辑现有简历，保持设计风格一致 |
| `/resume-pdf` | 将 HTML 转换为高质量矢量 PDF |
| `/resume-preview` | 在浏览器中预览简历 |

### 设计指南

设计指南位于 `.claude/skills/resume-new/references/design-guide.md`，包含：

- 页面规范（A4 尺寸、内边距、布局）
- 色彩方案（专业蓝、极简灰、温暖棕、森林绿）
- 字体规范（Inter、Noto Sans SC、JetBrains Mono）
- 内容区块优先级
- HTML 结构模板
- 常用样式组件

### 技术栈

- **Tailwind CSS** - 样式框架
- **Font Awesome** - 图标库
- **Google Fonts** - 字体（Inter、Noto Sans SC、JetBrains Mono）
- **Puppeteer** - PDF 生成

---

## English

### Features

- **Intelligent Resume Generation** - Dynamically generates resumes based on target position, industry, and style preferences without fixed template limitations
- **High-Quality PDF Output** - Vector PDF with selectable text, suitable for printing and online submission
- **Agent Skills** - Built-in design guidelines with conversational interaction for resume creation
- **Multiple Style Support** - Minimalist, modern, traditional, creative, and other design styles
- **Fully Customizable** - Based on Tailwind CSS, easy to modify and extend

### Quick Start

#### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm
- Google Chrome (for PDF generation)
- [Claude Code](https://claude.ai/claude-code)

#### Installation

```bash
git clone https://github.com/your-username/resumaker.git
cd resumaker
pnpm install
```

#### Usage with Claude Code

Start Claude Code in the project directory, then use the following skills:

```
/resume-new     # Intelligently generate new resume (will ask about scenario and preferences)
/resume-edit    # Edit existing resume
/resume-pdf     # Generate PDF
/resume-preview # Browser preview
```

#### Manual Usage

```bash
# Generate PDF (A4 scaling)
pnpm pdf

# Generate PDF (keep original size)
pnpm pdf:natural

# Specify input and output files
node scripts/generate-resume-pdf.js --input html/resume.html --output pdf/resume.pdf
```

### How It Works

Resumaker doesn't provide fixed templates. Instead, it uses **design guidelines** in Agent Skills to dynamically generate the most suitable resume based on your specific scenario (target position, industry, style preferences).

#### Workflow

1. **Collect Information** - Claude asks about your target position, industry, and style preferences
2. **Organize Materials** - You provide personal information, work experience, project experience, etc.
3. **Generate Resume** - Claude generates professional HTML resume based on design guidelines
4. **Preview and Adjust** - Preview in browser, use `/resume-edit` to adjust content
5. **Export PDF** - Use `/resume-pdf` to generate high-quality PDF

### Project Structure

```
resumaker/
├── assets/              # Image assets (avatars, project screenshots, etc.)
├── html/                # Generated HTML resumes
├── pdf/                 # Generated PDFs
├── reference/           # Reference materials
├── scripts/
│   └── generate-resume-pdf.js  # PDF generation script
├── .claude/
│   └── skills/          # Claude Code Agent Skills
│       ├── resume-new/      # Intelligent generation (with design guide)
│       ├── resume-edit/     # Intelligent editing
│       ├── resume-pdf/      # PDF generation
│       └── resume-preview/  # Preview
├── package.json
└── README.md
```

### Skills Reference

| Skill | Description |
|-------|-------------|
| `/resume-new` | Intelligently generate resume, dynamically create HTML based on scenario |
| `/resume-edit` | Edit existing resume while maintaining design consistency |
| `/resume-pdf` | Convert HTML to high-quality vector PDF |
| `/resume-preview` | Preview resume in browser |

### Design Guide

The design guide is located at `.claude/skills/resume-new/references/design-guide.md`, including:

- Page specifications (A4 size, padding, layout)
- Color schemes (Professional Blue, Minimalist Gray, Warm Brown, Forest Green)
- Font specifications (Inter, Noto Sans SC, JetBrains Mono)
- Content block priorities
- HTML structure templates
- Common style components

### Tech Stack

- **Tailwind CSS** - Styling framework
- **Font Awesome** - Icon library
- **Google Fonts** - Fonts (Inter, Noto Sans SC, JetBrains Mono)
- **Puppeteer** - PDF generation

---

## Contributing

欢迎 PR 和 Issue！ / PRs and Issues are welcome!

## License

MIT
