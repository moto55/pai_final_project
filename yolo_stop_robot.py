import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from ultralytics import YOLO


class YoloStopRobot(Node):
    def __init__(self):
        super().__init__('yolo_stop_robot')

        self.bridge = CvBridge()
        self.model = YOLO('yolo11n.pt')

        self.stopped = False
        self.safe_since = None

        # 停止判定
        self.stop_ratio = 0.08

        # 停止後、2秒間安全なら再発進
        self.resume_delay = 5.0

        self.image_sub = self.create_subscription(
            Image,
            '/front_camera',
            self.image_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.get_logger().info(
            'AI pedestrian safety controller started'
        )

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        h, w = frame.shape[:2]

        results = self.model(frame, verbose=False)

        person_detected = False
        person_close = False
        best_conf = 0.0
        largest_ratio = 0.0

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                name = self.model.names[class_id]

                if name != 'person' or confidence < 0.50:
                    continue

                person_detected = True

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                box_area = (x2 - x1) * (y2 - y1)
                image_area = w * h
                ratio = box_area / image_area

                best_conf = max(best_conf, confidence)
                largest_ratio = max(largest_ratio, ratio)

                if ratio > self.stop_ratio:
                    person_close = True

        now = time.monotonic()

        # 危険を検知したら即停止
        if person_close:
            self.stopped = True
            self.safe_since = None

        # 停止中で、もう危険でない
        elif self.stopped:
            if self.safe_since is None:
                self.safe_since = now

            elif now - self.safe_since >= self.resume_delay:
                self.stopped = False
                self.safe_since = None

        cmd = Twist()

        if self.stopped:
            cmd.linear.x = 0.0

            if person_close:
                self.get_logger().info(
                    f'PERSON CLOSE '
                    f'conf={best_conf:.2f} '
                    f'size={largest_ratio:.2f} -> STOP'
                )
            else:
                remaining = max(
                    0.0,
                    self.resume_delay - (now - self.safe_since)
                )

                self.get_logger().info(
                    f'Path clearing... resume in {remaining:.1f}s'
                )

        else:
            cmd.linear.x = 0.35

            if person_detected:
                self.get_logger().info(
                    f'Person far '
                    f'conf={best_conf:.2f} '
                    f'size={largest_ratio:.2f} -> FORWARD'
                )
            else:
                self.get_logger().info(
                    'No person -> FORWARD'
                )

        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = YoloStopRobot()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        stop = Twist()
        node.cmd_pub.publish(stop)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
