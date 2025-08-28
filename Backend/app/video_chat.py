import json, random, string
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Active users: name -> WebSocket
active_users: dict[str, WebSocket] = {}
# Paired users: name -> partner_name
pairs: dict[str, str] = {}

def random_suffix(length=4):
    """Generates a random alphanumeric suffix."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def send_message(user_name: str, message: dict):
    """Send JSON message safely to a user if still connected."""
    ws = active_users.get(user_name)
    if ws:
        try:
            await ws.send_text(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send message to {user_name}: {e}")

async def pair_users():
    """Pairs waiting users randomly, designating one as initiator."""
    waiting = [u for u in active_users if u not in pairs]
    while len(waiting) >= 2:
        u1, u2 = waiting.pop(0), waiting.pop(0)
        pairs[u1] = u2
        pairs[u2] = u1
        print(f"🤝 Paired {u1} <--> {u2}")
        
        # Send a flag to the initiator
        await send_message(u1, {"type": "partnerFound", "from_user": u2, "is_initiator": True})
        # Send no flag to the other user
        await send_message(u2, {"type": "partnerFound", "from_user": u1, "is_initiator": False})

@router.websocket("/{user_name}")
async def websocket_endpoint(websocket: WebSocket, user_name: str):
    """Main WebSocket endpoint for handling video chat signaling."""
    # Ensure unique username
    if user_name in active_users:
        user_name = f"{user_name}_{random_suffix()}"

    await websocket.accept()
    active_users[user_name] = websocket
    print(f"✅ {user_name} connected. Total users: {len(active_users)}")

    # Try to match this user
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

            # WebRTC signaling
            if msg_type in {"offer", "answer", "ice-candidate"} and partner:
                await send_message(partner, {
                    "type": msg_type,
                    "from_user": user_name,
                    "data": data.get("data")
                })

            # Skip to next partner
            elif msg_type == "next":
                old_partner = pairs.pop(user_name, None)
                if old_partner:
                    pairs.pop(old_partner, None)
                    await send_message(old_partner, {"type": "partnerSkipped"})
                await send_message(user_name, {"type": "searching"})
                await pair_users()

            # Manual disconnect
            elif msg_type == "disconnect":
                await websocket.close()
                break

    except WebSocketDisconnect:
        print(f"⚠️ {user_name} disconnected")

    finally:
        # Cleanup user and their partner
        active_users.pop(user_name, None)
        partner = pairs.pop(user_name, None)
        if partner:
            pairs.pop(partner, None)
            await send_message(partner, {"type": "partnerDisconnected"})
            await pair_users()
        print(f"🧹 Cleaned up {user_name}. Active: {len(active_users)}")