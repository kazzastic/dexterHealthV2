import asyncio
import websockets
import json

async def connect_to_server():
    uri = "ws://localhost:8000/messaging"  # WebSocket server URL

    async with websockets.connect(uri) as websocket:
        # Receive the client ID assigned by the server
        connect_msg = await websocket.recv()
        connect_data = json.loads(connect_msg)
        client_id = connect_data.get("id")
        print(f"Connected with client ID: {client_id}")

        async def send_message():
            while True:
                # Use asyncio.to_thread to avoid blocking on input
                message = await asyncio.to_thread(input, f"Client {client_id}: Enter message: ")
                
                await websocket.send(json.dumps({
                    "client_id": client_id,
                    "message": message
                }))

        async def receive_message():
            while True:
                try:
                    # Receive and display message from the WebSocket server
                    response = await websocket.recv()
                    data = json.loads(response)

                    if data.get("type") == "message":
                        # The message itself is a JSON string, so we need to parse it
                        message_content = json.loads(data.get("message", ""))
                        sender_id = message_content.get("client_id")
                        message_text = message_content.get("message")
                        
                        print(f"Message from {sender_id}: {message_text}")
                    elif data.get("type") == "disconnected":
                        disconnected_id = data.get("id")
                        print(f"Client {disconnected_id} has disconnected.")
                except websockets.ConnectionClosed:
                    print("Connection closed.")
                    break

        # Run both sending and receiving tasks concurrently
        receive_task = asyncio.create_task(receive_message())
        send_task = asyncio.create_task(send_message())
        await asyncio.gather(send_task, receive_task)

if __name__ == "__main__":
    asyncio.run(connect_to_server())