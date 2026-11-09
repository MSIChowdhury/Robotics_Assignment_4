# Sample Code for Robotics_Assignment_4
# Copyright: 2026 CS 4379K / CS 5342 Introduction to Autonomous Robotics, Robotics and Autonomous Systems

# YOLO Subscriber code for Jetson NX or Remote PC.

# This code is complete and runs as-is. Read through it to see how a ROS2 subscriber works.

# Refer to the Lab PowerPoint materials and Appendix of Assignment 3 to learn more about coding on ROS2 and the hardware architecture of Turtlebot3.
# You can run this code on Jeston NX or the Remote PC on the same network.
# You would need a basic understanding of Python Data Structure and Object Oriented Programming, along with ROS2 concepts, to understand this code.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

class YoloJsonSubscriber(Node):
    def __init__(self):
        super().__init__('yolo_json_subscriber')

        # Listen to the JSON strings published by the YOLO publisher.
        self.subscription = self.create_subscription(
            String, '/yolo/detections_json', self.detection_callback, 10)

        self.get_logger().info("Listening for YOLO JSON detections...")

    def detection_callback(self, msg):
        try:
            # Parse the incoming JSON string back into a Python dictionary
            data = json.loads(msg.data)

            # Extract the metadata
            timestamp = data.get("timestamp", 0.0)
            frame_id = data.get("frame_id", "unknown")
            detections = data.get("detections", [])

            self.get_logger().info(f"Received {len(detections)} detections at t={timestamp:.2f} [{frame_id}]:")

            # Iterate through the detection list
            for i, det in enumerate(detections):
                class_name = det["class_name"]
                score = det["confidence"]
                bbox = det["bbox"]

                self.get_logger().info(
                    f"  [{i}] {class_name} ({score:.2f}) | "
                    f"Center: ({bbox['cx']:.1f}, {bbox['cy']:.1f}), "
                    f"Size: {bbox['w']:.1f}x{bbox['h']:.1f}"
                )

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Failed to parse JSON string: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = YoloJsonSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
