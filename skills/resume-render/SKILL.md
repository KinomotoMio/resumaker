---
name: resume-render
description: 把结构化的简历内容（resume.yaml）用 Typst 排版成高质量 PDF，并自动检查版面——页数、末页留白、中文字体、ATS 文本层——再看渲染图逐轮修正。当用户想导出简历、生成 PDF、预览简历效果、调整简历排版/配色/密度，或 resume-tailor 生成了 resume.yaml 之后使用。
license: MIT
compatibility: 需要 typst（≥0.13）和 Python 3.8+；pdftotext（poppler）可选，用于文本层检查。
---

# Resume Render

**内容和排版分离**：`resume.yaml` 只管写什么，Typst 模板只管长什么样。
排版质量靠的不是一次生成，而是 **渲染 → 看图 → 修正** 的闭环。

## 输入

一个投递目录（通常是 `<vault>/applications/<日期>-<公司>-<岗位>/`），里面有 `resume.yaml`。
结构参考 `assets/example/resume.yaml`：

- `meta`：`lang`（zh/en）、`template`、`accent`（主色）、`density`（compact / normal / airy）、可选 `fonts`、`paper`
- `basics`：`name`、`headline`、`contacts[]`（`text` + 可选 `url`）
- `summary`：可选，一两句
- `sections[]`：`kind` 为 `entries`（经历/项目/教育）、`skills`（标签: 内容）、`list`、`text`
- bullet 写成 `{text, from}`，`from` 是成果 id（溯源用，不会渲染）；`**加粗**` 用于突出数字和关键词

## 渲染

```bash
python3 scripts/render.py <投递目录>
```

第一次运行会把模板复制成 `resume.typ` 放进投递目录——**针对这次投递的排版微调直接改这个副本**，不要改技能里的模板。
加 `--reset-template` 可以重新复制。

脚本输出 JSON 报告：

| 字段 | 含义 |
|---|---|
| `pages` / `last_page_fill` | 页数、最后一页填了多少 |
| `previews` | 每页的 PNG 预览图 |
| `cjk_font` | 实际可用的中文字体；为 null 时中文会变方块 |
| `text_layer` | PDF 文本层能否读出姓名（ATS 可解析性） |
| `hints` | 需要处理的问题 |

找不到 typst 时，报告里会给出各平台的安装命令，转告用户。

## 自检闭环（必须做）

每次渲染后：

1. **读 `hints`**，逐条处理。
2. **打开 `previews` 里的每张图亲眼看**，检查：
   - 有没有一行只剩一两个字的孤行（改写那条 bullet，让它短一点或长一点）
   - 段落、条目之间的间距是否均匀，有没有某个区块显得拥挤或空洞
   - 跨页处是否把一个条目的标题和内容拆开了
   - 加粗是否过多（每条 bullet 最多 1～2 处）
3. 修改 `resume.yaml`（内容）或 `resume.typ`（排版），重新渲染。
4. 最多 3 轮。还有解决不了的问题，如实告诉用户。

调整优先级：**先改内容，再改密度，最后才改模板。** 简历塞不下时，删掉和 JD 最不相关的 bullet，比缩小字号好。

## 页数标准

- 应届 / 3 年以内：**1 页**，填满 85% 以上
- 3～10 年：1～2 页；如果是 2 页，第二页至少用到一半
- 学术 CV：不限

## 换风格

- 改颜色：`meta.accent`（推荐深蓝 `#1F4E79`、墨绿 `#1E5631`、酒红 `#7A1F2B`、石墨 `#333F48`）
- 改疏密：`meta.density`
- 改字体：`meta.fonts`（数组，按顺序回退；拉丁字体放前面，中文字体放后面）
- 新模板：在 `assets/templates/` 加一个 `.typ`，读同样的 `resume.yaml` 结构，并在末尾保留 `<resume-end>` 元数据标记

## 字体

模板按顺序回退：Inter → Helvetica Neue → Arial → Noto Sans CJK SC → 思源黑体 → 苹方 → 冬青黑体 → 微软雅黑……
想要跨机器完全一致的效果，把字体文件放进 `~/.config/resumaker/fonts/`（或用 `RESUMAKER_FONTS` 指定目录），脚本会自动加载。

## 收尾

告诉用户 PDF 的路径，附上预览图，用一两句话说明你做了哪些版面调整。
