FROM python:3.11

WORKDIR /fish-bot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .env .
COPY ./app ./app

CMD ["python", "./app/main.py"]