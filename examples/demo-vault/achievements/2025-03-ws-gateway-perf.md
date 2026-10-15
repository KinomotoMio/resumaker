---
id: 2025-03-ws-gateway-perf
title: 重构 WebSocket 网关连接模型
period: 2025-02 ~ 2025-03
experience: 2024-07-acme
project: realtime-gateway
role: 主导设计与实现
skills: [Go, WebSocket, epoll, pprof, Prometheus]
tags: [performance, infra]
metrics:
  - text: P99 延迟 320ms → 85ms
    source: evidence/2025-03-ws-p99.png
    verified: true
  - text: 单机承载连接数提升约 3 倍
    source: 压测报告（口述，未存档）
    verified: false
sources:
  - session:claude-code:8f3a2c1e
confidentiality: internal
status: confirmed
---

## 背景
网关原来是每个连接一个 goroutine 读写，晚高峰百万连接时 goroutine 栈占用约 8GB，GC 停顿让 P99 出现 300ms 以上的毛刺。

## 做了什么
- 用 pprof 和 GC trace 定位到瓶颈在 goroutine 栈和 GC
- 改为 epoll 事件驱动 + 固定大小的 goroutine 池处理消息，连接只占一个 fd 和少量缓冲
- 写了对照压测脚本，灰度 5% → 30% → 100%

## 结果
P99 延迟 320ms → 85ms；单机连接数提升约 3 倍（压测结论，报告没存档）。

## 讲法
- **infra**：连接模型从 goroutine-per-connection 改为 epoll + 协程池，内存和 GC 压力大幅下降
- **product**：晚高峰弹幕卡顿明显减少，主播侧投诉下降

## 深挖
- 为什么不直接用 gnet / netpoll？团队对自研可控性更放心，而且只需要很小的子集
- 坑：协程池满时的背压策略，一开始是直接丢弃，后来改成分级
