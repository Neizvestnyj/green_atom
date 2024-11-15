FROM nginx:latest

# Устанавливаем netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

RUN mkdir -p /home/web/default

# Добавляем скрипт ожидания приложения
COPY wait-for-it.sh /usr/bin/wait-for-it.sh
RUN chmod +x /usr/bin/wait-for-it.sh

# Запуск NGINX через скрипт wait-for-it.sh
CMD ["/bin/bash", "-c", "/usr/bin/wait-for-it.sh organisation_service 8000 -- /usr/bin/wait-for-it.sh storage_service 8001 -- nginx -g 'daemon off;'"]
