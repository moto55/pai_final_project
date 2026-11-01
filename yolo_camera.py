import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO

class YoloCamera(Node):
    def __init__(self):
        super().__init__('yolo_camera')

        self.bridge = CvBridge()
        self.model = YOLO('yolo11n.pt')

        self.subscription = self.create_subscription(
            Image,
            '/front_camera',
            self.image_callback,
            10
        )

        self.get_logger().info('YOLO camera node started')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        results = self.model(frame, verbose=False)

        detected = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                name = self.model.names[class_id]

                detected.append(
                    f'{name} ({confidence:.2f})'
                )

        if detected:
            self.get_logger().info(
                'Detected: ' + ', '.join(detected)
            )
        else:
            self.get_logger().info('Detected: nothing')


def main():
    rclpy.init()
    node = YoloCamera()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
