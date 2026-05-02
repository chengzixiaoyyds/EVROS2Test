import serial
import logging
import sys
import threading
import time

SERIAL_PORT = 'COM11'
BAUDRATE = 115200
send_interval = 0.2  # 5 Hz
stop_event = threading.Event()

command = 0
value = 0

def connect_com():
    """初始化并连接串口"""
    try:
        com_serial = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"✅ 成功连接到串口 {SERIAL_PORT}, 波特率 {BAUDRATE}")
        logging.info(f"成功连接到串口 {SERIAL_PORT}")
        return com_serial
    except serial.SerialException as e:
        print(f"❌ 错误: 无法打开串口 {SERIAL_PORT}。")
        logging.error(f"无法打开串口 {e}")
        return None
    
def build_packet(command, value):
    """构建数据包"""
    HEADER = [0x5A, 0xA5]  # 包头
    Command = command  # 命令字
    Value = value  # 数据值
    packet = bytes([*HEADER, Command, Value])
    checksum = sum(packet) & 0xFF
    return packet + bytes([checksum])

def sender():
    """定时发送线程"""
    while not stop_event.is_set():
        # ----- 可自定义要发送的数据 -----
        com.write(build_packet(command, value))
        print("发送数据包: ", build_packet(command, value))
        time.sleep(send_interval)

if __name__ == "__main__":
    com = connect_com()
    if com is None:
        sys.exit(1)
    t = threading.Thread(target=sender, daemon=True)
    t.start()
    running = True
    while running:
        command = input("输入命令字 (0-255, q退出): ")
        if command.lower() == 'q':
            running = False
            continue
        value = input("输入数据值 (0-255): ")
    stop_event.set()
    com.close()
    sys.exit(0)