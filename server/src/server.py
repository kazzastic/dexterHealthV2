from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from dataclasses import dataclass
import json
import uuid
from schemas.User import UserCreate, UserLogin
from database import SessionLocal
from sqlalchemy.orm import Session
from models.User import User
from models.Chat import Chat
import bcrypt
from passwords.passhash import hash_password

@dataclass 
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        id = str(uuid.uuid4())  
        self.active_connections[id] = websocket

        # Send back the client ID upon connection
        await self.send_message_to(websocket, json.dumps({
            "type": "connect",
            "id": id
        }))

    def disconnect(self, websocket: WebSocket):
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        return id
    
    def find_connection_id(self, websocket: WebSocket):
        val_list = list(self.active_connections.values())
        key_list = list(self.active_connections.keys())
        id = val_list.index(websocket)
        return key_list[id]
    
    async def send_message_to(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

connection_manager = ConnectionManager()

@app.websocket("/messaging")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            data_json = json.loads(data)

            friend_name = data_json["friend_name"]

            try:
                friend_id = db.query(User).filter(User.username == friend_name).first().id
            except Exception as e:
                raise HTTPException(status_code=404, detail="User not found")

            # Broadcast the received message back to all clients
            await connection_manager.broadcast(json.dumps({
                "type": "message",
                "message": data
            }))

            new_chat = Chat(sender_id = data_json["client_id"], receiver_id = friend_id, message = data_json["message"])
            db.add(new_chat)
            db.commit()

            #in order to keep the connection alive
            await websocket.send_text(json.dumps({"type": "ping"}))

    except WebSocketDisconnect:
        id = connection_manager.disconnect(websocket)
        # Notify all clients of the disconnection
        await connection_manager.broadcast(json.dumps({
            "type": "disconnected", 
            "id": id
        }))

@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    #User already exists logic
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash the password
    hashed_password = hash_password(user.password)


    new_user = User(username=user.username, password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id, 
        "username": new_user.username
    }

@app.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Fetch the user from the database
    db_user = db.query(User).filter(User.username == user.username).first()

    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify the password using bcrypt
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    #lets fetch all the chat messages from this sender and reciever
    user_chats = db.query(Chat).filter(
        (Chat.sender_id == db_user.id) | (Chat.receiver_id == db_user.id)
    ).all()

    chat_history = []
    for chat in user_chats:
        sender = db.query(User).filter(User.id == chat.sender_id).first().username
        receiver = db.query(User).filter(User.id == chat.receiver_id).first().username
        chat_history.append({
            "sender": sender,
            "receiver": receiver,
            "message": chat.message
        })

    return {
        "message": "Login Successful",
        "id": db_user.id,
        "username": db_user.username,
        "chat_history": chat_history
    }