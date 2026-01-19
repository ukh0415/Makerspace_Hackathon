import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Quaternion
from nav_msgs.msg import Odometry
import RPi.GPIO as GPIO
import math

class FourWheelDriveController(Node):
    def __init__(self):
        super().__init__('four_wheel_drive_controller')
        
        # 1. 파라미터 설정 (실측치 입력 필요)
        self.declare_parameter('wheel_diameter', 0.065)
        self.declare_parameter('track_width', 0.20) # 실측 윤거 x 1.2 (Skid 보정)
        self.ppr = 334 * 4
        
        self.wheel_radius = self.get_parameter('wheel_diameter').value / 2.0
        self.track_width = self.get_parameter('track_width').value
        
        # 2. 변수 초기화
        self.ticks = {'fl': 0, 'rl': 0, 'fr': 0, 'rr': 0} #각 바퀴의 회전수 초기화. odom에서 사용
        self.x = 0.0; self.y = 0.0; self.th = 0.0
        self.last_time = self.get_clock().now() #odom에서 현재 로봇의 위치를 확인하기 위해 시간 간격 확인, cmd vel에서 속도*시간으로 거리구함

        # 3. ROS2 통신
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10) #여기서 ros2 로봇 기본노드1에서 발행하는 /cmd_ve토픽구독
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.timer = self.create_timer(0.05, self.update_odometry) # 20Hz주기로 로봇의 위치 최신화

        # 4. GPIO 설정 및 인터럽트 등록 (생략된 핀은 위 표 참고)
        self.setup_gpio() #모터 엔코더를 라즈베리파이와 연결시키는 함수

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM) #라즈베리파이 BCM번호 사용
        # 예시: FL 엔코더 등록 (나머지 바퀴도 동일하게 반복)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP) #4번핀을 이용하겠다.
        GPIO.add_event_detect(4, GPIO.BOTH, callback=lambda ch: self.encoder_cb('fl')) #4번핀에 신호가 들어오면 FL바퀴에 틱을 1 추가
         # GPIO.BOTH는 인코더모터 신호가 0에서1로, 1에서 0으로 변할떄 그 변화를 감지하여 이동거리 측정
         # GPI)BOTH에서 신호가 감지되는 순간(callback) lambda ch: self.encoder_cb('fl') 함수 실행, lamda가 fl에 숫자 1을 추가하라는 명령을 전해줌줌
        # ... RL, FR, RR 등록 로직 ...

    def encoder_cb(self, wheel):
        self.ticks[wheel] += 1 #바퀴에 신호가 오면 틱을 1 추가, 거리계산 근거

    def update_odometry(self):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9 #두 지점사이 시간 간격 계산
        
        # 각 바퀴별 이동 거리 (m)
        dist = {k: (v / self.ppr) * (2 * math.pi * self.wheel_radius) for k, v in self.ticks.items()} 
        
        # 좌우 평균 거리 계산
        d_left = (dist['fl'] + dist['rl']) / 2.0
        d_right = (dist['fr'] + dist['rr']) / 2.0
        
        delta_d = (d_left + d_right) / 2.0
        delta_th = (d_right - d_left) / self.track_width
        
        # 위치 업데이트 (Dead Reckoning)
        self.x += delta_d * math.cos(self.th + delta_th / 2.0)
        self.y += delta_d * math.sin(self.th + delta_th / 2.0)
        self.th += delta_th

       def publish_odom(self, current_time):
         odom_msg = Odometry()

    # 1. Header 설정
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

    # 2. Pose (위치 및 방향) 설정
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0 # 평면 주행이므로 0

    # 오일러 각(th)을 쿼터니언으로 변환
        odom_msg.pose.pose.orientation.x = 0.0
        odom_msg.pose.pose.orientation.y = 0.0
        odom_msg.pose.pose.orientation.z = math.sin(self.th / 2.0)
        odom_msg.pose.pose.orientation.w = math.cos(self.th / 2.0)

    # 3. Twist (현재 속도) 설정 - SLAM 성능 향상에 도움
        # delta_d / dt 등을 통해 계산된 값을 넣습니다.
        # odom_msg.twist.twist.linear.x = current_linear_velocity
        # odom_msg.twist.twist.angular.z = current_angular_velocity

    # 메시지 발행
        self.odom_pub.publish(odom_msg)
        
        # 틱 초기화 및 시간 갱신
        for k in self.ticks: self.ticks[k] = 0
        self.last_time = current_time

    def cmd_callback(self, msg):
        # 4륜 구동 모터 출력 제어 로직 (앞서 배운 2륜 확장형 사용)
        pass

def main():
    rclpy.init()
    node = FourWheelDriveController()
    try:
        rclpy.spin(node)
    finally:
        GPIO.cleanup()
        rclpy.shutdown()
