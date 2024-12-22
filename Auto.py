from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QApplication, QWidget
from picamera2.previews.qt import QGlPicamera2
from picamera2 import Picamera2
import RPi.GPIO as GPIO
from Command import COMMAND as cmd
from servo import *
from Motor import *
import socket
import threading
import time

# Initialize Motor and Servo
PWM = Motor()
pwm = Servo()

#Buzzer
Buzzer_Pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_Pin,GPIO.OUT)
class Buzzer:
    def run(self,command):
        if command!="0":
            GPIO.output(Buzzer_Pin,True)
        else:
            GPIO.output(Buzzer_Pin,False)
B=Buzzer()

# Camera Stream Function
def start_camera_stream():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    app = QApplication([])
    qpicamera2 = QGlPicamera2(picam2, width=800, height=600, keep_ar=False)

    # Create the main window and set layout
    window = QWidget()
    layout_v = QVBoxLayout()
    layout_v.addWidget(qpicamera2)
    window.setWindowTitle("Camera Stream with Servo and Motor Control")
    window.resize(180, 160)
    window.setLayout(layout_v)

    # Start the camera and show the window
    picam2.start()
    window.show()
    app.exec()

# Function for receiving and controlling the car
def receive_and_control():
    address = ('0.0.0.0', 12345)  # Listen on all interfaces, port 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(address)
    s.listen(1)
    print("Waiting for a connection...")
    conn, addr = s.accept()
    print(f"Connected to: {addr}")

    try:
        start_time = time.time()
        max_flex_value1 = max_flex_value2 = 0
        min_flex_value1 = min_flex_value2 = 65535
        max_gyrox = max_gyroz = min_gyrox = min_gyroz = 0
        i = 0

        # Calibration phase
        while time.time() - start_time < 10:
            data = conn.recv(1024)
            if i % 10 == 0:
                B.run('1')
            else:
                B.run('0')
            if data:
                try:
                    received_data = data.decode('utf-8')
                    list_with_values = received_data.split('#')
                    flex_value1, flex_value2 = int(list_with_values[0]), int(list_with_values[1])
                    gyrox, gyroz = float(list_with_values[2]), float(list_with_values[3])

                    max_flex_value1, min_flex_value1 = max(max_flex_value1, flex_value1), min(min_flex_value1, flex_value1)
                    max_flex_value2, min_flex_value2 = max(max_flex_value2, flex_value2), min(min_flex_value2, flex_value2)
                    max_gyrox, min_gyrox = max(max_gyrox, gyrox), min(min_gyrox, gyrox)
                    max_gyroz, min_gyroz = max(max_gyroz, gyroz), min(min_gyroz, gyroz)
                except (ValueError, IndexError):
                    print("Invalid data received during calibration.")
                print(max_flex_value1, min_flex_value1, max_flex_value2, min_flex_value2)
                print(max_gyrox, min_gyrox, max_gyroz, min_gyroz)
                i += 1
                
        flex_diff1, flex_diff2 = max_flex_value1 - min_flex_value1, max_flex_value2 - min_flex_value2
        mid_flex1, mid_flex2 = (max_flex_value1 + min_flex_value1) / 2, (max_flex_value2 + min_flex_value2) / 2
        amp_flex1, amp_flex2 = 4000 / flex_diff1, 4000 / flex_diff2

        # Main control loop
        servodata1 = 90
        servodata2 = 110
        while True:
            data = conn.recv(1024)
            if data:
                try:
                    received_data = data.decode('utf-8')
                    list_with_values = received_data.split('#')
                    flex_value1, flex_value2 = int(list_with_values[0]), int(list_with_values[1])
                    gyrox, gyroz = float(list_with_values[2]), float(list_with_values[3])

                    motordata1 = (flex_value1 - mid_flex1) * amp_flex1
                    motordata2 = (flex_value2 - mid_flex2) * amp_flex2
                    if gyrox > 10 or gyrox < -10 and servodata1 > 5 or servodata1 < 175:
                        servodata2 += gyrox/10
                    if gyrox > 10 or gyrox < -10 and servodata1 > 5 or servodata1 < 175:
                        servodata1 += gyroz/10

                    motordata1, motordata2 = round(motordata1), round(motordata2)
                    servodata1, servodata2 = round(servodata1), round(servodata2)

                    # Deadzone for motor and servo control
                    if abs(motordata1) < 500:
                        motordata1 = 0
                    if abs(motordata2) < 500:
                        motordata2 = 0
                        
                    if servodata1 > 175:
                        servodata1 = 174
                    elif servodata1 < 5:
                        servodata1 = 6
                        
                    if servodata2 > 175:
                        servodata2 = 174
                    elif servodata2 < 85:
                        servodata2 = 86
                        

                    # Send commands to motors and servos
                    PWM.setMotorModel(motordata2, motordata2, motordata1, motordata1)
                    pwm.setServoPwm('0', servodata1)
                    pwm.setServoPwm('1', servodata2)

                    print(f"Motors: {motordata1}, {motordata2}; Servos: {servodata1}, {servodata2}")
                except (ValueError, IndexError):
                    print("Invalid data received.")
            else:
                break
    except KeyboardInterrupt:
        print("Stopping motors and servos.")
        PWM.setMotorModel(0, 0, 0, 0)
        B.run('0')
    finally:
        conn.close()
        s.close()

# Start the camera stream in a separate thread
camera_thread = threading.Thread(target=start_camera_stream, daemon=True)
camera_thread.start()

# Run the main control program
receive_and_control()
