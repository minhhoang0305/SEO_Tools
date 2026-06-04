FROM python:3.11-slim

WORKDIR /app

# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY seo-audit-worker/requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

COPY seo-audit-worker/ .

CMD ["python", "main.py"]
