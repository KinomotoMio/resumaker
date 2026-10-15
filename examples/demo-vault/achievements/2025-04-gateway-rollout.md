---
id: 2025-04-gateway-rollout
title: 网关灰度发布与回滚规范
period: 2025-03 ~ 2025-04
experience: 2024-07-acme
project: realtime-gateway
role: 牵头
skills: [灰度发布, Kubernetes]
tags: [leadership, reliability]
metrics:
  - text: 联合 3 个业务组完成全量迁移，零 P1 事故
    source: 迁移复盘文档
    verified: true
confidentiality: internal
status: confirmed
---

## 做了什么
写灰度和回滚 checklist，和 3 个业务组对齐迁移窗口，逐组切流。

## 结果
3 个业务组全量迁移完成，迁移期间零 P1 事故。

## 讲法
- **lead**：跨组推动、风险控制
