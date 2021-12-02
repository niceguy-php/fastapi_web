# -*- coding:utf-8 -*-
"""
File Name: chat_redis_server
Author: 82405
Data: 2021/8/18 13:51
-----------------------
Info:

-----------------------
Change Activity:
    2021/8/18: create
"""
import uvicorn
import ujson
from uuid import uuid4
from aredis import StrictRedis
from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
from datetime import datetime

app = FastAPI()
websocket_ip = 'localhost'
redis_client = StrictRedis(host='localhost', port=6379, db=0)  # redis 客户端


class ChatText:
    def __init__(self,
                 chat_src,
                 chat_text):
        """

        :param chat_src:    0-客户端 1-服务端
        :param chat_text:
        """
        self.chat_src = chat_src
        self.chat_text = chat_text
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_data(self):
        return {
            'chat_src': self.chat_src,
            'chat_text': self.chat_text,
            'timestamp': self.timestamp
        }


class CustomerChatCurrentObj:
    """
    当前的客服聊天对象
    """

    def __init__(self,
                 client_id,
                 redis_client):
        self.client_id = client_id
        self.server_websocket = None  # 服务
        self.customer_websocket = None  # 客户
        self.active = False
        self.timestamp = None
        self.redis_client = redis_client
        self.chat_uuid = None

    async def chat_hash_redis_init(self):
        """
            {
                'begin_time': '2021-08-19 11:10:12',
                'last_time': '2021-08-19 11:10:12',
                'chat_uuid': '387943dd68f84a098bed9f2a4c67c227'

            }
        :return:
        """
        self.chat_uuid = uuid4().hex
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        chat_hash_content = ujson.dumps({
            'begin_time': self.timestamp,
            'last_time': self.timestamp,
            'chat_uuid': self.chat_uuid
        })
        await self.redis_client.hset('chat_hash', self.client_id, chat_hash_content)

    async def get_chat_message_list(self) -> []:
        """
            获取聊条记录
        :return:
        """
        chat_message_list = []
        chat_message_nums = await self.redis_client.llen(self.chat_uuid)
        if chat_message_nums > 0:
            _num = 0
            while True:
                if _num > chat_message_nums - 1:
                    break
                _content = await self.redis_client.lindex(self.chat_uuid, _num)
                chat_message_list.append(ujson.loads(_content.decode()))
                _num = _num + 1
        return chat_message_list

    async def add_chat_message_list(self, chat_content):
        """
            增加聊天记录
        :param chat_content:
        :return:
        """
        await self.redis_client.rpush(self.chat_uuid, ujson.dumps(chat_content))


class CustomerServiceUtils:
    def __init__(self):
        self.client_ids = []
        self.customer_active_connections: List[WebSocket] = []  # 客户端活跃链接
        self.server_active_connections: List[WebSocket] = []  # 服务端活跃链接
        self.customer_chat_obj: List[CustomerChatCurrentObj] = []
        self.redis_client = StrictRedis(host='localhost', port=6379, db=0)  # redis 客户端

    async def customer_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.customer_active_connections.append(websocket)

    async def server_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.server_active_connections.append(websocket)

    def customer_disconnect(self, websocket: WebSocket):
        self.customer_active_connections.remove(websocket)
        current_chat_obj = None
        for item in self.customer_chat_obj:
            if item.customer_websocket == websocket:
                current_chat_obj = item
        if current_chat_obj is not None:
            current_chat_obj.customer_websocket = None
            self.customer_chat_obj.remove(current_chat_obj)

    def server_disconnect(self, websocket: WebSocket):
        self.server_active_connections.remove(websocket)
        current_chat_obj = None
        for item in self.customer_chat_obj:
            if item.server_websocket == websocket:
                current_chat_obj = item
                break
        if current_chat_obj is not None:
            current_chat_obj.server_websocket = None
            self.customer_chat_obj.remove(current_chat_obj)

    async def get_customer_chat_obj(self, client_id) -> CustomerChatCurrentObj:
        """获取当前聊天对象

        :param client_id:
        :return:
        """
        for chat_item in self.customer_chat_obj:
            if chat_item.client_id == client_id:
                return chat_item
        chat_hash_content = await self.redis_client.hget('chat_hash', client_id)
        if chat_hash_content is None:
            current_chat_obj = CustomerChatCurrentObj(client_id, redis_client)
            await current_chat_obj.chat_hash_redis_init()
        else:
            chat_content_obj = ujson.loads(chat_hash_content.decode())
            current_chat_obj = CustomerChatCurrentObj(client_id, redis_client)
            current_chat_obj.timestamp = chat_content_obj['begin_time']
            current_chat_obj.chat_uuid = chat_content_obj['chat_uuid']
        self.customer_chat_obj.append(current_chat_obj)
        return current_chat_obj


customer_service_utils = CustomerServiceUtils()


@app.get("/chat/client/{client_id}")
async def chat_client(client_id: str):
    html_content = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>客户端</title>
    </head>
    <body>
        <h1>客户端 Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://{websocket_ip}:8001/ws/customer/{client_id}");
    """ + """
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var chat_obj = JSON.parse(event.data)
                console.log(chat_obj)
                if (chat_obj.src == 0){
                    chat_text = '我 ' + chat_obj.timestamp + ':' + chat_obj.content
                }else{
                    chat_text = '客服 ' + chat_obj.timestamp + ':' + chat_obj.content
                }
                console.log(chat_text)
                var content = document.createTextNode(chat_text)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
    return HTMLResponse(html_content)


@app.get("/chat/server/{client_id}")
async def chat_server(client_id: str):
    html_content = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>服务端</title>
    </head>
    <body>
        <h1>服务端 Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://{websocket_ip}:8001/ws/server/{client_id}");
    """ + """
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var chat_obj = JSON.parse(event.data)
                if (chat_obj.src == 0){
                    chat_text = '客户 ' + chat_obj.timestamp + ':' + chat_obj.content
                }else if(chat_obj.src == 1){
                    chat_text = '我 ' + chat_obj.timestamp + ':' + chat_obj.content
                }else{
                    chat_text = '系统 ' + chat_obj.timestamp + ':' + chat_obj.content
                }
                var content = document.createTextNode(chat_text)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
    return HTMLResponse(html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.websocket("/ws/customer/{client_id}")
async def websocket_endpoint_customer(websocket: WebSocket, client_id: str):
    await customer_service_utils.customer_connect(websocket)
    try:
        customer_chat_obj = await customer_service_utils.get_customer_chat_obj(client_id)
        customer_chat_obj.active = True
        customer_chat_obj.customer_websocket = websocket
        # 获取历史聊条记录
        chat_message_his_list = await customer_chat_obj.get_chat_message_list()
        for chat_message in chat_message_his_list:
            chat_text = {
                'timestamp': chat_message['timestamp'],
                'content': chat_message['chat_text'],
                'client_id': client_id,
                'src': chat_message['chat_src']  # 0-客户 1-客服
            }
            await websocket.send_text(ujson.dumps(chat_text))
        # 聊天轮询
        while True:
            data = await websocket.receive_text()
            print(f'客户端发送消息:{data}')
            _chat_text = ChatText(0, data)
            await customer_chat_obj.add_chat_message_list(_chat_text.get_data())
            chat_text = {
                'timestamp': _chat_text.timestamp,
                'content': data,
                'client_id': client_id,
                'src': 0  # 0-客户 1-客服
            }
            # 发送给自己
            await websocket.send_text(ujson.dumps(chat_text))
            # 发送给服务端
            if customer_chat_obj.server_websocket is not None:
                await customer_chat_obj.server_websocket.send_text(ujson.dumps(chat_text))
    except WebSocketDisconnect:
        customer_service_utils.customer_disconnect(websocket)


@app.websocket("/ws/server/{client_id}")
async def websocket_endpoint_server(websocket: WebSocket, client_id: str):
    await customer_service_utils.server_connect(websocket)
    try:
        customer_chat_obj = await customer_service_utils.get_customer_chat_obj(client_id)
        customer_chat_obj.server_websocket = websocket
        chat_message_his_list = await customer_chat_obj.get_chat_message_list()
        for chat_message in chat_message_his_list:
            chat_text = {
                'timestamp': chat_message['timestamp'],
                'content': chat_message['chat_text'],
                'client_id': client_id,
                'src': chat_message['chat_src']  # 0-客户 1-客服
            }
            await websocket.send_text(ujson.dumps(chat_text))
        if not customer_chat_obj.active:
            chat_text = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 时间戳
                'content': f'客户{client_id}离线',  # 内容
                'client_id': client_id,  # 客户端ID  支持字符串
                'src': 2  # 0-客户 1-客服 2-系统消息
            }
            await websocket.send_text(ujson.dumps(chat_text))
        while True:
            data = await websocket.receive_text()
            print(f'服务端发送消息:{data}')
            _chat_text = ChatText(1, data)
            await customer_chat_obj.add_chat_message_list(_chat_text.get_data())
            chat_text = {
                'timestamp': _chat_text.timestamp,  # 时间戳
                'content': data,  # 内容
                'client_id': client_id,  # 客户端ID  支持字符串
                'src': 1  # 0-客户 1-客服
            }
            await websocket.send_text(ujson.dumps(chat_text))
            if customer_chat_obj.customer_websocket is not None:
                await customer_chat_obj.customer_websocket.send_text(ujson.dumps(chat_text))
    except WebSocketDisconnect:
        customer_service_utils.server_disconnect(websocket)

uvicorn.run(app, host="0.0.0.0", port=8001)