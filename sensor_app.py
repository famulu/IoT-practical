from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import serial
import pymysql
import math
import atexit
import time

"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meow'
socketio = SocketIO(app, cors_allowed_origins='*')

threshold = 30

# ser = serial.Serial('/dev/ttyS0', 9600)

dbConn = pymysql.connect(host="localhost", user="pi", password="password", db="smoke_db")

actuator_data = {
    'buzzer': 0,
    'fan': 0
}

timeout = 5

prevTime = 0


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

"""
Get values and send it to our clients
"""
def background_thread():
    previous_value_id = None
    while True:
        sensor_value, push_button_value = get_value()

        query = "INSERT INTO smoke_log (smoke, detected_datetime) VALUES ('%s', '%s')" % (sensor_value, get_current_datetime())
        with dbConn.cursor() as cursor:
            cursor.execute(query)
        dbConn.commit()

        select_query = "SELECT * FROM `smoke_log` ORDER BY detected_datetime DESC, smoke_id DESC LIMIT 1"
        with dbConn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(select_query)
            result = cursor.fetchone()

            if time.time() - prevTime > timeout:
                if result['smoke'] > threshold or push_button_value == 1:
                    turn_buzzer_on()
                    turn_fan_on()
                else:
                    turn_buzzer_off()
                    turn_fan_off()
                socketio.emit('updateActuatorData', actuator_data)

            if (result['smoke_id'] != previous_value_id):
                socketio.emit('updateSensorData', {'value': result['smoke'], "date": str(result['detected_datetime']), 'push_button': push_button_value})
                previous_value_id = result['smoke_id']
            socketio.sleep(0.2)


@app.route('/')
def index():
    return render_template('index.html', threshold=threshold, actuators=actuator_data)


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

@app.route('/<actuator>/<value>')
def trigger_actuator(actuator, value):
    global prevTime

    prevTime = time.time()
    if actuator == 'buzzer':
        if value == 'on':
            turn_buzzer_on()
        elif value == 'off':
            turn_buzzer_off()
    elif actuator == 'fan':
        if value == 'on':
            turn_fan_on()
        elif value == 'off':
            turn_fan_off()

    return render_template('index.html', threshold=threshold, actuators=actuator_data)

@socketio.on('thresholdChange')
def threshold_change(value):
    print(value)
    global threshold
    threshold = int(value)

def get_value():
    # return ser.readline().decode('utf-8')
    x = 1 if (random() > 0.5) else 0
    return math.floor((random() * 50)), x
def write_value(value):
    # ser.write(value)
    print("value: " + value.decode('utf-8'))

@atexit.register
def goodbye():
    print("You are now leaving the Python file")
    dbConn.close()

def turn_buzzer_off():
    actuator_data['buzzer'] = 0
    write_value(b'1')

def turn_buzzer_on():
    actuator_data['buzzer'] = 1
    write_value(b'2')

def turn_fan_off():
    actuator_data['fan'] = 0
    write_value(b'3')

def turn_fan_on():
    actuator_data['fan'] = 1
    write_value(b'4')

if __name__ == '__main__':
    socketio.run(app)
