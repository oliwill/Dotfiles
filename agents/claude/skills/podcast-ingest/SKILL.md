---
name: podcast-ingest
description: >
  自动化播客知识库收录流程。从搜索播客、获取 RSS、解析单集，
  到生成 wiki 页面、提取实体、建立 wikilink 交叉引用、同步索引，全自动完成。
  触发场景: "收录XX播客", "ingest XX播客", "把XX播客加入知识库", "拉XX播客最近N期",
  "更新东亚观察局", "加入XX播客的最新一期", "归档XX播客", "生成XX播客的笔记",
  "把XX期播客整理成笔记", "整理XX播客", "导入XX播客到 wiki", "增量更新XX播客",
  "把这期播客记下来", "笔记化XX播客内容", "XX播客做成知识库", "把播客存进 obsidian"。
  适用对象: 中英文播客（小宇宙、Apple Podcasts、喜马拉雅 RSS 源）。需要 ~/podcast-wiki/ vault 已初始化。
---

# Podcast Ingest

自动化播客知识库收录流程：从用户的一句话指令（"收录东亚观察局最近3期"）到生成结构化 wiki 页面、建立交叉引用、更新索引，整套链路自动完成。

**核心设计**：基于 OpenCLI + llm-wiki 的组合，不重复造轮子，复用现有的 `~/podcast-wiki/scripts/fetch_episodes.py` 解析脚本。

---

## Step 1: 环境检测与参数解析

### 检测必需依赖

按顺序检查必需工具，缺一不可：

```bash
!command -v opencli || echo "MISSING: opencli (npm install -g @jackwener/opencli)"
!command -v llm-wiki || echo "MISSING: llm-wiki (npm install -g @jackwener/llm-wiki)"
!command -v python3 || echo "MISSING: python3"
!command -v jq || echo "MISSING: jq (brew install jq)"
!command -v curl || echo "MISSING: curl"
```

### 检测 Wiki Vault

```bash
!test -d ~/podcast-wiki && test -f ~/podcast-wiki/wiki-purpose.md || echo "MISSING: ~/podcast-wiki not initialized. Run 'cd ~/podcast-wiki && llm-wiki init'"
!test -f ~/podcast-wiki/scripts/fetch_episodes.py || echo "MISSING: fetch_episodes.py script. See references/fetch_episodes_template.py"
```

### 解析用户请求

从用户输入提取：

| 参数 | 示例 | 默认 |
|------|------|------|
| 播客名 | "东亚观察局" / "声东击西" | 必需 |
| 期数 | "最近3期" / "最新一期" / "10期" | 5 |
| 模式 | "增量"（只新的）/ "全量"（覆盖） | 增量 |

**Decision Tree**:
- 如果所有依赖齐全 → 进入 Step 2
- 如果 vault 缺失 → 引导用户运行 `cd ~/podcast-wiki && llm-wiki init`
- 如果 fetch_episodes.py 缺失 → 复制 `references/fetch_episodes_template.py` 到 `~/podcast-wiki/scripts/`

---

## Step 2: 搜索并锁定播客

### 已知播客快速通道

如果用户提到的播客已经在 wiki 中（检查 `~/podcast-wiki/wiki/<podcast-name>.md` 是否存在），直接复用历史 RSS URL：

```bash
!grep -h "RSS:" ~/podcast-wiki/wiki/*.md 2>/dev/null
```

### 通过 Apple Podcasts 搜索

```bash
opencli apple-podcasts search "<播客名>"
```

输出示例：
```
- id: 1604745062
  title: 东亚观察局
  author: 番薯剥壳工作室
  episodes: 295
```

### 获取 RSS Feed URL

```bash
curl -s "https://itunes.apple.com/lookup?id=<podcast_id>" | jq -r '.results[0].feedUrl'
```

**Decision Tree**:
- 单一精确匹配 → 直接进入 Step 3
- 多个同名播客 → 用 AskUserQuestion 让用户选择
- 没有匹配 → 询问用户是否提供 RSS URL

### 已知播客对照表（可扩展）

| 播客 | iTunes ID | RSS URL |
|------|-----------|---------|
| 东亚观察局 | 1604745062 | https://www.ximalaya.com/album/37399737.xml |

---

## Step 3: 拉取 RSS 并生成源文件

调用解析脚本，参数为期数：

```bash
python3 ~/podcast-wiki/scripts/fetch_episodes.py <N>
```

**注意**：当前的 fetch_episodes.py 默认只针对东亚观察局的 RSS。对于新播客，需要：

1. 复制脚本：`cp ~/podcast-wiki/scripts/fetch_episodes.py ~/podcast-wiki/scripts/fetch_<podcast>.py`
2. 修改 `RSS_URLS` 常量
3. 运行新脚本

更通用的方案见 `references/fetch_episodes_generic.md`。

### 增量去重

检查已存在的源文件，跳过已收录的期号：

```bash
!ls ~/podcast-wiki/sources/*/EP*.md 2>/dev/null | grep -oE "EP[0-9]+" | sort -u
```

只处理未在列表中的新期号。

---

## Step 4: 生成单集 Wiki 页面

为每期源文件创建对应的 wiki 页面。

### 命名规范

`EP{编号}-{简短标题}.md`，标题取自源文件 frontmatter 的 `title` 字段，去掉编号前缀，限制 8-15 字。

### 必需 Frontmatter

```yaml
---
title: "EP{N}: {简短标题}"
description: "{一句话核心议题}"
episode: {N}
date: {YYYY-MM-DD}
duration: "{HH:MM:SS}"
podcast: "{播客名}"
guests: [...]
host: "{主播名}"
tags: [...]
sources: ["{YYYY-MM-DD}/EP{N}-...md"]
related_topics: [...]
created: {today}
updated: {today}
---
```

### 内容结构（必备 sections）

1. **节目信息** - 日期、时长、主播、嘉宾
2. **核心议题** - 1-2 句话概括本期主旨
3. **内容概要** - 按主题分组的核心观点（不是简单复制时间轴）
4. **时间轴** - 逐项列出（直接来自源文件）
5. **相关页面** - 用 `[[wikilinks]]` 列出关联实体
6. **制作信息** - OP/ED/剪辑等

### Wikilink 策略

为每个**值得追踪的实体**创建 wikilink：
- **人物**：嘉宾、主持人、节目中重点讨论的人物
- **话题**：跨期反复出现的主题
- **节目/作品**：被提及的其他播客、书籍、电影
- **机构/地点**：重要的组织或地理位置

详细规则见 `references/wikilink-strategy.md`。

---

## Step 5: 提取并创建实体页面

### 扫描新增 wikilinks

```bash
cd ~/podcast-wiki && llm-wiki graph 2>&1 | grep -A 100 "Wanted Pages"
```

### 创建优先级

按引用次数排序：

| 优先级 | 标准 | 行动 |
|--------|------|------|
| **必创** | 被 ≥3 个页面引用 | 立即创建详细页面 |
| **建议** | 被 2 个页面引用 | 创建简要页面 |
| **暂缓** | 被 1 个页面引用 | 留作"wanted page"等后续 |

### 实体页面模板

详细模板见 `references/entity-page-templates.md`。三种主要类型：
- **人物页面** - role + 简介 + 出场节目 + 关联实体
- **话题页面** - 定义 + 现状/分析 + 相关讨论节目
- **机构/作品页面** - 简介 + 关联人物 + 关联节目

### 关键约束

- **不要**把节目内的所有提及都做成 wikilink，过度拆分会让知识库碎片化
- **必须**给每个实体页面写"Related"章节，至少 3 个交叉引用
- **优先**复用已存在的实体页面（先 grep 检查）

---

## Step 6: 同步索引并汇报

### 更新 wiki-log.md

追加一条 ingest 记录：

```markdown
## [{date}] batch-ingest | {播客名} EP{first}-EP{last}
- created {N} episode pages: EPx, EPy, ...
- created {M} entity pages: 人物1, 话题1, ...
- 总页面: {total}, 总链接: {links}
```

### 同步索引

```bash
cd ~/podcast-wiki && llm-wiki sync
```

### 健康检查

```bash
cd ~/podcast-wiki && llm-wiki status
```

### 输出格式（必备）

回复用户时使用以下结构：

```markdown
✅ 收录完成: {播客名} {N} 期

## 成果统计
| 指标 | 之前 | 之后 | 增长 |
|------|------|------|------|
| Wiki 页面 | X | Y | +Z |
| 源文件 | X | Y | +Z |
| Wikilinks | X | Y | +Z |

## 新增内容
### 单集页面 ({N} 个)
- [[EPx-...]] - 一句话简介
- ...

### 实体页面 ({M} 个)
- [[人物名]] - 角色
- [[话题名]] - 类型
- ...

## 健康状态
- Broken links: {X}（次要实体，可后续补全）
- Orphan pages: {Y}（新单集，会随更多收录建立反向链接）

## 建议下一步
- A. {建议1}
- B. {建议2}
```

---

## Defaults Table

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 期数 | 5 | 最近 N 期 |
| 模式 | 增量 | 跳过已收录的期号 |
| Vault 路径 | ~/podcast-wiki/ | llm-wiki vault 根目录 |
| 源文件位置 | sources/{YYYY-MM-DD}/ | 当天日期分桶 |
| 实体创建阈值 | ≥2 引用 | 至少被 2 个页面引用才创建 |
| 时间轴最大保留 | 全部 | 不截断 |

---

## Reference Files

- `references/wikilink-strategy.md` — 何时该建 wikilink、何时不建，避免过度拆分
- `references/entity-page-templates.md` — 人物/话题/机构页面的标准模板
- `references/fetch_episodes_generic.md` — 适配新播客 RSS 的通用脚本说明
- `references/known-podcasts.md` — 已收录播客的 ID/RSS 对照表（可扩展）
- `references/fetch_episodes_template.py` — 完整的 RSS 解析脚本模板
