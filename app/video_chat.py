import json, random, string
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Active users (name -> WebSocket)
active_users: dict[str, WebSocket] = {}
# Pair mappings (name -> partner_name)
pairs: dict[str, str] = {}

def random_suffix(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def send_message(user_name: str, message: dict):
    """Send a JSON message to a user safely."""
    if user_name in active_users:
        try:
            await active_users[user_name].send_text(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send message to {user_name}: {e}")

async def pair_users():
    """Pair users who are waiting (not already in a pair)."""
    waiting_users = [name for name in active_users if name not in pairs]
    while len(waiting_users) >= 2:
        user1 = waiting_users.pop(0)
        user2 = waiting_users.pop(0)
        pairs[user1] = user2
        pairs[user2] = user1

        await send_message(user1, {"type": "partnerFound", "partner": user2})
        await send_message(user2, {"type": "partnerFound", "partner": user1})

@router.websocket("/ws-video/{user_name}")
async def websocket_endpoint(websocket: WebSocket, user_name: str):
    # Ensure unique usernames (for guests)
    if user_name in active_users:
        user_name = f"{user_name}_{random_suffix()}"

    await websocket.accept()
    active_users[user_name] = websocket
    print(f"✅ {user_name} connected. Total users: {len(active_users)}")

    # Try pairing
    await pair_users()

    if user_name not in pairs:
        await send_message(user_name, {"type": "waiting"})

    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            msg_type = data.get("type")
            partner_name = pairs.get(user_name)

            if partner_name and partner_name in active_users:
                # Handle WebRTC signaling
                if msg_type in {"offer", "answer", "ice-candidate"}:
                    await send_message(partner_name, {
                        "type": msg_type,
                        "from_user": user_name,
                        "data": data.get("data")
                    })

                elif msg_type == "next":
                    # Break current pair and find new partner
                    old_partner = pairs.pop(user_name, None)
                    if old_partner:
                        pairs.pop(old_partner, None)
                        await send_message(old_partner, {"type": "partnerSkipped"})
                    await send_message(user_name, {"type": "searching"})
                    await pair_users()

                elif msg_type == "disconnect":
                    # Manual disconnect
                    await websocket.close()
                    break

    except WebSocketDisconnect:
        print(f"⚠️ {user_name} disconnected")
        active_users.pop(user_name, None)
        partner_name = pairs.pop(user_name, None)
        if partner_name:
            pairs.pop(partner_name, None)
            await send_message(partner_name, {"type": "partnerDisconnected"})
            await pair_users()
