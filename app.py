from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    format_type = request.form.get('format', 'mp4')
    quality = request.form.get('quality', 'best')

    is_instagram = 'instagram.com' in video_url

    # INSTAGRAM KE LIYE SIMPLE AUR FAST SETTINGS:
    if is_instagram:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
        }
    # YOUTUBE KE LIYE CHROME IMPERSONATION:
    else:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'impersonate': 'chrome',
            'remote_components': 'ejs:github',
        }
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best/best'
            ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

            base, ext = os.path.splitext(filename)
            final_filename = base + ('.mp3' if format_type == 'mp3' else '.mp4')

            if os.path.exists(filename) and filename != final_filename:
                os.rename(filename, final_filename)

        return send_file(final_filename, as_attachment=True)
    except Exception as e:
        return f"NexLoad Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
