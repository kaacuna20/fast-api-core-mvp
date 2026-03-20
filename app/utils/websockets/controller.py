from .manager import ConnectionManager
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from fastapi.responses import HTMLResponse

class WebSocketController:
    """Controlador para manejar las operaciones relacionadas con los WebSockets."""
    
    def __init__(self):
        self.manager = ConnectionManager()

    async def connect(self, websocket: WebSocket, client_id: int = 0):
        """Maneja la conexión de un nuevo cliente WebSocket."""
        await self.manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await self.manager.send_personal_message(f"Message text was: {data}", websocket)
                await self.manager.broadcast(f"Client #{client_id} says: {data}")
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
            await self.manager.broadcast(f"Client #{client_id} disconnected")
