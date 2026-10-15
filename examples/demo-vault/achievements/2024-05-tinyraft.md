---
id: 2024-05-tinyraft
title: tinyraft：从零实现 Raft
period: 2024-01 ~ 2024-05
role: 个人项目
skills: [Go, Raft, 分布式一致性]
tags: [distributed, oss]
metrics:
  - text: 通过 MIT 6.824 全部测试用例
    source: https://github.com/zhiyuan-lin/tinyraft
    verified: true
  - text: GitHub 420+ Star
    source: https://github.com/zhiyuan-lin/tinyraft
    verified: true
  - text: 修复 2 个网络分区下的日志截断 bug
    source: 仓库 issue
    verified: true
confidentiality: public
status: confirmed
---

## 做了什么
实现选主、日志复制、快照；用 Jepsen 风格的故障注入测试验证线性一致性。

## 结果
通过 MIT 6.824 全部测试用例；GitHub 420+ Star；修复 2 个网络分区下的日志截断 bug。
