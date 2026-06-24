import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import markdown


POSTS_DIR = Path("posts")
OUTPUT_FILE = Path("index.html")
SITE_TITLE = "Actugate blog"

COLORS = {
    "bg": "#202426",
    "bg-card": "#17181a",
    "header-bg": "#07070b",
    "text": "#e2e1e1",
    "accent": "#23af5f",
    "icon": "#e2e1e1",
}

TAG_COLORS = {
    "devlog": "#2c3e50",
    "blog": "#8e44ad",
    "idea": "#d35400",
    "update": "#27ae60",
    "tutorial": "#2980b9",
    "release": "#c0392b",
    "bugfix": "#f39c12",
    "announcement": "#16a085",
    "offtopic": "#7f8c8d",
    "code": "#3b5998",
    "kovyl": "#e67e22", 
    "actugate": "#2ecc71",
}

SOCIAL_LINKS = {
    "telegram": "https://t.me/actugate",
    "habr": "https://habr.com/ru/users/actugate/",
    "youtube": "https://youtube.com/@actugate",
    "itchio": "https://xlebore3o4ka.itch.io/",
}

PROFILE = {
    "name": "xlebore3o4ka",
    "avatar": "avatar.png",
    "link": "https://github.com/xlebore3o4ka",
}


def get_mtime(post_path: Path) -> float:
    return os.path.getmtime(post_path)


def format_date(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%b %d, %Y %H:%M")


def load_post_metadata(post_dir: Path) -> Optional[Dict]:
    data_json = post_dir / "data.json"
    if not data_json.exists():
        return {
            "title": post_dir.name,
            "tags": [],
            "description": "",
            "id": post_dir.name,
        }

    try:
        with open(data_json, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        return {
            "title": metadata.get("title", post_dir.name),
            "tags": metadata.get("tags", []),
            "description": metadata.get("description", ""),
            "id": metadata.get("id", post_dir.name),
        }
    except Exception as e:
        print(f"ERROR: Failed to parse {data_json}: {e}")
        return {
            "title": post_dir.name,
            "tags": [],
            "description": "",
            "id": post_dir.name,
        }


def markdown_to_html(content: str, post_dir: Path) -> str:
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
    ]

    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(content)

    def fix_image_path(match):
        img_src = match.group(1)
        if not img_src.startswith(('http://', 'https://', '/')):
            return f'<img src="posts/{post_dir.name}/{img_src}" class="post-image"'
        return match.group(0)

    html_content = re.sub(r'<img src="([^"]+)"', fix_image_path, html_content)

    def fix_resource_path(match):
        href = match.group(1)
        if not href.startswith(('http://', 'https://', '/')):
            return f'href="posts/{post_dir.name}/{href}"'
        return match.group(0)

    html_content = re.sub(r'href="([^"]+)"', fix_resource_path, html_content)

    return html_content


def generate_tags_html(tags: List[str]) -> str:
    if not tags:
        return ''

    tags_html_parts = []
    for tag in tags:
        tag_lower = tag.lower()
        bg_color = TAG_COLORS.get(tag_lower, TAG_COLORS["offtopic"])
        tags_html_parts.append(f'<span class="tag" style="background-color: {bg_color};">{tag}</span>')

    return '<div class="post-tags">' + ''.join(tags_html_parts) + '</div>'


def read_post(post_dir: Path) -> Tuple:
    post_md = post_dir / "post.md"
    if not post_md.exists():
        return None, None, None, None, None, None, None

    metadata = load_post_metadata(post_dir)

    with open(post_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    title = metadata["title"]
    if not title or title == post_dir.name:
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

    html_content = markdown_to_html(md_content, post_dir)
    publish_time = get_mtime(post_md)
    tags = metadata.get("tags", [])
    description = metadata.get("description", "")
    post_id = metadata.get("id", post_dir.name)

    return html_content, title, publish_time, post_dir, tags, description, post_id


def get_all_posts():
    if not POSTS_DIR.exists():
        POSTS_DIR.mkdir()
        return []

    posts = []
    for post_dir in POSTS_DIR.iterdir():
        if post_dir.is_dir():
            post_data = read_post(post_dir)
            if post_data[0] is not None:
                posts.append(post_data)

    posts.sort(key=lambda x: x[2], reverse=True)
    return posts


def generate_html(posts):
    posts_html = []
    for html_content, title, publish_time, post_dir, tags, description, post_id in posts:
        date_str = format_date(publish_time)
        tags_html = generate_tags_html(tags)

        escaped_description = description.replace('\\', '\\\\').replace('"', '&quot;').replace('\n', ' ').replace('\r',
                                                                                                                  '')

        posts_html.append(f'''
        <article class="post fade-in-up" data-date="{publish_time}" id="{post_id}">
            <div class="post-header">
                <div class="post-title-wrapper">
                    <h1 class="post-title">{title}</h1>
                    <div class="quote-icon" data-description="{escaped_description}">
                        <i class="fas fa-quote-right"></i>
                        <div class="quote-tooltip">
                            <div class="quote-tooltip-content">
                                <p>{description if description else 'No description provided'}</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="post-meta">
                    <time datetime="{datetime.fromtimestamp(publish_time).isoformat()}">{date_str}</time>
                    {tags_html}
                </div>
            </div>
            <div class="post-content">
                {html_content}
            </div>
            <div class="post-footer">
                <div class="post-share-group">
                    <span class="post-id-subtle">{post_id}</span>
                    <button class="share-button" data-post-id="{post_id}" aria-label="Share post">
                        <i class="fas fa-share-alt"></i>
                    </button>
                </div>
            </div>
        </article>
        ''')

    posts_html_str = "\n".join(posts_html)

    icon_html = ''
    if Path("icon.png").exists():
        icon_html = '<img src="icon.png" alt="icon" class="site-icon">'
    else:
        icon_html = '<span class="site-icon-fallback">A</span>'

    profile_html = ''
    avatar_exists = Path(PROFILE["avatar"]).exists() if PROFILE["avatar"] else False

    if avatar_exists:
        avatar_html = f'<img src="{PROFILE["avatar"]}" alt="avatar" class="profile-avatar">'
    else:
        avatar_html = '<div class="profile-avatar-placeholder"></div>'

    if PROFILE["link"]:
        profile_html = f'<a href="{PROFILE["link"]}" class="profile" target="_blank"><span class="profile-name">{PROFILE["name"]}</span>{avatar_html}</a>'
    else:
        profile_html = f'<div class="profile"><span class="profile-name">{PROFILE["name"]}</span>{avatar_html}</div>'

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <title>Actugate — deterministic sandbox with pistons, activators and boxes</title>
    <meta name="description" content="Actugate blog — development blog about deterministic 2D sandbox where you can build mechanisms from pistons, activators and boxes">
    <meta name="keywords" content="Actugate, sandbox, game, pistons, activators, boxes, logic game, indie, Nim, Raylib">
    <link rel="canonical" href="https://xlebore3o4ka.github.io/ActugateBlog/">
    <meta name="robots" content="index, follow">

    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

    <style>
        :root {{
            --bg: {COLORS["bg"]};
            --bg-card: {COLORS["bg-card"]};
            --header-bg: {COLORS["header-bg"]};
            --text: {COLORS["text"]};
            --accent: {COLORS["accent"]};
            --icon-color: {COLORS["icon"]};
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: linear-gradient(180deg, var(--bg) 0%, var(--header-bg) 200%);
            background-attachment: fixed;
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            min-height: 100vh;
        }}

        code, pre, .post-meta time {{
            font-family: 'JetBrains Mono', 'Courier New', monospace;
        }}

        .post code {{
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-weight: 500;
            background-color: rgba(226, 225, 225, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.85rem;
        }}

        .post pre {{
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            background-color: rgba(226, 225, 225, 0.05);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }}

        .post pre code {{
            background: none;
            padding: 0;
        }}

        .header {{
            position: sticky;
            top: 0;
            background-color: rgba(7, 7, 11, 0.95);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid rgba(226, 225, 225, 0.08);
            padding: 0.5rem 1rem;
            z-index: 100;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.2rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: opacity 0.2s ease;
            flex-shrink: 0;
        }}

        .logo:hover {{ opacity: 0.8; }}

        .site-icon {{
            width: 40px;
            height: 40px;
            object-fit: contain;
        }}

        .site-icon-fallback {{
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--accent);
        }}

        .logo-text {{
            color: var(--text);
            transition: color 0.2s ease;
            font-size: 1rem;
        }}

        .logo:hover .logo-text {{ color: var(--accent); }}

        .right-section {{
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-shrink: 1;
            min-width: 0;
        }}

        .social-links {{
            display: flex;
            gap: 0.75rem;
            flex-shrink: 1;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}

        .social-links a {{
            color: var(--icon-color);
            font-size: 1.2rem;
            transition: color 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 32px;
        }}

        .social-links a:hover {{ color: var(--accent); }}

        .profile {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            text-decoration: none;
            color: var(--text);
            transition: opacity 0.2s ease;
            flex-shrink: 0;
        }}

        .profile:hover {{ opacity: 0.8; }}

        .profile-name {{ font-size: 0.85rem; font-weight: 500; }}

        .profile-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent);
        }}

        .profile-avatar-placeholder {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), #1a7a45);
            border: 2px solid var(--accent);
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 1rem;
        }}

        .post {{
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(226, 225, 225, 0.196);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
            scroll-margin-top: 80px;
        }}

        .post:hover {{
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            border-color: rgba(226, 225, 225, 0.25);
        }}

        .fade-in-up {{
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), 
                        transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .fade-in-up.visible {{
            opacity: 1;
            transform: translateY(0);
        }}

        .post-header {{
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(226, 225, 225, 0.1);
            padding-bottom: 1rem;
        }}

        .post-title-wrapper {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }}

        .post-title {{
            font-size: 1.8rem;
            color: var(--text);
            margin: 0;
            line-height: 1.3;
            flex: 1;
        }}

        .quote-icon {{
            position: relative;
            cursor: pointer;
            flex-shrink: 0;
            color: var(--accent);
            font-size: 1.5rem;
            transition: transform 0.2s ease, color 0.2s ease;
            padding: 0.25rem;
        }}

        .quote-icon:hover {{
            transform: scale(1.1);
            color: var(--text);
        }}

        .quote-tooltip {{
            position: absolute;
            visibility: hidden;
            opacity: 0;
            right: 0;
            top: 100%;
            margin-top: 0.5rem;
            width: 320px;
            background-color: #2a2e33;
            border: 1px solid rgba(226, 225, 225, 0.196);
            border-radius: 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            transition: opacity 0.2s ease, visibility 0.2s ease;
            pointer-events: none;
        }}

        .quote-icon:hover .quote-tooltip {{
            visibility: visible;
            opacity: 1;
        }}

        .quote-tooltip-content {{
            padding: 1rem;
            position: relative;
            border-left: 3px solid var(--accent);
        }}

        .quote-tooltip-content p {{
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.5;
            font-style: italic;
            color: var(--text);
        }}

        .post-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}

        .post-meta time {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: rgba(226, 225, 225, 0.6);
            flex-shrink: 0;
        }}

        .post-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: flex-end;
        }}

        .tag {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: white;
            text-transform: lowercase;
            letter-spacing: 0.5px;
            transition: transform 0.1s ease, opacity 0.2s ease;
            cursor: default;
        }}

        .tag:hover {{
            transform: translateY(-1px);
            opacity: 0.9;
        }}

        .post-content h1 {{ font-size: 1.6rem; margin: 1rem 0 0.75rem; }}
        .post-content h2 {{ font-size: 1.4rem; margin: 1.25rem 0 0.6rem; }}
        .post-content h3 {{ font-size: 1.2rem; margin: 1rem 0 0.5rem; }}
        .post-content p {{ margin-bottom: 0.8rem; line-height: 1.6; }}
        .post-content a {{ color: var(--accent); text-decoration: none; }}
        .post-content a:hover {{ text-decoration: underline; }}

        .post-content ul, .post-content ol {{
            margin: 0.75rem 0;
            padding-left: 1.5rem;
        }}

        .post-content li {{ margin-bottom: 0.4rem; }}

        .post-content blockquote {{
            border-left: 3px solid var(--accent);
            margin: 0.75rem 0;
            padding-left: 1rem;
            color: rgba(226, 225, 225, 0.7);
        }}

        .post-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
        }}

        hr {{
            border: none;
            border-top: 1px solid rgba(226, 225, 225, 0.1);
            margin: 1rem 0;
        }}

        .post-content table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            overflow-x: auto;
            display: block;
        }}

        .post-content th, .post-content td {{
            border: 1px solid rgba(226, 225, 225, 0.2);
            padding: 0.5rem;
            text-align: left;
        }}

        .post-content th {{
            background-color: rgba(226, 225, 225, 0.05);
        }}

        .post-footer {{
            margin-top: 1.5rem;
            display: flex;
            justify-content: flex-end;
        }}

        .post-share-group {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .post-id-subtle {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: rgba(226, 225, 225, 0.3);
            letter-spacing: 0.3px;
        }}

        .share-button {{
            background: none;
            border: none;
            color: rgba(226, 225, 225, 0.5);
            cursor: pointer;
            font-size: 1.1rem;
            padding: 0.4rem 0.6rem;
            border-radius: 6px;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .share-button:hover {{
            color: var(--accent);
            background-color: rgba(35, 175, 95, 0.1);
            transform: scale(1.05);
        }}

        .share-button:active {{
            transform: scale(0.95);
        }}

        .notification {{
            position: fixed;
            top: 80px;
            right: 20px;
            background-color: #27ae60;
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: 500;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            opacity: 0;
            transform: translateX(100%);
            transition: opacity 0.3s ease, transform 0.3s ease;
            pointer-events: none;
        }}

        .notification.show {{
            opacity: 1;
            transform: translateX(0);
        }}

        .notification.hide {{
            opacity: 0;
            transform: translateX(100%);
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 0.75rem; }}
            .post {{ padding: 1rem; }}
            .post-title {{ font-size: 1.4rem; }}
            .post-content h1 {{ font-size: 1.3rem; }}
            .post-content h2 {{ font-size: 1.2rem; }}
            .post-content h3 {{ font-size: 1.1rem; }}

            .quote-tooltip {{
                width: 280px;
                right: -10px;
            }}

            .notification {{
                top: 70px;
                right: 10px;
                left: 10px;
                text-align: center;
            }}
        }}

        @media (max-width: 600px) {{
            .header-content {{
                flex-direction: column;
                align-items: stretch;
                gap: 0.75rem;
            }}

            .logo {{ justify-content: center; }}
            .right-section {{ justify-content: space-between; width: 100%; }}
            .profile-name {{ font-size: 0.8rem; }}
            .profile-avatar {{ width: 28px; height: 28px; }}

            .container {{ padding: 0.5rem; }}
            .post {{ padding: 0.875rem; }}
            .post-title {{ font-size: 1.2rem; }}

            .post-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .post-tags {{
                justify-content: flex-start;
            }}

            .tag {{ font-size: 0.6rem; padding: 0.15rem 0.5rem; }}

            .quote-icon .quote-tooltip {{
                width: 260px;
                right: -20px;
            }}

            .post-id-subtle {{
                font-size: 0.65rem;
            }}

            .share-button {{
                font-size: 1rem;
                padding: 0.3rem 0.5rem;
            }}
        }}

        @media (pointer: coarse) {{
            .quote-tooltip {{
                pointer-events: auto;
            }}

            .quote-icon .quote-tooltip {{
                visibility: hidden;
                opacity: 0;
            }}

            .quote-icon.active .quote-tooltip {{
                visibility: visible;
                opacity: 1;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a class="logo" href="#">
                {icon_html}
                <span class="logo-text">{SITE_TITLE}</span>
            </a>
            <div class="right-section">
                <div class="social-links">
                    <a href="{SOCIAL_LINKS['telegram']}" target="_blank" aria-label="Telegram"><i class="fab fa-telegram"></i></a>
                    <a href="{SOCIAL_LINKS['habr']}" target="_blank" aria-label="Habr"><i class="fas fa-newspaper"></i></a>
                    <a href="{SOCIAL_LINKS['youtube']}" target="_blank" aria-label="YouTube"><i class="fab fa-youtube"></i></a>
                    <a href="{SOCIAL_LINKS['itchio']}" target="_blank" aria-label="Itch.io"><i class="fab fa-itch-io"></i></a>
                </div>
                {profile_html}
            </div>
        </div>
    </header>

    <main class="container">
        {posts_html_str if posts_html_str else '<p style="text-align: center; padding: 2rem;">No posts found. Create a folder in posts/ with post.md and data.json</p>'}
    </main>

    <div id="notification" class="notification">Copied!</div>

    <script>
        const observerOptions = {{
            threshold: 0,
            rootMargin: '-60px 0px -60px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }} else {{
                    entry.target.classList.remove('visible');
                }}
            }});
        }}, observerOptions);

        document.querySelectorAll('.post').forEach(post => {{
            observer.observe(post);
        }});

        setTimeout(() => {{
            document.querySelectorAll('.post').forEach(post => {{
                const rect = post.getBoundingClientRect();
                const windowHeight = window.innerHeight;
                if (rect.top < windowHeight - 60 && rect.bottom > 60) {{
                    post.classList.add('visible');
                }}
            }});
        }}, 100);

        if (window.matchMedia('(pointer: coarse)').matches) {{
            let activeIcon = null;
            let clickOutsideHandler = null;

            function closeTooltip() {{
                if (activeIcon) {{
                    activeIcon.classList.remove('active');
                    activeIcon = null;
                }}
                if (clickOutsideHandler) {{
                    document.removeEventListener('click', clickOutsideHandler);
                    clickOutsideHandler = null;
                }}
            }}

            document.querySelectorAll('.quote-icon').forEach(icon => {{
                icon.addEventListener('click', (e) => {{
                    e.stopPropagation();

                    if (activeIcon === icon) {{
                        closeTooltip();
                        return;
                    }}

                    closeTooltip();

                    icon.classList.add('active');
                    activeIcon = icon;

                    clickOutsideHandler = (e) => {{
                        if (!icon.contains(e.target)) {{
                            closeTooltip();
                        }}
                    }};

                    setTimeout(() => {{
                        document.addEventListener('click', clickOutsideHandler);
                    }}, 0);
                }});
            }});

            document.addEventListener('touchstart', (e) => {{
                if (activeIcon && !activeIcon.contains(e.target)) {{
                    closeTooltip();
                }}
            }});
        }}

        let notificationTimeout = null;

        function showNotification() {{
            const notification = document.getElementById('notification');

            if (notificationTimeout) {{
                clearTimeout(notificationTimeout);
                notification.classList.remove('show', 'hide');
                void notification.offsetWidth;
            }}

            notification.classList.add('show');

            notificationTimeout = setTimeout(() => {{
                notification.classList.add('hide');
                notificationTimeout = setTimeout(() => {{
                    notification.classList.remove('show', 'hide');
                }}, 300);
            }}, 1500);
        }}

        document.querySelectorAll('.share-button').forEach(button => {{
            button.addEventListener('click', async (e) => {{
                e.preventDefault();
                const postId = button.getAttribute('data-post-id');
                const fullUrl = window.location.href.split('#')[0] + '#' + postId;

                try {{
                    await navigator.clipboard.writeText(fullUrl);
                    showNotification();
                }} catch (err) {{
                    const textArea = document.createElement('textarea');
                    textArea.value = fullUrl;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    showNotification();
                }}

                button.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    button.style.transform = '';
                }}, 150);
            }});
        }});

        if (window.location.hash) {{
            const targetId = window.location.hash.substring(1);
            const targetPost = document.getElementById(targetId);

            if (targetPost) {{
                setTimeout(() => {{
                    targetPost.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}, 100);
            }} else {{
                const notification = document.getElementById('notification');
                notification.textContent = 'Post not found';
                notification.style.backgroundColor = '#c0392b';
                showNotification();
                setTimeout(() => {{
                    notification.textContent = 'Copied!';
                    notification.style.backgroundColor = '#27ae60';
                }}, 2000);

                if (window.location.hash) {{
                    setTimeout(() => {{
                        window.location.hash = '';
                    }}, 100);
                }}
            }}
        }}
    </script>
</body>
</html>'''

    return html_template


def main():
    print("[INFO] Actugate blog generator started")
    print(f"[CONFIG] Posts directory: {POSTS_DIR.absolute()}")
    print(f"[CONFIG] Output file: {OUTPUT_FILE.absolute()}")
    print(f"[CONFIG] Site title: {SITE_TITLE}")

    if PROFILE["avatar"] and Path(PROFILE["avatar"]).exists():
        avatar_size = Path(PROFILE["avatar"]).stat().st_size
        print(f"[AVATAR] Found: {PROFILE['avatar']} ({avatar_size} bytes)")
    else:
        print(f"[AVATAR] Not found: {PROFILE['avatar']}, using placeholder")

    posts = get_all_posts()
    print(f"[SCAN] Found {len(posts)} post(s) in {POSTS_DIR}")

    if posts:
        print("[PROCESS] Analyzing posts:")
        for idx, (_, title, publish_time, post_dir, tags, description, post_id) in enumerate(posts, 1):
            tag_count = len(tags)
            tag_str = f", tags: {tag_count}" if tag_count > 0 else ", tags: none"
            desc_str = f", description: {len(description)} chars" if description else ", description: none"
            print(
                f"  [{idx}] {title} (id: {post_id}, mtime: {format_date(publish_time)}, slug: {post_dir.name}{tag_str}{desc_str})")
    else:
        print("[WARNING] No valid posts found. Creating empty index.")

    print("[RENDER] Generating HTML output...")
    html_content = generate_html(posts)

    output_size = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        output_size = len(html_content.encode('utf-8'))

    print(f"[SUCCESS] Blog generated successfully")
    print(f"[OUTPUT] {OUTPUT_FILE.absolute()} ({output_size:,} bytes)")
    print(
        f"[FEATURES] Markdown + syntax highlighting, tags with colors, scroll animations, quote tooltips with descriptions, responsive design")
    print(f"[READY] Deploy to GitHub Pages or any static hosting")


if __name__ == "__main__":
    main()
