---
name: article-extractor
description: Extract clean article content from URLs (blog posts, articles, tutorials) and save as readable text. Use when user wants to download, extract, or save an article/blog post from a URL without ads, navigation, or clutter.
allowed-tools:
  - Bash
  - Write
---

# Article Extractor

This skill extracts the main content from web articles and blog posts, removing navigation, ads, newsletter signups, and other clutter. Saves clean, readable text.

## When to Use This Skill

Activate when the user:
- Provides an article/blog URL and wants the text content
- Asks to "download this article"
- Wants to "extract the content from [URL]"
- Asks to "save this blog post as text"
- Needs clean article text without distractions

## How It Works

### Priority Order:
1. **Check if tools are installed** (reader or trafilatura)
2. **Download and extract article** using best available tool
3. **Clean up the content** (remove extra whitespace, format properly)
4. **Save to file** with article title as filename
5. **Confirm location** and show preview

## Installation Check

Check for article extraction tools in this order:

### Option 1: reader (Recommended - Mozilla's Readability)

```bash
command -v reader
```

If not installed:
```bash
npm install -g @mozilla/readability-cli
# or
npm install -g reader-cli
```

### Option 2: trafilatura (Python-based, very good)

```bash
command -v trafilatura
```

If not installed:
```bash
pip3 install trafilatura
```

### Option 3: Fallback (curl + simple parsing)

If no tools available, use basic curl + text extraction (less reliable but works)

## Extraction Methods

### Method 1: Using reader (Best for most articles)

```bash
# Extract article
reader "URL" > article.txt
```

**Pros:**
- Based on Mozilla's Readability algorithm
- Excellent at removing clutter
- Preserves article structure

### Method 2: Using trafilatura (Best for blogs/news)

```bash
# Extract article
trafilatura --URL "URL" --output-format txt > article.txt

# Or with more options
trafilatura --URL "URL" --output-format txt --no-comments --no-tables > article.txt
```

**Pros:**
- Very accurate extraction
- Good with various site structures
- Handles multiple languages

**Options:**
- `--no-comments`: Skip comment sections
- `--no-tables`: Skip data tables
- `--precision`: Favor precision over recall
- `--recall`: Extract more content (may include some noise)

### Method 3: Fallback (curl + basic parsing)

```bash
# Download and extract basic content
curl -s "URL" | python3 -c "
from html.parser import HTMLParser
import sys

class ArticleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_content = False
        self.content = []
        self.skip_tags = {'script', 'style', 'nav', 'header', 'footer', 'aside'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        if tag not in self.skip_tags:
            if tag in {'p', 'article', 'main', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                self.in_content = True
        self.current_tag = tag

    def handle_data(self, data):
        if self.in_content and data.strip():
            self.content.append(data.strip())

    def get_content(self):
        return '\\n\\n'.join(self.content)

parser = ArticleExtractor()
parser.feed(sys.stdin.read())
print(parser.get_content())
" > article.txt
```

**Note:** This is less reliable but works without dependencies.
