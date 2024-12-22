from machine import I2C, Pin, PWM, ADC
from imu import MPU6050
import time
import math
import socket
import network

# Initialize I2C and MPU6050
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
mpu = MPU6050(i2c)

# Initialize Flex Sensors
flex_sensor1 = ADC(Pin(26))
flex_sensor2 = ADC(Pin(27))

# Kalman filter variables
angle_x = 0  # Estimated angle for X-axis
angle_y = 0  # Estimated angle for Y-axis
bias_x = 0   # Bias for X-axis
bias_y = 0   # Bias for Y-axis
P = [[1, 0], [0, 1]]  # Error covariance matrix

# Kalman filter parameters
Q_angle = 0.001  # Process noise variance for the angle
Q_bias = 0.003   # Process noise variance for the gyro bias
R_measure = 0.03  # Measurement noise variance

# Complementary filter constant
alpha = 0.98

# Time step for integration
previous_time = time.ticks_ms()

SSID = 'Kasatka'
PASSWORD = 'FHG47TTMD3'

# Buzzer setup
buzzer = PWM(Pin(5))

def play_tone(frequency, duration, volume=0.3):
    duty = int(65535 * volume)
    buzzer.freq(frequency)
    buzzer.duty_u16(duty)
    time.sleep(duration)
    buzzer.duty_u16(0)

def no_connection_melody():
    play_tone(262, 0.1)
    time.sleep(0.01)
    play_tone(262, 0.1)

def connection_melody():
    melody = [
        (440, 0.05), (494, 0.05), (440, 0.05), (523, 0.05),
        (440, 0.05), (587, 0.05), (440, 0.05), (660, 0.05)
    ]
    for note, duration in melody:
        play_tone(note, duration)
        time.sleep(0.02)

def wlan_connection():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to network...")
        no_connection_melody()
        time.sleep(1)
    print("Connected to:", wlan.ifconfig())
    connection_melody()

def kalman_filter_update(angle, bias, rate, measurement, P, dt):
    rate_unbiased = rate - bias
    angle += rate_unbiased * dt
    P[0][0] += dt * (dt * P[1][1] - P[0][1] - P[1][0] + Q_angle)
    P[0][1] -= dt * P[1][1]
    P[1][0] -= dt * P[1][1]
    P[1][1] += Q_bias * dt

    S = P[0][0] + R_measure
    K = [P[0][0] / S, P[1][0] / S]
    y = measurement - angle
    angle += K[0] * y
    bias += K[1] * y

    P00_temp = P[0][0]
    P01_temp = P[0][1]

    P[0][0] -= K[0] * P00_temp
    P[0][1] -= K[0] * P01_temp
    P[1][0] -= K[1] * P00_temp
    P[1][1] -= K[1] * P01_temp

    return angle, bias, P

def calculate_angle_from_accel():
    accel_x = mpu.accel.x
    accel_y = mpu.accel.y
    accel_z = mpu.accel.z

    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * (180 / math.pi)
    roll = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)) * (180 / math.pi)
    return pitch, roll

# Main program
wlan_connection()
address = ('192.168.1.83', 12345)
s = socket.socket()
s.connect(address)

while True:
    current_time = time.ticks_ms()
    dt = (time.ticks_diff(current_time, previous_time)) / 1000.0
    previous_time = current_time

    # Read gyroscope values
    gyro_x = mpu.gyro.x
    gyro_y = mpu.gyro.y

    # Get accelerometer-based pitch and roll angles
    accel_pitch, accel_roll = calculate_angle_from_accel()

    # Apply Kalman filter
    angle_x, bias_x, P = kalman_filter_update(angle_x, bias_x, gyro_x, accel_pitch, P, dt)
    angle_y, bias_y, P = kalman_filter_update(angle_y, bias_y, gyro_y, accel_roll, P, dt)

    # Read flex sensor values
    flex_value1 = flex_sensor1.read_u16()
    flex_value2 = flex_sensor2.read_u16()

    # Combine all data into one message
    message = f"{flex_value1}#{flex_value2}#{angle_x:.2f}#{angle_y:.2f}"
    s.send(message.encode('utf-8'))
    print(message)

    time.sleep(0.05)
