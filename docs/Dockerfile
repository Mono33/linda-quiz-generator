# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY linda_test_eval2.py .
COPY README_LINDA_QUIZ.md .
COPY data_input/ ./data_input/

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama server in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for Ollama to start..."\n\
sleep 10\n\
\n\
# Pull the mistral model\n\
echo "Pulling Mistral model..."\n\
ollama pull mistral\n\
\n\
# Start Streamlit app\n\
echo "Starting Streamlit app..."\n\
streamlit run linda_test_eval2.py --server.port=7860 --server.address=0.0.0.0\n\
' > /app/start.sh

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 7860

# Start the application
CMD ["/app/start.sh"] 