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
    video_url = request.form.get('url')
    format_type = request.form.get('format')
    quality = request.form.get('quality')

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'ffmpeg_location': './ffmpeg_bin/bin', 
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',
        # IPHONE LOGIC: YouTube ko lagega ye iPhone App se request aa rahi hai
        'extractor_args': {'youtube': {'player_client': ['ios']}},
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    }

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
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
        
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
        return f"NexLoad Error: {str(e)}. Tip: Try 720p or check another video."

if __name__ == '__main__':
    app.run(debug=True)
