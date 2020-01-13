import time
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock
import MotorA
import MotorB
from multiprocessing import Process, Pipe
import multiprocessing
from datetime import datetime
from datetime import timedelta


async_mode = None

app = Flask(__name__)

socketio = SocketIO(app, async_mode=async_mode)

#FUNCTIONS FOR CALLING MOTOR_ULTRASOUND AND TURNING_INFRARED
def motorA(slider1,start):
    MotorA.run(slider1,start)

def motorB(slider2,autodrv,start):
    MotorB.run(slider2,autodrv,start)

#SENDERS AND RECEIVERS OBJECT FOR INTERPROCESS COMMUNICATION
motor_receiver, motor_sender = Pipe() #sender and receiver of slider for motor A value
motor_receiver_start, motor_sender_start = Pipe() #sender and receiver for start button
turning_receiver, turning_sender = Pipe() #sender and receiver for motor B value
autodrive_receiver, autodrive_sender = Pipe() #sender and receiver for autodrive button
turning_receiver_start, turning_sender_start = Pipe() #sender and receiver for start button

@app.route('/',  methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('start-btn', namespace='/CARPROJECT')
def start_btn(value):
    startValue = float(dict(value).get('value'))
    if startValue == 1:
        motor_sender_start.send(True)
        turning_sender_start.send(True)
    else:
        print("Retry")

@socketio.on('stop-btn', namespace='/CARPROJECT')
def stop_btn(value):
    startValue = float(dict(value).get('value'))
    if startValue == 0:
        motor_sender_start.send(False)
        turning_sender_start.send(False)
    else:
        print("Retry")

@socketio.on('autodrive-btn', namespace='/CARPROJECT')
def autodrive_btn(value):
    value_autodrive = float(dict(value).get('value'))
    if value_autodrive == 0:
        autodrive_sender.send(False)
    else:
        autodrive_sender.send(True)

@socketio.on('slider1_event', namespace='/CARPROJECT')
def test_message(message):
    slider1Value = float(dict(message).get('value'))
    motor_sender.send(slider1Value)

@socketio.on('slider2_event', namespace='/CARPROJECT')
def test_message(message):
    slider2Value = float(dict(message).get('value'))
    turning_sender.send(slider2Value)


@socketio.on('connect', namespace='/CARPROJECT')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/CARPROJECT')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    procesMotorA = Process(target=motorA, args=(motor_receiver,motor_receiver_start,))
    procesMotorB = Process(target=motorB, args=(turning_receiver,autodrive_receiver,turning_receiver_start,))
    procesMotorA.start()
    procesMotorB.start()
    socketio.run(app, host="0.0.0.0", port=80, debug=False)
