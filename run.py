from my_can import CanBus
from main_ui import MainUI
import os
import time
import threading
import queue
import cantools.database
import serial
import serial.tools.list_ports
from tkinter import messagebox

class MainUiUpdater:
    def __init__(self):
        self.init_class_variable()
        self.init_state_variable()
        self.init_receive_handler()
        self.set_button_command()


    def init_class_variable(self):
        self.ui = MainUI()
        self.can_bus = CanBus()
        base_path = os.path.dirname(os.path.abspath(__file__))
        dbc_relative_path = 'Ajin_CMID.dbc'
        dbc_absolute_path = os.path.join(base_path, dbc_relative_path)
        self.db = cantools.database.load_file(dbc_absolute_path)
        self.message_queue = queue.Queue()
        self.temp_message_queue = queue.Queue()
        self.is_running = False
        self.receive_thread = None
        self.send_thread = None
        self.receie_id_handlers = None
        self.message_update_id = None
        self.message_update_data = None
        self.button_state = False
        self.buffer= b""

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "USB 직렬 장치" in port.description:
                return port.device
        return None

    def send_message(self):
        interval = 0.095 # 100ms
        next_send_time = time.perf_counter()

        while self.is_running and self.can_bus.bus is not None:
            self.can_bus.send_message()
            # self.can_bus.send_messages["pe"].data = encoding 
            next_send_time += interval
            sleep_time = max(0, next_send_time - time.perf_counter())
            time.sleep(sleep_time)

    def set_button_command(self):
        self.ui.buttons["Connect"].config(command=self.connect_can_bus)
        self.ui.buttons["Disconnect"].config(command=self.exit_program)
        self.ui.buttons["Run"].config(command=self.set_full_speed)
        self.ui.buttons["Stop"].config(command=self.set_zero_speed)
      
    def connect_can_bus(self):
        if not self.is_running:  
            self.is_running = True

            if self.can_bus.bus is None:
                try:

                    port = self.find_serial_port()  # 사용자 입력 COM 포트
        
                    if not port:  # 입력이 없으면 에러
                         messagebox.showerror("Error", "Please enter a COM port.")

                    self.can_bus.start_can_bus(port)
                    
                except Exception as e:
                    print(f"Error initializing CAN bus: {e}")
                    self.is_running = False
                    return
                
            if self.button_state == False:
                self.button_state = True
                self.can_thread = threading.Thread(target=self.receive_listener)
                self.can_thread.daemon = True
                self.can_thread.start()

                self.send_thread = threading.Thread(target=self.send_message)
                self.send_thread.daemon = True
                self.send_thread.start()
            else:
                pass

    def exit_program(self):
        """프로그램 종료 및 자원 정리"""
        self.is_running = False  # 실행 플래그 중단

        # CAN 버스 종료
        if self.can_bus and self.can_bus.bus:
            try:
                self.can_bus.bus.close()
                print("CAN Bus 종료")
            except Exception as e:
                print(f"CAN Bus 종료 중 오류: {e}")

        # 스레드 종료 대기
        try:
            if hasattr(self, 'can_thread') and self.can_thread.is_alive():
                self.can_thread.join(timeout=2)  # 2초 내 종료 대기
                print("CAN 수신 스레드 종료")
            if hasattr(self, 'send_thread') and self.send_thread.is_alive():
                self.send_thread.join(timeout=2)  # 2초 내 종료 대기
                print("CAN 송신 스레드 종료")
            self.button_state == False
        except Exception as e:
            print(f"스레드 종료 중 오류: {e}")

    def set_zero_speed(self):
            self.can_bus.send_messages["pe"] = b'b01180000000000000000\r'
            self.can_bus.send_messages["batt"] = b'b02180000000000000000\r'
            self.can_bus.send_messages["valve"] = b'b03180000000000000000\r'
            self.ui.labels["pe"]["target_rpm"].config(text=f"0")
            self.ui.labels["batt"]["target_rpm"].config(text=f"0")
            self.ui.labels["valve"]["target_rpm"].config(text=f"0")
            

    def set_full_speed(self):
            self.can_bus.send_messages["pe"] = b'b011800C8000000000000\r'
            self.can_bus.send_messages["batt"] = b'b0218F200000000000000\r'
            self.can_bus.send_messages["valve"] = b'b03180100000000000000\r'
            self.ui.labels["pe"]["target_rpm"].config(text=f"5400")
            self.ui.labels["batt"]["target_rpm"].config(text=f"4000")
            self.ui.labels["valve"]["target_rpm"].config(text=f"Mode A")
        
    
    def receive_listener(self):
        """CAN 메시지를 수신하고 파싱."""
        if self.is_running and self.can_bus.bus is not None:
            try:
                message = self.can_bus.bus.read(self.can_bus.bus.in_waiting or 1)
                if message:
                    self.buffer += message
                    print(self.buffer)
                    while b'\r' in self.buffer:
                        split_index = self.buffer.index(b'\r')
                        frame = self.buffer[:split_index]
                        self.buffer = self.buffer[split_index + 1:]

                        # 메시지 파싱 및 처리
                        parsed_frame = self.can_bus.parse_can_frame(frame)
                        if parsed_frame:
                            id, dlc, data = parsed_frame
                            handler = self.receie_id_handlers.get(id)
                            if handler:
                                handler(data)
            except Exception as e:
                print(f"CAN 메시지 수신 중 오류: {e}")
                self.reconnect_can_bus()
        self.ui.root.after(95, self.receive_listener)

    def reconnect_thread(self):
        try:
            if hasattr(self, 'can_thread') and self.can_thread.is_alive():
                self.can_thread.join(timeout=2)  # 2초 내 종료 대기
            if hasattr(self, 'send_thread') and self.send_thread.is_alive():
                self.send_thread.join(timeout=2)  # 2초 내 종료 대기
        except Exception as e:
            print(f"스레드 초기화 중 오류: {e}")
            pass

        self.can_thread = threading.Thread(target=self.receive_listener)
        self.can_thread.daemon = True
        self.can_thread.start()

        self.send_thread = threading.Thread(target=self.send_message)
        self.send_thread.daemon = True
        self.send_thread.start()

    def reconnect_can_bus(self):
        """CAN 버스를 재연결."""
        print("CAN 버스 재연결 시도 중...")
        self.is_connected = False  # 연결 상태 초기화

        # 기존 연결 종료
        if self.can_bus and self.can_bus.bus:
            try:
                self.can_bus.bus.close()
                print("기존 CAN 버스 연결 종료")
            except Exception as e:
                print(f"기존 CAN 버스 종료 중 오류: {e}")

        # 재연결 시도
        try:
            port = self.find_serial_port()
            if not port:
                raise serial.SerialException("사용 가능한 시리얼 포트를 찾을 수 없습니다.")

            print(f"포트 {port}로 재연결 시도 중...")
            self.can_bus.start_can_bus(port)
            self.is_connected = True
            self.reconnect_thread()
            print("CAN 버스 재연결 성공")

        except Exception as e:
            messagebox.showerror("Error", "CAN 통신 재연결 오류 \n 프로그램 종료 후 다시 실행해주세요.")
            self.ui.root.destroy()

    def init_receive_handler(self):
        self.receie_id_handlers = {
            0x12: lambda signal: self.handler_update(0x12, signal),
            0x22: lambda signal: self.handler_update(0x22, signal),
            0x32: lambda signal: self.valve_handler_update(0x32, signal),
            0x66: lambda signal: self.temp_handler_update(0x66, signal)
        }

    def temp_handler_update(self, add, signal):
        try:
            decoded_message = self.db.decode_message(add, signal)
            temp_mapping = {
                'BATT_EWP_FB_TEMP': 'batt',
                'PE_EWP_FB_TEMP': 'pe',
                'VALVE_FB_TEMP': 'valve'
            }
            
            for message_name, name in temp_mapping.items():
                if message_name in decoded_message:
                    temp = decoded_message[message_name]

                    self.temp_message_queue.put({
                    "type": f"{name}_update",
                    #data
                    "temp": temp,
                    #flag
                    })
                        
        except KeyError as e:
            print(f"키를 찾을 수 없습니다: {e}")
        except Exception as e:
            print(f"CAN 통신 처리 중 오류 발생: {e}")
            
                

    def handler_update(self, add, signal):

        decoded_message = self.db.decode_message(add, signal)

        if add == 0x12:
            name = "batt"
            rpm = decoded_message['EWP1_ActRotSpd']
            voltage = decoded_message['EWP1_Input_Voltage']
            current = decoded_message['EWP1_Current_DC']
            FaultStatus = decoded_message['EWP1_FaultStatus']
            ProtectMode = decoded_message['EWP1_ProtectMode']
            Over_Current = decoded_message['EWP1_Over_Current']
            Low_Current = decoded_message['EWP1_Low_Currnet']
            Over_Voltage = decoded_message['EWP1_Over_Voltage']
            Under_Voltage = decoded_message['EWP1_Under_Voltage']
            Short_Circuit = decoded_message['EWP1_Short_Circuit']
            Power_Limit = decoded_message['EWP1_Power_Limit']
            CAN_Error = decoded_message['EWP1_CAN_Error']
            Speed_Error = decoded_message['EWP1_Speed_Error']
            Over_Temp = decoded_message['EWP1_Over_Temp']
            
        else:
            name="pe"
            #data
            rpm = decoded_message['EWP2_ActRotSpd']
            voltage = decoded_message['EWP2_Input_Voltage']
            current = decoded_message['EWP2_Current_DC']
            #flag
            FaultStatus = decoded_message['EWP2_FaultStatus']
            ProtectMode = decoded_message['EWP2_ProtectMode']
            Over_Current = decoded_message['EWP2_Over_Current']
            Low_Current = decoded_message['EWP2_Low_Current']
            Over_Voltage = decoded_message['EWP2_Over_Voltage']
            Under_Voltage = decoded_message['EWP2_Under_Voltage']
            Short_Circuit = decoded_message['EWP2_Short_Circuit']
            Power_Limit = decoded_message['EWP2_Power_Limit']
            CAN_Error = decoded_message['EWP2_CAN_Error']
            Speed_Error = decoded_message['EWP2_Speed_Error']
            Over_Temp = decoded_message['EWP2_Over_Temp']

        self.message_queue.put({
            "type": f"{name}_update",
            #data
            "rpm": rpm,
            "voltage": voltage,
            "current": current,
            #flag
            "FaultStatus": FaultStatus, 
            "ProtectMode": ProtectMode, 
            "Over_Current": Over_Current, 
            "Low_Current": Low_Current,
            "Short_Circuit": Short_Circuit, 
            "Over_Voltage": Over_Voltage, 
            "Under_Voltage": Under_Voltage, 
            "Power_Limit": Power_Limit,
            "CAN_Error": CAN_Error, 
            "Speed_Error": Speed_Error, 
            "Over_Temp": Over_Temp
        })

    

    def valve_handler_update(self, add, signal):
        decoded_message = self.db.decode_message(add, signal)
        name = "valve"
        rpm = decoded_message['cVALVE_Actual_Position']
        #flag 값
        Overcurrent_Fault = decoded_message['cVALVE_Motor_Overcurrent_Fault']
        Overvoltage_Fault = decoded_message['cVALVE_Overvoltage_Fault']
        Undervoltage_Fault = decoded_message['cVALVE_Undervoltage_Fault']
        CAN_Comm_Fault = decoded_message['cVALVE_CAN_Communication_Fault']
        Over_temp_Fault = decoded_message['cVALVE_Overtemperature_Fault']
        Under_temp_Fault = decoded_message['cVALVE_Undertemperature_Fault']
        Position_Fault = decoded_message['cVALVE_Position_Fault']
        Position_sensor_Fault = decoded_message['cVALVE_Position_Sensor_Fault']
        Motor_Open_Fault = decoded_message['cVALVE_Motor_Open_Fault']
        obstruction_detected = decoded_message['cVALVE_obstruction_detected']

    
        self.message_queue.put({
            "type": f"{name}_update",
            'rpm': rpm,
            #flag
            "Overcurrent_Fault": Overcurrent_Fault, 
            "Overvoltage_Fault": Overvoltage_Fault, 
            "Undervoltage_Fault": Undervoltage_Fault, 
            "CAN_Comm_Fault": CAN_Comm_Fault,
            "Over_temp_Fault": Over_temp_Fault, 
            "Under_temp_Fault": Under_temp_Fault, 
            "Position_Fault": Position_Fault, 
            "Position_sensor_Fault": Position_sensor_Fault,
            "Motor_Open_Fault": Motor_Open_Fault, 
            "obstruction_detected": obstruction_detected 
        })

    def init_state_variable(self):
        self.previous_state = {"batt": {}, "pe": {}, "valve": {}}  # 이전 상태 저장
        # 기존 변수 초기화 코드 유지

    def is_data_changed(self, category, new_data):
        """데이터가 변경되었는지 확인"""
        if category not in self.previous_state:
            self.previous_state[category] = new_data
            return True

        for key, value in new_data.items():
            if self.previous_state[category].get(key) != value:
                self.previous_state[category][key] = value
                return True
        return False  
          
    def update_ui(self):

        def handle_batt_update(data):
            if self.is_data_changed("batt", data):
                self.ui.labels["batt"]["actual_rpm"].config(text=f"{data['rpm']}")
                self.ui.labels["batt"]["current"].config(text=f"{round(data['current'],2)} A")
                self.ui.labels["batt"]["voltage"].config(text=f"{round(data['voltage'],2)} V")

        def handle_pe_update(data):
            if self.is_data_changed("pe", data):  # 변경된 경우만 업데이트
                self.ui.labels["pe"]["actual_rpm"].config(text=f"{data['rpm']}")
                self.ui.labels["pe"]["current"].config(text=f"{round(data['current'],2)} A")
                self.ui.labels["pe"]["voltage"].config(text=f"{round(data['voltage'],2)} V")
            
        def handle_valve_update(data):
            if self.is_data_changed("valve", data):  # 변경된 경우만 업데이트
                self.ui.labels["valve"]["actual_rpm"].config(text=f"{data['rpm']}")
            
        def flag_batt_update(data):
            if self.is_data_changed("batt", data):
            #flag_States=['FaultStatus', 'ProtectMode','Over_Current', 'Low_Current', 'Short_Circuit','Over_Voltage','Under_Voltage','Power_Limit','CAN_Error','Speed_Error','Over_Temp']
                self.ui.labels["batt"]["BATT_FaultStatus"].config(fg=get_text_color(data['FaultStatus']))
                self.ui.labels["batt"]["BATT_ProtectMode"].config(fg=get_text_color(data['ProtectMode']))
                self.ui.labels["batt"]["BATT_Over_Current"].config(fg=get_text_color(data['Over_Current']))
                self.ui.labels["batt"]["BATT_Low_Current"].config(fg=get_text_color(data['Low_Current']))
                self.ui.labels["batt"]["BATT_Short_Circuit"].config(fg=get_text_color(data['Short_Circuit']))
                self.ui.labels["batt"]["BATT_Over_Voltage"].config(fg=get_text_color(data['Over_Voltage']))
                self.ui.labels["batt"]["BATT_Under_Voltage"].config(fg=get_text_color(data['Under_Voltage']))
                self.ui.labels["batt"]["BATT_Power_Limit"].config(fg=get_text_color(data['Power_Limit']))
                self.ui.labels["batt"]["BATT_CAN_Error"].config(fg=get_text_color(data['CAN_Error']))
                self.ui.labels["batt"]["BATT_Speed_Error"].config(fg=get_text_color(data['Speed_Error']))
                self.ui.labels["batt"]["BATT_Over_Temp"].config(fg=get_text_color(data['Over_Temp']))

        def flag_pe_update(data):
            if self.is_data_changed("pe", data):  # 변경된 경우만 업데이트
                self.ui.labels["pe"]["PE_FaultStatus"].config(fg=get_text_color(data['FaultStatus']))
                self.ui.labels["pe"]["PE_ProtectMode"].config(fg=get_text_color(data['ProtectMode']))
                self.ui.labels["pe"]["PE_Over_Current"].config(fg=get_text_color(data['Over_Current']))
                self.ui.labels["pe"]["PE_Low_Current"].config(fg=get_text_color(data['Low_Current']))
                self.ui.labels["pe"]["PE_Short_Circuit"].config(fg=get_text_color(data['Short_Circuit']))
                self.ui.labels["pe"]["PE_Over_Voltage"].config(fg=get_text_color(data['Over_Voltage']))
                self.ui.labels["pe"]["PE_Under_Voltage"].config(fg=get_text_color(data['Under_Voltage']))
                self.ui.labels["pe"]["PE_Power_Limit"].config(fg=get_text_color(data['Power_Limit']))
                self.ui.labels["pe"]["PE_CAN_Error"].config(fg=get_text_color(data['CAN_Error']))
                self.ui.labels["pe"]["PE_Speed_Error"].config(fg=get_text_color(data['Speed_Error']))
                self.ui.labels["pe"]["PE_Over_Temp"].config(fg=get_text_color(data['Over_Temp']))

        def flag_valve_update(data):
            if self.is_data_changed("valve", data):  # 변경된 경우만 업데이트
                self.ui.labels["valve"]["Overcurrent_Fault"].config(fg=get_text_color(data['Overcurrent_Fault']))
                self.ui.labels["valve"]["Overvoltage_Fault"].config(fg=get_text_color(data['Overvoltage_Fault']))
                self.ui.labels["valve"]["Undervoltage_Fault"].config(fg=get_text_color(data['Undervoltage_Fault']))
                self.ui.labels["valve"]["CAN_Comm_Fault"].config(fg=get_text_color(data['CAN_Comm_Fault']))
                self.ui.labels["valve"]["Over_temp_Fault"].config(fg=get_text_color(data['Over_temp_Fault']))
                self.ui.labels["valve"]["Under_temp_Fault"].config(fg=get_text_color(data['Under_temp_Fault']))
                self.ui.labels["valve"]["Position_Fault"].config(fg=get_text_color(data['Position_Fault']))
                self.ui.labels["valve"]["Position_sensor_Fault"].config(fg=get_text_color(data['Position_sensor_Fault']))
                self.ui.labels["valve"]["Motor_Open_Fault"].config(fg=get_text_color(data['Motor_Open_Fault']))
                self.ui.labels["valve"]["obstruction_detected"].config(fg=get_text_color(data['obstruction_detected']))

        def temp_batt_updata(data):
            if self.is_data_changed("batt", data):  # 변경된 경우만 업데이트
                self.ui.labels["batt"]["temp"].config(text=f"{(data['temp'])} °C")

        def temp_pe_updata(data):
            if self.is_data_changed("pe", data):  # 변경된 경우만 업데이트
                self.ui.labels["pe"]["temp"].config(text=f"{(data['temp'])} °C")

        def temp_valve_updata(data):
            if self.is_data_changed("valve", data):  # 변경된 경우만 업데이트
                self.ui.labels["valve"]["temp"].config(text=f"{(data['temp'])} °C")

        def get_text_color(value):
            color = None
            if value == "Fail State":
                color = "red"
            elif value == "Protect State":
                color = "red"
            elif value == "Fault Stated":
                color = "red" 
            else:
                color = "green"
            return color
        
        try:
            # 일반 메시지 처리
            while not self.message_queue.empty():
                data = self.message_queue.get()
                if data['type'] == "batt_update":
                    handle_batt_update(data)
                    flag_batt_update(data)

                elif data['type'] == "pe_update":
                    handle_pe_update(data)
                    flag_pe_update(data)

                elif data['type'] == "valve_update":
                    handle_valve_update(data)
                    flag_valve_update(data)

            # 온도 메시지 처리
            while not self.temp_message_queue.empty():
                temp_data = self.temp_message_queue.get()
                if temp_data['type'] == "batt_update":
                    temp_batt_updata(temp_data)

                elif temp_data['type'] == "pe_update":
                    temp_pe_updata(temp_data)

                elif temp_data['type'] == "valve_update":
                    temp_valve_updata(temp_data)

        except queue.Empty:
            # 큐가 비어 있는 경우 무시
            pass

        # 20ms 후 다시 호출
        self.ui.root.after(100, self.update_ui)
                    

if __name__ == "__main__":
    updater = MainUiUpdater()
    updater.ui.root.after(0, updater.update_ui)
    updater.ui.ui_run()