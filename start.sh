#!/bin/bash

# Criar um diretório para armazenar o FFmpeg
mkdir -p ffmpeg
cd ffmpeg

# Baixar FFmpeg portátil
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz -o ffmpeg.tar.xz

# Extrair os arquivos
tar -xf ffmpeg.tar.xz --strip-components=1

# Voltar ao diretório do projeto
cd ..

# Iniciar o Flask com Gunicorn
gunicorn app:app