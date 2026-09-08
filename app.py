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

    # Base Options
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'ffmpeg_location': './ffmpeg_bin/bin', 
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
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
        # QUALITY LOGIC (Super-Safe Version)
        if quality == 'best':
            # Har haal mein best uthao
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            # Agar chuna hua resolution nahi mila, toh usse niche wala best file uthao
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best[height<={quality}]/best'
        
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Extension Handling
            base, ext = os.path.splitext(filename)
            final_filename = base + ('.mp3' if format_type == 'mp3' else '.mp4')
            
            if os.path.exists(filename) and filename != final_filename:
                os.rename(filename, final_filename)
                
        return send_file(final_filename, as_attachment=True)
    except Exception as e:
        # Agar koi format issue ho, toh ye last try karega bilkul basic video ke liye
        return f"NexLoad Error: {str(e)}. Tip: Try 'Best Quality' or another video."

if __name__ == '__main__':
    app.run(debug=True)
