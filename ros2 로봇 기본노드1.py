import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class SimpleAutonomousDrive(Node):
    def __init__(self):
        super().__init__('simple_autonomous_drive')
        
        # 라이다 데이터를 받기 위한 구독자(Subscriber) 설정
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # 모터 제어 명령을 보내기 위한 발행자(Publisher) 설정
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.move_cmd = Twist()

    def scan_callback(self, msg):
        # 전방 30도 범위(-15도 ~ +15도)의 거리 데이터 추출
        # msg.ranges는 라이다가 한 바퀴 돌며 측정한 거리 리스트입니다.
        front_ranges = msg.ranges[0:15] + msg.ranges[-15:]
        
        # 유효한 거리 값 중 가장 가까운 거리 확인
        min_distance = min([r for r in front_ranges if r > 0.1]) # 0.1m 이하는 무시

        if min_distance < 0.5:  # 0.5m 이내에 장애물이 있다면
            self.get_logger().info(f'장애물 감지! 거리: {min_distance:.2f}m - 회전합니다.')
            self.move_cmd.linear.x = 0.0   # 정지
            self.move_cmd.angular.z = 0.5  # 제자리 회전
        else:
            self.get_logger().info(f'전방 클리어. 전진 중...')
            self.move_cmd.linear.x = 0.2   # 0.2m/s 속도로 전진
            self.move_cmd.angular.z = 0.0

        # 최종 명령을 /cmd_vel 토픽으로 전송
        self.cmd_vel_pub.publish(self.move_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SimpleAutonomousDrive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('노드를 종료합니다.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
