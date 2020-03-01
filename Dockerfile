FROM python:3.8

RUN apt update
RUN apt install -y libpq-dev python3-dev build-essential postgresql-server-dev-all

# Рабочая директория внутри контейнера
WORKDIR /app

ADD ./app /app

COPY requirements.txt /app 
RUN pip install -r requirements.txt

EXPOSE 80

CMD python main.py
