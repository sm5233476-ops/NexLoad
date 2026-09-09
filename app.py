from flask import Flask, render_template, request, send_file, redirect, make_response
import yt_dlp
import requests
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Public Cobalt Instances (Zero Bot Block)
COBALT_INSTANCES = [
    "https://cobalt.canine.tools",
    "https://cobalt.meowing.de",
    "https://api.cobalt.tools"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    format_type = request.form.get('format', 'mp4')
    quality = request.form.get('quality', 'best')

    is_youtube = ('youtube.com' in video_url) or ('youtu.be' in video_url)

    # 1. YOUTUBE ENGINE (HIGH-SPEED API - NO BOT CHECKS)
    if is_youtube:
        payload = {
            "url": video_url,
            "videoQuality": "1080" if quality == "1080" else ("720" if quality == "720" else "max"),
            "downloadMode": "audio" if format_type == "mp3" else "auto"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        for instance in COBALT_INSTANCES:
            try:
                res = requests.post(instance, json=payload, headers=headers, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    dl_url = data.get('url')
                    if dl_url:
                        resp = make_response(redirect(dl_url))
                        resp.set_cookie('download_done', 'yes', path='/')
                        return resp
            except Exception:
                continue

        return "NexLoad Error: YouTube servers are busy. Please try again in a few seconds."

    # 2. INSTAGRAM ENGINE (LOCAL VPS ENGINE - 100% WORKING)
    else:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)

                base, ext = os.path.splitext(filename)
                final_filename = base + ('.mp3' if format_type == 'mp3' else '.mp4')

                if os.path.exists(filename) and filename != final_filename:
                    os.rename(filename, final_filename)

            resp = make_response(send_file(final_filename, as_attachment=True))
            resp.set_cookie('download_done', 'yes', path='/')
            return resp
        except Exception as e:
            return f"NexLoad Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
