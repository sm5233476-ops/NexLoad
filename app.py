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

    # Basic Options
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'ffmpeg_location': './ffmpeg_bin/bin', 
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',
        # YouTube ko lagega ye asli browser hai
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
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
        # QUALITY LOGIC (Solid Version):
        # Hum sirf height bata rahe hain, format (mp4/webm) YouTube ko khud chunne de rahe hain
        if quality == 'best':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            # Agar user ne 1080p ya 720p chuna hai toh usse niche ki best quality uthayega
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
        
        # Ye line kisi bhi format (WebM/VP9) ko jodd kar final MP4 bana degi
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Agar file merge hone ke baad extension change ho jaye (.mkv se .mp4), toh use handle karein
            base, ext = os.path.splitext(filename)
            final_filename = base + ('.mp3' if format_type == 'mp3' else '.mp4')
            
            # Agar asli file ka naam alag hai toh rename karein (Safe check)
            if os.path.exists(filename) and filename != final_filename:
                os.rename(filename, final_filename)
                
        return send_file(final_filename, as_attachment=True)
    except Exception as e:
        return f"NexLoad Error: {str(e)}. Try another quality or link."

if __name__ == '__main__':
    app.run(debug=True)
