# 通用 RSS 解析器适配指南

`fetch_episodes.py` 当前是为东亚观察局定制的，要适配新播客需要做哪些修改。

## 当前实现的限制

- `RSS_URLS` 硬编码为东亚观察局
- `SECTION_MARKERS` 是中文播客特定的标记（"聊天的人"、"时间轴"等）
- 输出文件命名以 `EP{编号}` 为前缀，假设节目有数字编号

## 适配新播客的方法

### 方法 1: 复制脚本（最快）

```bash
# 复制脚本
cp ~/podcast-wiki/scripts/fetch_episodes.py ~/podcast-wiki/scripts/fetch_<podcast>.py

# 修改 RSS_URLS
# 修改 SECTION_MARKERS（如果是英文播客）
# 调整输出文件命名规则
```

### 方法 2: 改造为通用脚本（推荐长期）

把 `fetch_episodes.py` 重构为接受 RSS URL 和 podcast 名作为参数：

```python
# 用法:
# python3 fetch_episodes.py <rss_url> <podcast_name> [N=10]

import sys

if len(sys.argv) < 3:
    print("Usage: fetch_episodes.py <rss_url> <podcast_name> [N=10]")
    sys.exit(1)

RSS_URL = sys.argv[1]
PODCAST_NAME = sys.argv[2]
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 10
```

### 方法 3: 配置驱动

创建 `~/podcast-wiki/scripts/podcasts.json`：

```json
{
  "东亚观察局": {
    "rss_url": "https://www.ximalaya.com/album/37399737.xml",
    "section_markers": {
      "聊天的人": "guests",
      "连线的人": "guests",
      "时间轴": "timeline"
    },
    "filename_prefix": "EP"
  },
  "声东击西": {
    "rss_url": "https://...",
    "section_markers": {...},
    "filename_prefix": "EP"
  }
}
```

然后脚本读取配置：

```python
import json
config = json.load(open(Path.home() / "podcast-wiki/scripts/podcasts.json"))
podcast_config = config[sys.argv[1]]
RSS_URL = podcast_config["rss_url"]
```

## 不同播客的常见差异

### 中文播客

通常用以下标记：
- 聊天的人 / 连线的人 / 嘉宾 / 主播 → guests
- 时间轴 / 节目目录 → timeline
- 相关链接 / 推荐阅读 → links
- OP / ED / 剪辑 → credits

### 英文播客

- Hosts / Guests → guests
- Show Notes / Timestamps → timeline
- Links / Resources → links

### 中英混合（如海外华人播客）

需要双语标记，扩展 `SECTION_MARKERS`：

```python
SECTION_MARKERS = {
    # Chinese
    '聊天的人': 'guests',
    '时间轴': 'timeline',
    # English
    'Hosts': 'guests',
    'Guests': 'guests',
    'Timestamps': 'timeline',
    'Show Notes': 'timeline',
}
```

## 时间戳格式差异

不同 RSS 源可能用不同格式：

| 格式 | 示例 | 正则 |
|------|------|------|
| `MM:SS` | `05:30` | `^\d{1,2}:\d{2}` |
| `HH:MM:SS` | `1:30:45` | `^\d{1,2}:\d{2}:\d{2}` |
| `[MM:SS]` | `[05:30]` | `^\[\d{1,2}:\d{2}\]` |
| `(MM:SS)` | `(05:30)` | `^\(\d{1,2}:\d{2}\)` |

当前脚本支持前两种，扩展时修改 `parse_timeline_item` 函数。

## 测试新适配

```bash
# 1. 先用小数量测试
python3 fetch_<podcast>.py 1

# 2. 检查生成的源文件
cat ~/podcast-wiki/sources/$(date +%Y-%m-%d)/*.md

# 3. 验证关键字段：
#    - title 是否完整
#    - guests 是否解析正确
#    - timeline 是否完整且时间格式正确

# 4. 满意后再批量
python3 fetch_<podcast>.py 10
```

## 故障排查

### 问题：timeline items 数量为 0

**原因**：section marker 没有匹配上
**调试**：
```python
# 在 fetch_episodes.py 添加 debug
print(f"DEBUG: detected sections: {list(sections.keys())}")
print(f"DEBUG: timeline count: {len(sections['timeline'])}")
```

### 问题：guests 是一长串

**原因**：guest section 后面没有正确切换到下一个 section
**调试**：检查 RSS 描述中 guest section 之后是什么标记，确保它在 `SECTION_MARKERS` 里

### 问题：文件名包含特殊字符

**原因**：`safe_filename` 函数没有过滤所有特殊字符
**修复**：扩展 `safe_filename` 中的正则，过滤 `/\:*?"<>|` 等
