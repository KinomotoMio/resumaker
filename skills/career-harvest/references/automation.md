# 定时采集

让 Agent 在后台定期执行一次 career-harvest：处理 hook 排进队列的会话，并扫描最近的会话记录。
产出只有 `inbox/` 里的草稿，不会改动 `achievements/`。

**工作目录一律设为履历库本身。** 这样定时任务自己产生的会话会被自动排除，不会出现"采集自己"的循环。

## 用哪个 Agent 跑

用用户日常在用的那个就行。下面的命令以履历库在 `~/career` 为例。

### Claude Code

```bash
cd ~/career && claude -p "使用 career-harvest skill，处理待采集的会话（含 --scan --since 3d），草稿写入 inbox。" \
  --add-dir ~/.claude/projects --add-dir ~/.codex/sessions --add-dir ~/.gemini/tmp \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash(python3:*)"
```

### Codex

```bash
codex exec -C ~/career --sandbox workspace-write --skip-git-repo-check \
  "使用 career-harvest skill，处理待采集的会话（含 --scan --since 3d），草稿写入 inbox。"
```

### Gemini CLI

```bash
cd ~/career && gemini --approval-mode auto_edit \
  --include-directories ~/.claude/projects,~/.codex/sessions,~/.gemini/tmp \
  -p "使用 career-harvest skill，处理待采集的会话（含 --scan --since 3d），草稿写入 inbox。"
```

> 权限只放开到"读会话记录 + 在履历库里写文件 + 运行 python3"。不要用 yolo 或 bypass 一类的全放开模式。

## 怎么定时

### macOS（launchd）

保存为 `~/Library/LaunchAgents/com.resumaker.harvest.plist`，然后执行 `launchctl load` 加载：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.resumaker.harvest</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>cd ~/career &amp;&amp; claude -p "使用 career-harvest skill，处理待采集的会话（含 --scan --since 3d），草稿写入 inbox。" --add-dir ~/.claude/projects --add-dir ~/.codex/sessions --allowedTools Read Write Edit Glob Grep "Bash(python3:*)"</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardOutPath</key><string>/tmp/resumaker-harvest.log</string>
  <key>StandardErrorPath</key><string>/tmp/resumaker-harvest.log</string>
</dict>
</plist>
```

### Linux（cron）

```cron
30 21 * * * cd ~/career && codex exec -C ~/career --sandbox workspace-write --skip-git-repo-check "使用 career-harvest skill，处理待采集的会话（含 --scan --since 3d），草稿写入 inbox。" >> /tmp/resumaker-harvest.log 2>&1
```

### Agent 自带的定时任务

如果用户的 Agent 支持定时任务或云端例行任务（比如 Claude Code 的 scheduled tasks），直接用它创建一个每天运行的任务，提示词同上。
注意：云端任务读不到本机的会话记录，只适合处理本来就同步在云端的履历库。

## 频率建议

每天一次就够了。重要的不是采集得多及时，而是用户每周花 10 分钟用 `career-review` 过一遍草稿。
