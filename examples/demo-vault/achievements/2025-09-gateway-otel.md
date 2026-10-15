---
id: 2025-09-gateway-otel
title: 网关接入 OpenTelemetry 全链路追踪
period: 2025-08 ~ 2025-09
experience: 2024-07-acme
project: realtime-gateway
role: 推动与实现
skills: [OpenTelemetry, Jaeger, Go]
tags: [observability]
metrics:
  - text: 线上问题平均定位时间从小时级缩短到 15 分钟内
    source: 值班复盘记录
    verified: true
confidentiality: internal
status: confirmed
---

## 做了什么
在网关和下游三个服务里接入 OTel，统一 trace id 透传到日志。

## 结果
线上问题平均定位时间从小时级缩短到 15 分钟内。

## 讲法
- **infra**：可观测性建设
