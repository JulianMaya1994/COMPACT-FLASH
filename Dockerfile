FROM python:3.11

WORKDIR /app

# Dependencias del sistema (CRÍTICO)
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2 \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

