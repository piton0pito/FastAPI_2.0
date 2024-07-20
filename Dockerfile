# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем gunicorn
RUN pip install gunicorn

# Копируем весь проект в рабочую директорию контейнера
COPY . .

# Запуск приложения с помощью gunicorn
# Предполагаем, что в 'main.py' есть приложение, например, 'app'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]

