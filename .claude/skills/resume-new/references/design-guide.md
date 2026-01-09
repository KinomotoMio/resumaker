# 简历设计指南

本文档提供 HTML 简历的完整设计规范，用于生成专业、美观的简历。

## 页面规范

```
尺寸: A4 (210mm x 297mm)
内边距: 8-16mm
推荐布局: 3:1 网格（主内容区 3 列，侧边栏 1 列）
单页设计: 所有内容控制在一页内
```

## 技术栈

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Font Awesome 图标 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

## 色彩方案

根据风格偏好选择：

### 专业蓝（推荐用于技术/商务）
```
Primary: #2563EB (Blue 600)
Accent: #0F172A (Slate 900)
Secondary: #7C3AED (Violet 600)
Text: #334155 (Slate 700)
Border: #e2e8f0 (Slate 200)
Background: #f8fafc (Slate 50)
```

### 极简灰（推荐用于设计/创意）
```
Primary: #374151 (Gray 700)
Accent: #111827 (Gray 900)
Text: #4B5563 (Gray 600)
Border: #E5E7EB (Gray 200)
```

### 温暖棕（推荐用于传统行业）
```
Primary: #92400E (Amber 800)
Accent: #78350F (Amber 900)
Text: #44403C (Stone 700)
```

### 森林绿（推荐用于环保/教育）
```
Primary: #166534 (Green 800)
Accent: #14532D (Green 900)
Text: #374151 (Gray 700)
```

## 字体规范

```css
/* 标题 */
font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
font-weight: 600-700;

/* 正文 */
font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
font-weight: 400;

/* 代码/等宽 */
font-family: 'JetBrains Mono', monospace;
```

## 字号规范

```
姓名: text-3xl (1.875rem) font-bold
职位: text-sm font-bold
区块标题: text-sm uppercase tracking-wider font-bold
公司/项目名: text-sm font-bold
正文: text-[10px] 到 text-[11px]
标签: text-[9px] 到 text-[10px]
时间: text-[10px] font-mono
```

## 内容区块

### 必要区块
1. **个人信息区**：姓名、职位、联系方式（邮箱、电话、城市）
2. **工作经历**：公司、职位、时间、职责描述
3. **教育背景**：学校、专业、学位、时间

### 可选区块（根据场景选择）
- 关于我/个人简介
- 项目经历（技术岗必选）
- 技能标签
- 证书/荣誉
- 语言能力

### 区块优先级

**技术岗**
个人信息 > 工作经历 > 项目经历 > 技能 > 教育背景

**应届生/学生**
个人信息 > 教育背景 > 项目经历 > 实习经历 > 技能

**管理岗**
个人信息 > 工作经历 > 关于我 > 教育背景 > 证书

## HTML 结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简历 - {{姓名}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        'sans': ['"Inter"', '"Noto Sans SC"', 'system-ui', 'sans-serif'],
                        'mono': ['"JetBrains Mono"', 'monospace'],
                    }
                }
            }
        }
    </script>

    <style>
        @media print {
            @page { margin: 0; size: A4; }
            html, body {
                width: 210mm;
                height: 297mm;
                margin: 0 !important;
                padding: 0 !important;
            }
            .page {
                width: 100% !important;
                height: 100% !important;
                margin: 0 !important;
                box-shadow: none !important;
            }
            .no-print { display: none !important; }
            * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        }

        body { background-color: #f8fafc; }

        .page {
            width: 210mm;
            height: 297mm;
            margin: 30px auto;
            background: white;
            box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }
    </style>
</head>
<body class="font-sans antialiased text-slate-700">
    <!-- 打印按钮 -->
    <div class="no-print fixed top-4 right-4 z-50">
        <button onclick="window.print()" class="bg-slate-900 hover:bg-black text-white px-4 py-2 rounded-lg shadow-lg font-medium text-sm">
            <i class="fas fa-print mr-2"></i>打印 / PDF
        </button>
    </div>

    <div class="page">
        <!-- 顶部装饰条 -->
        <div class="absolute top-0 left-0 w-full h-1 bg-slate-900"></div>

        <div class="p-8 h-full">
            <!-- 使用 grid 布局 -->
            <div class="grid grid-cols-4 gap-6 h-full">
                <!-- 主内容区 (3列) -->
                <div class="col-span-3 flex flex-col gap-4">
                    <!-- 内容区块 -->
                </div>

                <!-- 侧边栏 (1列) -->
                <div class="col-span-1 border-l border-slate-100 pl-4">
                    <!-- 侧边栏内容 -->
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

## 常用样式组件

### 区块标题
```html
<div class="flex items-center gap-2 mb-2">
    <div class="w-1 h-4 bg-blue-600"></div>
    <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider">
        工作经历 <span class="text-slate-400 font-normal normal-case ml-1">Experience</span>
    </h2>
</div>
```

### 卡片样式
```html
<div class="bg-white border border-slate-200 rounded-xl p-4 border-l-4 border-l-blue-500">
    <div class="flex justify-between items-center mb-1">
        <h3 class="font-bold text-slate-800 text-sm">公司名称</h3>
        <span class="text-[10px] font-mono text-slate-400">2023.01 - Present</span>
    </div>
    <p class="text-[10px] text-slate-500 font-medium mb-2">职位名称</p>
    <p class="text-[10px] text-slate-600 leading-relaxed">职责描述...</p>
</div>
```

### 标签
```html
<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
    标签文字
</span>
```

### 时间线
```html
<div class="border-l border-slate-200 pl-4 relative">
    <div class="absolute left-[-0.3rem] top-1 w-2 h-2 bg-blue-500 rounded-full"></div>
    <span class="text-[10px] font-mono text-slate-400 block mb-0.5">2023.01</span>
    <h4 class="text-xs font-bold text-slate-800 mb-1">里程碑标题</h4>
    <p class="text-[10px] text-slate-500">描述内容</p>
</div>
```

### 联系方式图标
```html
<span class="flex items-center gap-1.5 text-xs text-slate-500">
    <i class="fas fa-envelope text-slate-400"></i> email@example.com
</span>
<span class="flex items-center gap-1.5 text-xs text-slate-500">
    <i class="fas fa-phone text-slate-400"></i> 138-0000-0000
</span>
<span class="flex items-center gap-1.5 text-xs text-slate-500">
    <i class="fab fa-github text-slate-400"></i> github.com/username
</span>
<span class="flex items-center gap-1.5 text-xs text-slate-500">
    <i class="fas fa-map-marker-alt text-slate-400"></i> 北京
</span>
```

## 内容撰写指南

### 工作经历描述
- 使用动词开头：负责、主导、设计、开发、优化、推动
- 量化成果：提升 XX%、节省 XX 小时、服务 XX 用户
- 突出技术栈和方法论
- 每条描述控制在 1-2 行

### 项目描述
- 一句话说明项目是什么
- 你的角色和贡献
- 使用的技术栈
- 可量化的成果

### 技能标签
- 按类别分组：编程语言、框架、工具、软技能
- 突出与目标职位相关的技能
- 避免过于基础的技能（如 Office）

## 响应式考虑

简历主要用于打印/PDF，但在浏览器预览时：
- 使用 `margin: 30px auto` 居中显示
- 添加 `box-shadow` 增加层次感
- 背景色 `#f8fafc` 与白色页面形成对比
