from flask import Flask, render_template, request, send_file, make_response
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# कुकीज़ फ़ाइल का पक्का पाथ
COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    format_type = request.form.get('format', 'mp4')

    if not video_url:
        return "Please provide a valid video link."

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    # कुकीज़ जोड़ना (यही सबसे ज़रूरी चीज़ मिस थी)
    if os.path.exists(COOKIE_FILE):
        ydl_opts['cookiefile'] = COOKIE_FILE

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
