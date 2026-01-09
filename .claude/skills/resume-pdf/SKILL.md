---
name: resume-pdf
description: 简历 PDF 生成器。将 HTML 简历转换为高质量矢量 PDF（文字可选中）。当用户想要导出简历、生成 PDF、或说"把简历转成 PDF"时触发此 skill。
---

# Resume PDF - PDF 生成

将 HTML 简历转换为高质量矢量 PDF，文字可选中，适合打印和在线投递。

## 工作流程

### 1. 检查依赖

确认 Node.js 和 puppeteer 已安装：

```bash
# 检查 node_modules 是否存在
ls node_modules/puppeteer

# 如果不存在，安装依赖
pnpm install
# 或
npm install
```

### 2. 定位简历文件

查找 `html/` 目录下的 HTML 简历文件：
- 默认选择最新修改的文件
- 如有多个文件，询问用户选择

### 3. 选择输出模式

询问用户选择输出模式：

- **A4 缩放**（默认）：自动缩放适应 A4 纸张
- **原始尺寸**：保持 HTML 原始尺寸，不缩放

### 4. 执行生成

运行 PDF 生成脚本：

```bash
# A4 缩放模式（默认）
node scripts/generate-resume-pdf.js

# 原始尺寸模式
node scripts/generate-resume-pdf.js --natural

# 指定输入输出文件
node scripts/generate-resume-pdf.js --input html/resume.html --output pdf/resume.pdf
```

### 5. 返回结果

生成完成后：
- 告知用户 PDF 文件路径
- 提示可以使用 `open` 命令打开查看

## 脚本说明

PDF 生成脚本位于 `scripts/generate-resume-pdf.js`，功能：

- 使用 Puppeteer 控制 Chrome 浏览器
- 等待字体和外部资源完全加载
- 隐藏打印按钮（`.no-print` 元素）
- 输出矢量 PDF（文字可选中）
- 支持跨平台（macOS、Windows、Linux）

## 常见问题

### Chrome 未找到

脚本会自动检测系统 Chrome 路径，如果找不到会使用 Puppeteer 内置的 Chromium。

### 字体显示异常

确保网络连接正常，脚本会等待 Google Fonts 加载完成。

### PDF 内容溢出

检查 HTML 简历是否超出 A4 一页，使用 `/resume-edit` 精简内容。

## 示例交互

**用户**: 帮我生成 PDF

**Claude**: 好的，我来帮你生成 PDF。

[检查 html/ 目录下的简历文件]

找到简历文件：`html/2024-01-15_10-30-00.html`

选择输出模式：
1. A4 缩放（推荐，适合打印）
2. 原始尺寸

**用户**: A4 缩放

**Claude**: 正在生成 PDF...

[运行 node scripts/generate-resume-pdf.js]

PDF 生成成功！文件保存在：`pdf/2024-01-15_10-30-00.pdf`

使用以下命令打开查看：
```bash
open pdf/2024-01-15_10-30-00.pdf
```
