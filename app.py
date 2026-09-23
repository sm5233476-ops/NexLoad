from flask import Flask, render_template, request, send_file, make_response
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.abspath('downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# FFmpeg Path
ffmpeg_dir = os.path.abspath('./ffmpeg_bin/bin')
if os.path.exists(ffmpeg_dir):
    os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    format_type = request.form.get('format', 'mp4')

    if not video_url:
        return "Please provide a valid link."

    ffmpeg_loc = './ffmpeg_bin/bin' if os.path.exists('./ffmpeg_bin/bin') else None

    # Clean & Direct Engine (uses video ID to avoid filename crashes)
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
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
            video_id = info.get('id', 'video')

            if format_type == 'mp3':
                final_file = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp3")
                out_name = f"NexLoad_{video_id}.mp3"
            else:
                final_file = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")
                out_name = f"NexLoad_{video_id}.mp4"

        resp = make_response(send_file(final_file, as_attachment=True, download_name=out_name))
        resp.set_cookie('download_done', 'yes', path='/')
        return resp

    except Exception as e:
        return f"NexLoad Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
