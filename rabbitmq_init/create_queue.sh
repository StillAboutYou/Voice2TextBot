#!/bin/bash

# Ожидание, пока RabbitMQ станет доступен
until rabbitmqctl status; do
  echo "Waiting for RabbitMQ to be ready..."
  sleep 5
done

# Создание очереди
rabbitmqadmin -u "${RABBITMQ_USER}" -p "${RABBITMQ_PASSWORD}" declare queue name="${RABBITMQ_QUEUE}" durable=true

