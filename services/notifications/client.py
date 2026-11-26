import asyncio
import json
import os

import websockets


async def main():
    url = os.getenv("NOTIFICATION_WS_URL", "ws://127.0.0.1:8001/ws")
    async with websockets.connect(url) as websocket:
        print("[Client] Подключение установлено")
        print("[Client] Ожидание уведомлений...")
        async for message in websocket:
            data = json.loads(message)
            print("\nПолучено уведомление:")
            print(f"Событие: {data['event']}")
            print(f"ID записи: {data['appointment_id']}")
            print(f"ID пациента: {data['patient_id']}")
            print(f"ID логопеда: {data['speech_therapist_id']}")
            print(f"Сообщение: {data['message']}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nРабота завершена")
