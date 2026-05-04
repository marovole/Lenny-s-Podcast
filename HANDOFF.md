# Handoff: Lenny Podcast Analyzer - Ollama Embedding 集成

**日期**: 2025-03-29  
**状态**: 代码就绪，等待 Cloudflare 凭证执行上传

---

## ✅ 已完成

### 1. Ollama 本地 Embedding 支持
- **新增脚本**: `scripts/embed_with_ollama.py`
  - 使用 Ollama API 生成 embeddings
  - 支持 mxbai-embed-large (1024维)
  - 自动补零到 1536 维匹配 Vectorize 索引
  - 批量处理，带进度显示

- **修改文件**:
  - `lib/rag/vectorize.ts` - 添加 Ollama 作为 embedding 提供商
  - `app/api/chat/route.ts` - 支持 Ollama 用于查询 embedding
  - `wrangler.toml` - 添加 OLLAMA_HOST 和 OLLAMA_MODEL 配置

### 2. 文档
- **OLLAMA_SETUP.md** - 完整的 Ollama 配置和使用指南

### 3. 本地环境确认
- ✅ Ollama 已安装并运行
- ✅ mxbai-embed-large 模型已下载 (669MB)
- ✅ segments.jsonl 文件就绪 (50k+ segments, 57MB)

---

## ⏳ 待执行

### 任务: 生成并上传 Embeddings

**命令**:
```bash
cd /Users/marovole/GitHub/LennyPodcastAgent/lenny-podcast-analyzer

export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="your-api-token"
export OLLAMA_MODEL="mxbai-embed-large"

python scripts/embed_with_ollama.py
```

**预计时间**: 30-60 分钟 (50k segments)

**费用**: $0 (完全免费)

---

## 🔑 需要的凭证

| 变量 | 获取方式 | 权限要求 |
|------|----------|----------|
| `CF_ACCOUNT_ID` | https://dash.cloudflare.com → 右侧边栏 | - |
| `CF_API_TOKEN` | https://dash.cloudflare.com/profile/api-tokens | Vectorize Edit, R2 Edit |

**创建 API Token 步骤**:
1. 访问 https://dash.cloudflare.com/profile/api-tokens
2. 点击 "Create Token"
3. 使用模板 "Edit Cloudflare Workers"
4. 或自定义权限:
   - Vectorize:Edit
   - R2:Edit
   - Account:Read

---

## 🚀 下一步操作

### 1. 立即执行 (有凭证后)
```bash
# 设置凭证并运行
export CF_ACCOUNT_ID="xxx"
export CF_API_TOKEN="yyy"
export OLLAMA_MODEL="mxbai-embed-large"

python scripts/embed_with_ollama.py
```

### 2. 验证上传
```bash
# 检查 Vectorize 索引中的向量数量
# 通过 Cloudflare Dashboard → Vectorize → lenny-podcast 索引
```

### 3. 配置 Chat API (可选)
如想用 Ollama 处理查询 embedding，取消 wrangler.toml 中的注释:
```toml
[vars]
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mxbai-embed-large"
```

**注意**: 生产环境建议仍用 OpenRouter (免费 tier)，Ollama 仅用于本地开发。

### 4. 部署
```bash
# 设置 OpenRouter API Key (Chat 用)
npx wrangler secret put OPENROUTER_API_KEY

# 构建并部署
npm run build:pages
npm run deploy:pages
```

---

## 📊 成本对比

| 方案 | Embeddings | Chat | 总成本 |
|------|------------|------|--------|
| **纯 OpenRouter** | $5-10 | 免费 | $5-10 |
| **Ollama + OpenRouter** | **$0** | 免费 | **$0** |
| **纯 Ollama** (本地 LLM) | $0 | $0 | $0 (需硬件) |

**当前选择**: Ollama + OpenRouter = **完全免费**

---

## 🐛 故障排查

### Ollama 连接失败
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 启动服务
ollama serve
```

### 维度不匹配
脚本自动处理，无需干预:
- mxbai-embed-large: 1024维 → 补零到 1536维

### 上传中断
脚本支持断点续传 (基于 segment ID)，重新运行即可跳过已处理的 segments。

---

## 📁 相关文件

```
lenny-podcast-analyzer/
├── scripts/
│   ├── embed_with_ollama.py      # 新增: Ollama embedding 脚本
│   └── embed_and_upsert_local.py # 已有: sentence-transformers 方案
├── lib/rag/
│   └── vectorize.ts              # 修改: 支持 Ollama provider
├── app/api/chat/
│   └── route.ts                  # 修改: Ollama 查询支持
├── wrangler.toml                 # 修改: Ollama 配置选项
└── OLLAMA_SETUP.md               # 新增: 完整文档
```

---

## 🎯 成功标准

- [ ] 50,599 segments 全部上传到 Vectorize
- [ ] Chat API 能返回带引用的回答
- [ ] 总成本 = $0

---

**执行人**: 等待用户提供 CF_ACCOUNT_ID 和 CF_API_TOKEN 后立即执行
