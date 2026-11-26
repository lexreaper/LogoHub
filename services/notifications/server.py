import asyncio
import json
import os
from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

QUEUE_NAME = "appointment_notifications"
connected_clients: set[WebSocket] = set()


async def broadcast_notification(data: dict):
    if not connected_clients:
        print("[WebSocket] Нет подключённых клиентов")
        return

    for client in list(connected_clients):
        try:
            await client.send_json(data)
            print("[WebSocket] Уведомление отправлено")
        except Exception as exc:
            print(f"[WebSocket] Ошибка отправки: {exc}")
            connected_clients.discard(client)


async def consume_events(queue):
    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():
                data = json.loads(message.body.decode("utf-8"))
                print(f"[RabbitMQ] Получено событие: {data}")
                await broadcast_notification(data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await aio_pika.connect_robust(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        login=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASSWORD", "guest"),
    )
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        print(f"[RabbitMQ] Ожидание сообщений: {QUEUE_NAME}")
        task = asyncio.create_task(consume_events(queue))
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print("[WebSocket] Клиент подключился")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("[WebSocket] Клиент отключился")
    finally:
        connected_clients.discard(websocket)
