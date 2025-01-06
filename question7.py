import os
import time
import requests
from prometheus_client import start_http_server, Gauge

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", "15672")

QUEUE_MESSAGES = Gauge("rabbitmq_individual_queue_messages", "Total messages in queue", ["host", "vhost", "name"])
QUEUE_MESSAGES_READY = Gauge("rabbitmq_individual_queue_messages_ready", "Ready messages in queue", ["host", "vhost", "name"])
QUEUE_MESSAGES_UNACKNOWLEDGED = Gauge("rabbitmq_individual_queue_messages_unacknowledged", "Unacknowledged messages in queue", ["host", "vhost", "name"])

def fetch_queue_metrics():
    url = f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/queues"
    try:
        response = requests.get(url, auth=(RABBITMQ_USER, RABBITMQ_PASSWORD), timeout=10)
        response.raise_for_status()  
        queues = response.json()

        for queue in queues:
            vhost = queue.get("vhost", "default")
            name = queue.get("name")
            messages = queue.get("messages", 0)
            messages_ready = queue.get("messages_ready", 0)
            messages_unacknowledged = queue.get("messages_unacknowledged", 0)

            QUEUE_MESSAGES.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages)
            QUEUE_MESSAGES_READY.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages_ready)
            QUEUE_MESSAGES_UNACKNOWLEDGED.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages_unacknowledged)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RabbitMQ metrics: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    start_http_server(8000)
    while True:
        fetch_queue_metrics()
        time.sleep(10)
