#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import markdown

# Конфигурация
POSTS_DIR = Path("posts")
OUTPUT_FILE = Path("index.html")
SITE_TITLE = "Actugate blog"

# Цветовая схема (CSS переменные)
COLORS = {
    "bg": "#202426",
    "bg-card": "#17181a",
    "header-bg": "#07070b",
    "text": "#e2e1e1",
    "accent": "#23af5f",
    "icon": "#e2e1e1",
}

# Ссылки для соцсетей
SOCIAL_LINKS = {
    "telegram": "https://t.me/actugate",
    "habr": "https://habr.com/ru/users/actugate/",
    "youtube": "https://youtube.com/@actugate",
    "itchio": "https://xlebore3o4ka.itch.io/",
}

# Профиль пользователя
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

    # НЕ УДАЛЯЕМ ПЕРВЫЙ H1 - оставляем его как заголовок внутри поста

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


def read_post(post_dir: Path) -> Tuple:
    post_md = post_dir / "post.md"
    if not post_md.exists():
        return None, None, None, None

    with open(post_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Извлекаем первый h1 из markdown (если есть)
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    display_title = title_match.group(1).strip() if title_match else post_dir.name

    html_content = markdown_to_html(md_content, post_dir)
    mtime = get_mtime(post_md)

    return html_content, display_title, mtime, post_dir


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
    for html_content, display_title, mtime, post_dir in posts:
        date_str = format_date(mtime)
        posts_html.append(f'''
        <article class="post">
            <div class="post-header">
                <div class="post-meta">
                    <time datetime="{datetime.fromtimestamp(mtime).isoformat()}">{date_str}</time>
                </div>
                <div class="post-folder-name">{post_dir.name}</div>
            </div>
            {html_content}
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
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE}</title>
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

        /* Шапка */
        .header {{
            position: sticky;
            top: 0;
            background-color: rgba(7, 7, 11, 0.85);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid rgba(226, 225, 225, 0.08);
            padding: 0.75rem 2rem;
            z-index: 100;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }}

        .logo:hover {{
            opacity: 0.8;
        }}

        .site-icon {{
            width: 64px;
            height: 64px;
            object-fit: contain;
        }}

        .site-icon-fallback {{
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            font-weight: bold;
            color: var(--accent);
            transition: color 0.2s ease;
        }}

        .logo:hover .site-icon-fallback {{
            color: var(--text);
        }}

        .logo-text {{
            color: var(--text);
            transition: color 0.2s ease;
        }}

        .logo:hover .logo-text {{
            color: var(--accent);
        }}

        .right-section {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}

        .social-links {{
            display: flex;
            gap: 1.25rem;
        }}

        .social-links a {{
            color: var(--icon-color);
            font-size: 1.35rem;
            transition: color 0.2s ease;
            text-decoration: none;
        }}

        .social-links a:hover {{
            color: var(--accent);
        }}

        .profile {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            text-decoration: none;
            color: var(--text);
            transition: opacity 0.2s ease;
        }}

        .profile:hover {{
            opacity: 0.8;
        }}

        .profile-name {{
            font-size: 0.95rem;
            font-weight: 500;
        }}

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
            padding: 2rem;
        }}

        .post {{
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(226, 225, 225, 0.196);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}

        .post:hover {{
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            border-color: rgba(226, 225, 225, 0.25);
        }}

        .post-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(226, 225, 225, 0.1);
            padding-bottom: 1rem;
            position: relative;
        }}

        .post-meta {{
            font-size: 0.85rem;
            color: rgba(226, 225, 225, 0.6);
            flex-shrink: 0;
        }}

        .post-meta time {{
            font-family: monospace;
        }}

        .post-folder-name {{
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: 0.5px;
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap;
            transition: color 0.2s ease;
            cursor: default;
        }}

        .post:hover .post-folder-name {{
            color: var(--accent);
        }}

        .post h1, .post h2, .post h3 {{
            color: var(--text);
        }}

        .post h1 {{ font-size: 1.8rem; margin-bottom: 1rem; }}
        .post h2 {{ font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        .post h3 {{ font-size: 1.25rem; margin-top: 1rem; margin-bottom: 0.5rem; }}

        .post p {{ margin-bottom: 1rem; }}

        .post a {{
            color: var(--accent);
            text-decoration: none;
        }}

        .post a:hover {{
            text-decoration: underline;
        }}

        .post ul, .post ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}

        .post ul {{ list-style-type: disc; }}
        .post ul ul {{ list-style-type: circle; }}
        .post ol {{ list-style-type: decimal; }}
        .post li {{ margin-bottom: 0.5rem; }}

        .post code {{
            background-color: rgba(226, 225, 225, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: "Courier New", monospace;
            font-size: 0.9rem;
        }}

        .post pre {{
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

        .post blockquote {{
            border-left: 3px solid var(--accent);
            margin: 1rem 0;
            padding-left: 1rem;
            color: rgba(226, 225, 225, 0.7);
        }}

        .post-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
            display: block;
        }}

        hr {{
            border: none;
            border-top: 1px solid rgba(226, 225, 225, 0.1);
            margin: 1rem 0;
        }}

        .post table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }}

        .post th, .post td {{
            border: 1px solid rgba(226, 225, 225, 0.2);
            padding: 0.5rem;
            text-align: left;
        }}

        .post th {{
            background-color: rgba(226, 225, 225, 0.05);
        }}

        @media (max-width: 768px) {{
            .profile-name {{ display: none; }}
            .right-section {{ gap: 1rem; }}
            .social-links {{ gap: 0.75rem; }}

            .post-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.75rem;
                position: static;
            }}

            .post-folder-name {{
                position: static;
                transform: none;
                white-space: normal;
                font-size: 1.2rem;
                order: -1;
                margin-bottom: 0.25rem;
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
                    <a href="{SOCIAL_LINKS['telegram']}" target="_blank"><i class="fab fa-telegram"></i></a>
                    <a href="{SOCIAL_LINKS['habr']}" target="_blank"><i class="fas fa-newspaper"></i></a>
                    <a href="{SOCIAL_LINKS['youtube']}" target="_blank"><i class="fab fa-youtube"></i></a>
                    <a href="{SOCIAL_LINKS['itchio']}" target="_blank"><i class="fab fa-itch-io"></i></a>
                </div>
                {profile_html}
            </div>
        </div>
    </header>

    <main class="container">
        {posts_html_str if posts_html_str else '<p style="text-align: center;">Нет постов. Добавьте папки с post.md в posts/</p>'}
    </main>
</body>
</html>'''

    return html_template


def main():
    print("Генерация блога...")

    if PROFILE["avatar"] and Path(PROFILE["avatar"]).exists():
        print(f"✓ Аватарка найдена: {PROFILE['avatar']}")
    else:
        print(f"⚠ Аватарка не найдена: {PROFILE['avatar']}")

    posts = get_all_posts()
    print(f"Найдено постов: {len(posts)}")

    for _, title, mtime, post_dir in posts:
        print(f"  - {title} ({format_date(mtime)})")

    html_content = generate_html(posts)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nГотово! {OUTPUT_FILE}")


if __name__ == "__main__":
    main()