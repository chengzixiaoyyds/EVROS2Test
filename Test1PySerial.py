import serial
import logging
import sys
import pygame

SERIAL_PORT = 'COM11'
BAUDRATE = 115200

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
    
    
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    com = connect_com()
    if com is None:
        pygame.quit()
        sys.exit(1)
    clock = pygame.time.Clock()
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                com.close()
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    com.close()
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_a:
                    com.write(b'\xAA')
                    print("发送数据包: 0xAA")
                elif event.key == pygame.K_s:
                    com.write(b'\xAF')
                    print("发送数据包: 0xAF")
        clock.tick(60)