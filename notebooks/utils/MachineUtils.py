#!/usr/bin/env python
# coding: utf-8


import serial
from serial.tools import list_ports


class MachineCommunication:
    
    def __init__(self, port, baudRate = 115200):
        self.ser = serial.Serial(port, baudRate) 
        self.lineEnding = '\n'
        self.transform = []
        self.img_size = []
        
        
    def send(self, cmd):
        """Send GCode over serial connection"""
        cmd += self.lineEnding
        bcmd = cmd.encode('UTF-8')
        self.ser.write(bcmd)
        

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
        
    def move(self, dx = 0, dy = 0, dz = 0, s = 6000):
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
        dx = "{0:.2f}".format(dx)
        dy = "{0:.2f}".format(dy)
        dz = "{0:.2f}".format(dz)
        s = "{0:.2f}".format(s)
        
        self.setRelative()
        cmd = f"G1 X{dx} Y{dy} Z{dz} F{s}"
        self.send(cmd)
        self.setAbsolute() # restore absolute positioning
        
    def toolChange(self, toolIdx):
        """Change to specified tool"""
        cmd = f'T{toolIdx}'
        self.send(cmd)
        
    
    def setAbsolute(self):
        """Set machine to use absolute positioning"""
        cmd = "G90"
        self.send(cmd)
        
        
    def setRelative(self):
        """Set machine to use relative positioning"""
        cmd = "G91"
        self.send(cmd)
        
    def px_to_real(x,y, relative = False):
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
        
        
        