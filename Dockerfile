FROM python:3.9-alpine

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt