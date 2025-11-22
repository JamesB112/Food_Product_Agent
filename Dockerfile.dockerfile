# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip

# Install required Python packages
RUN pip install --no-cache-dir \
    streamlit>=1.25.0 \
    requests>=2.31.0 \
    google-cloud-aiplatform>=1.126.1 \
    google-auth>=2.23.0 \
    google-genai>=0.6.0 \
    pandas>=2.1.0

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables for Google Cloud / Vertex AI
ENV GOOGLE_CLOUD_PROJECT=your-project-id
ENV GOOGLE_CLOUD_LOCATION=global
ENV GOOGLE_GENAI_USE_VERTEXAI=True

# Streamlit config to avoid browser popups
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# Run the Streamlit app
CMD ["streamlit", "run", "streamlit_app_markdown.py"]
