from flask import Flask, request, render_template_string, send_file, after_this_request
import yt_dlp
import os
import uuid
import math

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aashu Downloader Pro</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; }
     .container { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 90%; max-width: 600px; text-align: center; }
        h1 { color: #38bdf8; margin-bottom: 1.5rem; }
        input { width: 100%; padding: 12px; margin-bottom: 1rem; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #38bdf8; color: #0f172a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 0.5rem; }
        button:hover { background: #0ea5e9; }
     .footer { margin-top: 1.5rem; font-size: 12px; color: #64748b; }
     .error { color: #f87171; margin-top: 1rem; }
     .video-info { margin-top: 1.5rem; text-align: left; }
     .video-info img { width: 100%; border-radius: 8px; margin-bottom: 1rem; }
     .video-info h3 { margin: 0.5rem 0; color: #e2e8f0; }
     .formats { margin-top: 1rem; }
     .format-btn { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px; background: #334155; color: #e2e8f0; border: none; border-radius: 6px; margin-bottom: 8px; cursor: pointer; text-align: left; }
     .format-btn:hover { background: #475569; }
     .format-btn span { font-size: 13px; color: #94a3b8; }
     .badge { background: #38bdf8; color: #0f172a; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aashu Downloader Pro 🚀</h1>
        
        {% if not video_info %}
        <form method="POST" action="/info">
            <input type="text" name="url" placeholder="YouTube video URL daal bhai" required>
            <button type="submit">Get Formats</button>
        </form>
        {% endif %}

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        {% if video_info %}
        <div class="video-info">
            <img src="{{ video_info.thumbnail }}" alt="Thumbnail">
            <h3>{{ video_info.title }}</h3>
            <p><b>Duration:</b> {{ video_info.duration }}</p>
            
            <div class="formats">
                <h4>Select Format to Download:</h4>
                {% for f in video_info.formats %}
                <form method="POST" action="/download">
                    <input type="hidden" name="url" value="{{ video_info.webpage_url }}">
                    <input type="hidden" name="format_id" value="{{ f.format_id }}">
                    <button class="format-btn" type="submit">
                        <div>
                            {{ f.resolution }} {{ f.ext.upper() }}
                            {% if f.note %}<span class="badge">{{ f.note }}</span>{% endif %}
                        </div>
                        <span>{{ f.filesize }}</span>
                    </button>
                </form>
                {% endfor %}
            </div>
            
            <form method="GET" action="/">
                <button style="background: #475569; margin-top: 1rem;" type="submit">Download Another</button>
            </form>
        </div>
        {% endif %}
        
        <div class="footer">Made by Aashu | Render Free Tier = Slow</div>
    </div>
</body>
</html>
"""

def format_bytes(size):
    if size == 0 or size is None:
        return "Unknown"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return f"{s} {size_name[i]}"

def format_duration(seconds):
    if not seconds:
        return "Unknown"
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(sec)}s"
    return f"{int(minutes)}m {int(sec)}s"

def get_best_formats(formats):
    # Sirf video+audio wale ya audio-only formats lo
    result = []
    seen = set()
    
    # MP3 Audio sabse upar
    for f in formats:
        if f.get('vcodec') == 'none' and f.get('acodec')!= 'none' and f.get('ext') == 'm4a':
            key = 'audio'
            if key not in seen:
                result.append({
                    'format_id': 'bestaudio[ext=m4a]/bestaudio',
                    'resolution': 'MP3 Audio',
                    'ext': 'mp3',
                    'filesize': format_bytes(f.get('filesize') or f.get('filesize_approx')),
                    'note': 'Audio Only'
                })
                seen.add(key)
            break

    # Video formats: 144p se 4K tak
    for f in formats:
        if f.get('vcodec')!= 'none' and f.get('acodec')!= 'none': # Video + Audio combined
            height = f.get('height')
            if height:
                key = f"{height}p"
                if key not in seen:
                    note = ''
                    if height >= 2160: note = '4K'
                    elif height >= 1440: note = '2K'
                    elif height >= 1080: note = 'FHD'
                    elif height >= 720: note = 'HD'
                    
                    result.append({
                        'format_id': f['format_id'],
                        'resolution': f"{height}p",
                        'ext': f.get('ext', 'mp4'),
                        'filesize': format_bytes(f.get('filesize') or f.get('filesize_approx')),
                        'note': note
                    })
                    seen.add(key)

    # Sort: 4K > 1080p > 720p > 480p >...
    def sort_key(x):
        if 'Audio' in x['resolution']: return 10000
        return int(x['resolution'].replace('p',''))
    
    result.sort(key=sort_key, reverse=True)
    return result[:8] # Max 8 options dikhao

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/info", methods=["POST"])
def get_info():
    url = request.form.get("url")
    if not url:
        return render_template_string(HTML, error="URL daal bhai")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    if os.path.exists('/etc/secrets/cookies.txt'):
        ydl_opts['cookiefile'] = '/etc/secrets/cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_info = {
                'title': info.get('title', 'No Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration')),
                'webpage_url': info.get('webpage_url', url),
                'formats': get_best_formats(info.get('formats', []))
            }
            return render_template_string(HTML, video_info=video_info)

    except Exception as e:
        return render_template_string(HTML, error=f"Info nahi nikli: {str(e)}")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_id = request.form.get("format_id")
    
    # Extension decide karo
    ext = 'mp4'
    if 'audio' in format_id:
        ext = 'mp3'
    
    filename = f"{uuid.uuid4()}.{ext}"

    ydl_opts = {
        'format': format_id,
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }] if ext == 'mp3' else [],
    }
    if os.path.exists('/etc/secrets/cookies.txt'):
        ydl_opts['cookiefile'] = '/etc/secrets/cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # MP3 ke liye extension change ho jata hai
        if ext == 'mp3' and not os.path.exists(filename):
            filename = filename.replace('.mp4', '.mp3')

        @after_this_request
        def remove_file(response):
            try:
                os.remove(filename)
            except Exception:
                pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return render_template_string(HTML, error=f"Download fail: {str(e)}")

if __name__ == "__main__":
    app.run()
