FROM python:3.13.1
LABEL mainteiner="asakira884@gmai.com"
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt && rm -rf /var/lib/apt/lists/*
CMD ["python", "main.py"]