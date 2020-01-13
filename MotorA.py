import RPi.GPIO as GPIO
import time
import serial
import pigpio
from multiprocessing import Process, Pipe
import multiprocessing


ser = serial.Serial('/dev/ttyAMA0', baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS)

def motor(motorA_value,start_value):
    print('Car switched on : connect to 111.111.111.199 for manual control')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT) #MOTOR SPEED
    GPIO.setup(23, GPIO.OUT) #MOTOR ON OFF
    pwmMotor = pigpio.pi()
    pwmMotor.set_PWM_frequency(18,400)
    GPIO.output(23, 0) #MOTOR OFF BY DEFAULT
    Motor_A = 0 #MOTOR VALUE GIVEN BY THE slider1
    Motor_on = False #MOTOR ON OR OFF DEPENDING ON THE START BTN
    start_btn_pressed = False #VALUE OF START BUTTON
    cmDist = 0 #DISTANCE IN CENTIMETERS COMPUTED BY US SENSOR
    dist = 0
    try:
        while True:
            ser.flushInput()
            ser.write(b'\x55')
            dist = ser.read(2)
            cmDist = int(dist.encode('hex'), 16)/10

            while start_value.poll():
                if start_value.recv(): #SET START BTN PRESSED TO TRUE IF TRUE IS RECEIVED
                    start_btn_pressed = True
                else:
                    start_btn_pressed = False
            if start_btn_pressed:
                if not Motor_on:
                    GPIO.output(23, 1)
                    print("Motor started")
                    Motor_on = True
                if cmDist < 20: #CHECK US DISTANCE
                    GPIO.output(23, 0) #TURNING OFF MOTOR IF DISTANCE IS <20
                    print("Obstacle detected!")
                    time.sleep(1)
            else:
                if Motor_on:
                    GPIO.output(23, 0)
                    print("Motor Stopped")
                    Motor_on = False
            while motorA_value.poll():
                Motor_A = motorA_value.recv()
                Motor_A = round(Motor_A,0)
            pwmMotor.set_PWM_dutycycle(18,Motor_A)

    except KeyboardInterrupt:
        GPIO.output(23, 0)
        GPIO.cleanup()
        print("Motor A Stopped")
        pass


def run(slider1_value,start_btn_value):
    pMotorA = Process(target=motor, args=(slider1_value,start_btn_value,))
    pMotorA.start()
    pMotorA.join()
