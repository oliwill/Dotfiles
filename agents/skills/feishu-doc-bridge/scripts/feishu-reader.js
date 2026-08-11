#!/usr/bin/env node
/**
 * 飞书文档读取脚本
 *
 * 用法: node feishu-reader.js <url> [space_id]
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// 从 .env 读取配置
function loadConfig() {
  const envPath = join(__dirname, '../../.env');
  if (!existsSync(envPath)) {
    // 尝试从项目根目录读取
    const rootEnvPath = join(process.cwd(), 'feishu-doc-bridge', '.env');
    if (existsSync(rootEnvPath)) {
      const content = readFileSync(rootEnvPath, 'utf-8');
      return parseEnv(content);
    }
    throw new Error('找不到 .env 文件，请先配置');
  }
  const content = readFileSync(envPath, 'utf-8');
  return parseEnv(content);
}

function parseEnv(content) {
  const config = {};
  for (const line of content.split('\n')) {
    const [key, ...valueParts] = line.split('=');
    if (key && !key.startsWith('#')) {
      config[key.trim()] = valueParts.join('=').trim();
    }
  }
  return config;
}

// URL 解析
function parseFeishuURL(url) {
  const patterns = [
    { type: 'docx', pattern: /feishu\.cn\/docx\/([a-zA-Z0-9_-]+)/ },
    { type: 'wiki', pattern: /feishu\.cn\/wiki\/([a-zA-Z0-9_-]+)/ },
    { type: 'bitable', pattern: /feishu\.cn\/base\/([a-zA-Z0-9_-]+)/ },
  ];

  for (const { type, pattern } of patterns) {
    const match = url.match(pattern);
    if (match) {
      return { type, token: match[1] };
    }
  }

  // 尝试从路径中提取
  try {
    const urlObj = new URL(url);
    const parts = urlObj.pathname.split('/').filter(Boolean);
    if (parts.length >= 2) {
      const possibleToken = parts[parts.length - 1];
      if (/^[a-zA-Z0-9_-]{10,}$/.test(possibleToken)) {
        return { type: 'unknown', token: possibleToken };
      }
    }
  } catch {}

  return null;
}

// API 请求
async function apiRequest(url, token) {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(`API Error (${data.code}): ${data.msg}`);
  }

  return data.data;
}

// 读取 Wiki 文档
async function readWiki(token, spaceId, userToken) {
  // 1. 获取 Wiki 节点
  let node;

  if (spaceId) {
    node = await apiRequest(
      `https://open.feishu.cn/open-apis/wiki/v2/spaces/${spaceId}/nodes/${token}`,
      userToken
    );
    node = node.node;
  } else {
    // 尝试搜索（需要额外权限）
    try {
      const searchResult = await apiRequest(
        'https://open.feishu.cn/open-apis/wiki/v2/spaces/search',
        userToken
      );
      // 这里需要处理搜索结果...
    } catch (e) {
      throw new Error('Wiki 文档需要 space_id 参数');
    }
  }

  if (!node) {
    throw new Error('无法找到 Wiki 节点');
  }

  // 2. 根据对象类型读取
  if (node.obj_type === 'docx' || node.obj_type === 'doc') {
    const content = await apiRequest(
      `https://open.feishu.cn/open-apis/docx/v1/documents/${node.obj_token}/raw_content`,
      userToken
    );
    return {
      title: node.title,
      content: content.content,
      type: 'wiki',
    };
  }

  if (node.obj_type === 'sheet') {
    // 获取 sheets
    const sheetsData = await apiRequest(
      `https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/${node.obj_token}/sheets/query`,
      userToken
    );

    if (!sheetsData.sheets || sheetsData.sheets.length === 0) {
      throw new Error('表格为空');
    }

    const sheet = sheetsData.sheets[0];
    const sheetData = await apiRequest(
      `https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/${node.obj_token}/values/${sheet.sheet_id}!A1:Z1000`,
      userToken
    );

    const content = sheetData.valueRange?.values || [];
    return {
      title: node.title || sheet.title,
      content: sheetToMarkdown(content),
      type: 'wiki',
    };
  }

  throw new Error(`不支持的 Wiki 对象类型: ${node.obj_type}`);
}

// 读取普通文档
async function readDocx(token, userToken) {
  const content = await apiRequest(
    `https://open.feishu.cn/open-apis/docx/v1/documents/${token}/raw_content`,
    userToken
  );

  // 同时获取标题
  let title = '文档';
  try {
    const meta = await apiRequest(
      `https://open.feishu.cn/open-apis/docx/v1/documents/${token}`,
      userToken
    );
    title = meta.title || title;
  } catch {}

  return {
    title,
    content: content.content,
    type: 'docx',
  };
}

// 表格转 Markdown
function sheetToMarkdown(rows) {
  if (!rows || rows.length === 0) return '(空表格)';

  const nonEmptyRows = rows.filter(row =>
    row && row.some(cell => cell !== null && cell !== undefined && cell !== '')
  );

  if (nonEmptyRows.length === 0) return '(空表格)';

  const lines = [];

  // 表头
  const header = nonEmptyRows[0].map(cell => String(cell ?? '').trim()).join(' | ');
  lines.push(`| ${header} |`);

  // 分隔线
  const separator = nonEmptyRows[0].map(() => '---').join(' | ');
  lines.push(`| ${separator} |`);

  // 数据行
  for (let i = 1; i < nonEmptyRows.length; i++) {
    const row = nonEmptyRows[i]
      .map(cell => String(cell ?? '').trim())
      .join(' | ');
    lines.push(`| ${row} |`);
  }

  return lines.join('\n');
}

// 主函数
async function main() {
  const url = process.argv[2];
  const spaceId = process.argv[3];

  if (!url) {
    console.log('用法: node feishu-reader.js <feishu_url> [space_id]');
    console.log('');
    console.log('示例:');
    console.log('  node feishu-reader.js https://my.feishu.cn/wiki/xxx 7527896412906979329');
    console.log('  node feishu-reader.js https://xxx.feishu.cn/docx/yyy');
    process.exit(1);
  }

  console.log(`读取飞书文档: ${url}\n`);

  // 加载配置
  const config = loadConfig();
  const userToken = config.FEISHU_USER_TOKEN || config.userAccessToken;

  if (!userToken) {
    console.error('错误: 未找到 FEISHU_USER_TOKEN，请先完成 OAuth 授权');
    console.log('');
    console.log('获取 token:');
    console.log('1. cd feishu-doc-bridge && npx tsx oauth-server.ts');
    console.log('2. 访问 http://localhost:3000 完成授权');
    console.log('3. 将 user_access_token 添加到 .env 文件');
    process.exit(1);
  }

  // 解析 URL
  const parsed = parseFeishuURL(url);
  if (!parsed) {
    console.error('错误: 无法解析飞书文档 URL');
    process.exit(1);
  }

  console.log(`文档类型: ${parsed.type}`);
  console.log(`文档 Token: ${parsed.token}\n`);

  let result;

  try {
    if (parsed.type === 'wiki') {
      result = await readWiki(parsed.token, spaceId, userToken);
    } else if (parsed.type === 'docx') {
      result = await readDocx(parsed.token, userToken);
    } else {
      console.error('不支持的文档类型:', parsed.type);
      process.exit(1);
    }

    // 输出结果
    console.log('=== 文档信息 ===');
    console.log(`标题: ${result.title}`);
    console.log(`类型: ${result.type}`);
    console.log(`\n=== 文档内容 ===\n`);
    console.log(result.content);

    // 同时保存到文件
    const outputFile = join(__dirname, '../../output/feishu-doc-output.txt');
    writeFileSync(outputFile, `# ${result.title}\n\n${result.content}`, 'utf-8');
    console.log(`\n\n内容已保存到: ${outputFile}`);

  } catch (error) {
    console.error('读取失败:', error.message);
    console.log('');
    console.log('常见问题:');
    console.log('- Token 过期: 重新访问 http://localhost:3000 授权');
    console.log('- Wiki 需要空间ID: 提供 space_id 参数');
    console.log('- 权限不足: 检查应用权限设置');
    process.exit(1);
  }
}

main();
