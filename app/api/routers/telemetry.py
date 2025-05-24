from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from typing import Optional

from app.services.telemetry_service import connection_manager
from app.core.security import decode_token
from app.crud import user as crud_user # Renamed to avoid conflict
from app.db.session import get_db # For token validation if needed
from sqlalchemy.orm import Session
from app.core.config import settings


router = APIRouter()

# Path for WebSocket defined in settings.WS_TELEMETRY_PATH
@router.websocket(settings.WS_TELEMETRY_PATH)
async def websocket_telemetry_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None) # Token for authentication
    # db: Session = Depends(get_db) # Cannot use Depends directly in WebSocket route like this
):
    """
    WebSocket endpoint for clients to connect and receive real-time telemetry.
    Authentication via token in query parameter.
    """
    # Authentication (simplified for WebSocket)
    # In a real app, you might want to create a short-lived WebSocket ticket
    # or handle token validation more robustly.
    user_id_from_token: Optional[int] = None
    if token:
        user_id_str = decode_token(token)
        if user_id_str:
            try:
                user_id_from_token = int(user_id_str)
                # Optional: Fetch user from DB to ensure they are active, etc.
                # This requires a synchronous DB call from an async context,
                # which can be tricky. For now, just validating token existence.
                # with SessionLocal() as db_session: # Example if you need DB access
                #     user = crud_user.user.get(db_session, id=user_id_from_token)
                #     if not user or not user.is_active:
                #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                #         return
            except ValueError:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token format")
                return
        else: # Token invalid or expired
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
            return
    else: # No token provided, could be public or require token
        # For MVP, let's assume if no token, it's a public (unauthenticated) connection
        # or close if auth is strictly required.
        # For now, let's allow connection even without token for simplicity of broadcast.
        # If strict auth needed:
        # await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")
        # return
        pass


    await connection_manager.connect(websocket)
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else "unknown"
    print(f"WebSocket client {client_host}:{client_port} connected (User ID: {user_id_from_token or 'Anonymous'}).")
    
    try:
        while True:
            # This loop keeps the connection alive.
            # The server broadcasts messages; clients primarily listen.
            # Client can send messages too (e.g., for filtering preferences),
            # but not implemented in this MVP.
            data = await websocket.receive_text() 
            # For MVP, we don't expect clients to send much data.
            # If they do, process it here.
            # Example: await websocket.send_text(f"Message text was: {data}")
            print(f"Received from {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}): {data}")
            # Echo back or process client messages if needed
            # await connection_manager.send_personal_message(f"You wrote: {data}", websocket)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        print(f"WebSocket client {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}) disconnected.")
    except Exception as e:
        connection_manager.disconnect(websocket)
        print(f"WebSocket error for client {client_host}:{client_port} (User ID: {user_id_from_token or 'Anonymous'}): {e}")
        # Optionally try to close with an error code if not already disconnected
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except RuntimeError: # Already closed
            pass