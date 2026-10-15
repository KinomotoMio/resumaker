# AGENTS.md

本仓库是 Resumaker 的源码：一组 Agent Skills，加上方法论文档和示例。

- 所有 skill 放在 `skills/<name>/`，遵循 [Agent Skills 规范](https://agentskills.io/specification)：`name` 必须与目录名一致，`description` 写清楚"做什么 + 什么时候用"。
- `.claude/skills` 和 `.agents/skills` 是指向 `skills/` 的符号链接，不要在里面直接新建文件。
- **每个 skill 必须自包含。** 用 `npx skills add` 安装时只会复制 skill 目录，所以不要引用仓库里 skill 目录以外的路径；要引用就用 GitHub URL。
- 脚本只用 Python 3 标准库。需要解析 YAML 时调用 `typst eval`（参见 `resume-tailor/scripts/trace.py`），不引入第三方依赖。
- 履历库的格式以 `skills/resumaker-init/assets/vault/VAULT.md` 为唯一来源。改格式时，同步检查 `examples/demo-vault/` 和各 skill 的说明。
- 改动模板或渲染脚本后，用示例验证：

  ```bash
  python3 skills/resume-tailor/scripts/trace.py examples/demo-vault/applications/2026-10-14-example-backend --vault examples/demo-vault
  python3 skills/resume-render/scripts/render.py examples/demo-vault/applications/2026-10-14-example-backend
  ```

- Commit 按意图原子化拆分，每个 commit 只做一件事。
