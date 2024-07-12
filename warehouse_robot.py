import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from pymavlink import mavutil
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

class WarehouseRobot(Node):
    def __init__(self):
        super().__init__('warehouse_robot')
        self.vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.laser_subscriber = self.create_subscription(LaserScan, 'scan', self.laser_callback, 10)
        self.mavlink_connection = mavutil.mavlink_connection('udpin:localhost:14540')
        
    def laser_callback(self, msg):
        if min(msg.ranges) < 0.5:
            self.send_velocity(0.0, 0.5)
        else:
            self.send_velocity(0.5, 0.0)
        
    def send_velocity(self, linear, angular):
        vel_msg = Twist()
        vel_msg.linear.x = linear
        vel_msg.angular.z = angular
        self.vel_publisher.publish(vel_msg)
        
    def send_mavlink_command(self, command):
        msg = mavutil.mavlink.MAVLink_command_long_message(
            0, 0, mavutil.mavlink.MAV_CMD_OVERRIDE_GOTO, 0,
            command, 0, 0, 0, 0, 0, 0)
        self.mavlink_connection.mav.send(msg)

class MainWindow(QMainWindow):
    def __init__(self, robot):
        super(MainWindow, self).__init__()
        loadUi('robotcontrol.ui', self)
        self.robot = robot
        self.forwardButton.clicked.connect(self.forward_clicked)
        self.backwardButton.clicked.connect(self.backward_clicked)
        self.leftButton.clicked.connect(self.left_clicked)
        self.rightButton.clicked.connect(self.right_clicked)
        self.stopButton.clicked.connect(self.stop_clicked)
        
    def forward_clicked(self):
        self.robot.send_mavlink_command(1)
        
    def backward_clicked(self):
        self.robot.send_mavlink_command(3)
        
    def left_clicked(self):
        self.robot.send_mavlink_command(2)
        
    def right_clicked(self):
        self.robot.send_mavlink_command(0)
        
    def stop_clicked(self):
        self.robot.send_mavlink_command(0)

def main(args=None):
    rclpy.init(args=args)
    robot = WarehouseRobot()
    app = QApplication(sys.argv)
    window = MainWindow(robot)
    window.show()
    app.exec_()
    robot.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()