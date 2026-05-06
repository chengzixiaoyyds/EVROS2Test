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
        COMMAND_MIN_LENGTH = 4

        while True:
            cur_len = self.get_length()
            if cur_len < COMMAND_MIN_LENGTH:
                return None

            # 寻找包头 0x5A 0xA5
            if self._read(self.read_index) != 0x5A or self._read(self.read_index + 1) != 0xA5:
                self._add_read_index(1)
                continue

            packet_len = 4

            if cur_len < packet_len:
                return None

            # 计算校验和（包内除校验字节外的所有字节求和，取低 8 位）
            checksum = sum(self._read(self.read_index + i) for i in range(packet_len - 1)) & 0xFF
            if checksum != self._read(self.read_index + packet_len - 1):
                self._add_read_index(1)   # 校验错，移动 1 字节
                continue

            # 提取完整数据包
            cmd_bytes = bytes(self._read(self.read_index + i) for i in range(packet_len))
            self._add_read_index(packet_len)
            return cmd_bytes