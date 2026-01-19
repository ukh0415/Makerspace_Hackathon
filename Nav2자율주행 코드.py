import rclpy
from rclpy.duration import Duration
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # 로봇의 초기 위치 설정
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.0
    initial_pose.pose.position.y = 0.0
    initial_pose.pose.orientation.z = 0.0
    initial_pose.pose.orientation.w = 1.0
    


    # 목적지(Goal Pose) 설정
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.5  # 2.5미터 전진
    goal_pose.pose.position.y = 1.0  # 1미터 왼쪽으로
    goal_pose.pose.orientation.w = 1.0 # 정면을 바라보며 도착

    # 3. 목적지로 이동 명령
    navigator.goToPose(goal_pose)

    # 4. 이동 상태 모니터링
    i = 0
    while not navigator.isTaskComplete():
        i += 1
        feedback = navigator.getFeedback()
        if feedback and i % 5 == 0:
            print(f'남은 거리: {feedback.distance_remaining:.2f} m')
            print(f'예상 도착 시간: {Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9:.1f} 초')

    # 5. 결과 확인
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('목적지에 성공적으로 도착했습니다!')
    elif result == TaskResult.CANCELED:
        print('이동 명령이 취소되었습니다.')
    elif result == TaskResult.FAILED:
        print('이동에 실패했습니다.')

    navigator.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
