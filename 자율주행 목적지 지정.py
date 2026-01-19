import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import sys

def create_pose(navigator, x, y, w):
    """좌표 생성을 위한 헬퍼 함수"""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.w = w
    return pose

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # 1. 목적지 사전 정의 (x, y, orientation_w)
    # 실제 환경에서 슬램(SLAM)을 통해 얻은 좌표를 입력해야 합니다.
    destinations = {
        "kitchen": [2.5, 0.5, 1.0],
        "table1": [1.5, -1.2, 1.0],
        "trash_can": [-0.5, 2.0, 1.0],
        "home": [0.0, 0.0, 1.0]
    }

    # 2. 로봇의 위치 추정(Localization)이 완료될 때까지 대기
    # navigator.waitUntilNav2Active()

    while True:
        # 3. 사용자 입력 받기
        print("\n=== 이동 가능한 목적지 ===")
        for key in destinations.keys():
            print(f"- {key}")
        print("- exit (종료)")
        
        target = input("목적지를 입력하세요: ").strip()

        if target == "exit":
            break
        
        if target not in destinations:
            print("알 수 없는 목적지입니다. 다시 입력해주세요.")
            continue

        # 4. 목적지 좌표 설정 및 이동 명령
        goal_data = destinations[target]
        goal_pose = create_pose(navigator, goal_data[0], goal_data[1], goal_data[2])
        
        print(f"{target}(으)로 이동을 시작합니다...")
        navigator.goToPose(goal_pose)

        # 5. 도착 여부 확인 및 피드백
        while not navigator.isTaskComplete():
            feedback = navigator.get_feedback()
            if feedback:
                # 약 2초마다 남은 거리 출력
                if int(feedback.distance_remaining * 10) % 5 == 0:
                    print(f"남은 거리: {feedback.distance_remaining:.2f} m")

        # 6. 결과 처리
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f"성공적으로 {target}에 도착했습니다!")
        elif result == TaskResult.CANCELED:
            print("이동 명령이 취소되었습니다.")
        elif result == TaskResult.FAILED:
            print("이동에 실패했습니다. 경로를 확인하세요.")

    navigator.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
