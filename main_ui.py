import tkinter as tk
import os
from PIL import Image, ImageTk

class MainUI:
    def __init__(self):
        self.init_class_variable()
        self.init_color_variable()
        self.init_main_ui()
        self.init_background_ui()
        self.init_frame()
        self.init_rpm_label()
        self.init_value_label()
        self.init_flag_label()
        self.init_control_button()
        
        self.debug_control()


    def init_color_variable(self):
        # 색상 초기화
        self.red = "#C05046"
        self.yellow = "#9DBB61"
        self.orange = "#F59D56"
        self.blue = "#4BACC6"
        self.gray = "#262626"
        self.black = "#0C0C0C"
        self.green = "#00D660"
        self.white = "#FEFEFE"
        self.light_green = "#B1D46D"

    def debug_control(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def on_canvas_click(self, event):
        # 클릭 좌표 출력
        print(f"x={event.x}, y={event.y}")
        
    def init_class_variable(self):
        self.root = None
        self.canvas = None
        
        self.frames = {"pe": {}, "batt": {}, "valve": {}, "control": {}}
        self.labels = {"pe": {}, "batt": {}, "valve": {}}
        self.buttons = {"start": {}, "stop": {}, "run": {}}
    
    def init_main_ui(self):
        self.root = tk.Tk()
        self.root.title("CMID SIMULATOR v1.01")
        self.root.geometry("964x691")
        self.root.resizable(False, False)
        
    def init_background_ui(self):
        # current_dir = os.getcwd()
        base_path = os.path.dirname(__file__)
        background_image = os.path.join(base_path, r"bg/cmid_4.png")
        background_image = Image.open(background_image)
        self.background_photo_image = ImageTk.PhotoImage(background_image)
        
        self.canvas = tk.Canvas(self.root, width=964, height=691)
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo_image)
        self.canvas.pack()
        
    def init_frame(self):
        # PE Frame set
        # frames["pe"] 아래에 frames["pe"]["actual_rpm"], frames["pe"]["value"], frames["pe"]["flags"] 존재
        pe_config = {
            "actual_rpm": (40, 133, 270, 203),
            "value": (170, 200, 280, 330),
            "flags": (322, 84, 455, 324)
        } # x1, y1, x2, y2
        
        for name, (x1, y1, x2, y2) in pe_config.items():
            frame = tk.Frame(self.root, width=x2-x1, height=y2-y1, bg=self.black)
            frame.place(x=x1, y=y1)
            self.frames["pe"][name] = frame
            
        # BATT Frame set
        batt_config = {
            "actual_rpm": (515, 133, 754, 203),
            "value": (633, 200, 754, 330),
            "flags": (788, 84, 915, 324)            
        }
        
        for name, (x1, y1, x2, y2) in batt_config.items():
            frame = tk.Frame(self.root, width=x2-x1, height=y2-y1, bg=self.black)
            frame.place(x=x1, y=y1)
            self.frames["batt"][name] = frame
            
        # Valve Frame set    
        valve_config = {
            "actual_rpm": (40, 464, 270, 525),
            "value": (198, 530, 288, 620),
            "flags": (322, 410, 455, 645)
        }
        
        for name, (x1, y1, x2, y2) in valve_config.items():
            frame = tk.Frame(self.root, width=x2-x1, height=y2-y1, bg=self.black)
            frame.place(x=x1, y=y1)
            self.frames["valve"][name] = frame
            
        # Control Frame set
        contorl_config = {
            "controls": (495, 390, 895, 620)
        }
        for name, (x1, y1, x2, y2) in contorl_config.items():    
            frame = tk.Frame(self.root, width=x2-x1, height=y2-y1, bg=self.black)
            frame.place(x=x1, y=y1)
            self.frames["control"][name] = frame
    
    def init_rpm_label(self):
        label = tk.Label(self.frames["pe"]["actual_rpm"], text="None", bg=self.black, fg=self.red, font=("현대하모닉L", 30, "bold"), anchor="e", width=50)
        self.labels["pe"]["actual_rpm"] = label
        self.labels["pe"]["actual_rpm"].place(x=0, y=0, width=200)
        
        label = tk.Label(self.frames["batt"]["actual_rpm"], text="None", bg=self.black, fg=self.blue, font=("현대하모닉L", 30, "bold"), anchor="e", width=50)
        self.labels["batt"]["actual_rpm"] = label
        self.labels["batt"]["actual_rpm"].place(x=0, y=0, width=200)
        
        label = tk.Label(self.frames["valve"]["actual_rpm"], text="None", bg=self.black, fg=self.orange, font=("현대하모닉L", 30, "bold"), anchor="e", width=50)
        self.labels["valve"]["actual_rpm"] = label
        self.labels["valve"]["actual_rpm"].place(x=0, y=0, width=200)
        
    def init_value_label(self):
        # PE frame에 라벨 생성하는 예제 코드
        # labels["pe"] 아래에 labels["pe"]["target_rpm"], labels["pe"]["voltage"], labels["pe"]["current"] 존재
        pe_config = { 
            "target_rpm": (1, 0.02),
            "voltage": (1, 0.25),
            "current": (1, 0.48),
            "temp" : (1, 0.71)
        } # relx, rely
        
        for name, (relx, rely) in pe_config.items():
            label = tk.Label(self.frames["pe"]["value"], text="None", bg=self.black, fg=self.white, font=("현대하모닉L",14, "bold"), anchor="e", width=16)
            label.place(relx=relx, rely=rely, anchor="ne")
            self.labels["pe"][name] = label
        
        batt_config = { 
            "target_rpm": (1, 0.02),
            "voltage": (1, 0.25),
            "current": (1, 0.48),
            "temp" : (1, 0.71)
        } 
        
        for name, (relx, rely) in batt_config.items():
            label = tk.Label(self.frames["batt"]["value"], text="None", bg=self.black, fg=self.white, font=("현대하모닉L",14, "bold"), anchor="e", width=20)
            label.place(relx=relx, rely=rely, anchor="ne")
            self.labels["batt"][name] = label
            
        valve_config = { 
            "target_rpm": (1, 0.0),
            "temp": (1, 0.65)
        } 
        
        for name, (relx, rely) in valve_config.items():
            label = tk.Label(self.frames["valve"]["value"], text="None", bg=self.black, fg=self.white, font=("현대하모닉L",15, "bold"), anchor="e", width=20)
            label.place(relx=relx, rely=rely, anchor="ne")
            self.labels["valve"][name] = label

    def init_flag_label(self):
        pe_config = {
            "PE_FaultStatus": 0, "PE_ProtectMode": 0, "PE_Over_Current": 0, "PE_Low_Current": 0,
            "PE_Short_Circuit": 0, "PE_Over_Voltage": 0, "PE_Under_Voltage": 0, "PE_Power_Limit": 0,
            "PE_CAN_Error": 0, "PE_Speed_Error": 0, "PE_Over_Temp": 0
        }  

        for idx, name in enumerate(pe_config.keys()): 
            label = tk.Label(self.frames["pe"]["flags"], text=f"● {name}", bg=self.black, fg=self.white, anchor="w", width=20)
            label.place(rely=idx * 0.09, anchor="nw") 
            self.labels["pe"][name] = label

        batt_config = {
            "BATT_FaultStatus": 0, "BATT_ProtectMode": 0, "BATT_Over_Current": 0, "BATT_Low_Current": 0,
            "BATT_Short_Circuit": 0, "BATT_Over_Voltage": 0, "BATT_Under_Voltage": 0, "BATT_Power_Limit": 0,
            "BATT_CAN_Error": 0, "BATT_Speed_Error": 0, "BATT_Over_Temp": 0
        }      
        
        for idx, name in enumerate(batt_config.keys()):
            label = tk.Label(self.frames["batt"]["flags"], text=f"● {name}", bg=self.black, fg=self.white, anchor="w", width=20)
            label.place(rely = idx * 0.085, anchor="nw")
            self.labels["batt"][name] = label
            
        valve_config = {
            "Overcurrent_Fault": 0, "Overvoltage_Fault": 0, "Undervoltage_Fault": 0, "CAN_Comm_Fault": 0,
            "Over_temp_Fault": 0, "Under_temp_Fault": 0, "Position_Fault": 0, "Position_sensor_Fault": 0,
            "Motor_Open_Fault": 0, "obstruction_detected": 0
        }      

        for idx, name in enumerate(valve_config.keys()): 
            label = tk.Label(self.frames["valve"]["flags"], text=f"● {name}", bg=self.black, fg=self.white, anchor="w", width=20)
            label.place(rely=idx * 0.09, anchor="nw")  
            self.labels["valve"][name] = label
      
            
    def init_control_button(self):
        control_config = {
            "Connect": (0.08, 0.1),  
            "Disconnect": (0.6, 0.1),   
            "Run": (0.08, 0.6),
            "Stop": (0.6, 0.6)
        }

        for name, (relx, rely) in control_config.items():
            button = tk.Button(self.frames["control"]["controls"], text=name, bg=self.black, fg=self.white, font=("현대하모닉L",13, "bold"), width=15, height=4)
            button.place(relx=relx, rely=rely, anchor="nw")  
            self.buttons[name] = button
                    
    def ui_run(self):
        self.root.mainloop()