import asyncio
import websockets
import json
import random

URI = "ws://localhost:8000/ws/stream?client_id=virtual-bot-{}&room=telemetry"

async def virtual_client(bot_id: int):
    uri = URI.format(bot_id)
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🤖 Bot #{bot_id} connected to event mesh.")
            # Send a ping after 2 seconds
            await asyncio.sleep(2)
            await websocket.send(json.dumps({"action": "PING", "timestamp": "test"}))
            
            # Listen for 10 seconds of streaming data
            for _ in range(5):
                response = await websocket.recv()
                print(f"🤖 Bot #{bot_id} received: {response[:60]}...")
                await asyncio.sleep(2)
    except Exception as e:
        print(f"🤖 Bot #{bot_id} connection error: {e}")

async def main():
    print("🚀 Launching concurrent virtual client load simulation...")
    tasks = [virtual_client(i) for i in range(1, 6)] # Spawn 5 concurrent bots
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())