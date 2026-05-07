from flask import Flask, request, render_template_string, send_file, after_this_request
import yt_dlp
import os
import uuid

app = Flask(__name__)

# HTML Frontend
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aashu Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 90%; max-width: 500px; text-align: center; }
        h1 { color: #38bdf8; margin-bottom: 1.5rem; }
        input { width: 100%; padding: 12px; margin-bottom: 1rem; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: white; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #38bdf8; color: #0f172a; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0ea5e9; }
        .footer { margin-top: 1.5rem; font-size: 12px; color: #64748b; }
        .error { color: #f87171; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aashu Downloader 🚀</h1>
        <form method="POST" action="/download">
            <input type="text" name="url" placeholder="YouTube video URL daal bhai" required>
            <button type="submit">Download Video</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <div class="footer">Made by Aashu | Render Free Tier = Slow</div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return render_template_string(HTML, error="URL daal bhai")

    # Unique filename taaki multiple download clash na kare
    filename = f"{uuid.uuid4()}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # MP4 prefer karo
        'outtmpl': filename,
        'cookiefile': '/etc/secrets/cookies.txt',  # Render secret file path
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as
