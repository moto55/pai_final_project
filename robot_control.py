import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.publisher = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

    def move(self, command):
        msg = Twist()

        if command == 'forward':
            msg.linear.x = 1.0
        elif command == 'left':
            msg.linear.x = 0.5
            msg.angular.z = 1.0
        elif command == 'right':
            msg.linear.x = 0.5
            msg.angular.z = -1.0
        elif command == 'stop':
            pass
        else:
            print('Unknown command')
            return

        self.publisher.publish(msg)
        print(f'Command sent: {command}')


def main():
    rclpy.init()
    node = RobotController()

    while True:
        command = input('command (forward / left / right / stop / exit): ')

        if command == 'exit':
            node.move('stop')
            break

        node.move(command)
        rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
