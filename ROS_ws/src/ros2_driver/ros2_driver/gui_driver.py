import rclpy
from rclpy.node import Node
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from std_msgs.msg import Int8
from std_msgs.msg import Float32
from std_msgs.msg import Bool
from ros2_driver import LightControl

ROS_SPIN_INTERVAL = 10  # ROS 消息处理间隔，单位毫秒

class MainWindow(QMainWindow, LightControl.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class GuiDriver(Node):
    def __init__(self, name):
        super().__init__(name)
        self.app = QApplication([])
        self.main_window = MainWindow()
        self.main_window.setWindowTitle("小灯控制与引脚信息显示")
        self.main_window.lightSlider.valueChanged.connect(self.light_slider_changed)
        self.main_window.openButton.clicked.connect(self.openButton_clicked)
        self.main_window.closeButton.clicked.connect(self.closeButton_clicked)
        self.main_window.transmitButton.clicked.connect(self.transmitButton_clicked)
        self.publisher_led_switch = self.create_publisher(Int8, 'cmd_led_switch', 10)
        self.publisher_led_brightness = self.create_publisher(Float32, 'cmd_led_brightness', 10)
        self.listener_gpio_state = self.create_subscription(Bool, 'gpio_state', self.gpio_state_callback, 10)
        self.timer = QTimer()
        self.timer.timeout.connect(self.ros_spin_once)
        self.timer.start(ROS_SPIN_INTERVAL)
        self.main_window.show()
        self.app.exec()

    def ros_spin_once(self):
        rclpy.spin_once(self, timeout_sec=0)
    
    def light_slider_changed(self, value):
        self.main_window.sliderLabel.setText(f"{value}")
        msg = Float32()
        msg.data = value / 100.0
        self.publisher_led_brightness.publish(msg)
        self.get_logger().info(f"发布亮度: {msg.data:.2f}")

    def openButton_clicked(self):
        msg = Int8()
        msg.data = 0x01
        self.publisher_led_switch.publish(msg)
        self.get_logger().info(f"发布开关信号: {msg.data}")
    def closeButton_clicked(self):
        msg = Int8()
        msg.data = 0x00
        self.publisher_led_switch.publish(msg)
        self.get_logger().info(f"发布开关信号: {msg.data}")

    def transmitButton_clicked(self):
        msg = Int8()
        msg.data = 0x02
        self.publisher_led_switch.publish(msg)
        self.get_logger().info(f"发布转换信号: {msg.data}")

    def gpio_state_callback(self, msg):
        if msg.data == True:
            self.main_window.gpioLabel.setText("引脚电平: 高电平")
        else:
            self.main_window.gpioLabel.setText("引脚电平: 低电平")
        
def main(args=None):
    rclpy.init(args=args)
    node = GuiDriver('gui_driver')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()