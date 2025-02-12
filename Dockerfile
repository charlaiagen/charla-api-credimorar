# Imagem python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar os arquivos de requisitos
COPY pyproject.toml .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Usa um ambiente virtual
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies using uv
RUN pip install --no-cache-dir uv && \
    uv pip install --no-cache .

# Copy custom Tesseract configuration
RUN mkdir -p /usr/share/tesseract-ocr/tessdata/configs && \
    echo "tessedit_char_whitelist ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.@_-☐☑✓✔×\ntessedit_pageseg_mode 6\ntessedit_ocr_engine_mode 3\npreserve_interword_spaces 1\ntextord_min_linesize 2.5\ntextord_space_size_is_variable 1\ntextord_preserve_minimums 1\ntessedit_class_miss_scale 0.9\ntessedit_certainty_threshold -1.0" > /usr/share/tesseract-ocr/tessdata/configs/custom

# Copy application code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Set environment variable for Tesseract path
ENV TESSERACT_PATH=/usr/bin/tesseract

# Command to run the application
CMD ["streamlit", "run", "app.py"]
