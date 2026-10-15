---
id: 2023-08-kafka-cdc
title: 基于 Kafka 的增量数据同步
period: 2023-07 ~ 2023-08
experience: 2023-06-xinghuo
role: 独立实现
skills: [Kafka, Canal, Go]
tags: [data]
metrics:
  - text: 同步延迟由 10 分钟降至秒级
    source: 导师验收
    verified: true
confidentiality: public
status: confirmed
---

## 做了什么
把定时全量拉取改为基于 binlog → Kafka 的增量订阅。

## 结果
同步延迟由 10 分钟降至秒级。
