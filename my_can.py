import serial
import serial.tools.list_ports

class CanBus:
    def __init__(self):
        self.init_class_variable()
        self.set_can_bus()
        
    
    def init_class_variable(self):
        self.SERIAL_PORT = None
        self.bus = None
        self.message_id = None
        self.message_data = None
        
        self.send_messages = {"pe": b'b01180000000000000000\r',
                              "batt": b'b02180000000000000000\r',
                              "valve": b'b03180000000000000000\r'}
        
    def set_can_bus(self):
        self.BAUD_RATE = 500000
        self.TIMEOUT = 1  # 1초 타임아웃 설정
    
    def start_can_bus(self, port):
        self.SERIAL_PORT = port  # 입력 받은 COM 포트를 설정
        try:
                self.bus = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=self.TIMEOUT)
                if self.bus.isOpen():
                    pass
                    # print(f"Opened serial port {self.SERIAL_PORT} with baud rate {self.BAUD_RATE}")

                # 초기화 및 비트 속도 설정
                self.send_command(b'C\r', response_length=1)
                self.send_command(b'S6\r', response_length=1)
                self.send_command(b'Y2\r', response_length=1)
                self.send_command(b'O\r', response_length=1)

                self.bus.flushInput()  # 시리얼 입력 버퍼 초기화
                # print("Waiting for data...")

        except serial.SerialException as e:
            print(f"Error: {e}")

    def send_command(self, command, response_length=0):
        """Send a command to the serial port and read the response."""
        self.bus.write(command)
        response = self.bus.read(response_length)
        return response  
    
    def stop_can_bus(self):
        if self.bus is not None:
            self.bus.close()

    def parse_can_frame(self, frame):
        """Parse a CAN frame into ID, DLC, and Data."""
        if len(frame) < 5:
            return None

        # Assuming the frame is in the format: 'bID DLC DATA\r'
        if frame[0] == ord('b'):
            id = int(frame[1:4].decode(), 16)  # CAN ID
            dlc = int(chr(frame[4]))          # DLC (데이터 길이)
            data = bytes.fromhex(frame[5:5+16].decode())             # 데이터 추출
            
            if len(data) < dlc:
                return None  # 데이터 부족 시 None 반환
            return (id, dlc, data)
        else:
            return None
                    
    def send_message(self):
        if self.bus is not None:
            for message in self.send_messages.values():
                self.bus.write(message)
                # print(f"message: {message}")