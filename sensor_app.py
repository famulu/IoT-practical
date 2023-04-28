from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import serial

"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

ser = serial.Serial('/dev/ttyS0', 9600)


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

"""
Get values and send it to our clients
"""
def background_thread():
    while True:
        dummy_sensor_value = ser.readline()
        socketio.emit('updateSensorData', {'value': dummy_sensor_value, "date": get_current_datetime()})
        socketio.sleep(1)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app)
