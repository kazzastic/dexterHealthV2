import asyncio
import websockets
import json
import requests

API_URL = "http://localhost:8000/"  # API endpoint for registration

async def connect_to_server(client_id, friend_name):
    uri = "ws://localhost:8000/messaging"  # WebSocket server URL

    async with websockets.connect(uri) as websocket:
        print(f"Connected with client ID: {client_id}")

        async def send_message():
            while True:
                message = await asyncio.to_thread(input, f"Client {client_id}: Enter message: ")
                await websocket.send(json.dumps({
                    "client_id": client_id,
                    "friend_name": friend_name,
                    "message": message
                }))

        async def receive_message():
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)

                    if data.get("type") == "message":
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

        receive_task = asyncio.create_task(receive_message())
        send_task = asyncio.create_task(send_message())
        await asyncio.gather(send_task, receive_task)


def register_user():
    print("Registering a new user...")
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Send POST request to the API to register the user
    REGISTER_URL = API_URL + "register"
    response = requests.post(REGISTER_URL, json={"username": username, "password": password})

    if response.status_code == 200:
        user_data = response.json()
        print(f"Registration successful. Your user ID is: {user_data['id']}")
        return user_data['id']
    else:
        print(f"Error: ", response.json().get("details"))
        return None
    
def login_user():
    print("Logging in the user...")
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Send a POST req to the API server to login the user
    LOGIN_URL = API_URL + "login"
    response = requests.post(LOGIN_URL, json={"username": username, "password": password})

    if response.status_code == 200:
        user_data = response.json()
        print(f"Login was successful. Your user ID is: {user_data['id']}")
        return user_data['id']
    else:
        print(f"Error: ", response.json().get("details"))
        return None


if __name__ == "__main__":
    choice = input("Enter 1 to register: or Enter 2 to login...")

    if choice == "1":
        # User registration
        client_id = register_user()
        if client_id:
            friend_name = input("Enter your friend's username: ")
            # If registration is successful, connect to the WebSocket server
            asyncio.run(connect_to_server(client_id, friend_name))

    else:
        client_id = login_user()
        if client_id:
            friend_name = input("Enter your friend's username: ")
            # If registration is successful, connect to the WebSocket server
            asyncio.run(connect_to_server(client_id, friend_name))
