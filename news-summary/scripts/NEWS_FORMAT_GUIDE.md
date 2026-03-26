# 新闻 Markdown 文件组织指南

本文档说明如何组织和编写新闻 Markdown 文件，以便 `news_fetcher.py` 脚本能够正确读取和解析。

## 目录结构

```
/home/news/                    # 新闻根目录
├── general_news_01.md         # 通用新闻（直接放在根目录）
├── general_news_02.md
│
├── tech/                      # tech 关键词目录
│   ├── ai_breakthrough.md
│   ├── new_gpu_released.md
│   └── startup_funding.md
│
├── business/                  # business 关键词目录
│   ├── market_update.md
│   └── earnings_report.md
│
├── world/                     # world 关键词目录
│   ├── international_summit.md
│   └── climate_agreement.md
│
└── science/                   # science 关键词目录
    └── space_discovery.md
```

### 目录规则

| 位置 | 用途 | 读取方式 |
|------|------|----------|
| `/home/news/*.md` | 通用新闻 | `fetch_all()` 会归类到 `general` 分类 |
| `/home/news/{keyword}/*.md` | 关键词新闻 | `fetch_category(keyword)` 或 `fetch_by_keyword(keyword)` |

---

## Markdown 文件格式

### 推荐格式

```markdown
# 新闻标题

这是新闻的摘要部分，通常是一段简短的描述。
脚本会自动提取第一段作为摘要。

## 详细内容

这里是新闻的详细正文内容...

- 要点一
- 要点二
- 要点三

## 相关信息

更多补充信息...
```

### 格式说明

| 元素 | 规则 | 示例 |
|------|------|------|
| **标题** | 第一个 `# ` 一级标题 | `# OpenAI 发布 GPT-5` |
| **摘要** | 标题后的第一段文字 | 第一段内容会被提取为 `summary` |
| **发布时间** | 自动使用文件修改时间 | 格式：`2026-03-26 14:30:00` |
| **来源** | 自动使用所在目录名 | `tech`、`business` 等 |

### 最简格式

如果不需要复杂结构，最简单的格式只需要：

```markdown
# 标题

正文内容写在这里即可。
```

脚本会自动：
- 从 `# 标题` 提取标题
- 从第一段提取摘要
- 使用文件名作为备用标题（如果没有 `#` 标题）

---

## 文件命名规范

### 推荐命名方式

```
yyyy-mm-dd_brief_title.md        # 推荐：日期 + 简短标题
brief_title.md                   # 可接受：简短标题（使用下划线或连字符）
```

### 示例

```
2026-03-26_openai_gpt5.md        ✓ 推荐
ai_breakthrough.md               ✓ 可接受
OpenAI 发布 GPT-5.md             ✗ 避免中文和空格（某些系统可能有问题）
```

---

## 完整示例

### 文件路径
```
/home/news/tech/2026-03-26_quantum_computing.md
```

### 文件内容

```markdown
# 谷歌量子计算机实现新突破

谷歌宣布其量子计算机在特定计算任务上达到了新的里程碑，
比传统超级计算机快了数百万倍。这一成果有望加速药物研发
和材料科学的发展。

## 技术细节

研究团队使用 70 个量子比特完成了复杂的量子模拟实验，
量子纠错技术也得到了显著改进。

## 行业影响

- 加速新药研发进程
- 推动材料科学创新
- 提升人工智能算力

## 专家评论

MIT 量子计算专家表示，这一成果是量子计算商业化的重要一步，
但距离实际应用仍有距离。
```

### 解析结果

```json
{
  "title": "谷歌量子计算机实现新突破",
  "link": "/home/news/tech/2026-03-26_quantum_computing.md",
  "published": "2026-03-26 10:15:00",
  "summary": "谷歌宣布其量子计算机在特定计算任务上达到了新的里程碑，比传统超级计算机快了数百万倍...",
  "content": "# 谷歌量子计算机实现新突破\n\n谷歌宣布...",
  "source": "tech",
  "filename": "2026-03-26_quantum_computing.md"
}
```

---

## 常见问题

### Q: 没有一级标题怎么办？

A: 脚本会使用文件名（不含扩展名）作为标题。

```markdown
这是一个没有标题的文档。
```

标题将显示为：`这是没有标题的文档`（假设文件名为 `这是没有标题的文档.md`）

### Q: 支持哪些文件扩展名？

A: 支持 `.md` 和 `.markdown` 两种扩展名。

### Q: 文章排序规则是什么？

A: 按文件修改时间倒序排列（最新的在前）。

### Q: 如何创建新的关键词分类？

A: 只需在 `/home/news/` 下创建新目录，放入对应的 markdown 文件即可：

```bash
mkdir /home/news/sports
echo "# 体育新闻标题\n\n内容..." > /home/news/sports/sample.md
```

然后就可以通过 `fetch_category("sports")` 获取该分类的新闻。

---

## 快速测试

创建测试文件：

```bash
# 创建测试目录
mkdir -p /home/news/tech

# 创建测试新闻
cat > /home/news/tech/test_news.md << 'EOF'
# 测试新闻标题

这是一条测试新闻的摘要内容。

这里是详细正文。
EOF

# 运行测试
python news_fetcher.py -c tech
```
