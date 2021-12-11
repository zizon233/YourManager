import socketio

# standard Python
sio = socketio.Client()
try:
    sio.connect(
        "http://ec2-3-23-132-5.us-east-2.compute.amazonaws.com/socket.io",
        headers="Connection",
        transports="websocket",
        wait_timeout=10,
    )

    print("my sid ids", sio.sid)

    sio.emit("my event", {"data": "test"})

    sio.disconnect()
except Exception as e:
    print(e)
