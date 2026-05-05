import serial
import logging
import sys
import threading
import time
import struct
import Command

# ---------- 配置 ----------
SERIAL_PORT = '/dev/ttyUSB0'  # 根据实际情况修改
BAUDRATE = 115200
SEND_INTERVAL = 0.2  # 5 Hz
RECV_POLL_INTERVAL = 0.01    # 接收轮询间隔

# 全局共享变量（线程安全）
latest_command = 0
latest_value = 0
data_lock = threading.Lock()
stop_event = threading.Event()
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
        brightness = value / 100.0
        # 亮度值转为 4 字节 float（小端序，可改为 '>f' 大端）
        payload = HEADER + bytes([command]) + struct.pack('<f', brightness)
    else:
        # 普通命令，value 占 1 字节
        payload = HEADER + bytes([command, value])
    checksum = sum(payload) & 0xFF
    return payload + bytes([checksum])  

# ---------- 发送线程 ----------
def sender(ser: serial.Serial):
    last_time = time.time()
    while not stop_event.is_set():
        # 获取最新的命令和值（线程安全）
        with data_lock:
            cmd = latest_command
            val = latest_value
        
        packet = build_packet(cmd, val)
        ser.write(packet)
        
        # 精准 5Hz 延时（避免累积误差）
        elapsed = time.time() - last_time
        sleep_time = SEND_INTERVAL - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        last_time += SEND_INTERVAL
    
# ---------- 接收线程 ----------
def receiver(ser: serial.Serial, buf: Command.CommandBuffer):
    """持续读取串口数据并写入循环缓冲区"""
    while not stop_event.is_set():
        try:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                buf.write(data)
                pkt = cmd_buf.get_command()
                if pkt:
                    decode_and_show(pkt)
        except serial.SerialException:
            break
        time.sleep(RECV_POLL_INTERVAL)

# ---------- 解码并显示数据包 ----------
def decode_and_show(packet: bytes):
    cmd = packet[2]
    print(f"\r[接收] 电平值 = {cmd}", end="")

# ---------- 用户输入处理 ----------
def get_user_input(prompt: str) -> int:
    """循环直到用户输入 0~255 的整数"""
    while True:
        raw = input(prompt).strip()
        if not raw.isdigit():
            print("❌ 请输入 0~255 的整数")
            continue
        num = int(raw)
        if 0 <= num <= 255:
            return num
        print("❌ 数值超出范围，请输入 0~255")

# ---------- 主程序 ----------
if __name__ == "__main__":
    ser = connect_com()
    if ser is None:
        sys.exit(1)

    print("输入命令字和数据值 (0~255)，发送线程会以 5Hz 持续发送最新数据包")
    print("输入 'q' 退出\n")

    # 启动发送线程
    cmd_buf = Command.CommandBuffer()
    t_send = threading.Thread(target=sender, args=(ser,), daemon=True)
    t_send.start()

     # 启动接收线程
    t_recv = threading.Thread(target=receiver, args=(ser, cmd_buf), daemon=True)
    t_recv.start()

    try:
        while True:
             # 处理接收到的数据包（非阻塞）
            
            cmd_input = input("").strip()
            if cmd_input.lower() == 'q':
                break
            if not cmd_input.isdigit():
                print("❌ 请输入数字或 'q'")
                continue
            cmd = int(cmd_input)
            if not 0 <= cmd <= 255:
                print("❌ 命令字需在 0~255 之间")
                continue

            # 输入数据值
            val = get_user_input("")

            # 更新共享变量（线程安全）
            with data_lock:
                latest_command = cmd
                latest_value = val
            print(f"✅ 已更新发送内容: 命令={cmd}, 值={val}\n")

    finally:
        stop_event.set()        # 通知线程退出
        t_send.join(timeout=1)
        t_recv.join(timeout=1)
        ser.close()
        print("串口已关闭，程序结束。")
        sys.exit(0)