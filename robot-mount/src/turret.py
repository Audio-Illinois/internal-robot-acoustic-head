import serial
import time
import numpy as np
import sys, time

# Constants
DEFAULT_PORT = 'COM4'
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 0.1
DEFAULT_STARTUP_DELAY = 2
USTEPS_PER_STEP = 4
STEPS_PER_REV = 200
OFFSET_HOME = 9
CMD_HOME = 'home'
CMD_MOVE = 'move'
RPS_QSCALE = 1000
DEFAULT_SPEED = 0.1
INT_MAX = 2**15 # 16 bit Arduino, unsigned

class Turret:
    def __init__(
            self,
            port:str=DEFAULT_PORT,
            baudrate:int=DEFAULT_BAUDRATE,
            timeout:float=DEFAULT_TIMEOUT,
            startup_delay:float=DEFAULT_STARTUP_DELAY,
        ):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        time.sleep(startup_delay) # Allow Arduino to initialize
        print ('Setup complete.')

    def GracefulExit(self):
        self.Home()        
        sys.exit(0)

    def Command(self, command:str, values=[], scales=None, block=True, on_start=None, on_end=None):
        '''
        Send a `command` string with a list of `values` (optional, int) along the serial port to the Arduino
        '''
        if scales is None: scales = np.ones(len(values), dtype=int)

        scaled = np.array([value*scale for value, scale in zip(values, scales)])
        assert np.allclose(scaled, scaled.astype(int)), f"{scaled}"
        assert np.all(abs(scaled) < INT_MAX)

        quantized = [str(int(value)) for value in scaled]
        packet = '\n'.join([command, *quantized, ''])

        log_packet = packet.replace("\n", " ")
        print(f'Command: {log_packet:<30}', end='' if on_start is None else '\n', flush=True)
        self.arduino.write(packet.encode())
        self.arduino.flush()

        if on_start is not None:
            on_start()
        print('\tStatus: ', end='', flush=True)

        if block:
            while True:
                from_arduino = self.arduino.readline().decode().strip()
                if from_arduino == command: # successful echo
                    if on_end is not None: on_end()
                    print ('Done')
                    break

    def Home(self, on_start=None, on_end=None):
        self.Command(CMD_HOME, on_start=on_start, on_end=on_end)
        self.Move(deg=-OFFSET_HOME,rps=DEFAULT_SPEED)
        self.Command(CMD_HOME, on_start=on_start, on_end=on_end)

    def Move(self, deg:int, rps:float=DEFAULT_SPEED, delay_ms:int=0, on_start=None, on_end=None):
        usteps = deg * USTEPS_PER_STEP * STEPS_PER_REV / 360.0
        if not np.isclose(usteps, int(usteps)):
            print (f'WARNING: {usteps:.3f} not int! Casted to {int(usteps)}')
            usteps = int(usteps)
        self.Command(
            CMD_MOVE,
            values=[rps, usteps, delay_ms],
            scales=[RPS_QSCALE, 1, 1],
            on_start=on_start,
            on_end=on_end
        )
