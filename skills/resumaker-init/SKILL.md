---
name: resumaker-init
description: 初始化 Resumaker 个人履历库（career vault）——选择存储方式（项目内忽略 / 独立私有仓库 / 已有目录）、生成目录骨架、可选开启被动采集。当用户第一次使用 Resumaker、说"开始建简历库""初始化履历""我想系统地维护简历素材"，或其它 resumaker skill 找不到履历库时使用。
license: MIT
compatibility: 需要 Python 3.8+；git 可选。适用于任何支持 Agent Skills 的 Agent（Claude Code、Codex、Gemini CLI 等）。
---

# Resumaker Init

为用户建立一个**长期维护的个人履历库**。履历库是 Resumaker 的核心资产——简历只是从它编译出来的产物。
方法论见仓库中的 `docs/methodology.md`；库的格式定义在 `assets/vault/VAULT.md`，初始化时会复制进库里。

## 0. 先检查是否已经有库

```bash
python3 scripts/init_vault.py --show
```

已有 `vault` 时，告诉用户库在哪，问是否要换位置或重新配置；没有就继续。

## 1. 用一句话讲清楚这是什么

不要长篇大论。大致是：

> 我们会建一个"履历库"：每做成一件事记一个小文件，带上数字和出处。
> 以后看到 JD，就从库里挑最对口的内容编译成简历，同时生成面试会被追问的问题。

## 2. 问存储方式

一次问完，给推荐：

| 选项 | 适合谁 | 做法 |
|---|---|---|
| **A. 独立私有仓库（推荐）** | 想长期维护、多台电脑同步 | 默认 `~/career`，`git init`；可选在 GitHub/GitLab 建私有远端，像网盘一样同步 |
| **B. 放在当前项目里，但 git 忽略** | 先试试 / 只在这台机器用 | `./career/`，自动加进当前仓库的 `.gitignore` |
| **C. 指向已有目录** | 已经在用 Obsidian / iCloud / 个人 wiki | 用户给路径，在其中建骨架，不动已有文件 |

对应命令：

```bash
# A
python3 scripts/init_vault.py --path ~/career --git
# B（在用户当前的仓库根目录执行）
python3 scripts/init_vault.py --path ./career --ignore-in .
# C
python3 scripts/init_vault.py --path "<用户给的路径>"
```

脚本只会补齐缺失的骨架文件，不会覆盖已有内容，并把库路径写入 `~/.config/resumaker/config.json`。

**选 A 并且想要远端时**：先确认用户要用哪个平台和仓库名，**明确得到同意后**再创建，并且一定是私有仓库，例如：

```bash
cd ~/career && git add -A && git commit -m "init career vault" && \
  gh repo create <name> --private --source . --push
```

## 3. 填基本信息

打开库里的 `profile.md`，和用户一起填：姓名、联系方式、教育背景、求职方向。
能从用户已有简历里读出来的就直接填，填完给用户看一眼。

## 4. 问是否开启被动采集（可选）

> 你平时用 Claude Code / Codex / Gemini CLI 干活吗？
> 可以让它们在会话结束后，把"可能值得写进简历的事"自动起草到草稿箱，你定期确认就行。

用户愿意的话，转到 `career-harvest` skill 的「开启采集」一节。不愿意就跳过，以后随时可以开。

## 5. 收尾：给下一步

- 有旧简历 / LinkedIn / GitHub / 周报 → 用 `career-capture` 批量导入，这是最快的冷启动方式。
- 什么都没有 → 用 `career-capture` 做一次 15 分钟的访谈，先记 3～5 件最拿得出手的事。

## 履历库定位约定（所有 resumaker skill 通用）

按顺序查找，找到即止：

1. 环境变量 `RESUMAKER_VAULT`
2. `~/.config/resumaker/config.json` 中的 `vault`
3. 当前目录下的 `./career/`（存在 `VAULT.md` 时）

都找不到 → 运行本 skill。
