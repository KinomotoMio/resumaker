---
name: career-harvest
description: 从用户和 Agent（Claude Code、Codex、Gemini CLI）的历史会话里，自动发现值得写进履历的工作成果，起草成草稿放进履历库的 inbox 等用户确认。也负责开启/关闭会话结束时的自动采集。当用户说"看看我最近做了什么值得写的""从会话记录里整理成果""harvest""开启自动采集"，或定时任务调用时使用。
license: MIT
compatibility: 需要 Python 3.8+。会话记录读取支持 Claude Code、Codex、Gemini CLI 的本地 transcript。依赖 resumaker 履历库。
---

# Career Harvest

> 你每天都在和 Agent 一起干活，这些会话本身就是最好的履历素材。
> Harvest 只负责**起草**，草稿进 `inbox/`，由用户在 `career-review` 里确认。

这是一个**可选**功能。用户没开启也不影响其他任何 skill。

## 采集流程

### 1. 找到待处理的会话

```bash
python3 scripts/sessions.py pending            # 只看会话结束 hook 排进队列的
python3 scripts/sessions.py pending --scan --since 14d   # 再扫一遍本机各 Agent 的会话记录
```

返回每个会话的 `agent`、`transcript_path`、`first_request`（第一条用户请求）。

### 2. 粗筛（看 `first_request` 就够了）

明显不是"工作成果"的直接标记跳过，不用读全文：

- 闲聊、查资料、问个命令怎么用、翻译
- 个人事务（购物、日程、生活问题）
- 在履历库本身里进行的会话（已自动排除）

```bash
python3 scripts/sessions.py mark <session_id> ... --skip
```

### 3. 细读候选会话

```bash
python3 scripts/sessions.py digest <transcript_path>
```

摘要包含：用户的需求、Agent 的关键回复、改动的文件、git 提交，常见密钥已自动脱敏。

用这个标准判断**值不值得起草**：

- ✅ 有明确的产出：功能上线、bug 修复、性能提升、方案落地、工具交付
- ✅ 有可以量化的结果，或者有值得面试时讲的技术取舍
- ✅ 用户是主导者（提出需求、做决策），Agent 只是帮手
- ❌ 只是探索、半途而废、纯粹的环境配置、琐碎修改

**宁缺毋滥。** 十个会话里起草一两条是正常的。

同一件事经常跨好几个会话（比如周一设计、周三实现、周五上线），要合并成一条草稿，`sources` 里列出所有相关会话。
先看 `inbox/` 和 `achievements/` 里有没有同一件事：有的话，往已有的草稿里追加信息，不要新建。

### 4. 写草稿

按 `<vault>/VAULT.md` 的格式写进 `inbox/<YYYY-MM>-<slug>.md`：

```yaml
status: draft
captured_by: career-harvest
sources:
  - session:claude-code:<session_id>
  - <commit message 或 PR 链接，如果有>
confidentiality: internal     # 工作项目默认 internal；用户的个人开源项目可以 public
```

正文写清楚背景、做了什么、结果。**会话里没有出现的数字不要写**；只有定性结果时，在 `metrics` 里留空，并在正文末尾加一行"待补：结果数据"。
不要把代码片段、内部 URL、客户名或任何凭据写进草稿。

### 5. 标记已处理

```bash
python3 scripts/sessions.py mark <session_id> ...
```

### 6. 回报

一句话就够："看了 N 个会话，起草了 M 条，建议有空时用 `career-review` 确认。"
在定时任务里运行时不需要回报，草稿留在 inbox 等用户下次查看即可。
