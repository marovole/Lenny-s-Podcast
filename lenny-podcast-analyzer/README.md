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

# 本地构建（不包含适配器）
npm run build:site
```

可选参数：
- `RSS_URL`：未传 `--rss` 时的默认 RSS 源
- `RSS_USER_AGENT`：抓取 RSS 的 UA
- `RSS_TIMEOUT`：RSS 请求超时秒数
- `TRANSLATION_MODEL` 或 `--translation-model`：翻译模型
- `TRANSLATION_BATCH_SIZE`：每批翻译段落数量

### Cloudflare Pages 配置
- Root directory: `lenny-podcast-analyzer`
- Build command: `npm run build:pages`
- Output directory: `.vercel/output/static`
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
