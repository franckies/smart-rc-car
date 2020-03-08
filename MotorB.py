import RPi.GPIO as GPIO
import pigpio
import time
from multiprocessing import Process, Pipe
import multiprocessing

def turning(motorB_value,autodrive_btn_value,start_btn_value):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(12, GPIO.OUT) #SERVO ANGLE
    GPIO.setup(25, GPIO.OUT) #SERVO ON OFF
    GPIO.setup(3, GPIO.IN) # IR1
    GPIO.setup(4, GPIO.IN) # IR2
    GPIO.setup(17, GPIO.IN) # IR3
    pwmturning = pigpio.pi()
    GPIO.output(25, 0)
    Motor_B = 1500
    IR_on = False
    temp = 0
    last_IR = 0
    start_btn_pressed = False
    try:
        while True:
            while autodrive_btn_value.poll():
                if autodrive_btn_value.recv():
                    IR_on = True
                else:
                    IR_on = False
            while start_btn_value.poll():
                if start_btn_value.recv():
                    GPIO.output(25, 1) #IF START BUTTON IS PRESSED MOTOR B IS ACTIVATED
                    start_btn_pressed = True
                else:
                    GPIO.output(25, 0)
                    start_btn_pressed = False
            if not IR_on: #WHEN AUTODRIVE IS NOT ACTIVE
                while motorB_value.poll():
                    Motor_B = motorB_value.recv() #TAKE VALUE FROM SLIDER AND UPDATE MOTORB VALUE
                pwmturning.set_servo_pulsewidth(12,Motor_B)
            else: #WHEN AUTODRIVE IS ACTIVE:
                if GPIO.input(17) == 1:
                    last_IR = 0
                    if GPIO.input(4) == 1:
                        Motor_B = 1600
                    if GPIO.input(3) == 1:
                        Motor_B = 1400
                else:
                    if GPIO.input(4) == 1:
                        Motor_B = 1650
                        last_IR = 1
                    if GPIO.input(3) == 1:
                        Motor_B = 1350
                        last_IR = 2
                    if GPIO.input(4) == 0 and GPIO.input(3) == 0 and GPIO.input(17) == 0 and  last_IR == 1:
                        Motor_B = 1700
                    if GPIO.input(4) == 0 and GPIO.input(3) == 0 and GPIO.input(17) == 0 and last_IR == 2:
                        Motor_B = 1300

                pwmturning.set_servo_pulsewidth(12,Motor_B)
            time.sleep(0.01)
    except KeyboardInterrupt:
        GPIO.output(25, 0)
        GPIO.cleanup()
        print("Motor B Stopped")
        pass

def run(slider2_value,autodrive_value,start_btn_value):
    pMotorB = Process(target=turning, args=(slider2_value,autodrive_value,start_btn_value,))
    pMotorB.start()
    pMotorB.join()
