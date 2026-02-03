#!/usr/bin/env python3

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/coffee/"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Send a test message
            test_message = {
                "test": "Hello WebSocket!"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for a response (optional)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received (this is normal)")
            
            print("🎉 WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing WebSocket connection...")
    asyncio.run(test_websocket()) 