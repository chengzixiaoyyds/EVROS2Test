import rclpy
from rclpy.node import Node
import serial
import logging
import sys
import struct
from std_msgs.msg import Int8
from std_msgs.msg import Float32
from std_msgs.msg import Bool

SERIAL_PORT = '/dev/ttyUSB0'  # 根据实际情况修改
BAUDRATE = 115200
RECV_POLL_INTERVAL = 0.01    # 接收轮询间隔

class CommandBuffer:
    """循环缓冲区，用于解析串口指令"""
    
    BUFFER_SIZE = 255 # 缓冲区大小
    
    def __init__(self):
        self.buffer = bytearray(self.BUFFER_SIZE)
        self.read_index = 0
        self.write_index = 0
    
    def _read(self, index: int) -> int:
        """读取缓冲区第 index 位（自动循环）"""
        return self.buffer[index % self.BUFFER_SIZE]
    
    def _add_read_index(self, length: int) -> None:
        """读指针前进 length 字节"""
        self.read_index = (self.read_index + length) % self.BUFFER_SIZE
    
    def get_length(self) -> int:
        """未处理数据长度"""
        return (self.write_index - self.read_index + self.BUFFER_SIZE) % self.BUFFER_SIZE

    def get_remain(self) -> int:
        """剩余空间"""
        return self.BUFFER_SIZE - self.get_length()

    def write(self, data: bytes) -> int:
        """写入数据，返回实际写入的字节数（空间不足返回0）"""
        length = len(data)
        if self.get_remain() < length:
            return 0

        # 分情况写入：不跨边界 / 跨边界
        first_part = self.BUFFER_SIZE - self.write_index
        if length <= first_part:
            self.buffer[self.write_index : self.write_index + length] = data
            self.write_index += length
        else:
            # 先写尾部，再回头写头部
            self.buffer[self.write_index :] = data[:first_part]
            second_part = length - first_part
            self.buffer[:second_part] = data[first_part:]
            self.write_index = second_part
        return length

    def get_command(self):
        """
        尝试提取一条完整指令。
        成功时返回 bytes 类型的指令包（包含包头、命令、数据、校验），失败返回 None。
        """
        COMMAND_MIN_LENGTH = 4  # 包头2 + 命令1 + 校验1

        while True:
            cur_len = self.get_length()
            if cur_len < COMMAND_MIN_LENGTH:
                return None

            # 寻找包头 0x5A 0xA5
            if self._read(self.read_index) != 0x5A or self._read(self.read_index + 1) != 0xA5:
                self._add_read_index(1)
                continue

            packet_len = 6

            if cur_len < packet_len:
                return None

            # 计算校验和（包内除校验字节外的所有字节求和，取低 8 位）
            checksum = sum(self._read(self.read_index + i) for i in range(packet_len - 1)) & 0xFF
            if checksum != self._read(self.read_index + packet_len - 1):
                self._add_read_index(1)   # 校验错，只移动 1 字节
                continue

            # 提取完整数据包
            cmd_bytes = bytes(self._read(self.read_index + i) for i in range(packet_len))
            self._add_read_index(packet_len)
            return cmd_bytes

command_buffer = CommandBuffer()

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
                self.publisher_gpio_state.publish(Bool(cmd))  # 假设 0x10 表示 GPIO 状态为 True
                self.get_logger().info(f"接收: {packet.hex()}，发布 GPIO 状态: {cmd}")

def main(args=None):
    rclpy.init(args=args)
    serial_driver = SerialDriver('serial_driver')
    rclpy.spin(serial_driver)
    serial_driver.destroy_node()
    rclpy.shutdown()