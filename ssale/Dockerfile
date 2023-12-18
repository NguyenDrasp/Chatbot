FROM python:3.10-slim-bullseye
RUN pip install --upgrade pip
COPY ./ssale/requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY ./ssale .
EXPOSE 80
RUN python manage.py makemigrations
RUN python manage.py migrate