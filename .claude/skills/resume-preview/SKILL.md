---
name: resume-preview
description: 简历预览工具。在浏览器中打开 HTML 简历进行预览。当用户想要预览简历、查看简历效果、或说"打开简历看看"时触发此 skill。
---

# Resume Preview - 简历预览

在浏览器中打开 HTML 简历进行预览。

## 工作流程

### 1. 定位简历文件

查找 `html/` 目录下的 HTML 简历文件：
- 默认选择最新修改的文件
- 如有多个文件，列出供用户选择

### 2. 打开浏览器预览

使用系统默认浏览器打开 HTML 文件：

```bash
# macOS
open html/resume.html

# Windows
start html/resume.html

# Linux
xdg-open html/resume.html
```

### 3. 提示用户

预览打开后提示：
- 可以直接在浏览器中按 Cmd+P (macOS) 或 Ctrl+P (Windows/Linux) 打印为 PDF
- 或使用 `/resume-pdf` 生成高质量 PDF

## 预览功能

HTML 简历在浏览器中预览时：
- 显示为 A4 纸张大小
- 带有阴影效果，模拟纸张
- 右上角有"打印 / PDF"按钮
- 点击按钮可直接调用浏览器打印功能

## 示例交互

**用户**: 预览一下简历

**Claude**: 好的，我来帮你预览简历。

[查找 html/ 目录下的简历文件]

找到以下简历文件：
1. `2024-01-15_10-30-00.html`（最新）
2. `2024-01-10_14-20-00.html`

正在打开最新的简历...

[运行 open html/2024-01-15_10-30-00.html]

简历已在浏览器中打开。你可以：
- 直接在浏览器中查看效果
- 点击右上角"打印 / PDF"按钮导出
- 或使用 `/resume-pdf` 生成高质量 PDF
