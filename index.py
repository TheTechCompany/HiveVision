import json
import time
import os
import sys
import asyncio
import websockets

from spectacles.index import Spectacle

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

lastTime = 0
currentTime = 0


header = {'Access-Control-Allow-Origin' : '*'}

specs = Spectacle()

connected = set()

async def handler(websocket):
    connected.add(websocket)

    while True:
        pos = specs.get_pos()

        await websocket.send(json.dumps(pos))
        await asyncio.sleep(0.2)

async def server():

    async with websockets.serve(handler, '0.0.0.0', 8000, extra_headers=header):
        await asyncio.Future()

async def emitter():
    print("Send")
    while True:
        print("emitting arms")

        websockets.broadcast(connected, json.dumps({'state': 'hands', 'bounds': []}))
        time.sleep(0.2)

if __name__ == '__main__':

    specs.start()

    asyncio.run(server())

