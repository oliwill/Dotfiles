# Podcast Ingest Skill

自动化播客知识库收录流程的 skill。基于 OpenCLI + llm-wiki，从用户的一句话指令到生成结构化知识库，全自动完成。

## 触发场景

- "收录东亚观察局最近3期"
- "ingest 声东击西最新一期"
- "把忽左忽右加入知识库"
- "更新东亚观察局"
- "拉东亚观察局最近10期"

## 完整链路

```
用户输入
   ↓
Step 1: 检测环境（opencli / llm-wiki / vault）
   ↓
Step 2: 搜索播客 → 获取 RSS URL
   ↓
Step 3: 解析 RSS → 生成源文件
   ↓
Step 4: 创建单集 wiki 页面
   ↓
Step 5: 提取实体 → 创建实体页面
   ↓
Step 6: 同步索引 → 汇报成果
```

## 依赖

| 工具 | 用途 |
|------|------|
| `opencli` | 搜索播客（apple-podcasts adapter） |
| `llm-wiki` | 知识库管理 |
| `python3` | RSS 解析脚本 |
| `jq` | iTunes Lookup API JSON 解析 |
| `curl` | HTTP 请求 |

## 文件结构

```
podcast-ingest/
├── SKILL.md                                # 主流程
├── README.md                               # 本文件
└── references/
    ├── wikilink-strategy.md                # 何时建/不建 wikilink
    ├── entity-page-templates.md            # 实体页面模板
    ├── fetch_episodes_generic.md           # 适配新播客的指南
    ├── known-podcasts.md                   # 已知播客 ID/RSS 表
    └── fetch_episodes_template.py          # RSS 解析脚本模板
```

## 使用前置

1. **安装依赖**
   ```bash
   npm install -g @jackwener/opencli @jackwener/llm-wiki
   brew install jq
   ```

2. **初始化 vault**
   ```bash
   mkdir -p ~/podcast-wiki && cd ~/podcast-wiki && llm-wiki init
   ```

3. **复制脚本**
   ```bash
   mkdir -p ~/podcast-wiki/scripts
   cp ~/.claude/skills/podcast-ingest/references/fetch_episodes_template.py \
      ~/podcast-wiki/scripts/fetch_episodes.py
   ```

## 测试用例

### 用例 1: 增量更新

```
用户: 更新东亚观察局
预期: 检查最新期号 → 拉取新期 → 生成页面 → 同步
```

### 用例 2: 全新播客

```
用户: 收录"声东击西"最近5期
预期: 搜索播客 → 找到 ID → 获取 RSS → 复制并修改脚本 → 拉取 → 生成
```

### 用例 3: 模糊请求

```
用户: 把这期播客记下来
预期: 询问具体播客和期数 → 进入正常流程
```

## 设计权衡

### 为什么不用 RAG？

llm-wiki 的核心理念是"compile knowledge once, query forever"。把播客内容编译成结构化页面，比每次重新解析原始转录更高效。

### 为什么需要实体页面？

单集页面是"事件"的快照，实体页面是"概念/人物"的累积。两者结合形成知识网络，避免信息孤岛。

### 为什么不全部自动化？

- 实体页面创建需要判断（哪些值得拆出来）
- Wikilink 策略需要权衡（不能滥建断链）
- 这些"判断"任务交给 LLM Agent，比脚本更灵活

## 维护建议

每次成功收录新播客后：

1. 更新 `references/known-podcasts.md` 添加新播客
2. 如果遇到新的 section markers，更新 `fetch_episodes_template.py`
3. 如果发现新的反模式，记录到 `wikilink-strategy.md`
