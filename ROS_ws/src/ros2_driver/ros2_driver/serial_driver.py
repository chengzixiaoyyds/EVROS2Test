import rclpy
from rclpy.node import Node
import serial
import logging
import sys
import struct
from std_msgs.msg import Int8
from std_msgs.msg import Float32
from std_msgs.msg import Bool
from ros2_driver import Command

SERIAL_PORT = '/dev/ttyUSB0'  # 根据实际情况修改
BAUDRATE = 115200
RECV_POLL_INTERVAL = 0.01    # 接收轮询间隔

command_buffer = Command.CommandBuffer()

# ---------- 串口 ----------
def connect_com():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"✅ 成功连接到串口 {SERIAL_PORT}，波特率 {BAUDRATE}")
        logging.info(f"成功连接到串口 {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"❌ 无法打开串口 {SERIAL_PORT}: {e}")
        logging.error(f"无法打开串口: {e}")
        return None
    
# ---------- 数据包构建 ----------
def build_packet(command: int, value: int) -> bytes:
    HEADER = bytes([0x5A, 0xA5])
    # 构建数据部分：包头 + 命令 + 值
    if command == 2:
        # 亮度值转为 4 字节 float（小端序，可改为 '>f' 大端）
        payload = HEADER + bytes([command]) + struct.pack('<f', value)
    else:
        # 普通命令，value 占 1 字节
        payload = HEADER + bytes([command, value])
    checksum = sum(payload) & 0xFF
    return payload + bytes([checksum])

class SerialDriver(Node):
    def __init__(self, name):
        super().__init__(name)
        self.com = connect_com()
        if self.com is None:
            self.get_logger().error("无法连接到串口，节点将退出")
            self.destroy_node()
            rclpy.shutdown()
            sys.exit(1)
        self.listener_led_switch = self.create_subscription(Int8, 'cmd_led_switch', self.led_switch_callback, 10)
        self.listener_led_brightness = self.create_subscription(Float32, 'cmd_led_brightness', self.led_brightness_callback, 10)
        self.publisher_gpio_state = self.create_publisher(Bool, 'gpio_state', 10)
        self.timer = self.create_timer(RECV_POLL_INTERVAL, self.publish_gpio_state)
        
    def led_switch_callback(self, msg):
        packet = build_packet(0x01, msg.data)
        self.com.write(packet)
        self.get_logger().info(f"发送: {packet.hex()}")

    def led_brightness_callback(self, msg):
        packet = build_packet(0x02, msg.data)
        self.com.write(packet)
        self.get_logger().info(f"发送: {packet.hex()}")

    def publish_gpio_state(self):
        if self.com.in_waiting:
            data = self.com.read(self.com.in_waiting)
            command_buffer.write(data)
            packet = command_buffer.get_command()
            if packet:
                cmd = packet[2]
                self.publisher_gpio_state.publish(Bool(data = bool(cmd)))  # 假设 0x10 表示 GPIO 状态为 True
                self.get_logger().info(f"接收: {packet.hex()}，发布 GPIO 状态: {cmd}")

def main(args=None):
    rclpy.init(args=args)
    serial_driver = SerialDriver('serial_driver')
    rclpy.spin(serial_driver)
    serial_driver.destroy_node()
    rclpy.shutdown()