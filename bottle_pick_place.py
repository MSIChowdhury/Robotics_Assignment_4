# Sample Code for Robotics_Assignment_4
# Copyright: 2026 CS 4379K / CS 5342 Introduction to Autonomous Robotics, Robotics and Autonomous Systems

# Bottle visual servoing, pick and place for Turtlebot3 + OpenManipulatorX (Part 3).

# This code is complete and runs as-is. You do NOT need to write any code for Part 3.
# Your job is to set STAGE, copy your arm poses from Assignment 3, and tune the numbers in the
# settings block below by experimenting on the robot.

# It combines what you already know from Assignment 3 (Twist on /cmd_vel, arm and gripper action
# clients) with the YOLO detections from Part 2 (/yolo/detections_json).
# Run it on the Remote PC (Docker shell) or the Jetson, while the Jetson is running
#   1) ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
#   2) python3 yolo_publisher_sample_code.py
# Press Ctrl+C at any time to stop the robot.

import json
import math
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from control_msgs.action import FollowJointTrajectory, GripperCommand
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

##############################################################################
# SETTINGS - this is the only part you need to touch.
##############################################################################

# Which part of the task to run. Use one at a time for Part C a), b), c) of the demo.
#   "servo" : Part C a) Only turn the wheels to keep the bottle in the center. Does not drive forward.
#   "pick"  : Part C b) Servo, drive up to the bottle, grab it and lift it.
#   "full"  : Part C c) Everything in "pick", then drive back to the start point and place the bottle.
STAGE = "servo"

# --- What to look for -------------------------------------------------------
# YOLO sometimes mislabels objects. List every COCO label that should count as your target.
# Example for the bear doll: ["teddy bear", "donut"]
TARGET_CLASSES = ["bottle"]
MIN_CONFIDENCE = 0.4        # Ignore detections below this confidence.

# --- Visual servoing (turning) ----------------------------------------------
CENTER_TOLERANCE_PX = 40    # The bottle is "centered" if its center is within this many pixels of the image center.
TURN_GAIN = 0.002           # rad/s of turning per pixel of error. Too high: robot wobbles. Too low: robot is slow to react.
MAX_ANGULAR_VEL = 0.5       # rad/s, upper limit when turning.
MIN_ANGULAR_VEL = 0.1       # rad/s, lowest turn speed that still moves the wheels.
SEARCH_ANGULAR_VEL = 0.3    # rad/s, spin speed when the bottle is lost (only used in "pick" and "full").

# --- Approach (driving forward) ---------------------------------------------
FORWARD_VEL = 0.05          # m/s while approaching the bottle. Your Assignment 3 LIN_VEL_STEP_SIZE is a hint for a slow, safe speed.
# Stop when the bounding box is at least this tall (pixels). A taller box means the bottle is closer.
# Find your own value: run the subscriber from Part 2 and read the bbox Size (h) when the bottle is at grabbing distance.
STOP_BBOX_HEIGHT = 400

# --- Arm and gripper --------------------------------------------------------
# Joint angles in radians [joint1, joint2, joint3, joint4].
# IMPORTANT: copy these from your Assignment 3 code. HOME_POSE is POSES['9'], EXTEND_POSE is POSES['0'].
# The values below are only placeholders.
HOME_POSE = [0.0, 0.0, 0.0, 0.0]
EXTEND_POSE = [0.0, 0.9, 0.0, 0.5]
GRIPPER_OPEN = 0.01         # Copy from GRIPPER_KEY_BINDINGS in your Assignment 3 code ('g' = open, 'h' = close).
GRIPPER_CLOSE = -0.01
ARM_MOVE_SEC = 3.0          # Time given to the arm to reach a pose.
GRIPPER_MOVE_SEC = 2.0      # Time given to the gripper to open or close.

# --- Return and place (only used in "full") ---------------------------------
RETURN_VEL = 0.1            # m/s while driving back to the start point.
HOME_TOLERANCE = 0.15       # m, how close to the start point counts as "arrived".
RETURN_TIMEOUT = 60.0       # s, give up returning after this long.

##############################################################################
# END OF SETTINGS
##############################################################################

CONTROL_PERIOD = 0.1        # s, the control loop runs at 10 Hz.
DETECTION_TIMEOUT = 1.0     # s, a detection older than this is treated as "bottle lost".
ARRIVAL_FRAMES = 3          # Stop condition must hold for this many loops in a row.
ARM_JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4']


def clamp(value, limit):
    return max(-limit, min(limit, value))


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class BottlePickPlace(Node):
    def __init__(self):
        super().__init__('bottle_pick_place')

        # Same interfaces as Assignment 3
        self.arm_client = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(self, GripperCommand, '/gripper_controller/gripper_cmd')
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # New: YOLO detections from Part 2, and odometry so the robot can find its way back
        self.create_subscription(String, '/yolo/detections_json', self.detection_callback, 10)
        self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        self.image_width = 1280
        self.target = None          # latest detection of the target: dict with cx, h, stamp
        self.last_side = 1.0        # +1: target was last seen on the left, -1: on the right
        self.pose = None            # latest odometry (x, y, yaw)

    # ------------------------------------------------------------------ callbacks
    def detection_callback(self, msg):
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            return
        self.image_width = data.get("image_width", self.image_width)

        best = None
        for det in data.get("detections", []):
            if det["class_name"] in TARGET_CLASSES and det["confidence"] >= MIN_CONFIDENCE:
                if best is None or det["confidence"] > best["confidence"]:
                    best = det
        if best is None:
            return
        self.target = {
            "cx": best["bbox"]["cx"],
            "h": best["bbox"]["h"],
            "stamp": time.monotonic(),
        }

    def odom_callback(self, msg):
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.pose = (msg.pose.pose.position.x, msg.pose.pose.position.y, yaw)

    def get_target(self):
        """Latest target detection, or None if it is older than DETECTION_TIMEOUT."""
        if self.target is None or time.monotonic() - self.target["stamp"] > DETECTION_TIMEOUT:
            return None
        return self.target

    # ------------------------------------------------------------------ base
    def drive(self, linear, angular):
        twist = Twist()
        twist.linear.x = float(linear)
        twist.angular.z = float(angular)
        self.cmd_vel_pub.publish(twist)

    def stop(self):
        self.drive(0.0, 0.0)

    def turn_command(self, error_px):
        """Angular velocity that turns the robot toward a target error_px pixels from the center."""
        angular = clamp(-TURN_GAIN * error_px, MAX_ANGULAR_VEL)
        if abs(angular) < MIN_ANGULAR_VEL:
            angular = math.copysign(MIN_ANGULAR_VEL, angular if angular != 0.0 else -error_px)
        return angular

    def servo_step(self, approach):
        """One control step. Returns True when the bottle is close enough to grab (approach only)."""
        target = self.get_target()
        if target is None:
            # Bottle lost: spin toward the side it was last seen on (or just wait in "servo" stage).
            if approach:
                self.drive(0.0, SEARCH_ANGULAR_VEL * self.last_side)
            else:
                self.stop()
            return False

        error = target["cx"] - self.image_width / 2.0     # positive: bottle is right of center
        self.last_side = -1.0 if error > 0 else 1.0

        if abs(error) > CENTER_TOLERANCE_PX:
            self.drive(0.0, self.turn_command(error))      # turn in place until centered
            return False

        if not approach:
            self.stop()
            return False

        if target["h"] >= STOP_BBOX_HEIGHT:
            self.stop()
            return True

        self.drive(FORWARD_VEL, clamp(-TURN_GAIN * error, MAX_ANGULAR_VEL))
        return False

    # ------------------------------------------------------------------ arm and gripper
    def send_arm_goal(self, positions, duration_sec):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = ARM_JOINT_NAMES
        goal.trajectory.points.append(JointTrajectoryPoint(
            positions=positions,
            time_from_start=Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        ))
        self.arm_client.send_goal_async(goal)
        time.sleep(duration_sec + 0.5)

    def send_gripper_goal(self, position):
        goal = GripperCommand.Goal()
        goal.command.position = position
        goal.command.max_effort = 1.0
        self.gripper_client.send_goal_async(goal)
        time.sleep(GRIPPER_MOVE_SEC)

    # ------------------------------------------------------------------ return to start
    def turn_to_yaw(self, yaw, deadline):
        while rclpy.ok() and time.monotonic() < deadline:
            error = wrap_angle(yaw - self.pose[2])
            if abs(error) < 0.1:
                break
            self.drive(0.0, math.copysign(max(abs(clamp(error, 0.5)), MIN_ANGULAR_VEL), error))
            time.sleep(CONTROL_PERIOD)
        self.stop()

    def go_to(self, x, y):
        deadline = time.monotonic() + RETURN_TIMEOUT
        while rclpy.ok() and time.monotonic() < deadline:
            dx, dy = x - self.pose[0], y - self.pose[1]
            if math.hypot(dx, dy) < HOME_TOLERANCE:
                break
            error = wrap_angle(math.atan2(dy, dx) - self.pose[2])
            if abs(error) > 0.3:
                self.drive(0.0, math.copysign(max(abs(clamp(error, 0.5)), MIN_ANGULAR_VEL), error))
            else:
                self.drive(RETURN_VEL, clamp(1.5 * error, 0.5))
            time.sleep(CONTROL_PERIOD)
        self.stop()
        return time.monotonic() < deadline

    # ------------------------------------------------------------------ main sequence
    def run(self):
        self.get_logger().info(f"STAGE = {STAGE}, looking for {TARGET_CLASSES}")

        if STAGE != "servo":
            self.get_logger().info("Waiting for arm and gripper controllers and odometry...")
            self.arm_client.wait_for_server()
            self.gripper_client.wait_for_server()
            while rclpy.ok() and self.pose is None:
                time.sleep(0.1)
            start_x, start_y, start_yaw = self.pose
            self.get_logger().info(f"Start point recorded at x={start_x:.2f} y={start_y:.2f}")

            self.get_logger().info("Arm to home pose, gripper open.")
            self.send_arm_goal(HOME_POSE, ARM_MOVE_SEC)
            self.send_gripper_goal(GRIPPER_OPEN)

        # Lock onto the bottle (and approach it unless STAGE is "servo")
        approach = STAGE != "servo"
        arrived = 0
        self.get_logger().info("Tracking the bottle. Press Ctrl+C to stop.")
        while rclpy.ok():
            arrived = arrived + 1 if self.servo_step(approach) else 0
            if arrived >= ARRIVAL_FRAMES:
                break
            time.sleep(CONTROL_PERIOD)
        if not approach:
            return
        self.stop()

        # Pick: extend, close the gripper on the bottle, retract to home with the bottle lifted
        self.get_logger().info("Picking up the bottle.")
        self.send_arm_goal(EXTEND_POSE, ARM_MOVE_SEC)
        self.send_gripper_goal(GRIPPER_CLOSE)
        self.send_arm_goal(HOME_POSE, ARM_MOVE_SEC)
        if STAGE == "pick":
            self.get_logger().info("Pick complete.")
            return

        # Return to the start point and place the bottle on the ground
        self.get_logger().info("Returning to the start point.")
        if not self.go_to(start_x, start_y):
            self.get_logger().warn("Return timed out, placing the bottle here.")
        self.turn_to_yaw(start_yaw, time.monotonic() + 15.0)
        self.get_logger().info("Placing the bottle.")
        self.send_arm_goal(EXTEND_POSE, ARM_MOVE_SEC)
        self.send_gripper_goal(GRIPPER_OPEN)
        self.send_arm_goal(HOME_POSE, ARM_MOVE_SEC)
        self.get_logger().info("Pick and place complete.")


def main(args=None):
    rclpy.init(args=args)
    node = BottlePickPlace()
    # Spin callbacks (detections, odometry) in the background; the main thread runs the task sequence.
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
