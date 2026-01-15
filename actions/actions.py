from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time

# 구역별 좌표 데이터베이스 (나중에 SLAM 지도 좌표로 수정하세요)
LOCATION_MAP = {
    "A": {"x": 1.2, "y": 0.5},
    "B": {"x": 3.5, "y": -1.2},
    "C": {"x": -0.8, "y": 2.0},
}

class ActionMoveRobot(Action):
    def name(self) -> Text:
        # domain.yml의 actions 리스트에 있는 이름과 일치해야 합니다.
        return "action_move_robot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. 사용자가 말한 구역(area) 추출
        area = tracker.get_slot("area")
        
        if not area:
            dispatcher.utter_message(text="어떤 구역으로 갈까요? A, B, C 구역 중에서 말씀해주세요.")
            return []

        if area not in LOCATION_MAP:
            dispatcher.utter_message(text=f"죄송합니다. '{area}' 구역은 아직 지도에 등록되지 않았습니다.")
            return []

        # 2. 목표 좌표 설정
        goal = LOCATION_MAP[area]
        dispatcher.utter_message(text=f"확인했습니다. {area} 구역(좌표: {goal['x']}, {goal['y']})으로 로봇을 보낼게요.")

        # 3. ROS2로 좌표 전송 및 결과 확인
        success = self.publish_ros_goal(goal['x'], goal['y'])

        if success:
            print(f"✅ [SUCCESS] ROS2 Topic '/goal_pose'에 {area} 구역 좌표가 성공적으로 발행되었습니다!")
        else:
            print(f"❌ [ERROR] ROS2 Topic 발행에 실패했습니다. ROS2 환경을 확인하세요.")

        return []

    def publish_ros_goal(self, x, y):
        try:
            # ROS2 초기화 (이미 되어있지 않은 경우에만)
            if not rclpy.ok():
                rclpy.init()
            
            node = Node('rasa_action_node')
            # Nav2가 기본적으로 사용하는 목표 좌표 토픽은 /goal_pose 입니다.
            publisher = node.create_publisher(PoseStamped, '/goal_pose', 10)
            
            # 메시지 구성
            msg = PoseStamped()
            msg.header.frame_id = "map"
            msg.header.stamp = node.get_clock().now().to_msg()
            msg.pose.position.x = float(x)
            msg.pose.position.y = float(y)
            msg.pose.orientation.w = 1.0  # 정면 방향
            
            # 메시지 발행 (안정성을 위해 0.1초 대기 후 발행)
            time.sleep(0.1)
            publisher.publish(msg)
            
            node.destroy_node()
            return True
        except Exception as e:
            print(f"ROS2 Publish Error: {e}")
            return False