FROM python:3.10-slim

WORKDIR /app

# Install Redis
RUN apt-get update && \
    apt-get install -y redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Create startup script
RUN echo '#!/bin/bash\nservice redis-server start\nexec uvicorn main:app --host 0.0.0.0 --port 80' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 80
CMD ["/app/start.sh"]
