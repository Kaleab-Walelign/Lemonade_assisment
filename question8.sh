#!/bin/bash

SERVICE_NAME="php-fpm"
CPU_THRESHOLD=80

while true; do
  CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print ($2+$4)}')

  if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    echo "$(date) - CPU usage exceeded $CPU_THRESHOLD% ($CPU_USAGE%). Restarting $SERVICE_NAME..."

    if systemctl is-active --quiet "$SERVICE_NAME"; then
      systemctl restart "$SERVICE_NAME"
      echo "$(date) - $SERVICE_NAME restarted."
    else
      echo "$(date) - $SERVICE_NAME is not running. Starting..."
      systemctl start "$SERVICE_NAME"
      echo "$(date) - $SERVICE_NAME started."
    fi
  else
    echo "$(date) - CPU usage is $CPU_USAGE%. OK."
  fi
  sleep 60
done
