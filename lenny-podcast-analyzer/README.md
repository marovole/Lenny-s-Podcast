# Lenny's Podcast Analyzer

从320期 Lenny's Podcast 播客转录中提取、组织、可视化高价值洞察的交互式工具。

## 快速开始

### 1. 安装依赖

```bash
cd lenny-podcast-analyzer
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenRouter API Key
```

获取 API Key: https://openrouter.ai/

推荐模型（按价格）：
- 免费: `deepseek/deepseek-r1:free`
- 免费: `mistralai/devstral-2512:free`
- 便宜: `anthropic/claude-3-haiku`
- 高质: `anthropic/claude-3-5-sonnet`

### 3. 处理数据

```bash
# 解析所有转录文件
python src/processor.py

# 构建向量索引
python src/search.py
```

### 4. 提取洞察（可选，需要 LLM）

```bash
python src/insights.py
```

### 5. 运行应用

```bash
streamlit run app.py
```

## 功能

| 功能 | 描述 |
|------|------|
| 🔍 语义搜索 | 用自然语言搜索播客内容 |
| 📚 主题浏览 | 按产品、增长、领导力等主题浏览 |
| 📕 Failure Playbook | 系统学习失败案例 |
| 🧠 框架库 | 收藏专家决策框架 |
| 📝 面试题库 | 按岗位查找面试问题 |
| 👥 嘉宾列表 | 查看嘉宾出现频率 |

## 公共多语言站点（Next.js）

```bash
# 安装依赖
npm install

# 生成站点数据（可选 RSS、翻译）
python3 src/site_data.py --rss <rss-url-or-path>

# Cloudflare Pages 构建（推荐）
npm run build:pages

# 部署到 Cloudflare Pages（避免重新打包 _worker.js）
npm run deploy:pages

# 本地构建（不包含适配器）
npm run build:site
```

可选参数：
- `RSS_URL`：未传 `--rss` 时的默认 RSS 源
- `RSS_USER_AGENT`：抓取 RSS 的 UA
- `RSS_TIMEOUT`：RSS 请求超时秒数
- `TRANSLATION_MODEL` 或 `--translation-model`：翻译模型
- `TRANSLATION_BATCH_SIZE`：每批翻译段落数量
- `SEARCH_INDEX_LOCALES`：生成搜索索引的语言（默认 `en`，用于控制 Pages 文件大小）
- `SEARCH_MAX_DOCUMENTS`：搜索索引最大条数（默认 20000）
- `SEARCH_CONTENT_MAX_CHARS`：搜索片段最大字符数（默认 280）

### R2 全文上传（Chat 引用必需）

Chat API 从 R2 桶 `lenny-segments` 按 `metadata.content_key` 取 segment 原文；桶为空时引用卡片会被过滤。

```bash
# 1. 生成 segments.jsonl
python3 scripts/normalize_segments.py

# 2. 配置 R2 S3 API 凭证（Cloudflare Dashboard → R2 → Manage R2 API Tokens）
export CF_ACCOUNT_ID="your-account-id"
export R2_ACCESS_KEY_ID="your-access-key-id"
export R2_SECRET_ACCESS_KEY="your-secret-access-key"

# 3. 批量上传（boto3 并发，约 5 万对象）
pip install boto3
python3 scripts/upload_segments_to_r2.py
```

验收：R2 桶 `lenny-segments` 对象数 ≈ 50,599；线上 Chat 引用卡片能展示原文片段。

### Cloudflare Pages 配置
- Root directory: `lenny-podcast-analyzer`
- Build command: `npm run build:pages`
- Output directory: `.vercel/output/static`
- CLI 部署请使用 `npm run deploy:pages`（包含 `--no-bundle`）
- 环境变量（至少设置 `RSS_URL`）

## 项目结构

```
lenny-podcast-analyzer/
├── app.py                    # Streamlit 界面
├── requirements.txt          # 依赖
├── .env                      # API Key 配置
├── data/
│   ├── raw/                  # 原始 txt 文件
│   ├── processed/            # 解析后的 JSON
│   ├── insights/             # LLM 提取的洞察
│   └── search/               # FAISS 索引
└── src/
    ├── processor.py          # 数据解析
    ├── insights.py           # LLM 洞察提取
    ├── taxonomy.py           # 分类系统
    └── search.py             # 向量搜索
```

## 技术栈

- **前端**: Streamlit
- **LLM**: OpenRouter (支持多种模型)
- **向量搜索**: FAISS + Sentence-Transformers
- **数据格式**: JSON

## 致谢

数据来源: [Lenny's Podcast](https://www.lennysnewsletter.com/podcast)
