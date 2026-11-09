# Sample Code for Robotics_Assignment_4
# Copyright: 2026 CS 4379K / CS 5342 Introduction to Autonomous Robotics, Robotics and Autonomous Systems

# YOLO Publisher code for Jetson NX.

# This code is complete and runs as-is. Read through it to see how a ROS2 publisher works.
# The only things you may want to change are the settings right below the imports.

# Refer to the Lab PowerPoint materials and Appendix of Assignment 3 to learn more about coding on ROS2 and the hardware architecture of Turtlebot3.
# You have to run this code on Turtlebot3 Nvidia Jetson.
# You would need a basic understanding of Python Data Structure and Object Oriented Programming, along with ROS2 concepts, to understand this code.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import cv2
import json
from ultralytics import YOLO

##############################################################################
# Settings you can tune
# MODEL_PATH:
#   'yolo11n.pt'      CUDA - Nvidia GPU without optimizations (downloads on the first run).
#   'yolo11n.engine'  CUDA+TensorRT - optimized. Copy the .engine file from
#                     Assignment_4_demo/CUDA_Demo into the same folder as this script first.
#   Larger models (yolo11s, yolo11m, ...) are slower but more accurate.
MODEL_PATH = 'yolo11n.pt'
# PUBLISH_PERIOD: seconds between camera frames (0.05 = 20 Hz).
PUBLISH_PERIOD = 0.05
##############################################################################

class YoloJsonPublisher(Node):
    def __init__(self):
        super().__init__('yolo_json_publisher')

        # Publish detections as a JSON string on this topic.
        self.publisher_ = self.create_publisher(String, '/yolo/detections_json', 10)

        # Load YOLOv11 base model (Not Pose, Not Seg) onto the Jetson's GPU
        self.get_logger().info("Loading YOLOv11 model on CUDA...")
        if MODEL_PATH.endswith('.engine'):
            self.model = YOLO(MODEL_PATH, task='detect')
        else:
            self.model = YOLO(MODEL_PATH)
            self.model.to('cuda:0')

        # GStreamer pipeline for Raspberry Pi V2 Camera on Jetson CSI port
        gstreamer_pipeline = (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)30/1 ! "
            "nvvidconv ! "
            "video/x-raw, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
        )

        self.get_logger().info("Initializing CSI Camera...")
        self.cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            self.get_logger().error("Failed to open camera.")
            return

        # Capture a frame, run YOLO and publish every PUBLISH_PERIOD seconds.
        self.timer = self.create_timer(PUBLISH_PERIOD, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Run YOLO inference
        results = self.model(frame, verbose=False)[0]

        # Initialize the dictionary to hold our data
        detection_data = {
            "timestamp": self.get_clock().now().nanoseconds / 1e9,
            "frame_id": "camera_link",
            "image_width": frame.shape[1],
            "image_height": frame.shape[0],
            "detections": []
        }

        # Populate the dictionary with YOLO results
        for box in results.boxes:
            x_center, y_center, width, height = box.xywh[0].tolist()
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            detection_data["detections"].append({
                "class_name": self.model.names[class_id],
                "confidence": confidence,
                "bbox": {"cx": x_center, "cy": y_center, "w": width, "h": height}
            })

        # Convert the dictionary into a JSON string, wrap it in a String message and publish it.
        msg = String()
        msg.data = json.dumps(detection_data)
        self.publisher_.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = YoloJsonPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
