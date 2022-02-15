import argparse
import asyncio
from asyncio.windows_events import NULL
import logging
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
import socketio

config = ""

async def create_client():
    sio = socketio.AsyncClient()

    @sio.event
    async def connect():
        print('connection established')
        await sio.emit('pyping')

    @sio.on('pypong')
    def on_message(data):
        print('client received a message!',data)

    @sio.on('offer')
    async def on_message(data):
        await handle_offer(data)

    @sio.on('config')
    def on_message(data):
        print('config:', data)
        config=data

    @sio.event
    def message(data):
        print('message received with ', data)
        # sio.emit('client', {'response': 'my response'})

    @sio.event
    async def connect_error():
        print("The connection failed!")
        await sio.disconnect()

    @sio.event
    async def disconnect():
        print('disconnected from server')
        await sio.disconnect()

    async def handle_offer(offer):
        print('offer', offer)
        pc = RTCPeerConnection()

        @pc.on("track")
        def on_track(track):
            print('get track', track.kind)
            pc.addTrack(track)

        remoteRD = RTCSessionDescription(sdp=offer['sdp'], type=offer['type'])
        await pc.setRemoteDescription(remoteRD)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        await sio.emit('answer', {'type': 'answer', 'sdp': pc.localDescription.sdp })

    await sio.connect('http://52.173.25.116:8080')
    await sio.wait()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_client())
    