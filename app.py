from fastapi import FastAPI, Request, Header, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
from db import db_request
import asyncio
import json


app = FastAPI()



@app.get("/")
async def get():
    html = open('index.html', 'r').read()
    return HTMLResponse(html)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            await websocket.send_json({
            "id": 'UUID',
            "message": 'ping'
            })

            #await manager.broadcast(f"Отправить всем")
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)




@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/api/notifications")
def get_notifications():

    return db_request(f'SELECT * FROM notifications')


@app.post("/api/notifications")
def post_notifications(type: int = Header(), title: str = Header(), content: str = Header()):

    response = db_request(f"INSERT INTO notifications (type, title, content) VALUES ({type}, '{title}', '{content}');")

    if response['status'] == 'ok':
        return db_request(f"SELECT * FROM notifications WHERE id = (SELECT MAX(id) FROM notifications);")
    else:
        return response


@app.put("/api/notifications/{id}")
def put_notifications(id: int, type: int = Header(default=None), title: str = Header(default=None), content: str = Header(default=None)):

    if type == None and title == None and content == None:
        return {
            'status': 'error',
            'data': 'Empty header fields'
        }
    else:
        sql = f"UPDATE notifications SET "

        sql_appnd = []

        if type != None:
            sql_appnd.append(f"type = {type}")
        if title != None:
            sql_appnd.append(f"title = '{title}'")
        if content != None:
            sql_appnd.append(f"content = '{content}'")

        sql += ", ".join(sql_appnd)

        sql += f" WHERE id = {id};"

        print(sql)

        response = db_request(sql)

        if response['status'] == 'ok':
            return db_request(f"SELECT * FROM notifications WHERE id = {id};")
        else:
            return response


@app.delete("/api/notifications/{id}")
def delete_notifications(id: int):

    response = db_request(f"SELECT * FROM notifications WHERE id = {id};")

    if len(response['data']) > 0:

        response = db_request(f"DELETE FROM notifications WHERE id = {id};")

        if response['status'] == 'ok':
            return {
                'status': 'ok', 
                'data': f'{id} deleted successfully'
            }
        else:
            return response

    else:
        return{
            'status': 'error', 
            'data': 'Id is not found'
        }


@app.post("/api/notifications/{id}/send")
async def post_notifications_send(id: int, delay: int = Header(default=0)):

    response = db_request(f"SELECT * FROM notifications WHERE id = {id};")

    if len(response['data']) > 0:
        await asyncio.sleep(delay)
        await manager.broadcast( str(response['data'][0]) )
        return {
            'status': 'ok', 
            'data': response['data'][0]
        }
    else:
        return {
            'status': 'error', 
            'data': 'Id is not found'
        }



if __name__ == "__main__":
    uvicorn.run(app, host = 'localhost', port = 8000)