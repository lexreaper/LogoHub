
import json
import os

import pika


def publish_appointment_created(
    appointment_id: int,
    patient_id: int,
    speech_therapist_id: int,
):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
        )
    )

    try:
        channel = connection.channel()

        channel.queue_declare(
            queue="appointment_notifications",
            durable=True,
        )

        message = {
            "event": "appointment_created",
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "speech_therapist_id": speech_therapist_id,
            "message": "Создана новая запись на приём",
        }

        channel.basic_publish(
            exchange="",
            routing_key="appointment_notifications",
            body=json.dumps(
                message,
                ensure_ascii=False
            ).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

        print(f"[RabbitMQ] Отправлено событие: {message}")

    finally:
        connection.close()
