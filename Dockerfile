# Usar imagem oficial do Python
FROM python:3.9

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Definir a variável de ambiente para Flask
ENV FLASK_APP=app.py

# Expor a porta usada pelo Flask
EXPOSE 8080

# Comando para rodar o app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
