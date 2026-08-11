# 已知播客对照表

记录已收录或已知 RSS URL 的播客，避免重复搜索。每次成功收录新播客后追加到此表。

## 中文播客

| 播客名 | iTunes ID | RSS URL | 收录时间 |
|--------|-----------|---------|----------|
| 东亚观察局 | 1604745062 | https://www.ximalaya.com/album/37399737.xml | 2026-04-25 |

## 添加新播客的步骤

1. 用 `opencli apple-podcasts search "<播客名>"` 找到 iTunes ID
2. 用 `curl -s "https://itunes.apple.com/lookup?id=<id>" | jq -r '.results[0].feedUrl'` 获取 RSS URL
3. 测试 RSS 可访问性：`curl -sL <rss_url> | head -20`
4. 添加一行到上面的表格
5. 如果 section markers 与默认不同，记录在备注

## 已知播客的特殊配置

### 东亚观察局

- Section markers 标准（聊天的人/连线的人/时间轴）
- 包含嵌套结构（【官宣】+【正片】）
- 时间轴格式：HH:MM:SS 或 MM:SS

## 待收录候选

如果在节目中被反复提及，可以加到这里作为下次收录候选：

- 《[[正文三台]]》 - 韩国相关播客（EP280 提及）
- 《[[现在进行时]]》 - 在日华人播客（EP275 提及）
- 《[[南武线放送]]》 - 在日华人播客（EP275 提及）
- 《[[东京无聊俱乐部]]》 - 在日华人播客（EP275 提及）
- 《[[面红耳赤]]》 - EP275 推荐
- 《[[山手线上睡着了]]》 - EP275 推荐
- 《[[少点套路]]》 - EP275 推荐

## 数据源说明

### Apple Podcasts (iTunes Lookup API)

最权威的播客元数据源，但 RSS feed URL 取决于播客发行平台：

- 喜马拉雅 → `https://www.ximalaya.com/album/<id>.xml`
- 小宇宙 → 需要订阅链接，无公开 RSS
- 苹果原创 → 不提供 RSS（需要 Apple Podcasts API）

### 喜马拉雅 RSS

格式相对统一，时间轴信息丰富，适合解析。

### 小宇宙

通过 web 抓取或第三方工具获取（参考 ../../sources/2026-04-25/dongya-guanchaju 的获取经验）。
