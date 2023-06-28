#!/usr/bin/env python
# coding: utf-8


import serial
from serial.tools import list_ports
# import serial.threaded

def available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.name for port in ports]

class MachineCommunication:
    
    def __init__(self, port=None, baudRate = 115200):
        print(port)
        if port == None:
            # autoconnect to ttyACM* if it exists & is unique
            ports = [p.name for p in serial.tools.list_ports.comports() if 'ttyACM' in p.name]
            if len(ports) > 1:
                print('More than one possible serial device found. Please connect to an explicit port.')
                return
            else:
                port = f"/dev/{ports[0]}"
        print(port)
        self.ser = serial.Serial(port, baudRate) 
        self.lineEnding = '\n'
        self.transform = []
        self.img_size = []
        
#         self.serialRead()
        
    def send(self, cmd):
        """Send GCode over serial connection"""
        cmd += self.lineEnding
        bcmd = cmd.encode('UTF-8')
        self.ser.write(bcmd)
    
#     def serialRead(self):
        
#         class LineReader(serial.threaded.LineReader):
#             def __init__(self):
#                 print('test!')
#                 super(LineReader, self).__init__()
#                 self.received_lines = []
                
#             def handle_line(self, data):
#                 print(data)
#                 self.received_lines.append(data)
                
#         with serial.threaded.ReaderThread(self.ser, LineReader) as protocol:
#             protocol.run()
        

    def moveTo(self, x=None, y=None, z=None, s = 6000):
        """Move to an absolute (x,y,z) position

        Parameters
        ----------
        x: x position on the bed, in whatever units have been set (default mm)
        y: y position on the bed, in whatever units have been set (default mm)
        z: z position on the bed, in whatever units have been set (default mm)
        s: (optional) speed at which to move (default 6000 mm/min)

        Returns
        -------
        Nothing

        """
        x = "{0:.2f}".format(x) if x is not None else None
        y = "{0:.2f}".format(y) if y is not None else None
        z = "{0:.2f}".format(z) if z is not None else None
        s = "{0:.2f}".format(s)
        x_cmd = y_cmd = z_cmd = f_cmd = ''
        if x is not None:
            x_cmd = f'X{x}'
        if y is not None:
            y_cmd = f'Y{y}'
        if z is not None:
            z_cmd = f'Z{z}'
        if s is not None:
            f_cmd = f'F{s}'
        
        self.setAbsolute()
        cmd = f"G0 {x_cmd} {y_cmd} {z_cmd} {f_cmd}"
        self.send(cmd)
        
    def move(self, dx = None, dy = None, dz = None, de = None, s = 6000):
        """Move relative to the current position

        Parameters
        ----------
        dx: change in x position, in whatever units have been set (default mm)
        dy: change in y position, in whatever units have been set (default mm)
        dz: change in z position, in whatever units have been set (default mm)
        s: (optional) speed at which to move (default 6000 mm/min)

        Returns
        -------
        Nothing

        """
        dx = "{0:.2f}".format(dx) if dx is not None else None
        dy = "{0:.2f}".format(dy) if dy is not None else None
        dz = "{0:.2f}".format(dz) if dz is not None else None
        de = "{0:.2f}".format(de) if de is not None else None
        s = "{0:.2f}".format(s)
        x_cmd = y_cmd = z_cmd = e_cmd = f_cmd = ''
        if dx is not None:
            x_cmd = f'X{dx}'
        if dy is not None:
            y_cmd = f'Y{dy}'
        if dz is not None:
            z_cmd = f'Z{dz}'
        if de is not None:
            e_cmd = f'E{de}'
        if s is not None:
            f_cmd = f'F{s}'
        
        
        self.setRelative()
        self.setExtruderRelative()
        cmd = f"G1 {x_cmd} {y_cmd} {z_cmd} {e_cmd} {f_cmd}"
        self.send(cmd)
        self.setAbsolute() # restore absolute positioning
        
    def dwell(self, t, millis=True):
        """Pause the machine for a period of time.

        Parameters
        ----------
        t: time to pause, in milliseconds by default
        millis (optional): boolean, set to false to use seconds. default unit is milliseconds.
        dz: change in z position, in whatever units have been set (default mm)

        Returns
        -------
        Nothing

        """
        
        param = 'P' if millis else 'S'
        cmd = f"G4 {param}{t}"
        
        self.send(cmd)
        
        
        
    def toolChange(self, toolIdx):
        """Change to specified tool"""
        cmd = f'T{toolIdx}'
        self.send(cmd)
        
    
    def setAbsolute(self):
        """Set machine to use absolute positioning"""
        cmd = "G90"
        self.send(cmd)
        
        
    def setRelative(self):
        """Set machine to use relative positioning
        This does NOT set the extruder to relative mode"""
        cmd = "G91"
        self.send(cmd)
    
    def setExtruderRelative(self):
        """Set extruder axis to use relative positioning"""
        cmd = "G91"
        self.send(cmd)
        
    def px_to_real(x,y, relative = False):
        """Convert pixel location to bed location. Requires camera-machine calibration"""
        x = (x / self.img_size[0]) - 0.5
        y = (y / self.img_size[1]) - 0.5
        rel = 1 if relative else 0

        return (self.transform.T @ np.array([x**2, y**2, x * y, x, y, rel]))

    def homeX(self):
        """Home the X axis"""
        cmd = "G28 X"
        self.send(cmd)
        
    def homeY(self):
        """Home the Y axis"""
        cmd = "G28 Y"
        self.send(cmd)
        
    def homeZ(self):
        """Home the Z axis"""
        cmd = "G28 Z"
        self.send(cmd)
        
    def homeU(self):
        """Home the U (tool) axis"""
        cmd = "G28 U"
        self.send(cmd)
    
    def homeAll(self):
        """Home all axes"""
        cmd = "G28"
        self.send(cmd)
    
    def getPosition(self):
        """Get the current position
        Returns a dictionary with X/Y/Z/U/E keys"""
        self.ser.reset_input_buffer() # flush the buffer
        cmd = "M114"
        self.send(cmd)
        resp = self.ser.readline().decode('UTF-8') # read the response
        print(f'the raw response is: {resp}') # sometimes i'm just getting 'ok' here
        if resp == 'ok\n':
            resp = self.ser.readline().decode('UTF-8') # read another line
            
        positions = {}
        keyword = " Count " # this is the keyword hosts like e.g. pronterface search for to track position
        keyword_idx = resp.find(keyword)
        
        count = 0
        if keyword_idx > -1:
            resp = resp[:keyword_idx]
            position_elements = resp.split(' ')
            for e in position_elements:
                axis, pos = e.split(':', 2)
                positions[axis] = pos          
        
        self.ser.reset_input_buffer() # flush the buffer
        print(f"now im returning: {positions}")  
        return positions
        
    # ***************MACROS***************
    def tool_lock(self):
        """Runs Jubilee tool lock macro
        Assumes tool_lock.g macro exists"""
        macro_file = "0:/macros/tool_lock.g"
        cmd = f"M98 P{macro_file}"
        self.send(cmd)
        
    def tool_unlock(self):
        """Runs Jubilee tool unlock macro
        Assumes tool_unlock.g macro exists"""
        macro_file = "0:/macros/tool_unlock.g"
        cmd = f"M98 P{macro_file}"
        self.send(cmd)
        
    
        
        
        