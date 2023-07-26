#!/usr/bin/env python
# coding: utf-8

import serial
from serial.tools import list_ports
import json

class MachineStateError(Exception):
    """Raise this error if the machine is in the wrong state to perform the requested action."""
    pass

def machine_homed(func):
    def homing_check(self, *args, **kwds):
        # Check the cached value if one exists.
        if self.axes_homed and all(self.axes_homed):
            return func(self, *args, **kwds)
        # Request homing status from the object model if not known.
        self.axes_homed = json.loads(self.send('M409 K"move.axes[].homed"'))["result"] # check if this works, could alternatively check number of configured axes with move.axes?
        if not all(self.axes_homed):
            raise MachineStateError("Error: machine must first be homed.")
        return func(self, *args, **kwds)
    return homing_check

class MachineCommunication:
     """Driver for sending commands and polling the machine state."""
    def __init__(self, port=None, baudRate = 115200):
        """Set default values and connect to the machine"""
        # Serial Info
        self.ser = None
        self.lineEnding = '\n'
        
        # Machine Info
        self._configured_axes = None
        self._configured_tools = None
        self._absolute_positioning = True # Absolute positioning by default
        self._absolute_extrusion = True # Extrusion positioning is set separately from other axes
        self._active_tool_index = None # Cached value under the @property.
        self._tool_z_offsets = None # Cached value under the @property.
        self._axis_limits = None # Cached value under the @property.
        self.axes_homed = [False]*4 # We have at least X/Y/Z/U axes to home. Additional axes handled below in connect()
        
        # Camera Info
        # ToDo: separate this out
        self.transform = []
        self.img_size = []
        
        self.connect(self, port, baudrate)

        
    
    def connect(self, port, baudrate):
        """Connect to the machine over serial"""
        if port == None:
            # autoconnect to ttyACM* if it exists & is unique
            ports = [p.name for p in serial.tools.list_ports.comports() if 'ttyACM' in p.name]
            if len(ports) > 1:
                raise MachineStateError("More than one possible serial device found. Please connect to an explicit port.")
            else:
                port = f"/dev/{ports[0]}"
        self.ser = serial.Serial(port, baudRate) 
        self.send("M450") # sample command to initialize serial connection
        
        # update machine state with info from the object model
        self.axes_homed = json.loads(self.send('M409 K"move.axes[].homed"'))["result"] # check if this works, could alternatively check number of configured axes with move.axes?
            
        # clear all previous values and reset
        self.configured_axes = None
        self._active_tool_index = None
        self._tool_z_offsets = None
        self._axis_limits = None
        
        self.configured_axes
        self.active_tool_index
        self.tool_z_offsets
        self.axis_limits
        self._set_absolute_positioning()
            
    def send(self, cmd: str = ""):
        """Send GCode over serial connection"""
        cmd += self.lineEnding
        bcmd = cmd.encode('UTF-8')
        self.ser.write(bcmd)
        
        # read response
        # ToDo: Test this
        self.ser.reset_input_buffer() # flush the buffer
        resp = self.ser.readline().decode('UTF-8') # read the response
        if resp == 'ok\n':
            resp = self.ser.readline().decode('UTF-8') # read another line if first is just confirmation
        
        # do I need to flush the buffer again? check this
        return resp
    
    def _set_absolute_positioning(self):
        """Set absolute positioning for all axes except extrusion"""
        self.send("G90")
        self._absolute_positioning = True

    def _set_relative_positioning(self):
        """Set relative positioning for all axes except extrusion"""
        self.send("G91")
        self.absolute_positioning = False
        
    def _set_absolute_extrusion(self):
        """Set absolute positioning for extrusion"""
        self.send("M82")
        self._absolute_extrusion = True

    def _set_relative_extrusion(self):
        """Set relative positioning for extrusion"""
        self.send("M83")
        self.absolute_extrusion = False
    
    def push_machine_state(self):
        """Push machine state onto a stack"""
        self.send("M120")

    def pop_machine_state(self):
        """Recover previous machine state"""
        self.send("M121")
    
    @property
    def configured_axes(self):
        """Return the configured axes of the machine. Particularly relevant V axis is in use for e.g. pipetting"""
        # ToDo: test this
        if configured_axes is None: # Starting from a fresh connection
            try:
                response = json.loads(self.send('M409 K"move.axes[]"'))["result"]
                # set _configured_axes
                # need to seee what response looks like before doing more here
            except ValueError as e:
                print("Error occurred trying to read axis limits on each axis!")
                raise e
        
        # Return the cached value.
        return self._configured_axes
    
    @property
    def configured_tools(self):
        """Return the configured tools."""
        # ToDo: test this
        if configured_tools is None: # Starting from a fresh connection
            try:
                response = json.loads(self.send('M409 K"tools[]"'))["result"] 
                # need to check what the response looks like
                # if it includes human readable name, could allow to choose with that in addition to number
                # set _configured_tools
            except ValueError as e:
                print("Error occurred trying to read axis limits on each axis!")
                raise e
        
        # Return the cached value.
        return self._configured_tools
    
    @property
    def active_tool_index(self):
        """Return the index of the current tool."""
        if self._active_tool_index is None: # Starting from a fresh connection.
            try:
                response = self.send("T")
                # ToDo: Check the following
                # On HTTP Interface, we get a string instead of -1 when there are no tools.
                if response.startswith('No tool'):
                    return -1
                # On HTTP Interface, we get a string instead of the tool index.
                elif response.startswith('Tool'):
                    # Recover from the string: 'Tool X is selected.'
                    self._active_tool_index = int(response.split()[1])
                else:
                    self._active_tool_index = int(response)
            except ValueError as e:
                print("Error occurred trying to read current tool!")
                raise e
        # Return the cached value.
        return self._active_tool_index
    
    @property
    def tool_z_offsets(self):
        """Return (in tool order) a list of tool's z offsets"""
        # Starting from fresh connection, query from the Duet.
        if self._tool_z_offsets is None:
            try:
                response = json.loads(self.send('"M409 K"tools"'))["result"]
                self._tool_z_offsets = [] # Create a fresh list.
                for tool_data in response:
                    tool_z_offset = tool_data["offsets"][2] # Pull Z axis
                    self._tool_z_offsets.append(tool_z_offset)
            except ValueError as e:
                print("Error occurred trying to read z offsets of all tools!")
                raise e
        # Return the cached value.
        return self._tool_z_offsets


    @property
    def axis_limits(self):
        """Return (in XYZU order) a list of tuples specifying (min, max) axis limit"""
        # Starting from fresh connection, query from the Duet.
        if self._axis_limits is None:
            try:
                response = json.loads(self.gcode('M409 K"move.axes"'))["result"]
                self._axis_limits = [] # Create a fresh list.
                for axis_data in response:
                    axis_min = axis_data["min"]
                    axis_max = axis_data["max"]
                    self._axis_limits.append((axis_min, axis_max))
            except ValueError as e:
                print("Error occurred trying to read axis limits on each axis!")
                raise e
        # Return the cached value.
        return self._axis_limits
        
    def home_x(self):
        """Home the X axis"""
        cmd = "G28 X"
        self.send(cmd)
        
    def home_y(self):
        """Home the Y axis"""
        cmd = "G28 Y"
        self.send(cmd)
        
    def home_z(self):
        """Home the Z axis"""
        cmd = "G28 Z"
        self.send(cmd)
        
    def home_u(self):
        """Home the U (tool) axis"""
        cmd = "G28 U"
        self.send(cmd)
    
    def home_v(self):
        """Home the V axis"""
        cmd = "G28 V"
        self.send(cmd)
    
    def home_all(self):
        """Home all axes. This will look for the homeall.g macro-- ensure that this file homes any added axes (e.g. V)"""
        cmd = "G28"
        self.send(cmd)
       
    @machine_homed
    def _move_xyzev(self, x: float = None, y: float = None, z: float = None, e: float = None, v: float = None, s: float = 6000):
        """Move X/Y/Z/E/V axes. Set absolute/relative mode externally.

        Parameters
        ----------
        x: x position on the bed, in whatever units have been set (default mm)
        y: y position on the bed, in whatever units have been set (default mm)
        z: z position on the bed, in whatever units have been set (default mm)
        e: extruder position, in whatever units have been set (default mm)
        v: v axis position, in whatever units have been set (default mm)
        s: speed at which to move (default 6000 mm/min)

        Returns
        -------
        Nothing

        """
        if v and (v > 200.0 or v < 0):
                v=None
                raise Exception ('V cannot be less than O or greater than 200.0')

        
        x = "{0:.2f}".format(x) if x is not None else None
        y = "{0:.2f}".format(y) if y is not None else None
        z = "{0:.2f}".format(z) if z is not None else None
        e = "{0:.2f}".format(e) if e is not None else None
        v = "{0:.2f}".format(v) if v is not None else None
        s = "{0:.2f}".format(s)
        x_cmd = y_cmd = z_cmd = e_cmd = v_cmd = f_cmd = ''
        
        if x is not None:
            x_cmd = f'X{x}'
        if y is not None:
            y_cmd = f'Y{y}'
        if z is not None:
            z_cmd = f'Z{z}'
        if e is not None:
            e_cmd = f'E{e}'
        if v is not None:
            v_cmd = f'V{v}'
        if s is not None:
            f_cmd = f'F{s}'
        
        cmd = f"G0 {x_cmd} {y_cmd} {z_cmd} {e_cmd} {v_cmd} {f_cmd}"
        self.send(cmd)
        
    
    def move_to(self, x: float = None, y: float = None, z: float = None, e: float = None, v: float = None, s: float = 6000, force_extrusion: bool = True):
        """Move to an absolute X/Y/Z/E/V position.

        Parameters
        ----------
        x: x position on the bed, in whatever units have been set (default mm)
        y: y position on the bed, in whatever units have been set (default mm)
        z: z position on the bed, in whatever units have been set (default mm)
        e: extruder position, in whatever units have been set (default mm)
        v: v axis position, in whatever units have been set (default mm)
        s: speed at which to move (default 6000 mm/min)
        force_extrusion: whether to force extrusion to also be absolute positioning (default True)

        Returns
        -------
        Nothing

        """
        self._set_absolute_positioning()
        if force_extrusion:
            self._set_absolute_extrusion()
        
        self._move_xyzev(x = x, y = y, z = z, e = e, v = v, s = s)
        
    def move(self, dx: float = None, dy: float = None, dz: float = None, de: float = None, dv: float = None, s: float = 6000, force_extrusion: bool = True):
        """Move relative to the current position

        Parameters
        ----------
        dx: change in x position, in whatever units have been set (default mm)
        dy: change in y position, in whatever units have been set (default mm)
        dz: change in z position, in whatever units have been set (default mm)
        de: change in e position, in whatever units have been set (default mm)
        dv: change in v position, in whatever units have been set (default mm)
        s:  speed at which to move (default 6000 mm/min)
        force_extrusion: whether to force extrusion to also be relative positioning (default True)

        Returns
        -------
        Nothing

        """
        self._set_relative_positioning()
        if force_extrusion:
            self._set_relative_extrusion()
        
        self._move_xyzev(x = dx, y = dy, z = dz, e = de, v = dv, s = s)
        
    def dwell(self, t: float, millis: bool =True):
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
        
    def tool_change(self, tool_idx: int):
        """Change to specified tool"""
        # ToDo: use info from _configured_tools here to make sure tool exists, and address by human-readable name
        cmd = f'T{tool_idx}'
        self.send(cmd)
        
    def park_tool(self):
        """Deselect tool"""
        self.send("T-1")
        
    def px_to_real(x,y, relative = False):
        """Convert pixel location to bed location. Requires camera-machine calibration"""
        x = (x / self.img_size[0]) - 0.5
        y = (y / self.img_size[1]) - 0.5
        rel = 1 if relative else 0

        return (self.transform.T @ np.array([x**2, y**2, x * y, x, y, rel]))
        
    
    def get_position(self):
        """Get the current position, returns a dictionary with X/Y/Z/U/E/V keys"""
        # I've changed this; todo: check it all works
        response = self.send("M114")  
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

        return positions
    
    def aspirate(self, vol): # volume is in microliters. 50 is the max volume
        dv=(vol*-152.0/50)
        end_pos = float(self.getPosition()['V']) + dv
        self.moveTo(v=end_pos)
        
    def dispense(self, vol): # volume is in microliters. 50 is the max volume
        dv=(vol*152.0/50)
        end_pos = float(self.getPosition()['V']) + dv
        self.moveTo(v=end_pos)
        

    def aspirate_prime(self):
        self.moveTo(v=200*0.76)
        
    def eject_tip(self):
        self.moveTo(v=190.0)
        self.aspirate_prime()
                             
                             
        
    # ***************MACROS***************
    def tool_lock(self):
        """Runs Jubilee tool lock macro. Assumes tool_lock.g macro exists."""
        macro_file = "0:/macros/tool_lock.g"
        cmd = f"M98 P{macro_file}"
        self.send(cmd)
        
    def tool_unlock(self):
        """Runs Jubilee tool unlock macro. Assumes tool_unlock.g macro exists."""
        macro_file = "0:/macros/tool_unlock.g"
        cmd = f"M98 P{macro_file}"
        self.send(cmd)
        
    
        
        
        