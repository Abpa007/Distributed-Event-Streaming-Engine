import asyncio
import websockets
import json

URI = "ws://localhost:8000/ws/stream?client_id=persistent-bot-{}&room=telemetry"

async def persistent_bot(bot_id: int):
    uri = URI.format(bot_id)
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🤖 Persistent Bot #{bot_id} connected and staying alive...")
            # Stay connected in a loop listening for data
            while True:
                response = await websocket.recv()
                print(f"🤖 Bot #{bot_id} received stream packet.")
    except Exception as e:
        print(f"🤖 Bot #{bot_id} disconnected: {e}")

async def main():
    print("🚀 Launching persistent client load simulation (Press Ctrl+C to stop)...")
    tasks = [persistent_bot(i) for i in range(1, 4)] # 3 persistent bots
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Simulation stopped.")