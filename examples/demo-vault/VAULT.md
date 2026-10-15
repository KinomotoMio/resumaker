# 履历库说明书（VAULT.md）

这是一个 [Resumaker](https://github.com/KinomotoMio/resumaker) 履历库。
**任何 Agent 在读写这个目录之前，请先读完本文件。** 它定义了目录结构、文件格式和几条不能破的规矩。

## 目录结构

```
.
├── VAULT.md              # 本文件
├── profile.md            # 个人基本信息、教育背景、求职偏好
├── experiences/          # 经历（公司 / 学校 / 组织），容器
├── projects/             # 项目，容器
├── achievements/         # ★ 成果，履历库的最小单位
├── evidence/             # 证据附件：截图、导出数据、报告（可选）
├── inbox/                # 草稿箱：自动采集或快速记录，待确认
├── applications/         # 每份 JD 一个目录：匹配报告、简历、深挖卡
└── .resumaker/           # 工具状态（采集队列、游标），不用手动改
```

文件名统一用 `kebab-case`，时间前缀用 `YYYY-MM`（或 `YYYY-MM-DD`）。

## 成果文件（achievements/*.md）

一件**具体的、有结果的事**一个文件。粒度参考：能在简历里写成一条 bullet，能在面试里讲 3 分钟。

```markdown
---
id: 2025-03-ws-gateway-perf          # 与文件名一致
title: 重构 WebSocket 网关连接模型
period: 2025-02 ~ 2025-03
experience: 2024-07-acme             # 指向 experiences/ 下的文件名（不含 .md）
project: realtime-gateway            # 指向 projects/ 下的文件名，可省略
role: 主导设计与实现                   # 你在其中的角色，诚实写
skills: [Go, WebSocket, epoll, Prometheus]
tags: [performance, infra]
metrics:
  - text: P99 延迟 320ms → 85ms
    source: evidence/2025-03-ws-p99.png
    verified: true
  - text: 单机连接数提升约 3 倍
    source: 压测报告（口述，未存档）
    verified: false
sources:                             # 这件事从哪来的：PR、文档、会话
  - https://github.com/acme/gateway/pull/123
  - session:claude-code:8f3a...
confidentiality: internal            # public | internal | secret
status: confirmed                    # draft | confirmed
---

## 背景
为什么要做，当时的问题是什么。（Situation / Task）

## 做了什么
你具体做了什么，关键决策和取舍。（Action）

## 结果
可量化的结果，以及定性的影响。（Result）

## 讲法
- **infra**：连接模型从每连接一协程改为 epoll + 协程池，内存占用下降……
- **product**：直播间弹幕卡顿投诉下降……
- **lead**：推动三个组联合压测，制定灰度方案……

## 深挖
可能被追问的细节、踩过的坑、没做好的地方、如果重来会怎么做。
```

## 容器文件

**experiences/*.md**

```markdown
---
id: 2024-07-acme
org: Acme 科技
title: 后端工程师
period: 2024-07 ~ 至今
location: 上海
type: fulltime          # fulltime | intern | parttime | education | community
---
一两句话说明团队和职责范围。
```

**projects/*.md**

```markdown
---
id: realtime-gateway
name: 实时消息网关
experience: 2024-07-acme
period: 2024-09 ~ 2025-06
stack: [Go, Redis, Kafka]
links: []
confidentiality: internal
---
项目是什么、规模多大、你在其中的位置。
```

## 草稿箱（inbox/*.md）

格式与成果文件相同，但 `status: draft`，并多一个字段：

```yaml
captured_by: career-harvest     # 或 career-capture / manual
```

草稿只是"可能值得写"的线索。**只有经过用户确认，才能移入 `achievements/` 并改为 `status: confirmed`。**

## 投递目录（applications/<YYYY-MM-DD>-<company>-<role>/）

```
jd.md            # JD 原文 + 来源链接
match.md         # 匹配报告：要求拆解、命中、缺口、建议
resume.yaml      # 简历内容（结构化），每条 bullet 带 from: 指向成果 id
resume.typ       # 排版模板（可针对这次投递微调）
resume.pdf       # 产物
grill.md         # 面试深挖卡
notes.md         # 投递记录、面试反馈、结果
```

## 规矩

1. **不编造。** 简历和深挖卡里的每个事实都必须能追溯到本库中的文件。库里没有的数字，宁可不写。
2. **草稿要确认。** 自动采集的内容只能进 `inbox/`，不能直接写进 `achievements/`。
3. **保密分级要尊重。**
   - `public`：可以原样写进简历。
   - `internal`：写进简历前要脱敏——内部系统名换成通用描述，客户名去掉，未公开数据用相对值。
   - `secret`：只供本人回忆，永远不出现在任何生成物里。
4. **改容器不删成果。** 合并、重命名项目或经历时，同步更新成果文件里的引用。
5. **追加优于覆盖。** 更新成果时补充新信息，不要悄悄删掉旧的数字或来源；确实错了就改，并在 `## 深挖` 里注明。
