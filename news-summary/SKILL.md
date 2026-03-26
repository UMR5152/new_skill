# Daily News Summary (news-summary)

## Description

Automatically fetch and summarize daily news from various sources. This skill helps you stay informed by aggregating top headlines and generating concise summaries.

## Usage

```bash
python scripts/news_fetcher.py [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--category` | News category (tech, business, world, science, health) | all |
| `--count` | Number of articles to summarize | 10 |
| `-l` | List available keyword categories | / |
| `--output` | Output format (text, markdown, json) | markdown |

## Examples

```bash
# Get today's news
python scripts/news_fetcher.py --category all

# Get tech news 
python scripts/news_fetcher.py --category tech

# Get 5 tech news 
python scripts/news_fetcher.py --category tech --count 5

# List available news categories
python scripts/news_fetcher.py -l

# Export summary as JSON
python scripts/news_fetcher.py --output json

```

## Features

- Fetches news from multiple RSS feeds and news APIs
- Groups news by category
- Supports multiple output formats
- Caching to avoid duplicate requests


### Default News Sources

- Technology: TechCrunch, The Verge, Ars Technica, Wired
- Business: Bloomberg, Financial Times, Reuters Business
- World: BBC World, CNN International, Al Jazeera
- Science: Nature, Science Daily, Scientific American
- Health: WHO News, Healthline, Medical News Today

## Requirements

- Python 3.8+

## Workflow

1. Use scripts/news_fetcher.py to fetch RSS feeds from configured sources
2. Parse and extract article metadata
3. Group articles by category
4. Generate summary using AI


