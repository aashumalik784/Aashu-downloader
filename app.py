from flask import Flask, request, render_template_string, send_file, after_this_request
import yt_dlp
import os
import uuid
import math
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aashu Downloader Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 1rem; }
    .container { background: #1e293b; padding: 2rem; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.4); width: 100%; max-width: 600px; }
        h1 { color: #38bdf8; margin-bottom: 1.5rem; text-align: center; font-size: 2rem; }
        input { width: 100%; padding: 14px; margin-bottom: 1rem; border: 2px solid #334155; border-radius: 10px; background: #0f172a; color: #e2e8f0; font-size: 15px; }
        input:focus { outline: none; border-color: #38bdf8; }
        button { width: 100%; padding: 14px; background: #38bdf8; color: #0f172a; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 16px; transition: 0.2s; }
        button:hover { background: #0ea5e9; transform: translateY(-1px); }
        button:active { transform: translateY(0); }
    .footer { margin-top: 1.5rem; font-size: 12px; color: #64748b; text-align: center; }
    .error { color: #f87171; margin-top: 1rem; padding: 12px; background: #7f1d1d30; border-radius: 8px; text-align: center; }
    .loading { color: #38bdf8; margin-top: 1rem; text-align: center; }
    .video-info { margin-top: 1.5rem; }
    .video-info img { width: 100%; border-radius: 12px; margin-bottom: 1rem; max-height: 320px; object-fit: cover; }
    .video-info h3 { margin: 0.5rem 0; color: #e2e8f0; font-size: 18px; line-height: 1.4; }
    .video-info p { margin: 0.4rem 0; color: #94a3b8; font-size: 14px; }
    .formats { margin-top: 1.5rem; }
    .formats h4 { margin-bottom: 1rem; color: #cbd5e1; }
    .format-btn { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 14px; background: #334155; color: #e2e8f0; border: 2px solid transparent; border-radius: 10px; margin-bottom: 10px; cursor: pointer; text-align: left; transition: 0.2s; }
    .format-btn:hover { background: #475569; border-color: #38bdf8; }
    .format-btn div { display: flex; align-items: center; gap: 8px; }
    .format-btn span { font-size: 13px; color: #94a3b8; font-weight: 600; }
    .badge { background: #38bdf8; color: #0f172a; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .back-btn { background: #475569; margin-top: 1rem; }
    .back-btn:hover { background: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aashu Downloader Pro 🚀</h1>
        
        {% if not video_info and not loading %}
        <form method="POST" action="/info">
            <input type="text" name="url" placeholder="YouTube video/Shorts URL paste karo" required autocomplete="off">
            <button type="submit">Get Download Links</button>
        </form>
        {% endif %}

        {% if loading %}
            <p class="loading">Fetching video info... ⏳</p>
        {% endif %}

        {% if error %}
            <p class="error">{{ error }}</p>
            <form method="GET" action="/">
                <button class="back-btn" type="submit">Try Again</button>
            </form>
        {% endif %}

        {% if video_info %}
        <div class="video-info">
            {% if video_info.thumbnail %}
            <img src="{{ video_info.thumbnail }}" alt="Thumbnail" onerror="this.style.display='none'">
            {% endif %}
            <h3>{{ video_info.title }}</h3>
            <p><b>Duration:</b> {{ video_info.duration }} | <b>Uploader:</b> {{ video_info.uploader }}</p>
            
            <div class="formats">
                <h4>👇 Select Quality to Download:</h4>
                {% if video_info.formats %}
                    {% for f in video_info.formats %}
                    <form method="POST" action="/download">
                        <input type="hidden" name="url" value="{{ video_info.webpage_url }}">
                        <input type="hidden" name="format_id" value="{{ f.format_id }}">
                        <input type="hidden" name="title" value="{{ video_info.title }}">
                        <button class="format-btn" type="submit">
                            <div>
                                <b>{{ f.resolution }}</b>
                                {% if f.note %}<span class="badge">{{ f.note }}</span>{% endif %}
                            </div>
                            <span>{{ f.filesize }}</span>
                        </button>
                    </form>
                    {% endfor %}
                {% else %}
                    <p class="error">No downloadable formats found. Video may be private or restricted.</p>
                {% endif %}
            </div>
            
            <form method="GET" action="/">
                <button class="back-btn" type="submit">⬅️ Download Another Video</button>
            </form>
        </div>
        {% endif %}
        
        <div class="footer">Made by Aashu | Works best on Chrome</div>
    </div>
</body>
</html>
"""

def format_bytes(size):
    if not size or size == 0:
        return "~"
    try:
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 1)
        return f"{s} {size_name[i]}"
    except:
        return "~"

def format_duration(seconds):
    if not seconds:
        return "Live/Unknown"
    try:
        seconds = int(seconds)
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {sec}s"
        return f"{minutes}m {sec}s"
    except:
        return "Unknown"

def get_clean_formats(formats):
    result = []
    seen_heights = set()
    
    # 1. Audio Only - M4A
    audio_found = False
    for f in formats:
        if f.get('vcodec') == 'none' and f.get('acodec')!= 'none' and f.get('ext') == 'm4a':
            result.append({
                'format_id': f.get('format_id', 'bestaudio[ext=m4a]'),
                'resolution': 'Audio Only',
                'ext': 'm4a',
                'filesize': format_bytes(f.get('filesize') or f.get('filesize_approx')),
                'note': 'Audio'
            })
            audio_found = True
            break
    
    if not audio_found:
        result.append({
            'format_id': 'bestaudio',
            'resolution': 'Audio Only',
            'ext': 'm4a',
            'filesize': '~',
            'note': 'Audio'
        })

    # 2. Video formats - Only standard heights: 144,240,360,480,720,1080,1440,2160
    standard_heights = [2160, 144
