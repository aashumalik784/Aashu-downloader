from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "yt-dlp API is running ✅"

@app.route('/api')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url parameter missing"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    formats.append({
                        'quality': f.get('format_note') or f.get('resolution'),
                        'ext': f.get('ext'),
                        'url': f.get('url')
                    })
            
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "video_formats": formats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
