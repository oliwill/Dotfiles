#!/usr/bin/env python3
"""
Fetch and parse Xiaoyuzhou (Ximalaya) RSS feed for 东亚观察局
Generates clean markdown files compatible with llm-wiki ingest

Improvements over v1:
- Properly handles HTML <p> tags (preserves paragraph breaks)
- Correctly extracts sections (聊天的人, 时间轴, etc.)
- Parses timeline with proper HH:MM format
- Cleanly extracts guest information
"""

import sys
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import html as html_lib

RSS_URLS = [
    "https://www.ximalaya.com/album/37399737.xml",
    "http://www.ximalaya.com/album/37399737.xml",
]
OUTPUT_DIR = Path.home() / "podcast-wiki" / "sources"

# Section markers in episode descriptions
SECTION_MARKERS = {
    '聊天的人': 'guests',
    '连线的人': 'guests',
    '出场的人': 'guests',
    '嘉宾': 'guests',
    '主播': 'guests',
    '时间轴': 'timeline',
    '相关链接': 'links',
    '相关阅读': 'links',
    '推荐阅读': 'links',
    'OP': 'op',
    'ED': 'ed',
    'Logo': 'logo',
    '剪辑': 'editor',
    '收听方式': 'listen',
    '出品': 'production',
    '出品・制作': 'production',
    '官宣': 'announcement',
    '正片': 'main',
    '注意': 'notice',
}


def html_to_text(html_content):
    """Convert HTML to clean text, preserving paragraph structure"""
    if not html_content:
        return ""

    text = html_content

    # Step 1: Replace block-level tags with newlines
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'</li>', '\n', text)

    # Step 2: Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Step 3: Decode HTML entities
    text = html_lib.unescape(text)

    # Step 4: Clean up whitespace within lines but preserve newlines
    lines = []
    for line in text.split('\n'):
        cleaned = re.sub(r'[ \t]+', ' ', line).strip()
        if cleaned:
            lines.append(cleaned)

    return '\n'.join(lines)


def parse_section_marker(line):
    """Detect if a line is a section marker like '- 时间轴 -'"""
    # Match patterns like "- 时间轴 -" or "【时间轴】" or "- OP -"
    patterns = [
        r'^-\s*(.+?)\s*-$',
        r'^【(.+?)】$',
        r'^=+\s*(.+?)\s*=+$',
    ]
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            return match.group(1).strip()
    return None


def parse_timeline_item(line):
    """Parse a timeline item like '00:40 内容' or '1:02:00 内容'"""
    # Match HH:MM:SS or HH:MM or MM:SS at start of line
    match = re.match(r'^((?:\d{1,2}:)?\d{1,2}:\d{2})\s*(.+?)$', line)
    if match:
        return {
            'time': match.group(1).strip(),
            'description': match.group(2).strip()
        }
    return None


def parse_description(description_text):
    """Parse cleaned description text into structured sections.

    Strategy: First pass identifies all timeline items globally (anywhere
    in the text), then a second pass categorizes other content into sections.
    This handles episodes with nested sections like 【官宣】 + 【正片】.
    """
    if not description_text:
        return {}

    text = html_to_text(description_text)
    lines = [line for line in text.split('\n') if line.strip()]

    sections = {
        'guests': [],
        'timeline': [],
        'announcement': [],
        'main_content': [],
        'op': '',
        'ed': '',
        'editor': '',
        'production': '',
        'logo': '',
        'other': [],
    }

    # Pass 1: Extract all timeline items globally (anywhere in text)
    # Timeline items have HH:MM or HH:MM:SS at the start
    timeline_indices = set()
    for idx, line in enumerate(lines):
        item = parse_timeline_item(line)
        if item:
            sections['timeline'].append(item)
            timeline_indices.add(idx)

    # Pass 2: Categorize non-timeline lines into sections
    current_section = 'main_content'

    # Special markers that should NOT switch section but mark sub-content
    nested_markers = {'官宣', '正片', '注意'}

    for idx, line in enumerate(lines):
        # Skip lines already classified as timeline
        if idx in timeline_indices:
            continue

        # Check if this is a section marker
        marker = parse_section_marker(line)
        if marker:
            # Check if it's a nested marker that doesn't change section
            if marker in nested_markers:
                # Mark as part of announcement/main content but don't switch
                if marker == '官宣':
                    current_section = 'announcement'
                elif marker == '正片':
                    current_section = 'main_content'
                continue

            section_key = SECTION_MARKERS.get(marker)
            if section_key:
                current_section = section_key
            else:
                current_section = 'other'
            continue

        # Categorize line based on current section
        if current_section == 'guests':
            if line.strip() and not line.startswith('-'):
                sections['guests'].append(line.strip())
        elif current_section in ('op', 'ed', 'editor', 'production', 'logo'):
            if line.strip() and not sections.get(current_section):
                sections[current_section] = line.strip()
        elif current_section == 'announcement':
            sections['announcement'].append(line.strip())
        elif current_section == 'timeline':
            # If we're in timeline section but line isn't a timeline item,
            # it's probably a sub-section header - skip
            pass
        elif current_section == 'main_content':
            sections['main_content'].append(line.strip())
        else:
            sections['other'].append(line.strip())

    return sections


def parse_episode(item):
    """Parse a single episode from RSS item"""
    title = item.find('title')
    title_text = title.text.strip() if title is not None and title.text else 'Untitled'

    # Extract episode number from title (e.g., "281 ..." -> 281)
    ep_match = re.match(r'^(\d+)', title_text)
    episode_num = ep_match.group(1) if ep_match else '000'

    # Extract clean episode title (remove leading number)
    clean_title = re.sub(r'^\d+\s*', '', title_text).strip()

    # Get publication date
    pub_date = item.find('pubDate')
    pub_date_text = pub_date.text.strip() if pub_date is not None and pub_date.text else ''

    # Parse and reformat date
    try:
        from email.utils import parsedate_to_datetime
        date_obj = parsedate_to_datetime(pub_date_text)
        date_iso = date_obj.strftime('%Y-%m-%d')
    except Exception:
        date_iso = pub_date_text[:16]

    # Get description
    description = item.find('description')
    desc_text = description.text if description is not None else ''

    # Get audio URL
    enclosure = item.find('enclosure')
    audio_url = enclosure.get('url') if enclosure is not None else ''

    # Get duration
    duration_elem = item.find('duration')
    duration = duration_elem.text if duration_elem is not None else ''

    # Parse description into structured sections
    sections = parse_description(desc_text)

    return {
        'episode': episode_num,
        'title': title_text,
        'clean_title': clean_title,
        'date': date_iso,
        'audio_url': audio_url,
        'duration': duration,
        'sections': sections,
    }


def safe_filename(text, max_length=50):
    """Generate safe filename from text"""
    # Remove invalid filename characters
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', text)
    # Remove emojis and special chars
    text = re.sub(r'[^\w\s\-一-鿿]', '', text)
    # Compress whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_length]


def generate_markdown(ep):
    """Generate markdown content for a single episode"""
    sections = ep['sections']

    # Build YAML frontmatter
    yaml_lines = [
        '---',
        f'title: "{ep["title"]}"',
        f'podcast: "东亚观察局"',
        f'date: {ep["date"]}',
        f'episode: {ep["episode"]}',
    ]

    if sections['guests']:
        # Extract just names from guest entries
        guest_names = []
        for g in sections['guests']:
            # Handle case where multiple guests are on one line: "沙青青、梵一如"
            if '、' in g and '（' not in g and '(' not in g:
                # Split by 、 and add each name
                for name in g.split('、'):
                    name = name.strip()
                    if name and len(name) < 30:
                        guest_names.append(name)
            else:
                # Extract name before parenthesis or special chars
                name_match = re.match(r'^([^（(\-—]+)', g)
                if name_match:
                    name = name_match.group(1).strip().rstrip('、')
                    if name and len(name) < 30:
                        guest_names.append(name)
        if guest_names:
            yaml_lines.append(f'guests: {guest_names}')

    yaml_lines.append('---')
    yaml_lines.append('')

    # Build content body
    body_lines = [
        f'# {ep["title"]}',
        '',
        '## 节目信息',
        '',
        f'- **期号**: EP{ep["episode"]}',
        f'- **发布日期**: {ep["date"]}',
    ]

    if ep.get('duration'):
        body_lines.append(f'- **时长**: {ep["duration"]}')

    body_lines.append('')

    # Guests section - normalize multi-guest lines
    if sections['guests']:
        body_lines.append('## 出场嘉宾')
        body_lines.append('')
        for guest in sections['guests']:
            # Split combined entries like "沙青青、梵一如"
            if '、' in guest and '（' not in guest and '(' not in guest:
                for name in guest.split('、'):
                    name = name.strip()
                    if name:
                        body_lines.append(f'- {name}')
            else:
                body_lines.append(f'- {guest}')
        body_lines.append('')

    # Announcement section (if exists, often contains important info)
    if sections.get('announcement'):
        body_lines.append('## 节目预告')
        body_lines.append('')
        for line in sections['announcement']:
            body_lines.append(line)
        body_lines.append('')

    # Timeline section (the most important part)
    if sections['timeline']:
        body_lines.append('## 时间轴')
        body_lines.append('')
        for item in sections['timeline']:
            body_lines.append(f'- **{item["time"]}** {item["description"]}')
        body_lines.append('')

    # Main content (intro/description that wasn't in any section)
    if sections.get('main_content'):
        # Filter out very short or noise lines
        meaningful_content = [l for l in sections['main_content']
                            if len(l) > 5 and not re.match(r'^[\W_]+$', l)]
        if meaningful_content:
            body_lines.append('## 内容简介')
            body_lines.append('')
            for line in meaningful_content[:10]:  # Limit
                body_lines.append(line)
            body_lines.append('')

    # Production credits (compact)
    credits = []
    if sections.get('op'):
        credits.append(f'- **OP**: {sections["op"]}')
    if sections.get('ed'):
        credits.append(f'- **ED**: {sections["ed"]}')
    if sections.get('editor'):
        credits.append(f'- **剪辑**: {sections["editor"]}')
    if sections.get('production'):
        credits.append(f'- **出品**: {sections["production"]}')

    if credits:
        body_lines.append('## 制作信息')
        body_lines.append('')
        body_lines.extend(credits)
        body_lines.append('')

    # Audio link
    if ep['audio_url']:
        body_lines.append('## 音频链接')
        body_lines.append('')
        body_lines.append(f'{ep["audio_url"]}')
        body_lines.append('')

    body_lines.append('---')
    body_lines.append('*数据来源: 喜马拉雅 RSS feed*')

    return '\n'.join(yaml_lines + body_lines)


def fetch_rss():
    """Fetch RSS feed with fallback URLs"""
    for url in RSS_URLS:
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; PodcastWiki/1.0)'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                if content and len(content) > 100:
                    print(f"Fetched from: {url}")
                    return content
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            continue

    raise RuntimeError("Could not fetch RSS feed from any URL")


def main():
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [number_of_episodes]")
            sys.exit(1)

    print(f"Fetching {limit} most recent episodes from 东亚观察局...")

    # Fetch and parse RSS
    rss_content = fetch_rss()
    root = ET.fromstring(rss_content)

    # Remove namespaces
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[1]

    # Get episodes
    channel = root.find('channel')
    items = channel.findall('item')[:limit]

    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = OUTPUT_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for item in items:
        try:
            ep = parse_episode(item)
            md_content = generate_markdown(ep)

            filename = f"EP{ep['episode']}-{safe_filename(ep['clean_title'])}.md"
            output_path = output_dir / filename
            output_path.write_text(md_content, encoding='utf-8')

            timeline_count = len(ep['sections']['timeline'])
            guest_count = len(ep['sections']['guests'])
            print(f"  [✓] EP{ep['episode']}: {timeline_count} timeline items, {guest_count} guests")
            print(f"      → {filename}")

            success_count += 1
        except Exception as e:
            print(f"  [✗] Error parsing episode: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\nDone! Created {success_count}/{len(items)} episode files in:")
    print(f"  {output_dir}")
    print(f"\nNext step: cd ~/podcast-wiki and ingest the files")


if __name__ == '__main__':
    main()
