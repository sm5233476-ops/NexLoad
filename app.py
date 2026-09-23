from flask import Flask, render_template, request, send_file, make_response
import yt_dlp
import requests
import re
import os
import subprocess

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Ensure FFmpeg is in system PATH
ffmpeg_dir = os.path.abspath('./ffmpeg_bin/bin')
if os.path.exists(ffmpeg_dir):
    os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"

def extract_instagram_direct(reel_url):
    """Bypasses Instagram 429 rate limit using embed extraction"""
    match = re.search(r'instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_-]+)', reel_url)
    if not match:
        return None, None
    shortcode = match.group(1)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.instagram.com/',
    }

    # 1. Instagram Embed Strategy (No 429 Rate-Limits)
    embed_targets = [
        f"https://www.instagram.com/reel/{shortcode}/embed/captioned/",
        f"https://www.instagram.com/p/{shortcode}/embed/captioned/",
        f"https://www.instagram.com/reel/{shortcode}/embed/",
    ]
    for url in embed_targets:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                # Video src dhoondhein
                vids = re.findall(r'<video[^>]+src="([^">]+)"', res.text)
                if vids:
                    return vids[0].replace('&amp;', '&'), shortcode
                
                # JSON data dhoondhein
                json_vids = re.findall(r'"video_url"\s*:\s*"([^"]+)"', res.text)
                if json_vids:
                    clean = json_vids[0].replace(r'\/', '/').encode().decode('unicode_escape')
                    return clean, shortcode
        except Exception:
            continue

    # 2. Backup Engine Fallback
    backup_apis = [
        "https://api.cobalt.tools",
        "https://cobalt-backend.canine.tools"
    ]
    for api in backup_apis:
        try:
            c_res = requests.post(api, json={"url": reel_url}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, timeout=8)
            if c_res.status_code == 200:
                dl = c_res.json().get('url')
                if dl:
                    return dl, shortcode
        except Exception:
            continue

    return None, shortcode

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    format_type = request.form.get('format', 'mp4')

    if not video_url:
        return "Please provide a valid Instagram link."

    # PEHLE 429-BYPASS ENGINE TRY KAREIN:
    direct_url, shortcode = extract_instagram_direct(video_url)

    if direct_url and shortcode:
        try:
            r = requests.get(direct_url, stream=True, timeout=30)
            if r.status_code == 200:
                mp4_file = os.path.join(DOWNLOAD_FOLDER, f"NexLoad_{shortcode}.mp4")
                with open(mp4_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)

                if format_type == 'mp3':
                    mp3_file = os.path.join(DOWNLOAD_FOLDER, f"NexLoad_{shortcode}.mp3")
                    ffmpeg_bin = './ffmpeg_bin/bin/ffmpeg' if os.path.exists('./ffmpeg_bin/bin/ffmpeg') else 'ffmpeg'
                    
                    subprocess.run([
                        ffmpeg_bin, '-y', '-i', mp4_file, '-vn',
                        '-acodec', 'libmp3lame', '-q:a', '2', mp3_file
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    final_out = mp3_file if os.path.exists(mp3_file) else mp4_file
                else:
                    final_out = mp4_file

                resp = make_response(send_file(final_out, as_attachment=True))
                resp.set_cookie('download_done', 'yes', path='/')
                return resp
        except Exception:
            pass

    # AGAR KISI WAJAH SE BYPASS NA CHALE, TOH FALLBACK TO YT-DLP:
    ffmpeg_loc = './ffmpeg_bin/bin' if os.path.exists('./ffmpeg_bin/bin') else None
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }
    if ffmpeg_loc:
        ydl_opts['ffmpeg_location'] = ffmpeg_loc

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

            base, ext = os.path.splitext(filename)
            if format_type == 'mp3':
                final_filename = base + '.mp3'
            else:
                final_filename = base + '.mp4'

            if os.path.exists(filename) and filename != final_filename:
                os.rename(filename, final_filename)

        resp = make_response(send_file(final_filename, as_attachment=True))
        resp.set_cookie('download_done', 'yes', path='/')
        return resp

    except Exception as e:
        return f"NexLoad Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
