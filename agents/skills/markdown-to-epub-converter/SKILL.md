---
name: markdown-to-epub-converter
description: Convert markdown documents and chat summaries into formatted EPUB ebook files that can be read on any device or uploaded to Kindle.
---

# Markdown to EPUB Converter Skill

This skill transforms markdown documents into professional EPUB ebook files. Perfect for converting research documents, blog posts, articles, or chat conversation summaries into portable, device-agnostic ebook formats.

## Overview

The skill accepts markdown content in multiple formats and generates a properly formatted EPUB3 file that works across all major ebook readers including:
- Apple Books
- Amazon Kindle (via Kindle for Mac/Windows/iOS/Android)
- Google Play Books
- Kobo and other EPUB readers
- Any standard EPUB reader

## Input Formats

### Option 1: Raw Markdown Text
Provide markdown content directly in your message:

```
Convert this markdown to EPUB:
# My Book Title
## Chapter 1
This is chapter one content...
```

### Option 2: File Path
Provide a path to a markdown file to be converted.

## How It Works

1. **Markdown Parsing**: Analyzes your markdown and automatically:
   - Treats H1 headers (`#`) as chapter boundaries
   - Treats H2 headers (`##`) as section headings within chapters
   - Preserves formatting (bold, italic, links, lists, code blocks)

2. **Structure Generation**: Creates proper EPUB structure:
   - Automatic table of contents from chapters
   - Navigation document (EPUB3 standard)
   - Metadata (title, language, etc.)

3. **File Creation**: Generates a valid EPUB3 file ready for download and use

## Usage Examples

### Example 1: Convert a Blog Post
"Convert this markdown blog post to EPUB:
# How to Build a Simple Web Server
## Introduction
...content..."

### Example 2: Convert a Research Summary
"I have research notes in markdown format. Convert them to an EPUB ebook. The content is:
# Research Project: Machine Learning Basics
## Chapter 1: Fundamentals
..."

### Example 3: Convert a Chat Summary
"Summarize our conversation so far as markdown and convert it to an EPUB for reference"

## Output

The skill generates a downloadable EPUB file that includes:
- Professional formatting
- Automatic table of contents
- Proper chapter structure
- Support for markdown formatting elements

## Markdown Elements Supported

| Element | Markdown | Support |
|---------|----------|---------|
| Headers | `# H1` through `###### H6` | Full |
| Bold | `**text**` | Full |
| Italic | `*text*` | Full |
| Links | `[text](url)` | Full |
| Lists | `- item` or `1. item` | Full |
| Code blocks | ` ```language ` | Enhanced |
| Tables | Markdown tables | Enhanced |
| Blockquotes | `> quote` | Full |

## Technical Details

- **Format**: EPUB3 (compatible with all modern readers)
- **Encoding**: UTF-8
- **HTML Version**: XHTML 1.1
- **CSS Support**: Responsive styling
