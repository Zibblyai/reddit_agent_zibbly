FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install praw openai gspread google-auth requests

CMD ["python", "reddit_agent.py"]
