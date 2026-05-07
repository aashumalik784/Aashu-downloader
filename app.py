from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aashu Downloader — Multi API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 1rem; }
.container { background: #1e293b; padding: 2rem; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.4); width: 100%; max-width: 600px; }
        h1 { color: #38bdf8; margin-bottom: 0.5rem; text-align: center; font-size: 2rem; }
.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 1.5rem; }
        input { width: 100%; padding: 14px; margin-bottom: 1rem; border: 2px solid #334155; border-radius: 10px; background: #0f172a; color: #e2e8f0; font-size: 15px; }
        input:focus { outline: none; border-color: #38bdf8; }
        button { width: 100%; padding: 14px; background: #38bdf8; color: #0f172a; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 16px; }
        button:hover { background: #0ea5e9; }
.footer { margin-top: 1.5rem; font-size: 12px; color: #64748b; text-align: center; }
.error { color: #f87171; margin-top: 1rem; padding: 12px; background: #7f1d1d30; border-radius: 8px; text-align: center; }
.video-info { margin-top: 1.5rem; text-align: center; }
.video-info img { width: 100%; border-radius: 12px; margin-bottom: 1rem; max-height: 320px; object-fit: cover; }
.video-info h3 { margin: 0.5rem 0; color: #e2e8f0; font-size: 18px; line-height: 1.4; }
.download-btn { display: block; width: 100%; padding: 14px; background: #22c55e; color: #0f172a; border: none; border-radius: 10px; margin-top: 1rem; cursor: pointer; text-align: center; font-weight: 700; text-decoration: none; }
.download-btn:hover { background: #16a34a; }
.back-btn { background: #475569; margin-top: 1rem; }
.back-btn:hover { background: #64748b; }
.badge { background: #22c55e; color: #0f172a; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; display: inline-block; margin-bottom: 1rem; }
.server { font-size: 11px; color: #64748b; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aashu Downloader 🚀</h1>
        <p class="subtitle">Multi-Server Technology — Ek band to dusra chalega</p>
        
        {% if not video_info %}
        <span class="badge">✅ YouTube, Insta, FB, TikTok, X, Pinterest</span>
        <form method="POST" action="/get">
            <input type="text" name="url" placeholder="Video link yahan paste karo..." required autocomplete="off">
            <button type="submit">Download Link Banao</button>
        </form>
        {% endif %}

        {% if error %}
            <p class="error">{{ error }}</p>
            <form method="GET" action="/">
                <button class="back-btn" type="submit">Wapas Jao</button>
            </form>
        {% endif %}

        {% if video_info %}
        <div class="video-info">
            {% if video_info.thumbnail %}
            <img src="{{ video_info.thumbnail }}" alt="Thumbnail" onerror="this.style.display='none'">
            {% endif %}
            <h3>{{ video_info.title }}</h3>
            
            <a href="{{ video_info.url }}" class="download-btn" target="_blank" rel="noopener">
                ⬇️ Download Now — {{ video_info.quality }}
            </a>
            <p class="server">Server: {{ video_info.server }}</p>
            
            <form method="GET" action="/">
                <button class="back-btn" type="submit">⬅️ Dusra Video Download Karo</button>
            </form>
        </div>
        {% endif %}
        
        <div class="footer">Tera IP safe hai | 3 Backup Servers | Auto Switch</div>
    </div>
</body>
</html>
"""

# 3 alag Cobalt instances — ek fail to dusra try hoga
COBALT_APIS = [
    "https://co.wuk.sh/api/json",
    "https://cobalt.ryanrd.id/api/json", 
    "https://api.cobalt.tools/api/json"
]

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/get", methods=["POST"])
def get_download():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template_string(HTML, error="Link daal bhai")
    
    headers = {
        "Accept": "application/json", 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "url": url,
        "vQuality": "1080",
        "aFormat": "mp3", 
        "isAudioOnly": False,
        "disableMetadata": False
    }
    
    last_error = "Sabhi servers busy hain. 1 min baad try karo"
    
    # 3 servers try karo ek ek karke
    for api_url in COBALT_APIS:
        try:
            r = requests.post(api_url, json=payload, headers=headers, timeout=25)
            res = r.json()
            
            if res.get('status') == 'error':
                last_error = f"Error: {res.get('text', 'Link support nahi hai')}"
                continue
            
            if res.get('status') in ['redirect', 'stream', 'tunnel', 'success']:
                video_info = {
                    'title': res.get('text', 'Video Download Ready'),
                    'thumbnail': res.get('thumbnail', ''),
                    'url': res['url'],
                    'quality': 'Best Quality',
                    'server': api_url.split('/')[2]
                }
                return render_template_string(HTML, video_info=video_info)
                
        except requests.exceptions.Timeout:
            last_error = "Server timeout. Dusra server try kar raha hun..."
            continue
        except Exception as e:
            last_error = f"Server fail: {str(e)[:50]}"
            continue
    
    return render_template_string(HTML, error=last_error)

if __name__ == "__main__":
    app.run(debug=False)
