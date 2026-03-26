#!/usr/bin/env python3
"""
News Fetcher - Reads news from local markdown documents
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class NewsFetcher:
    """Reads and parses news from local markdown files."""

    DEFAULT_NEWS_DIR = "/home/news"

    def __init__(self, news_dir: Optional[str] = None):
        """
        Initialize the news fetcher.

        Args:
            news_dir: Base directory containing news markdown files
        """
        self.news_dir = Path(news_dir or self.DEFAULT_NEWS_DIR)

    def _parse_markdown_file(self, file_path: Path) -> Dict:
        """
        Parse a markdown file and extract article information.

        Args:
            file_path: Path to the markdown file

        Returns:
            Article dictionary with title, content, summary, etc.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first # heading or filename
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem

            # Extract summary from first paragraph or use first 200 chars of content
            # Remove the title first
            content_without_title = re.sub(r'^#\s+.+$', '', content, count=1, flags=re.MULTILINE).strip()
            summary_match = re.search(r'^(.+?)(?:\n\n|\n#|$)', content_without_title, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else content_without_title[:200]

            # Get file modification time as published date
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            published = mod_time.strftime("%Y-%m-%d %H:%M:%S")

            article = {
                "title": title,
                "link": str(file_path),
                "published": published,
                "summary": summary,
                "content": content,
                "source": file_path.parent.name,
                "filename": file_path.name,
            }
            return article

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _get_markdown_files(self, directory: Path) -> List[Path]:
        """
        Get all markdown files from a directory.

        Args:
            directory: Directory to search

        Returns:
            List of Path objects for markdown files
        """
        if not directory.exists():
            print(f"Directory does not exist: {directory}")
            return []

        md_files = list(directory.glob("*.md"))
        # Also check for .markdown extension
        md_files.extend(directory.glob("*.markdown"))
        return sorted(md_files, key=lambda f: f.stat().st_mtime, reverse=True)

    def fetch_by_keyword(self, keyword: str, count: int = 10) -> List[Dict]:
        """
        Fetch news from a keyword-specific directory.

        Args:
            keyword: Keyword subdirectory name (e.g., 'tech', 'business')
            count: Number of articles to return

        Returns:
            List of article dictionaries
        """
        keyword_dir = self.news_dir / keyword
        return self.fetch_from_directory(keyword_dir, count)

    def fetch_from_directory(self, directory: Path, count: int = 10) -> List[Dict]:
        """
        Fetch news from a specific directory.

        Args:
            directory: Directory path to read from
            count: Number of articles to return

        Returns:
            List of article dictionaries
        """
        md_files = self._get_markdown_files(directory)
        articles = []

        for md_file in md_files[:count]:
            article = self._parse_markdown_file(md_file)
            if article:
                articles.append(article)

        return articles

    def fetch_category(self, category: str, count: int = 10) -> List[Dict]:
        """
        Fetch news from a specific category (keyword directory).

        Args:
            category: News category (used as subdirectory name)
            count: Number of articles to return

        Returns:
            List of article dictionaries
        """
        return self.fetch_by_keyword(category, count)

    def fetch_all(self, count_per_category: int = 5) -> Dict[str, List[Dict]]:
        """
        Fetch news from all subdirectories in the base news directory.

        Args:
            count_per_category: Number of articles per category

        Returns:
            Dictionary of categories to article lists
        """
        result = {}

        if not self.news_dir.exists():
            print(f"News directory does not exist: {self.news_dir}")
            return result

        # Get all subdirectories (keywords)
        subdirs = [d for d in self.news_dir.iterdir() if d.is_dir()]

        for subdir in subdirs:
            category_name = subdir.name
            articles = self.fetch_from_directory(subdir, count_per_category)
            if articles:
                result[category_name] = articles

        # Also check for files in the root news directory
        root_articles = self.fetch_from_directory(self.news_dir, count_per_category)
        if root_articles:
            result["general"] = root_articles

        return result

    def list_available_keywords(self) -> List[str]:
        """
        List all available keyword directories.

        Returns:
            List of keyword names
        """
        if not self.news_dir.exists():
            return []

        subdirs = [d.name for d in self.news_dir.iterdir() if d.is_dir()]
        return sorted(subdirs)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Read news from local markdown files")
    parser.add_argument(
        "--category", "-c",
        default="all",
        help="News category/keyword to fetch (subdirectory name)"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="Number of articles to fetch"
    )
    parser.add_argument(
        "--output", "-o",
        default="markdown",
        choices=["text", "markdown", "json"],
        help="Output format"
    )
    parser.add_argument(
        "--news-dir",
        default="/home/news",
        help="Base directory containing news markdown files"
    )
    parser.add_argument(
        "--list-keywords", "-l",
        action="store_true",
        help="List available keyword directories"
    )

    args = parser.parse_args()

    fetcher = NewsFetcher(news_dir=args.news_dir)

    if args.list_keywords:
        keywords = fetcher.list_available_keywords()
        print("Available keywords/categories:")
        for kw in keywords:
            print(f"  - {kw}")
        return

    if args.category == "all":
        news = fetcher.fetch_all(args.count)
    else:
        news = {args.category: fetcher.fetch_category(args.category, args.count)}

    if args.output == "json":
        print(json.dumps(news, ensure_ascii=False, indent=2))
    else:
        for category, articles in news.items():
            print(f"\n## {category.upper()}\n")
            for article in articles:
                if args.output == "markdown":
                    print(f"- [{article['title']}]({article['link']})")
                    print(f"  _{article['source']} - {article['published']}_\n")
                else:
                    print(f"- {article['title']} ({article['source']})")


if __name__ == "__main__":
    main()
