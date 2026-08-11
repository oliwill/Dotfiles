# 飞书文档自动读取 Skill

自动检测并读取飞书文档内容，注入到对话上下文中。

## 功能

- 自动检测飞书文档链接（docx、wiki、base）
- 支持普通文档、Wiki 文档、电子表格
- 读取私有文档（需要 OAuth 授权）

## 使用前提

### 首次使用：OAuth 授权

1. 进入项目目录：
```bash
cd E:/Git/ClaudeCode/feishu-doc-bridge
```

2. 启动 OAuth 服务器：
```bash
npx tsx oauth-server.ts
```

3. 浏览器访问 http://localhost:3000

4. 点击「发起授权」，扫码登录飞书

5. 授权完成后，token 会自动保存

### 获取 Wiki Space ID（可选）

如果读取 Wiki 文档，需要 `space_id`：

1. 打开 Wiki 文档
2. 按 **F12** 打开开发者工具
3. **Network** 标签中查找包含 `space_id` 的请求
4. 记录该值

## 使用示例

```
用户：帮我总结这个文档 https://my.feishu.cn/wiki/MX8CwQj6wiTT12k5J70cWRtWnBJ

Claude：已读取 1 个飞书文档：
- 《小红书 benchmark for 星果》（wiki-电子表格）

文档内容已注入到对话上下文中，你可以继续提问。
```

## 配置文件

在 `.env` 文件中保存：

```env
FEISHU_USER_TOKEN=你的user_access_token
FEISHU_SPACE_ID=你的wiki_space_id
```

## 支持的文档类型

| 类型 | URL 格式 | 支持情况 |
|------|----------|----------|
| 普通文档 | `feishu.cn/docx/xxx` | ✅ |
| Wiki 文档 | `feishu.cn/wiki/xxx` | ✅ |
| Wiki 中的表格 | `sheet` | ✅ |
| 多维表格 | `feishu.cn/base/xxx` | ⚠️ 基础支持 |

## 注意事项

1. **Token 有效期**：约 2 小时，过期需重新授权
2. **权限要求**：确保应用已开通 `docx:document`、`wiki:wiki:readonly`、`sheets:spreadsheet:readonly`
3. **内容长度**：自动截断过长内容（默认 30000 字符）

## 故障排查

| 问题 | 解决方法 |
|------|----------|
| Token 过期 | 重新访问 http://localhost:3000 授权 |
| Wiki 404 | 提供 space_id 参数 |
| 权限不足 | 检查飞书开放平台应用权限 |
