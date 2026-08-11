---
name: feishu-doc-bridge
description: 飞书文档自动读取。当用户消息中包含飞书文档链接（feishu.cn/docx、feishu.cn/wiki、电子表格等）时，自动读取文档内容并注入到对话上下文中。支持普通文档、Wiki文档、电子表格。用户需要先完成 OAuth 授权才能读取私有文档。无论用户是否明确要求"读取"文档，只要检测到飞书链接就应主动读取。
compatibility: Requires Node.js with fetch API and user OAuth token
---

# 飞书文档自动读取

这个 skill 用于自动检测和读取飞书文档内容，包括普通文档、Wiki 和电子表格。

## 何时使用

- 用户消息中包含任何 `feishu.cn` 的链接（docx、wiki、base 等）
- 用户提到"飞书文档"、"飞书表格"、"飞书 Wiki"等关键词
- 用户想要总结、分析或提取飞书文档中的信息

## 前置条件

### 1. 用户授权

读取私有文档需要用户授权。首次使用时需要：

1. 启动 OAuth 服务器并完成授权
2. 获取 `user_access_token` 和 `wiki_space_id`

### 2. 检查 Token

在使用前，检查是否已有有效的 token：

```bash
curl http://localhost:3000/token
```

## 工作流程

### 步骤 1: 检测飞书链接

从用户消息中提取所有飞书 URL：

```javascript
// 支持的 URL 格式
feishu.cn/docx/{token}     // 普通文档
feishu.cn/wiki/{token}     // Wiki 文档
feishu.cn/base/{token}     // 多维表格
```

### 步骤 2: 解析文档类型和 Token

```javascript
// URL 解析
- 提取文档/节点 token
- 判断文档类型 (docx/wiki/sheet)
```

### 步骤 3: 读取文档内容

根据文档类型调用相应 API：

| 类型 | API 端点 | 说明 |
|------|----------|------|
| docx | `/docx/v1/documents/{id}/raw_content` | 获取纯文本 |
| wiki | `/wiki/v2/spaces/{space_id}/nodes/{node_token}` | 先获取节点，再根据 obj_type 读取 |
| sheet | `/sheets/v2/spreadsheets/{token}/values/{sheet_id}` | 获取表格数据转为 Markdown |

### 步骤 4: 注入到对话上下文

将文档内容按以下格式注入到用户消息前：

```
---
以下是飞书文档《{title}》的内容：

{content}

---
```

## API 调用示例

### 获取 Wiki 节点

```bash
curl https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes/{node_token} \
  -H "Authorization: Bearer {user_access_token}"
```

响应：
```json
{
  "code": 0,
  "data": {
    "node": {
      "title": "文档标题",
      "obj_type": "sheet|docx|bitable",
      "obj_token": "实际文档ID"
    }
  }
}
```

### 获取电子表格数据

```bash
curl "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values/{sheet_id}!A1:Z1000" \
  -H "Authorization: Bearer {user_access_token}"
```

### 获取文档纯文本

```bash
curl https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/raw_content \
  -H "Authorization: Bearer {user_access_token}"
```

## 错误处理

| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| 99991672 | 权限不足 | 检查应用权限，完成 OAuth 授权 |
| 1770002 | not found | 检查 token 是否正确，Wiki 需要提供 space_id |
| 99991679 | 未授权用户操作 | 重新授权，添加所需权限 |

## 配置参数

在 `.env` 文件中保存：

```env
FEISHU_USER_TOKEN=用户访问令牌
FEISHU_SPACE_ID=Wiki空间ID（可选）
FEISHU_APP_ID=应用ID
FEISHU_APP_SECRET=应用密钥
```

## 输出格式

读取完成后，告诉用户：

```
已读取 {N} 个飞书文档：
- 《{title1}》（{type1}）
- 《{title2}》（{type2}）

文档内容已注入到对话上下文中，你可以继续提问。
```

## 注意事项

1. **Token 有效期**：`user_access_token` 有效期约 2 小时，过期需重新授权
2. **内容长度限制**：建议截断过长内容（默认 30000 字符）避免超出上下文限制
3. **Wiki 空间**：读取 Wiki 文档需要 `space_id`，可从浏览器 F12 → Network 中获取
4. **权限要求**：确保应用已开通 `docx:document`、`wiki:wiki:readonly`、`sheets:spreadsheet:readonly` 权限

## 快速测试

测试 token 是否有效：

```bash
curl https://open.feishu.cn/open-apis/authen/v1/user_info \
  -H "Authorization: Bearer {user_access_token}"
```

返回用户信息表示 token 有效。
