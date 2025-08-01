FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir streamlit requests

COPY . /app

CMD ["streamlit", "run", "dashboards/add_player.py", "--server.port=8501", "--server.address=0.0.0.0"]
