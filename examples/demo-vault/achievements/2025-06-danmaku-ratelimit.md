---
id: 2025-06-danmaku-ratelimit
title: 弹幕分级限流与降级
period: 2025-05 ~ 2025-06
experience: 2024-07-acme
project: realtime-gateway
role: 方案设计与实现
skills: [Go, Redis, 令牌桶]
tags: [reliability, infra]
metrics:
  - text: 晚高峰峰值 12 万条/秒下核心房间零丢弃
    source: Grafana 看板
    verified: true
  - text: 弹幕相关投诉下降 60%
    source: 客服月报
    verified: true
confidentiality: internal
status: confirmed
---

## 背景
头部主播开播时弹幕洪峰会拖垮整个网关，所有房间一起卡。

## 做了什么
按房间等级和消息类型分级限流（令牌桶 + Redis 全局配额），超限时先合并、再采样、最后丢弃低优先级消息。

## 结果
晚高峰峰值 12 万条/秒下核心房间零丢弃；弹幕相关投诉下降 60%。

## 讲法
- **infra**：分级限流和多级降级设计
- **product**：保住核心房间体验，投诉下降
