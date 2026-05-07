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
    <title>Aashu Universal Downloader</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 1rem; }
 .container { background: #1e293b; padding: 2rem; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.4); width: 100%; max-width: 600px; }
        h1 { color: #38bdf8; margin-bottom: 0.5rem; text-align: center; font-size: 2rem; }
     .subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 1.5rem; }
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
 .platforms { display: flex; justify-content: center; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
 .platform-tag { font-size: 11px; background: #334155; padding: 4px 8px; border-radius: 6px; color: #94a3b8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aashu Universal Downloader 🚀</h1>
        <p class="subtitle">YouTube, Instagram, Facebook, TikTok, X, Pinterest</p>
        
        {% if not video_info and not loading %}
        <div class="platforms">
            <span class="platform-tag">YouTube</span>
            <span class="platform-tag">Instagram</span>
            <span class="platform-tag">Facebook</span>
            <span class="platform-tag">TikTok</span>
            <span class="platform-tag">Twitter/X</span>
            <span class="platform-tag">Pinterest</span>
        </div>
        <form method="POST" action="/info">
            <input type="text" name="url" placeholder="Koi bhi video link paste karo..." required autocomplete="off">
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
            <p><b>Source:</b> {{ video_info.platform }} | <b>Duration:</b> {{ video_info.duration }} | <b>Uploader:</b> {{ video_info.uploader }}</p>
            
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
        
        <div class="footer">Made by Aashu | Supports 1000+ sites via yt-dlp</div>
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
        return "N/A"
    try:
        seconds = int(seconds)
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {sec}s"
        return f"{minutes}m {sec}s"
    except:
        return "N/A"

def get_platform_name(url):
    if 'youtube.com' in url or 'youtu.be' in url: return 'YouTube'
    if 'instagram.com' in url: return 'Instagram'
    if 'facebook.com' in url or 'fb.watch' in url: return 'Facebook'
    if 'tiktok.com' in url: return 'TikTok'
    if 'twitter.com' in url or 'x.com' in url: return 'Twitter/X'
    if 'pinterest.com' in url or 'pin.it' in url: return 'Pinterest'
    return 'Unknown'

def get_ydl_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'socket_timeout': 20,
        # Bot bypass tricks 👇
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'], # Android client zyada stable hai
                'player_skip': ['webpage'],
            }
        },
    }
    if os.path.exists('/etc/secrets/cookies.txt'):
        opts['cookiefile'] = '/etc/secrets/cookies.txt'
    return opts

def get_clean_formats(formats, url):
    result = []
    
    # 1. Audio Only
    for f in formats:
        if f.get('vcodec') == 'none' and f.get('acodec')!= 'none':
            result.append({
                'format_id': f.get('format_id', 'bestaudio'),
                'resolution': 'Audio Only',
                'ext': 'm4a',
                'filesize': format_bytes(f.get('filesize') or f.get('filesize_approx')),
                'note': 'Audio'
            })
            break
    
    if not any('Audio' in r['resolution'] for r in result):
        result.append({
            'format_id': 'bestaudio/best',
            'resolution': 'Audio Only',
            'ext': 'm4a',
            'filesize': '~',
            'note': 'Audio'
        })

    # 2. Video formats
    standard_heights = [2160, 1440, 1080, 720, 480, 360, 240, 144]
    seen_heights = set()
    
    for height in standard_heights:
        for f in formats:
            if f.get('height') == height and f.get('vcodec')!= 'none':
                if height not in seen_heights:
                    note = ''
                    if height >= 2160: note = '4K'
                    elif height >= 1440: note = '2K'
                    elif height >= 1080: note = 'FHD'
                    elif height >= 720: note = 'HD'
                    elif height >= 480: note = 'SD'
                    
                    result.append({
                        'format_id': f['format_id'],
                        'resolution': f"{height}p",
                        'ext': 'mp4',
                        'filesize': format_bytes(f.get('filesize') or f.get('filesize_approx')),
                        'note': note
                    })
                    seen_heights.add(height)
                    break
    
    if len(result) == 1:
        result.append({
            'format_id': 'best[ext=mp4]/best',
            'resolution': 'Best Quality',
            'ext': 'mp4',
            'filesize': '~',
            'note': 'Auto'
        })
    
    return result

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/info", methods=["POST"])
def get_info():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template_string(HTML, error="URL daalo bhai")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return render_template_string(HTML, error="Video info nahi mili. Link sahi hai?")
            
            video_info = {
                'title': info.get('title', 'Unknown Title')[:100],
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration')),
                'uploader': info.get('uploader', info.get('channel', 'Unknown'))[:30],
                'webpage_url': info.get('webpage_url', url),
                'platform': get_platform_name(url),
                'formats': get_clean_formats(info.get('formats', []), url)
            }
            
            if not video_info['formats']:
                return render_template_string(HTML, error="Is link ke download links nahi mile. Private ya login required ho sakta hai")
                
            return render_template_string(HTML, video_info=video_info)

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Private' in error_msg or 'private' in error_msg:
            return render_template_string(HTML, error="Ye video private hai")
        elif 'Sign in to confirm' in error_msg or 'bot' in error_msg:
            return render_template_string(HTML, error="YouTube bot samajh raha hai. Cookies.txt update karo ya 2-3 min baad try karo")
        elif 'Video unavailable' in error_msg:
            return render_template_string(HTML, error="Video available nahi hai ya delete ho gayi")
        else:
            return render_template_string(HTML, error=f"YouTube block kar raha hai. Cookies update karo")
    except Exception as e:
        app.logger.error(f"Info error: {e}")
        return render_template_string(HTML, error="Kuch galat ho gaya. Dusra link try karo")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    format_id = request.form.get("format_id", "best")
    title = request.form.get("title", "video")
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
    filename = f"{safe_title}_{uuid.uuid4().hex[:6]}.mp4"

    ydl_opts = get_ydl_opts()
    ydl_opts.update({
        'format': format_id,
        'outtmpl': filename,
        'merge_output_format': 'mp4',
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(filename):
            for ext in ['.m4a', '.webm', '.mkv', '.mp3']:
                new_name = filename.replace('.mp4', ext)
                if os.path.exists(new_name):
                    filename = new_name
                    break

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                app.logger.error(f"File delete error: {e}")
            return response

        return send_file(filename, as_attachment=True, download_name=f"{safe_title}.mp4")

    except Exception as e:
        app.logger.error(f"Download error: {e}")
        return render_template_string(HTML, error="Download fail. 2 min baad try karo")

if __name__ == "__main__":
    app.run(debug=False)
