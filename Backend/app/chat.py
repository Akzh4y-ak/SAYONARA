# import json
# import asyncio
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from collections import deque
# from typing import Dict
# from starlette.websockets import WebSocketState

# router = APIRouter()

# waiting_queue: deque[WebSocket] = deque()
# active_pairs: Dict[WebSocket, WebSocket] = {}


# async def notify(ws: WebSocket, event: str, data: dict = None):
#     """Send a JSON message to a websocket safely."""
#     if ws.client_state != WebSocketState.CONNECTED:
#         return
#     try:
#         await ws.send_text(json.dumps({"event": event, "data": data or {}}))
#     except Exception:
#         # if sending fails, disconnect this socket
#         await unpair(ws, requeue_partner=True)


# async def pair_users(a: WebSocket, b: WebSocket):
#     """Pair two users and notify them."""
#     if a in active_pairs or b in active_pairs:
#         return  # already paired

#     active_pairs[a] = b
#     active_pairs[b] = a

#     # 'a' is initiator for WebRTC
#     await notify(a, "paired", {"message": "✅ Connected with a stranger!", "initiator": True})
#     await notify(b, "paired", {"message": "✅ Connected with a stranger!", "initiator": False})


# async def enqueue_or_pair(ws: WebSocket):
#     """Put user in queue or pair immediately if possible."""
#     while waiting_queue:
#         partner = waiting_queue.popleft()
#         if partner.client_state == WebSocketState.CONNECTED:
#             await pair_users(ws, partner)
#             return
#     # no partner available → enqueue
#     waiting_queue.append(ws)
#     await notify(ws, "waiting", {"message": "⌛ Waiting for a stranger..."})


# async def unpair(ws: WebSocket, requeue_partner: bool = True):
#     """Remove a websocket from active pairs and handle partner logic."""
#     partner = active_pairs.pop(ws, None)
#     if partner:
#         active_pairs.pop(partner, None)
#         await notify(partner, "partner-left", {"message": "❌ Stranger disconnected."})

#         if requeue_partner and partner.client_state == WebSocketState.CONNECTED:
#             await asyncio.sleep(0.5)
#             await enqueue_or_pair(partner)


# @router.websocket("/ws")
# async def ws_handler(ws: WebSocket):
#     await ws.accept()
#     try:
#         await enqueue_or_pair(ws)

#         while True:
#             raw = await ws.receive_text()
#             try:
#                 msg = json.loads(raw)
#             except Exception:
#                 msg = {"event": "chat", "data": {"text": raw}}

#             event = msg.get("event")
#             data = msg.get("data", {})
#             partner = active_pairs.get(ws)

#             if event == "chat":
#                 if partner:
#                     await notify(partner, "chat", {"from": "stranger", "text": data.get("text", "")})
#                 else:
#                     await notify(ws, "waiting", {"message": "⌛ Still waiting for a stranger..."})

#             elif event in {"webrtc-offer", "webrtc-answer", "webrtc-ice"}:
#                 if partner:
#                     await notify(partner, event, data)

#             elif event == "next":
#                 await unpair(ws, requeue_partner=True)
#                 await notify(ws, "system", {"message": "🔄 Searching for a new partner..."})
#                 await enqueue_or_pair(ws)

#             elif event == "disconnect":
#                 await unpair(ws, requeue_partner=False)
#                 await notify(ws, "system", {"message": "👋 You disconnected."})
#                 break

#     except WebSocketDisconnect:
#         if ws in waiting_queue:
#             try:
#                 waiting_queue.remove(ws)
#             except ValueError:
#                 pass
#         await unpair(ws, requeue_partner=True)

#     except Exception:
#         if ws in waiting_queue:
#             try:
#                 waiting_queue.remove(ws)
#             except ValueError:
#                 pass
#         await unpair(ws, requeue_partner=True)
