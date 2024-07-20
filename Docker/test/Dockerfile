# /Docker/test/Dockerfile
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /test

# Копируем все директории и файлы, кроме /app
COPY ./test /test
COPY ./Docker /Docker
COPY ./.gitlab-ci.yml /.gitlab-ci.yml
COPY ./docker-compose.yml /docker-compose.yml
COPY ./requirements.txt /requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /requirements.txt
