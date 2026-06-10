FROM python:3.12-slim

WORKDIR /app

COPY dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app

EXPOSE 8050

CMD ["python", "app/main.py"]
