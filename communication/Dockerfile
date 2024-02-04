FROM python:3.8.5-alpine

WORKDIR /usr/src/app/communication

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]