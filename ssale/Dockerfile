FROM python:3.10-slim-bullseye
RUN pip install --upgrade pip
WORKDIR /app
COPY ./ssale/requirements.txt .
RUN pip install -r requirements.txt
COPY ./ssale .
EXPOSE 80
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput