from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import subprocess

app = Flask(__name__)
DOWNLOAD_PATH = "downloads"

# Criar pasta de downloads se não existir
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Caminho do FFmpeg no Railway (caso precise indicar manualmente)
FFMPEG_PATH = "/usr/bin/ffmpeg"
FFPROBE_PATH = "/usr/bin/ffprobe"

@app.route("/")
def index():
    return render_template("index.html")


def baixar_video(url, formato, plataforma):
    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
            "ffmpeg_location": FFMPEG_PATH,
            "merge_output_format": "mp4" if formato == "mp4" else None,
        }

        # Se for MP3, configurar conversão automática
        if formato == "mp3":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            })
        else:
            ydl_opts.update({
                "format": "bestvideo+bestaudio/best" if plataforma == "YouTube" else "best",
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Ajustar extensão se for MP3 e for Facebook ou Instagram
        if formato == "mp3" and plataforma in ["Facebook", "Instagram"]:
            mp3_filename = filename.rsplit(".", 1)[0] + ".mp3"
            subprocess.run([FFMPEG_PATH, "-i", filename, "-vn", "-acodec", "libmp3lame", "-q:a", "2", mp3_filename])
            os.remove(filename)  # Remove o arquivo original
            filename = mp3_filename

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Erro ao baixar: {e}", 500


@app.route("/download/youtube", methods=["POST"])
def download_youtube():
    url = request.form.get("url")
    formato = request.form.get("formato")
    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return "Erro: URL inválida para YouTube!", 400
    return baixar_video(url, formato, "YouTube")


@app.route("/download/facebook", methods=["POST"])
def download_facebook():
    url = request.form.get("url")
    formato = request.form.get("formato")
    if not url or "facebook.com" not in url:
        return "Erro: URL inválida para Facebook!", 400
    return baixar_video(url, formato, "Facebook")


@app.route("/download/instagram", methods=["POST"])
def download_instagram():
    url = request.form.get("url")
    formato = request.form.get("formato")
    if not url or "instagram.com" not in url:
        return "Erro: URL inválida para Instagram!", 400
    return baixar_video(url, formato, "Instagram")


if __name__ == "__main__":
    app.run(debug=True)
