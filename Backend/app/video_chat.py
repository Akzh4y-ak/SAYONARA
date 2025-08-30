import json, random, string
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional

router = APIRouter()

active_users: Dict[str, WebSocket] = {}
pairs: Dict[str, str] = {}
waiting_queue = []

def random_suffix(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def send_message(user_name: str, message: dict):
    ws = active_users.get(user_name)
    if ws:
        try:
            await ws.send_text(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send message to {user_name}: {e}")

async def pair_users():
    global waiting_queue
    if len(waiting_queue) < 2:
        return
    
    while len(waiting_queue) >= 2:
        u1 = waiting_queue.pop(0)
        u2 = waiting_queue.pop(0)
        
        if u1 not in active_users or u2 not in active_users:
            continue
            
        pairs[u1] = u2
        pairs[u2] = u1
        
        print(f"🤝 Paired {u1} <--> {u2}")
        
        await send_message(u1, {"type": "partnerFound", "from_user": u2, "is_initiator": True})
        await send_message(u2, {"type": "partnerFound", "from_user": u1, "is_initiator": False})

@router.websocket("/{user_name}")
async def websocket_endpoint(websocket: WebSocket, user_name: str):
    await websocket.accept()

    if user_name in active_users:
        user_name = f"{user_name}_{random_suffix()}"

    active_users[user_name] = websocket
    print(f"✅ {user_name} connected. Total users: {len(active_users)}")

    waiting_queue.append(user_name)
    await pair_users()

    if user_name not in pairs:
        await send_message(user_name, {"type": "waiting"})

    try:
        while True:
            try:
                data_text = await websocket.receive_text()
                data = json.loads(data_text)
            except Exception:
                print(f"⚠️ Invalid message from {user_name}")
                continue

            msg_type = data.get("type")
            partner = pairs.get(user_name)

            if msg_type in {"offer", "answer", "ice-candidate"} and partner:
                await send_message(partner, {
                    "type": msg_type,
                    "from_user": user_name,
                    "data": data.get("data")
                })
            elif msg_type == "next":
                old_partner = pairs.pop(user_name, None)
                if old_partner:
                    pairs.pop(old_partner, None)
                    await send_message(old_partner, {"type": "partnerSkipped"})
                await send_message(user_name, {"type": "searching"})
                waiting_queue.append(user_name)
                await pair_users()
            elif msg_type == "disconnect":
                await websocket.close()
                break
    except WebSocketDisconnect:
        print(f"⚠️ {user_name} disconnected")
    except Exception as e:
        print(f"An unexpected error occurred with {user_name}: {e}")
    finally:
        active_users.pop(user_name, None)
        partner = pairs.pop(user_name, None)
        if partner:
            pairs.pop(partner, None)
            await send_message(partner, {"type": "partnerDisconnected"})
            waiting_queue.append(partner)
            await pair_users()
        print(f"🧹 Cleaned up {user_name}. Active: {len(active_users)}")