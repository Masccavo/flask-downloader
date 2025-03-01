from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_PATH = "downloads"

# Criar pasta de downloads se não existir
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Configurar FFmpeg portátil
FFMPEG_PATH = os.path.abspath("ffmpeg")
os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# Caminho dos cookies (se existir)
COOKIES_FILE = "cookies.txt"


@app.route("/")
def index():
    return render_template("index.html")


def baixar_video(url, formato, plataforma):
    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
            "ffmpeg_location": FFMPEG_PATH,
        }

        # Se o arquivo cookies.txt existir, adicionamos ao yt-dlp
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

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

        # Baixar o arquivo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Ajustar extensão se for MP3
        if formato == "mp3":
            filename = filename.rsplit(".", 1)[0] + ".mp3"

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
