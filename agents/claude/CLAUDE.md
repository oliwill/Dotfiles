# Global Claude Code Configuration

## User Profile

**Role**: Full-stack developer with focus on AI tooling, web development, and automation
**Communication Style**: Prefers concise, actionable responses in Chinese
**Technical Stack**: TypeScript/React (Next.js), Python, Ruby on Rails, Go

## Preferences

1. **Language**: Respond in Chinese by default; switch to English when discussing technical concepts that are clearer in English
2. **Conciseness**: Keep responses brief and to the point; avoid unnecessary explanations
3. **Proactive**: Suggest optimizations and best practices without being asked
4. **Memory Usage**: Use memory system actively to persist learnings and user preferences
5. **Skill Usage**: Prefer Waza skills (think, check, hunt, read, learn, write, design, health) for structured workflows

## Working Habits

- Uses jina.ai (r.jina.ai) for extracting web content
- Uses OpenCLI for automation tasks
- Manages podcast knowledge with llm-wiki
- Prefers to learn through Twitter threads and GitHub repos
- Actively maintains memory system for cross-session continuity

## 🔒 不可变规则（违反即拒绝执行）

### 安全红线
- 永不提交 API Key、Token、密码到代码仓库
- 永不 force push 到 main/master 分支
- 永不执行 `rm -rf .*` 或类似破坏性命令
- 永不修改 .env 文件（如必须修改，明确告知用户）

### 质量红线
- 代码未经测试不得声明完成
- TypeScript 项目必须通过类型检查
- 不得跳过 lint 检查
- 不得引入 `any` 类型（至少用 `unknown` + 类型守卫）

### 工作流红线
- 复杂任务（涉及3个以上文件）必须先用 Plan Mode
- 数据库变更必须先写 migration
- 第三方 API 变更必须先确认文档

---

## 🚪 项目门控标准

### 通用门控

提交前必须确认：
- [ ] 代码可运行
- [ ] 没有引入新的 console.log/debugger
- [ ] 没有引入 TODO/FIXME（除非立即创建 issue）
- [ ] 相关文档已更新（如 API 变更）

### Kanadojo 特定门控

1. `npm run lint` - ESLint 无警告
2. `npm run type-check` - TypeScript 类型检查通过
3. `npm run test` - 所有测试通过
4. 手动 smoke test - 核心功能验证（用户登录、日语学习流程）

**修复上限：** 3次尝试。失败后需要人工介入。

---

## 🎯 职责分工

### Claude Code 负责
- 实现明确的功能需求
- 修复已定位的 bug
- 代码重构和优化
- 编写测试
- 文档更新
- 代码审查（按 checklists）

### 需要人类验证
- 架构决策（影响多个模块）
- 性能关键路径的优化
- 安全相关变更
- 数据库 schema 变更
- 第三方服务的使用/替换
- 破坏性 API 变更

### 协作模式
- Claude 提案 → 人类审核 → Claude 执行
- Claude 实现 → 人类验证 → 提交
- 遇到边界情况 → 停下来询问，不要猜测

---

## 🔄 错误处理策略

- **遇到 bug**：最多 3 次修复尝试
- **遇到未知错误**：先用 hunt skill 排查，不要盲目改代码
- **测试失败**：先分析失败原因，再修复，不要反复试错
- **修复上限**：单个问题最多尝试 3 次。超过后停下来报告卡点

---

## 📝 Memory 准入标准

只在以下情况创建新记忆：
- ✅ 改变了你对某个工具/框架的理解
- ✅ 发现了会导致重复错误的知识盲区
- ✅ 跨项目可复用的经验
- ✅ 失败教训及避免方法
- ❌ 临时状态、一次性信息
- ❌ 可以从代码/Git 历史获取的事实
- ❌ 纯粹的代码细节

### 失败复盘模板

```markdown
## 失败复盘

**问题**：发生了什么
**原因**：为什么发生（技术原因/认知盲区）
**解决**：怎么修好的
**预防**：以后如何避免
```

---

## ⏱️ 上下文管理策略

- 一件事做完就 `/clear`（保留 CLAUDE.md）
- 对话变长时 `/compact 专注于当前正在做的任务`
- 用子 Agent 处理噪声任务（跑测试、搜代码）
- 复杂任务分多次会话完成，每次关注一个目标

---

## 🎭 设计哲学

> "约束像重力——你以为它在拉你，其实它让你站得住。"
> — Yoyo (自进化 Rust Agent)

**核心理念：**
- 规则不是束缚，是信任的基础
- 明确的边界让 AI 更可靠
- 失败的透明度与成功一样重要
- 知道什么该 AI 做，什么该人类验证

---

## Fixed Rules（原有）

1. **Security**: Never commit API keys or tokens; always use .env or settings.local.json
2. **Git Safety**: Never force push to main; always create new commits instead of amending
3. **Code Quality**: Always run tests before declaring a task complete
4. **Documentation**: Update memory files after learning new concepts

## Project Structure

This is a user home directory containing multiple independent projects (all under `~/`):
- `~/kanadojo` - Next.js 15 Japanese learning app
- `~/clash-ip-checker` - Python proxy utility
- `~/rsswil` - Ruby on Rails RSS service
- `~/donut` - C/Go binary obfuscation tool

When working here, first identify which project you're working in before making changes.
